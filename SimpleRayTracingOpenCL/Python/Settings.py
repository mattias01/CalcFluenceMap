
# Collimator defines
NUMBER_OF_LEAVES = 40

# Global defines
FLX = 256
FLY = 256
LSAMPLES = 20
MODE = 2
NUMBER_OF_COLLIMATORS = 4
LINE_TRIANGLE_INTERSECTION_ALGORITHM = 1 # SS, MT, MT2, MT3, MT4 (does not work)
SOA = 1

# Work group sizes
WG_LIGHT_SAMPLING_X = 2
WG_LIGHT_SAMPLING_Y = 32
WG_LIGHT_SAMPLING_Z = 4
#WG_LIGHT_SAMPLING_X = 1
#WG_LIGHT_SAMPLING_Y = 16
#WG_LIGHT_SAMPLING_Z = 4

# Adress spaces. 0: private, 1: local, 2: constant (not working), 3: global (not implemented)
RAY_AS = 0 # Valid 0, 1.
LEAF_AS = 1 # Valid 1, 3.

# Run settings
OPENCL = 1
PYTHON = 0
SHOW_PLOT = 1
SHOW_3D_SCENE = 0

# Returns a string with all the settings as compiler arguments that can be passed to the OpenCL compiler to define macros.
def settingsString():
    return "-D NUMBER_OF_LEAVES=" + str(NUMBER_OF_LEAVES) + " -D FLX=" + str(FLX) + " -D FLY=" + str(FLY) + " -D LSAMPLES=" + str(LSAMPLES) + " -D MODE=" + str(MODE) + " -D NUMBER_OF_COLLIMATORS=" + str(NUMBER_OF_COLLIMATORS) + " -D LINE_TRIANGLE_INTERSECTION_ALGORITHM=" + str(LINE_TRIANGLE_INTERSECTION_ALGORITHM) + " -D SOA=" + str(SOA) + " -D WG_LIGHT_SAMPLING_X=" + str(WG_LIGHT_SAMPLING_X) + " -D WG_LIGHT_SAMPLING_Y=" + str(WG_LIGHT_SAMPLING_Y) + " -D WG_LIGHT_SAMPLING_Z=" + str(WG_LIGHT_SAMPLING_Z) + " -D RAY_AS=" + str(RAY_AS) + " -D LEAF_AS=" + str(LEAF_AS)