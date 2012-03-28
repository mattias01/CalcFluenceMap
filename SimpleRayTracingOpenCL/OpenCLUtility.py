import pyopencl as cl

class OpenCLUtility(object):
    """Utility class for OpenCL"""
    def __init__(self):
        self.fstr = None

    def readFile(self, filename):
        f = open(filename, 'r')
        return "".join(f.readlines())

    def loadCachedProgram(self, context, filename, buildOptions=[]):
        if self.fstr == None:
            self.fstr = self.readFile(filename)
        program = cl.Program(context, self.fstr).build(options=buildOptions)
        return program

    def loadProgram(context, filename, buildOptions=[]):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())
        f.close()
        #print fstr
        #create the program
        program = cl.Program(context, fstr).build(options=buildOptions)
        return program

    loadProgram = staticmethod(loadProgram)
