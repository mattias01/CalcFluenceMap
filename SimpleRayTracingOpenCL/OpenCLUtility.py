import pyopencl as cl

class OpenCLUtility(object):
    """Utility class for OpenCL"""
    def __init__(self):
        self

    def loadProgram(context, filename):
        #read in the OpenCL source file as a string
        f = open(filename, 'r')
        fstr = "".join(f.readlines())
        #print fstr
        #create the program
        return cl.Program(context, fstr).build()

    loadProgram = staticmethod(loadProgram)
