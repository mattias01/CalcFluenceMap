class Parameter(object):
    """Parameter class"""
    def __init__(self, name, values, sendToKernel=False):
        """name is a string, values is a list"""
        self.name = name
        self.values = values
        self.currentIndex = 0
        self.valueLength = len(self.values)
        self.sendToKernel = sendToKernel

    def initWithInterval(self, start, stop, stride):
        values = xrange(start, stop, stride)
        return self.__init__(name, values)

    def current(self):
        return self.values[self.currentIndex]

    def next(self):
        """Current parameter value is set to the next parameter value.
        Returns 0 if it was successful, 1 if reached end and restarted."""
        self.currentIndex += 1
        if self.currentIndex < len(values):
            result = 0
        else:
            result = 1
            self.currentIndex = 0
        return result

    #Initializers
    initWithInterval = staticmethod(initWithInterval)