from ctypes import *
from OpenCLTypes import *
from Python.Primitives import *

###################### Class definitions ######################

class SimpleCollimator(Structure):
    _fields_ = [("leftRectangle", Rectangle),
                ("rightRectangle", Rectangle)]

class FlatCollimator(Structure):
    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", Rectangle * 40)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            #leaf = self.leaves[i]
            #t0p0 = (leaf.p0.x, leaf.p0.y, leaf.p0.z)
            #t0p1 = (leaf.p1.x, leaf.p1.y, leaf.p1.z)
            #t0p2 = (leaf.p2.x, leaf.p2.y, leaf.p2.z)
            #t1p0 = (leaf.p0.x, leaf.p0.y, leaf.p0.z)
            #t1p1 = (leaf.p2.x, leaf.p2.y, leaf.p2.z)
            #t1p2 = (leaf.p3.x, leaf.p3.y, leaf.p3.z)
            #list.append(t0p0)
            #list.append(t0p1)
            #list.append(t0p2)
            #list.append(t1p0)
            #list.append(t1p1)
            #list.append(t1p2)
            list.extend(self.leaves[i].getVertices())
        return list

class BBoxCollimator(Structure):
    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", BBox * 40)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            list.extend(self.leaves[i].getVertices())
        return list

class BoxCollimator(Structure):
    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leaves", Box * 40)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            list.extend(self.leaves[i].getVertices())
        return list

class Collimator(Structure):
    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("height", c_float),
                ("width", c_float),
                ("numberOfLeaves", c_int),
                ("leafPositions", c_float * 40),
                ("flatCollimator", FlatCollimator),
                ("bboxCollimator", BBoxCollimator),
                ("boxCollimator", BoxCollimator)]

###################### Collimator generation ######################

def calculateCollimatorBoundingBox(collimator):
    maxPosition = 0
    for i in range(collimator.numberOfLeaves):
        if maxPosition < collimator.leafPositions[i]:
            maxPosition = collimator.leafPositions[i]

    x = normalize(collimator.xdir) * maxPosition
    y = normalize(collimator.ydir) * collimator.width
    down = normalize(cross(collimator.xdir, collimator.ydir)) * collimator.height

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

def createBBoxes(position, xdir, ydir, boxHeight, boxWidth, numberOfBoxes, boxLength):
    box_array = BBox * 40
    boxes = box_array()
    x = normalize(xdir)
    y = normalize(ydir)*boxWidth
    z = normalize(cross(xdir, ydir))*boxHeight
    for i in range(numberOfBoxes):
        boxes[i] = boundingBox(position + y*i, position + y*(i+1), position + x*boxLength[i] + y*(i+1), position + y*i + x*boxLength[i],
                               position + y*i + z, position + y*(i+1) + z, position + x*boxLength[i] + y*(i+1) + z, position + y*i + x*boxLength[i] + z)

    return boxes

def createBoxes(position, xdir, ydir, height, width, numberOfBoxes, boxLength):
    box_array = Box * 40
    boxes = box_array()
    #topBoxWidth = abs(position.z*0.4)/numberOfBoxes
    topBoxWidth = width/numberOfBoxes
    #topPosition = float4(position.z*0.2, position.z*0.2, position.z, 0)
    tr = createRectangles(position, xdir, ydir, topBoxWidth, numberOfBoxes, boxLength)
    bottomz = position.z-height
    tanAlpha = width/abs(position.z)
    bottomBoxWidth = (tanAlpha*abs(bottomz))/numberOfBoxes
    #bottomRatio = bottomWidth/topWidth
    bottomOffset = (bottomBoxWidth-topBoxWidth)*numberOfBoxes/2
    bottomPosition = float4(position.x, position.y, bottomz, 0)-xdir*bottomOffset-ydir*bottomOffset
    br = createRectangles(bottomPosition, xdir, ydir, bottomBoxWidth, numberOfBoxes, boxLength)

    bbox = None

    for i in range(numberOfBoxes):
        #boxes[i] = createBoxFromPoints(br[i].p1, br[i].p0, br[i].p3, br[i].p2, tr[i].p1, tr[i].p2, tr[i].p3, tr[i].p0)
        boxes[i] = createBoxFromPoints(br[i].p0, br[i].p1, br[i].p2, br[i].p3, tr[i].p0, tr[i].p1, tr[i].p2, tr[i].p3)
        if bbox == None:
            bbox = boundingBox(tr[i].p0, tr[i].p1, tr[i].p2, tr[i].p3, br[i].p0, br[i].p1, br[i].p2, br[i].p3)
        else:
            bbox = boundingBox10(tr[i].p0, tr[i].p1, tr[i].p2, tr[i].p3, br[i].p0, br[i].p1, br[i].p2, br[i].p3, bbox.min, bbox.max)

    return [boxes, bbox]

def createFlatCollimator(collimator):
    plane = Plane(collimator.position, cross(collimator.xdir, collimator.ydir)) # Plane perpendicular to xdir and ydir.
    bbox = BBox(projectPointOntoPlane(collimator.boundingBox.min, plane), projectPointOntoPlane(collimator.boundingBox.max, plane))
    leaves = createRectangles(collimator.position, collimator.xdir, collimator.ydir, collimator.width/collimator.numberOfLeaves, collimator.numberOfLeaves, collimator.leafPositions)
    fc = FlatCollimator()
    fc.boundingBox = bbox
    fc.position = collimator.position
    fc.xdir = collimator.xdir
    fc.ydir = collimator.ydir
    fc.absorptionCoeff = collimator.absorptionCoeff
    fc.numberOfLeaves = collimator.numberOfLeaves
    fc.leaves = leaves
    return fc

def createBBoxCollimator(collimator):
    bboxes = createBBoxes(collimator.position, collimator.xdir, collimator.ydir, collimator.height, collimator.width/collimator.numberOfLeaves, collimator.numberOfLeaves, collimator.leafPositions)
    bc = BBoxCollimator()
    bc.boundingBox = collimator.boundingBox
    bc.position = collimator.position
    bc.xdir = collimator.xdir
    bc.ydir = collimator.ydir
    bc.absorptionCoeff = collimator.absorptionCoeff
    bc.numberOfLeaves = collimator.numberOfLeaves
    bc.leaves = bboxes
    return bc

def createBoxCollimator(collimator):
    [boxes, bbox] = createBoxes(collimator.position, collimator.xdir, collimator.ydir, collimator.height, collimator.width, collimator.numberOfLeaves, collimator.leafPositions)
    collimator.boundingBox = bbox
    bc = BoxCollimator()
    bc.boundingBox = bbox
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

def intersectLineFlatCollimatorLeaf(line, leaf):
    return intersectLineRectangle(line, leaf)

def intersectLineBBoxCollimatorLeaf(line, leaf):
    return intersectLineBBoxInOut(line, leaf)

def intersectLineBoxCollimatorLeaf(line, leaf):
    return intersectLineBoxInOut(line, leaf)
