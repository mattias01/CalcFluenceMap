from ctypes import *
from OpenCLTypes import *
from Python.Primitives import *

###################### Class definitions ######################

class SimpleCollimator(Structure):
    _fields_ = [("leftRectangle", Rectangle),
                ("rightRectangle", Rectangle)]

class FlatCollimator(Structure):
    _fields_ = [("boundingBox", Box),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", Rectangle * 40)]

class BoxCollimator(Structure):
    _fields_ = [("boundingBox", Box),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", Box * 40)]

class Collimator(Structure):
    _fields_ = [("boundingBox", Box),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("height", c_float),
                ("leafWidth", c_float),
                ("numberOfLeaves", c_int),
                ("leafPositions", c_float * 40),
                ("flatCollimator", FlatCollimator),
                ("boxCollimator", BoxCollimator)]

###################### Collimator generation ######################

def calculateCollimatorBoundingBox(collimator):
    maxPosition = 0
    for i in range(collimator.numberOfLeaves):
        if maxPosition < collimator.leafPositions[i]:
            maxPosition = collimator.leafPositions[i]

    x = normalize(collimator.xdir) * maxPosition
    y = normalize(collimator.ydir) * collimator.numberOfLeaves * collimator.leafWidth
    down = normalize(cross(collimator.xdir, collimator.ydir))*collimator.height

    p0 = collimator.position
    p1 = p0 + down
    p2 = p0 + down + y
    p3 = p0 + y
    p4 = p0 + x
    p5 = p4 + down
    p6 = p4 + down + y
    p7 = p4 + y

    return boundingBox(p0, p1, p2, p3, p4, p5, p6, p7)

def createRectangles(position, xdir, ydir, rectangleWidth, numberOfRect, rectangleLength):
    rectangle_array = Rectangle * 40
    rectangles = rectangle_array()
    x = normalize(xdir)
    y = normalize(ydir)*rectangleWidth
    for i in range(numberOfRect):
        rectangles[i] = Rectangle(position + y*i, position + y*(i+1), position + x*rectangleLength[i] + y*(i+1), position + y*i + x*rectangleLength[i])
    
    return rectangles

def createBoxes(position, xdir, ydir, boxHeight, boxWidth, numberOfBoxes, boxLength):
    box_array = Box * 40
    boxes = box_array()
    x = normalize(xdir)
    y = normalize(ydir)*boxWidth
    z = normalize(cross(xdir, ydir))*boxHeight
    for i in range(numberOfBoxes):
        boxes[i] = boundingBox(position + y*i, position + y*(i+1), position + x*boxLength[i] + y*(i+1), position + y*i + x*boxLength[i],
                               position + y*i + z, position + y*(i+1) + z, position + x*boxLength[i] + y*(i+1) + z, position + y*i + x*boxLength[i] + z)

    return boxes

def createFlatCollimator(collimator):
    plane = Plane(collimator.position, cross(collimator.xdir, collimator.ydir)) # Plane perpendicular to xdir and ydir.
    bbox = Box(projectPointOntoPlane(collimator.boundingBox.min, plane), projectPointOntoPlane(collimator.boundingBox.max, plane))
    leaves = createRectangles(collimator.position, collimator.xdir, collimator.ydir, collimator.leafWidth, collimator.numberOfLeaves, collimator.leafPositions)
    fc = FlatCollimator()
    fc.boundingBox = bbox
    fc.position = collimator.position
    fc.xdir = collimator.xdir
    fc.ydir = collimator.ydir
    fc.absorptionCoeff = collimator.absorptionCoeff
    fc.numberOfLeaves = collimator.numberOfLeaves
    fc.leaves = leaves
    return fc

def createBoxCollimator(collimator):
    boxes = createBoxes(collimator.position, collimator.xdir, collimator.ydir, collimator.height, collimator.leafWidth, collimator.numberOfLeaves, collimator.leafPositions)
    bc = BoxCollimator()
    bc.boundingBox = collimator.boundingBox
    bc.position = collimator.position
    bc.xdir = collimator.xdir
    bc.ydir = collimator.ydir
    bc.absorptionCoeff = collimator.absorptionCoeff
    bc.numberOfLeaves = collimator.numberOfLeaves
    bc.leaves = boxes
    return bc

###################### Intersection calculations ######################

def intersectLineSimpleCollimator(line, collimator):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leftRectangle)
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.rightRectangle)

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineFlatCollimator(line, collimator):
    #[intersectBBox, intersectionDistanceBBox, intersectionPointBBox] = intersectLineBox(line, collimator.boundingBox)
    #if intersectBBox:
    for i in range(collimator.numberOfLeaves):
        [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leaves[i])
        if intersect:
            return [intersect, intersectionDistance, intersectionPoint]

    return [False, None, None]

def intersectLineBoxCollimator(line, collimator):
    #[intersectBBox, intersectionDistanceBBox, intersectionPointBBox] = intersectLineBox(line, collimator.boundingBox)
    #if intersectBBox:
    for i in range(collimator.numberOfLeaves):
        [intersect, intersectionDistanceIn, intersectionDistanceOut, intersectionPointIn, intersectionPointOut] = intersectLineBoxInOut(line, collimator.leaves[i])
        if intersect:
            return [intersect, intersectionDistanceIn, intersectionPointIn, intersectionDistanceOut-intersectionDistanceIn]

    return [False, None, None, None]
