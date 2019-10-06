import os
from . import cigarHandle


class MappingLine(object):

    __slots__ = ["transcriptID", "contig", "transcriptStart", "cigar", "direction"]

    def __init__(self, rawInputLine:str, delimiter:str="\t", processCigar:bool=True):
        lineSplit = rawInputLine.strip().split(delimiter)
        if len(lineSplit) == 4:
            lineSplit.append(1)
        assert len(lineSplit) == 5, "Input lines must be four or five elements long, with the first four being transcript ID, contig (chromosome), transcript start position, and cigar string, and the last optional value being direction (1 or -1). %s was given." %rawInputLine
        self.transcriptID, self.contig, self.transcriptStart, self.cigar, self.direction = lineSplit
        try:
            self.transcriptStart = int(self.transcriptStart)
        except ValueError:
            raise ValueError("Transcript start needs to be an integer value. %s was given." %self.transcriptStart)
        try:
            self.direction = int(self.direction)
        except ValueError:
            raise ValueError("Transcript direction (if given) must be either 1 or -1. %s was given." %self.direction)
        if not abs(self.direction) == 1:
            raise ValueError("Transcript direction (if given) must be either 1 or -1. %s was given." % self.direction)
        if processCigar:
            cigarOperators = cigarHandle.makeValidatedCigarOperatorSet(cigarHandle.basicCigarOperators)
            self.cigar = cigarHandle.CigarString(self.cigar, cigarOperators)


    def __str__(self):
        printList = [self.transcriptID, self.contig, self.transcriptStart, self.direction]
        printList = [str(item) for item in printList]
        return "\t".join(printList)


class QueryLine(object):

    __slots__ = ["transcriptID", "position"]

    def __init__(self, rawInputLine:str, delimiter:str="\t"):
        lineSplit = rawInputLine.strip().split(delimiter)
        assert len(lineSplit) == 2, "Query lines must be exactly two elements long, with the first being the transcript ID and the second being the position. %s was given." %rawInputLine
        self.transcriptID, self.position = lineSplit
        try:
            self.position = int(self.position)
        except ValueError:
            raise ValueError("Position must be a non-negative integer. %s was given." %self.position)
        if self.position < 0:
            raise ValueError("Position must be a non-negative integer. %s was given." %self.position)

    def __str__(self):
        printList = [self.transcriptID, self.position]
        printList = [str(item) for item in printList]
        return "\t".join(printList)


def readMappingFile(path:str):
    if not os.path.isfile(path):
        raise FileNotFoundError("Unable to find mapping file at %s" %path)
    file = open(path, 'r')
    transcriptMaps = {}
    for line in file:
        line = line.strip()
        if not line:
            continue
        mappingLine = MappingLine(line)
        if mappingLine.transcriptID in transcriptMaps:
            raise DuplicateTranscriptMapError("Found a duplicate map for transcript %s in the file. Please check file integrity and correct this issue." %mappingLine.transcriptID)
        transcriptMaps[mappingLine.transcriptID] = mappingLine
    file.close()
    return transcriptMaps


def readQueryFile(path:str):
    if not os.path.isfile(path):
        raise FileNotFoundError("Unable to find query file at %s" %path)
    file = open(path, 'r')
    queries = []
    for line in file:
        line = line.strip()
        if not line:
            continue
        queries.append(QueryLine(line))
    file.close()
    return queries


class DuplicateTranscriptMapError(Exception):
    pass