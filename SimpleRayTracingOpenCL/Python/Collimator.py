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
                ("attenuation", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", Rectangle * 40)]

class Collimator(Structure):
    _fields_ = [("boundingBox", Box),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("attenuation", c_float),
                ("height", c_float),
                ("leafWidth", c_float),
                ("numberOfLeaves", c_int),
                ("leafPositions", c_float * 40),
                ("flatCollimator", FlatCollimator)]

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

    xmin = min([p0.x, p1.x, p2.x, p3.x, p4.x, p5.x, p6.x, p7.x])
    ymin = min([p0.y, p1.y, p2.y, p3.y, p4.y, p5.y, p6.y, p7.y])
    zmin = min([p0.z, p1.z, p2.z, p3.z, p4.z, p5.z, p6.z, p7.z])

    xmax = max([p0.x, p1.x, p2.x, p3.x, p4.x, p5.x, p6.x, p7.x])
    ymax = max([p0.y, p1.y, p2.y, p3.y, p4.y, p5.y, p6.y, p7.y])
    zmax = max([p0.z, p1.z, p2.z, p3.z, p4.z, p5.z, p6.z, p7.z])

    return Box(float4(xmin,ymin,zmin,0), float4(xmax,ymax,zmax,0))

def createRectangles(position, xdir, ydir, rectangleWidth, numberOfRect, rectangleLength):
    rectangle_array = Rectangle * 40
    rectangles = rectangle_array()
    x = normalize(xdir)
    y = normalize(ydir)*rectangleWidth
    for i in range(numberOfRect):
        rectangles[i] = Rectangle(position + y*i, position + y*(i+1), position + x*rectangleLength[i] + y*(i+1), position + y*i + x*rectangleLength[i])
    
    return rectangles

def createFlatCollimator(collimator):
    plane = Plane(collimator.position, cross(collimator.xdir, collimator.ydir)) # Plane perpendicular to xdir and ydir.
    bbox = Box(projectPointOntoPlane(collimator.boundingBox.min, plane), projectPointOntoPlane(collimator.boundingBox.max, plane))
    leaves = createRectangles(collimator.position, collimator.xdir, collimator.ydir, collimator.leafWidth, collimator.numberOfLeaves, collimator.leafPositions)
    fc = FlatCollimator()
    fc.boundingBox = bbox
    fc.position = collimator.position
    fc.xdir = collimator.xdir
    fc.ydir = collimator.ydir
    fc.attenuation = collimator.attenuation
    fc.numberOfLeaves = collimator.numberOfLeaves
    fc.leaves = leaves
    return fc

###################### Intersection calculations ######################

def intersectLineSimpleCollimator(line, collimator):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leftRectangle)
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.rightRectangle)

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineFlatCollimator(line, collimator):
    [intersectBBox, intersectionDistanceBBox, intersectionPointBBox] = intersectLineBox(line, collimator.boundingBox)
    if intersectBBox:
        for i in range(collimator.numberOfLeaves):
            [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leaves[i])
            if intersect:
                return [intersect, intersectionDistance, intersectionPoint]

    return [False, None, None]
