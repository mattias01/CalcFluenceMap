class Autotune(object):
    """Module to auto-tune parameters for OpenCL kernels"""
    def __init__(self, parameters, runFunc, initFunc, deinitFunc):
        self.parameterSet(parameters)
        self.runFunc = runFunc
        self.initFunc = initFunc
        self.deinitFunc = deinitFunc

    def run(self):
        self.runFunc(parameterSet.getRunParameters())
