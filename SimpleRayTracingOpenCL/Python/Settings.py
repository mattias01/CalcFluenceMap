
# Collimator defines
NUMBER_OF_LEAVES = 40

# Global defines
FLX = 128
FLY = 128
#XSTEP = 0.0
#YSTEP = 0.0
#XOFFSET = 0.0
#YOFFSET = 0.0
LSAMPLES = 20
#LSTEP = 0.0
MODE = 2
NUMBER_OF_COLLIMATORS = 4
LINE_TRIANGLE_INTERSECTION_ALGORITHM = 1 # SS, MT, MT2, MT3
SOA = 1

# Work group sizes
#WG_LIGHT_SAMPLING_X = 1
#WG_LIGHT_SAMPLING_Y = 1
#WG_LIGHT_SAMPLING_Z = 1
WG_LIGHT_SAMPLING_X = 1
WG_LIGHT_SAMPLING_Y = 32
WG_LIGHT_SAMPLING_Z = 8
#WG_LIGHT_SAMPLING_X = 2
#WG_LIGHT_SAMPLING_Y = 16
#WG_LIGHT_SAMPLING_Z = 2

# Adress spaces. 0: private, 1: local, 2: constant, 3: global
RAY_AS = 0 # Valid: 0, 1.
LEAF_AS = 1 # Valid: 1, 3.
SCENE_AS = 2 # Valid: 2, 3.

# Run settings
OPENCL = 1
PYTHON = 0
SHOW_PLOT = 1
SHOW_3D_SCENE = 0
PATH_OPENCL = "OpenCL/"
#PATH_OPENCL = "/Users/mattias/Skola/exjobb/CalcFluenceMap/SimpleRayTracingOpenCL/OpenCL/"

def getDefaultSettingsList():
    list = []
    list.append(("NUMBER_OF_LEAVES", str(NUMBER_OF_LEAVES)))
    list.append(("FLX", str(FLX)))
    list.append(("FLY", str(FLY)))
    list.append(("LSAMPLES", str(LSAMPLES)))
    list.append(("MODE", str(MODE)))
    list.append(("NUMBER_OF_COLLIMATORS", str(NUMBER_OF_COLLIMATORS)))
    list.append(("LINE_TRIANGLE_INTERSECTION_ALGORITHM", str(LINE_TRIANGLE_INTERSECTION_ALGORITHM)))
    list.append(("SOA", str(SOA)))
    list.append(("WG_LIGHT_SAMPLING_X", str(WG_LIGHT_SAMPLING_X)))
    list.append(("WG_LIGHT_SAMPLING_Y", str(WG_LIGHT_SAMPLING_Y)))
    list.append(("WG_LIGHT_SAMPLING_Z", str(WG_LIGHT_SAMPLING_Z)))
    list.append(("RAY_AS", str(RAY_AS)))
    list.append(("LEAF_AS", str(LEAF_AS)))
    list.append(("SCENE_AS", str(SCENE_AS)))
    list.append(("PATH_OPENCL", str(PATH_OPENCL)))
    return list

# Argument list is a list of tupels with the first element being the macro name and the second its value.
def macroString(list):
    s = "-I " + PATH_OPENCL + " -I OpenCL/"
    for x in list:
        s += " -D " + x[0] + "=" + str(x[1])
    return s

# Returns a string with all the settings as compiler arguments that can be passed to the OpenCL compiler to define macros.
def settingsString():
    return "-D NUMBER_OF_LEAVES=" + str(NUMBER_OF_LEAVES) + " -D FLX=" + str(FLX) + " -D FLY=" + str(FLY) + " -D LSAMPLES=" + str(LSAMPLES) + " -D MODE=" + str(MODE) + " -D NUMBER_OF_COLLIMATORS=" + str(NUMBER_OF_COLLIMATORS) + " -D LINE_TRIANGLE_INTERSECTION_ALGORITHM=" + str(LINE_TRIANGLE_INTERSECTION_ALGORITHM) + " -D SOA=" + str(SOA) + " -D WG_LIGHT_SAMPLING_X=" + str(WG_LIGHT_SAMPLING_X) + " -D WG_LIGHT_SAMPLING_Y=" + str(WG_LIGHT_SAMPLING_Y) + " -D WG_LIGHT_SAMPLING_Z=" + str(WG_LIGHT_SAMPLING_Z) + " -D RAY_AS=" + str(RAY_AS) + " -D LEAF_AS=" + str(LEAF_AS) + " -I " + str(PATH_OPENCL) + " -I " + "OpenCL/" + " -D XSTEP=" + str(XSTEP) + " -D YSTEP=" + str(YSTEP) + " -D XOFFSET=" + str(XOFFSET) + " -D YOFFSET=" + str(YOFFSET) + " -D LSTEP=" + str(LSTEP)