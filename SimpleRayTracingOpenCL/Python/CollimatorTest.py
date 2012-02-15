from OpenCLTypes import *
from Python.Collimator import *
from Python.Primitives import *

def testCreateFlatCollimator():
    collimator = Collimator2()
    collimator.boundingBox = Box(float4(-3.5,-3.5,-91,0), float4(3.5,-2.5,-90,0))
    collimator.position = float4(-3.5,-3.5,-90,0)
    collimator.xdir = float4(0,1,0,0)
    collimator.ydir = float4(1,0,0,0)
    collimator.attenuation = 0.5
    collimator.height = 1
    collimator.leafWidth = 3.5
    collimator.numberOfLeaves = 2
    collimator.leafPositions = (0.5,1)
    fc = createFlatCollimator2(collimator)
    if fc.leaves[0].p0 == float4(-3.5,-3.5,-90,0) and fc.leaves[1].p2 == float4(3.5,-2.5,-90,0):
         return True
    else:
        print "createFlatCollimator FAILED"
        return False

def collimatorTest():
    passed = False
    if testCreateFlatCollimator():
        passed = True
    else:
        passed = False

    if passed == True:
        print "Python Collimator unit tests PASSED"
    else:
        print "Python Collimator unit tests FAILED"

    return passed