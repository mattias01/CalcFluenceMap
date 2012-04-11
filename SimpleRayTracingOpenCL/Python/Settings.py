# Platform
PLATFORM = 2 # 0: Windows NVidia, 1: Windows Intel, 2: OSX-CPU, 3: OSX-GPU, 4: AMD-CPU, 5: AMD-GPU

# Collimator defines
NUMBER_OF_LEAVES = 10

# Global defines
FLX = 128
FLY = 128
#XSTEP = 0.0
#YSTEP = 0.0
#XOFFSET = 0.0
#YOFFSET = 0.0
LSAMPLES = 20
LSAMPLESSQR = LSAMPLES*LSAMPLES
#LSTEP = 0.0

MODE = 0
NUMBER_OF_COLLIMATORS = 10

# Optimization parameters
LINE_TRIANGLE_INTERSECTION_ALGORITHM = 2 # SS, MT, MT2, MT3

# Work group sizes
if PLATFORM in [1, 2, 4]: # Best CPU
    WG_LIGHT_SAMPLING_X = 1
    WG_LIGHT_SAMPLING_Y = 1
    WG_LIGHT_SAMPLING_Z = 1
elif PLATFORM in [0]: # Best NVIDIA GTX 470
    WG_LIGHT_SAMPLING_X = 1
    WG_LIGHT_SAMPLING_Y = 4
    WG_LIGHT_SAMPLING_Z = 16
else:
    WG_LIGHT_SAMPLING_X = 2
    WG_LIGHT_SAMPLING_Y = 2
    WG_LIGHT_SAMPLING_Z = 4
WG_LIGHT_SAMPLING_SIZE = WG_LIGHT_SAMPLING_X * WG_LIGHT_SAMPLING_Y * WG_LIGHT_SAMPLING_Z

# Adress spaces. 0: private, 1: local, 2: constant, 3: global
RAY_AS = 0 # Valid: 0, 1.
LEAF_AS = 3 # Valid: 1, 3.
SCENE_AS = 2 # Valid: 2, 3. 2 only for osx-gpu

# Structure
STRUCTURE = 0 # Valid 0: Detpth first, 1: Breadth first.

# Run settings
OPENCL = 1
PYTHON = 0
SHOW_PLOT = 1
SHOW_3D_SCENE = 0
if PLATFORM in [0, 1, 4, 5]:
    PATH_OPENCL = "OpenCL/"
elif PLATFORM in [2, 3]:
    PATH_OPENCL = "/Users/mattias/Skola/exjobb/CalcFluenceMap/SimpleRayTracingOpenCL/OpenCL/"

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
    list.append(("STRUCTURE", str(STRUCTURE), True))
    
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