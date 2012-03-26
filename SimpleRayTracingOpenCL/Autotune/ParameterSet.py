from Autotune.Parameter import Parameter

class ParameterSet(object):
    def __init__(self, parameters):
        self.parameters = parameters
    
    # Get all parameters as a tuple
    def getRunParametersTuple(self):
        tuple = ()
        for x in self.parameters:
            tuple += x.start
        return tuple

    def getRunParametersList(self):
        list = []
        for x in self.parameters:
            list.append(x.name)
            list.append(x.start)
        return list