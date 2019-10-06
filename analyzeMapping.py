import mapperSupport

def readInputs(mapFilePath:str, queryFilePath:str):
    transcriptMaps = mapperSupport.inputReader.readMappingFile(mapFilePath)
    queryList = mapperSupport.inputReader.readQueryFile(queryFilePath)
    for query in queryList:
        if not query.transcriptID in transcriptMaps:
            raise KeyError("A query was submitted for transcript %s, but this transcript was not found in the mapping data. Found transcripts: %s" %(query.transcriptID, list(transcriptMaps.keys())))
    return transcriptMaps, queryList

def calculateMapPositionByTranscript(transcriptMap:mapperSupport.inputReader.MappingLine, query:mapperSupport.inputReader.QueryLine):
    readPosition = 0
    referencePosition = transcriptMap.transcriptStart
    for count, operator in transcriptMap.cigar:
        for i in range(count):
            if readPosition >= query.position:
                return referencePosition
            readPosition += operator.readAdvance
            referencePosition += operator.refAdvance * transcriptMap.direction
    if readPosition >= query.position:
        return referencePosition
    raise ValueError("Query appears to be beyond the end of the transcript. Query: %s. Mapping: %s" %(query, transcriptMap))

def generateMappingData(transcriptMaps:dict, query:mapperSupport.inputReader.QueryLine):
    if not query.transcriptID in transcriptMaps:
        raise KeyError("Transcript %s from query %s was not found in transcript maps. Transcripts in transcript maps: %s" %(query.transcriptID, query, list(transcriptMaps.keys())))
    transcriptMap = transcriptMaps[query.transcriptID]
    mapPosition = calculateMapPositionByTranscript(transcriptMap, query)
    return query.transcriptID, query.position, transcriptMap.contig, mapPosition


if __name__ == "__main__":
    transcriptMaps, queryList = readInputs("sampleMap.txt", "sampleQueries.txt")

    mappingResults = [] #if this gets beyond trivial numbers of queries, use my easyMultiprocessing library here as I'm setting up an embarrassingly parallel problem for this block
    for query in queryList:
        mappingResults.append(generateMappingData(transcriptMaps, query))

    mappingResultTextLines = []
    for result in mappingResults:
        mappingResultTextLines.append("\t".join([str(item) for item in result]))
    resultText = "\n".join(mappingResultTextLines)
    outputFile = open("results.txt", 'w')
    outputFile.write(resultText)
    outputFile.close()