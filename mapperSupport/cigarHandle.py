import re
from . import validations

class CigarOperator(object):

    __slots__ = ["character", "description", "readAdvance", "refAdvance", "presentInRead", "presentInRef", "match", "mismatch"]

    def __init__(self, character:str, description:str, refAdvance:int, readAdvance:int, match:bool=False, mismatch:bool=False, presentInRead:bool=True, presentInRef:bool=True):
        assert type(character) == str and len(character) == 1, "Character value for cigar operator must be a single character of string type. %s of %s type was given." %(character, type(character))
        validations.isValidType(description, "Operator meaning description (description)", str)
        validations.isValidType(refAdvance, "Reference position advance (refAdvance)", int)
        validations.isValidType(readAdvance, "Read position advance (readAdvance)", int)
        validations.isValidType(match, "Read base matches reference (match)", bool)
        validations.isValidType(mismatch, "Read base mismatch to reference (mismatch)", bool)
        validations.isValidType(presentInRead, "Base present in read (presentInRead)", bool)
        validations.isValidType(presentInRef, "Base is present in reference (presentInRef)", bool)
        assert not (match and mismatch), "No operator can indicate read both matches and mismatches reference. It is logically impossible."
        self.character = character
        self.description = description
        self.refAdvance = refAdvance
        self.readAdvance = readAdvance
        self.presentInRead = presentInRead
        self.match = match
        self.mismatch = mismatch
        self.presentInRead = presentInRead
        self.presentInRef = presentInRef

    def __str__(self):
        return self.character


cigarOperatorReferenceTable = {
#                       ID | Description      |  Ref Adv  |  Read Adv  |  Match  |  Mismatch  |  In Read  |  In Ref
    "D" : CigarOperator("D", "Deletion",            1,         0,         False,    False,        False,     True ),
    "H" : CigarOperator("H", "Hard Clip",           1,         0,         False,    False,        False,     True ),
    "I" : CigarOperator("I", "Insertion",           0,         1,         False,    False,        True,      False),
    "M" : CigarOperator("M", "Position Match",      1,         1,         False,    False,        True,      True ),
    "N" : CigarOperator("N", "Skipped",             1,         0,         False,    False,        False,     True ),
    "P" : CigarOperator("P", "Padding",             0,         0,         False,    False,        False,     False),
    "S" : CigarOperator("S", "Soft Clip",           1,         1,         False,    False,        True,      True ),
    "X" : CigarOperator("X", "Base mismatch",       1,         1,         False,    True,         True,      True ),
    "=" : CigarOperator("=", "Base match",          1,         1,         True,     False,        True,      True )
}


basicCigarOperators = "DMI"
expandedCigarOperators = "".join(cigarOperatorReferenceTable.keys())


def makeValidatedCigarOperatorSet(operatorSet:[str, tuple, list, set]):
    operatorSet = set(operatorSet)
    validatedOperatorSet = set()
    for character in operatorSet:
        if not type(character) == str:
            raise ValueError("Operator set must contain only characters. %s was found of %s type.\nOperator set: %s" %(character, type(character), operatorSet))
        if not character.upper() in cigarOperatorReferenceTable:
            raise KeyError("%s not in valid cigar operators. Valid cigar operators are %s. Custom cigar operators can be added to cigarHandle.cigarOperatorReferenceTable as key:value for a standard dictionary where keys are single characters and values are of cigarHandle.CigarOperator type." % (character, list(cigarOperatorReferenceTable.keys())))
        validatedOperatorSet.add(character.upper())
    validOperatorDict = {}
    for operator in validatedOperatorSet:
        validOperatorDict[operator] = cigarOperatorReferenceTable[operator]
    return validOperatorDict


defaultCigarOperators = makeValidatedCigarOperatorSet(expandedCigarOperators)


def cigarCutter(cigarString:str, cigarOperators:dict=defaultCigarOperators):
    operators = re.split(r'\d+', cigarString)
    operators = [operator for operator in operators if operator]
    counts = re.split(r'\D+', cigarString)
    counts = [int(count) for count in counts if count]
    basicCigarTable = zip(counts, operators)
    advancedCigarTable = []
    for count, operator in basicCigarTable:
        assert count > 0, "Invalid cigar count found in cigar table. Value: %s. Table: %s. Values must be positive integers." %(count, basicCigarTable)
        assert operator in cigarOperators, "Invalid cigar operator found in cigar table. Operator: %s. Table: %s. Valid operators: %s." %(operator, basicCigarTable, list(cigarOperators.keys()))
        advancedCigarTable.append((count, cigarOperators[operator]))
    return tuple(advancedCigarTable)


class CigarString(object):

    __slots__ = ["cigarString", "cigarTable", "index"]

    def __init__(self, cigarString:str, cigarOperators:dict=defaultCigarOperators):
        self.cigarString = cigarString
        self.cigarTable = cigarCutter(cigarString, cigarOperators)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index >= len(self.cigarTable):
            raise StopIteration
        returnValue = self.cigarTable[self.index]
        self.index += 1
        return returnValue

    def __str__(self):
        return self.cigarString


