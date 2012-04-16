# Init all variables
AUTOTUNE = 0
PLATFORM = 0
NUMBER_OF_LEAVES = 0
NUMBER_OF_COLLIMATORS = 0
PIECES = 0
FLX = 0
FLY = 0
LSAMPLES = 0
LSAMPLESSQR = 0
MODE = 0
LINE_TRIANGLE_INTERSECTION_ALGORITHM = 0
WG_LIGHT_SAMPLING_X = 0
WG_LIGHT_SAMPLING_Y = 0
WG_LIGHT_SAMPLING_Z = 0
WG_LIGHT_SAMPLING_SIZE = 0
RAY_AS = 0
LEAF_AS = 0
SCENE_AS = 0
OPENCL = 0
PYTHON = 0
SHOW_PLOT = 0
SHOW_3D_SCENE = 0
PATH_OPENCL = ""

def getDefaultSettingsList():
    list = []
    list.append(("PLATFORM", str(PLATFORM), True))
    list.append(("NUMBER_OF_LEAVES", str(NUMBER_OF_LEAVES), True))
    list.append(("FLX", str(FLX), True))
    list.append(("FLY", str(FLY), True))
    list.append(("LSAMPLES", str(LSAMPLES), True))
    list.append(("LSAMPLESSQR", str(LSAMPLESSQR), True))
    list.append(("MODE", str(MODE), True))
    list.append(("NUMBER_OF_COLLIMATORS", str(NUMBER_OF_COLLIMATORS), True)) 
    list.append(("PATH_OPENCL", str(PATH_OPENCL), True))
    return list

def getDefaultOptimizationParameterList():
    list = []
    list.append(("LINE_TRIANGLE_INTERSECTION_ALGORITHM", str(LINE_TRIANGLE_INTERSECTION_ALGORITHM), True))
    list.append(("WG_LIGHT_SAMPLING_X", str(WG_LIGHT_SAMPLING_X), False))
    list.append(("WG_LIGHT_SAMPLING_Y", str(WG_LIGHT_SAMPLING_Y), False))
    list.append(("WG_LIGHT_SAMPLING_Z", str(WG_LIGHT_SAMPLING_Z), False))
    #list.append(("WG_LIGHT_SAMPLING_SIZE", str(WG_LIGHT_SAMPLING_SIZE), True))
    list.append(("RAY_AS", str(RAY_AS), True))
    list.append(("LEAF_AS", str(LEAF_AS), True))
    list.append(("SCENE_AS", str(SCENE_AS), True))
    
    return list

# Argument list is a list of tupels with the first element being the macro name and the second its value.
def macroString(list):
    s = "-I " + PATH_OPENCL
    for x in list:
        if x[2] == True: # x[0]: name, x[1]: value, x[2]: sendToKernel
            s += " -D " + x[0] + "=" + str(x[1])
    return s

# Returns a string with all the settings as compiler arguments that can be passed to the OpenCL compiler to define macros.
def settingsString():
    return "-D NUMBER_OF_LEAVES=" + str(NUMBER_OF_LEAVES) + " -D FLX=" + str(FLX) + " -D FLY=" + str(FLY) + " -D LSAMPLES=" + str(LSAMPLES) + " -D MODE=" + str(MODE) + " -D NUMBER_OF_COLLIMATORS=" + str(NUMBER_OF_COLLIMATORS) + " -D LINE_TRIANGLE_INTERSECTION_ALGORITHM=" + str(LINE_TRIANGLE_INTERSECTION_ALGORITHM) + " -D WG_LIGHT_SAMPLING_X=" + str(WG_LIGHT_SAMPLING_X) + " -D WG_LIGHT_SAMPLING_Y=" + str(WG_LIGHT_SAMPLING_Y) + " -D WG_LIGHT_SAMPLING_Z=" + str(WG_LIGHT_SAMPLING_Z) + " -D RAY_AS=" + str(RAY_AS) + " -D LEAF_AS=" + str(LEAF_AS) + " -I " + str(PATH_OPENCL) + " -I " + "OpenCL/" + " -D XSTEP=" + str(XSTEP) + " -D YSTEP=" + str(YSTEP) + " -D XOFFSET=" + str(XOFFSET) + " -D YOFFSET=" + str(YOFFSET) + " -D LSTEP=" + str(LSTEP)
