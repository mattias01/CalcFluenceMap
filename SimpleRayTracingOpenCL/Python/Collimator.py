from ctypes import *
from Python.Primitives import *

###################### Class definitions ######################

class SimpleCollimator(Structure):
    _fields_ = [("leftRectangle", Rectangle),
                ("rightRectangle", Rectangle)]

class FlatCollimatorRect(Structure):
    __fields__ = [("boundingBox", Box),
                  ("noOfBlades", c_int),
                  ("blades", Rectangle*2)]

class FlatCollimator(Structure):
    __fields__ = [("boundingBox", Box),
                  ("noOfBlades", c_int),
                  ("spacing", c_float),
                  ("blades", c_float*2)]

###################### Intersection calculations ######################

def intersectLineSimpleCollimator(line, collimator):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leftRectangle)
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.rightRectangle)

    return [intersect, intersectionDistance, intersectionPoint]
