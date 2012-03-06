
# Collimator defines
NUMBER_OF_LEAVES = 40

# Global defines
FLX = 64
FLY = 64
LSAMPLES = 10
MODE = 2

# Returns a string with all the settings as compiler arguments that can be passed to the OpenCL compiler to define macros.
def settingsString():
    return "-D NUMBER_OF_LEAVES=" + str(NUMBER_OF_LEAVES) + " -D FLX=" + str(FLX) + " -D FLY=" + str(FLY) + " -D LSAMPLES=" + str(LSAMPLES) + " -D MODE=" + str(MODE)