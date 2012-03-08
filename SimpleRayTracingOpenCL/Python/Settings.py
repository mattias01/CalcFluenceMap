
# Collimator defines
NUMBER_OF_LEAVES = 40

# Global defines
FLX = 128
FLY = 128
LSAMPLES = 10
MODE = 2
NUMBER_OF_COLLIMATORS = 4
LINE_TRIANGLE_INTERSECTION_ALGORITHM = 1 # SS, MT, MT2, MT3, MT4 (does not work)

# Returns a string with all the settings as compiler arguments that can be passed to the OpenCL compiler to define macros.
def settingsString():
    return "-D NUMBER_OF_LEAVES=" + str(NUMBER_OF_LEAVES) + " -D FLX=" + str(FLX) + " -D FLY=" + str(FLY) + " -D LSAMPLES=" + str(LSAMPLES) + " -D MODE=" + str(MODE) + " -D NUMBER_OF_COLLIMATORS=" + str(NUMBER_OF_COLLIMATORS) + " -D LINE_TRIANGLE_INTERSECTION_ALGORITHM=" + str(LINE_TRIANGLE_INTERSECTION_ALGORITHM)