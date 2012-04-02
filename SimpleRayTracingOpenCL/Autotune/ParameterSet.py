#from Autotune import Parameter
import itertools

class ParameterSet(object):
    def __init__(self, parameters):
        self.parameters = parameters
        self.stateSpaceIterator = self.generateStateSpaceIterator()

    def getNumberOfStates(self):
        result = 0
        if len(self.parameters) != 0:
            result = 1
            for x in self.parameters:
                result *= x.valueLength
        return result

    def getRunParametersTuple(self):
        """Get all parameters as a tuple"""
        tuple = ()
        for x in self.parameters:
            tuple += (x.name, x.current(), x.sendToKernel)
        return tuple

    def getRunParametersTupleOnlyValues(self):
        """Get values of all parameters as a tuple"""
        tuple = ()
        for x in self.parameters:
            tuple += (x.current(),)
        return tuple

    def getRunParametersList(self):
        """Get all parameters as a list"""
        list = []
        for x in self.parameters:
            list.append((x.name, x.current(), x.sendToKernel))
        return list

    def getRunParametersListOnlyNames(self):
        """Get all parameters as a list"""
        list = []
        for x in self.parameters:
            list.append(x.name)
        return list

    def generateStateSpaceIterator(self):
        listOfIndices = []
        for x in self.parameters:
            listOfIndices.append(range(x.valueLength))
        return itertools.product(*listOfIndices)

    def next(self):
        """Current state is set to the next state in the parameter state space.
        Returns 0 if it was successful, 1 if reached end and restarted."""
        valueIndices = list(self.stateSpaceIterator.next())
        for i in range(len(valueIndices)):
            self.parameters[i].currentIndex = valueIndices[i]

        #for currentParameter in range(parameters):
            
        """result = self.parameters[self.currentParameterIndex].next()
        if result == 1:
            while self.parameters[self.currentParameterIndex].next() == 1: # Find next parameter that has more than one state.
                self.current_parameter += 1
            if self.currentParameterIndex < len(parameters): # More parameters to vary.
                result = 0
            else:
                self.currentParameterIndex = 0 # Restart
        return result"""

    def toStringCurrent(self):
        string = ""
        for x in self.parameters:
            string += x.name + " " + str(x.current()) + " "
        return string

    def toStringCurrentValue(self):
        string = ""
        for x in self.parameters:
            string += str(x.current()) + " "
        return string