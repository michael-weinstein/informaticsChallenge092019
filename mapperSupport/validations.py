import collections

def isValidType(valueToCheck, name:str, validTypes:[str, type, list], throwException:bool=True):
    if not type(validTypes) == list:
        validTypes = [validTypes]
    for index, value in enumerate(validTypes):
        if value == "iterable":
            validTypes[index] = collections.Iterable
    if type(valueToCheck) in validTypes:
        return True
    else:
        if throwException:
            raise TypeError("%s must be of the following types: %s. %s of type %s was given." %(name, validTypes, valueToCheck, type(valueToCheck)))
        else:
            return False