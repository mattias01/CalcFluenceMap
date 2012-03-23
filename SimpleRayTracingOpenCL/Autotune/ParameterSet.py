class ParameterSet(object):
    def __init__(self, parameters):
        self.parameters = parameters
    
    # Get all parameters as a tuple
    def getRunParameters(self):
        tuple = ()
        for x in self.parameters:
            tuple += x.start
        return tuple