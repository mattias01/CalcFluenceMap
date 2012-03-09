from ctypes import *
from OpenCLTypes import *
from Python.Primitives import *
from Python.Settings import MODE, NUMBER_OF_COLLIMATORS, NUMBER_OF_LEAVES, SOA

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
                ("leafDataLength", c_int)]
                #("leaves", Rectangle * NUMBER_OF_LEAVES)]
                #("leaves", Triangle * (2 * NUMBER_OF_LEAVES))]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves*2):
            list.extend(self.leaves[i].getVertices())
        return list

class BBoxCollimator(Structure):
    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("numberOfLeaves", c_int),
                ("leafDataLength", c_int)]
                #("leaves", BBox * NUMBER_OF_LEAVES)]

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
                ("leafDataLength", c_int)]
                #("leaves", Box * NUMBER_OF_LEAVES)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            list.extend(self.leaves[i].getVertices())
        return list

class Collimator(Structure):
    def selectMode(mode):
        if mode == 0:
            return ("flatCollimator", FlatCollimator)
        elif mode == 1:
            return ("bboxCollimator", BBoxCollimator)
        elif mode ==2:
            return ("boxCollimator", BoxCollimator)

    _fields_ = [("boundingBox", BBox),
                ("position", float4),
                ("xdir", float4),
                ("ydir", float4),
                ("absorptionCoeff", c_float),
                ("height", c_float),
                ("width", c_float),
                ("numberOfLeaves", c_int),
                ("leafPositions", c_float * NUMBER_OF_LEAVES),
                #("flatCollimator", FlatCollimator),
                #("bboxCollimator", BBoxCollimator),
                #("boxCollimator", BoxCollimator))]
                selectMode(MODE)]

class FlatCollimatorSoA(Structure):
    _fields_ = [("boundingBox", BBox * NUMBER_OF_COLLIMATORS),
                ("position", float4 * NUMBER_OF_COLLIMATORS),
                ("xdir", float4 * NUMBER_OF_COLLIMATORS),
                ("ydir", float4 * NUMBER_OF_COLLIMATORS),
                ("absorptionCoeff", c_float * NUMBER_OF_COLLIMATORS),
                ("numberOfLeaves", c_int * NUMBER_OF_COLLIMATORS),
                ("leafDataLength", c_int * NUMBER_OF_COLLIMATORS)]
                #("leaves", Rectangle * NUMBER_OF_LEAVES)]
                #("leaves", Triangle * (2 * NUMBER_OF_LEAVES) * NUMBER_OF_COLLIMATORS)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves*2):
            list.extend(self.leaves[i].getVertices())
        return list

class BBoxCollimatorSoA(Structure):
    _fields_ = [("boundingBox", BBox * NUMBER_OF_COLLIMATORS),
                ("position", float4 * NUMBER_OF_COLLIMATORS),
                ("xdir", float4 * NUMBER_OF_COLLIMATORS),
                ("ydir", float4 * NUMBER_OF_COLLIMATORS),
                ("absorptionCoeff", c_float * NUMBER_OF_COLLIMATORS),
                ("numberOfLeaves", c_int * NUMBER_OF_COLLIMATORS),
                ("leafDataLength", c_int * NUMBER_OF_COLLIMATORS)]
                #("leaves", BBox * NUMBER_OF_LEAVES * NUMBER_OF_COLLIMATORS)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            list.extend(self.leaves[i].getVertices())
        return list

class BoxCollimatorSoA(Structure):
    _fields_ = [("boundingBox", BBox * NUMBER_OF_COLLIMATORS),
                ("position", float4 * NUMBER_OF_COLLIMATORS),
                ("xdir", float4 * NUMBER_OF_COLLIMATORS),
                ("ydir", float4 * NUMBER_OF_COLLIMATORS),
                ("absorptionCoeff", c_float * NUMBER_OF_COLLIMATORS),
                ("numberOfLeaves", c_int * NUMBER_OF_COLLIMATORS),
                ("leafDataLength", c_int * NUMBER_OF_COLLIMATORS)]
                #("leaves", Box * NUMBER_OF_LEAVES * NUMBER_OF_COLLIMATORS)]

    def getVertices(self):
        list = []
        for i in range(self.numberOfLeaves):
            list.extend(self.leaves[i].getVertices())
        return list

class CollimatorSoA(Structure):
    def selectMode(mode):
        if mode == 0:
            return ("flatCollimator", FlatCollimatorSoA)
        elif mode == 1:
            return ("bboxCollimator", BBoxCollimatorSoA)
        elif mode ==2:
            return ("boxCollimator", BoxCollimatorSoA)

    _fields_ = [("boundingBox", BBox * NUMBER_OF_COLLIMATORS),
                ("position", float4 * NUMBER_OF_COLLIMATORS),
                ("xdir", float4 * NUMBER_OF_COLLIMATORS),
                ("ydir", float4 * NUMBER_OF_COLLIMATORS),
                ("absorptionCoeff", c_float * NUMBER_OF_COLLIMATORS),
                ("height", c_float * NUMBER_OF_COLLIMATORS),
                ("width", c_float * NUMBER_OF_COLLIMATORS),
                ("numberOfLeaves", c_int * NUMBER_OF_COLLIMATORS),
                ("leafPositions", c_float * NUMBER_OF_LEAVES * NUMBER_OF_COLLIMATORS),
                #("flatCollimator", FlatCollimator),
                #("bboxCollimator", BBoxCollimator),
                #("boxCollimator", BoxCollimator))]
                selectMode(MODE)]

###################### Other stuff ################################

def CollimatorAoStoSoA(collimator_array):
    csoa = CollimatorSoA()
    for i in range(NUMBER_OF_COLLIMATORS):
        csoa.boundingBox[i] = collimator_array[i].boundingBox
        csoa.position[i] = collimator_array[i].position
        csoa.xdir[i] = collimator_array[i].xdir
        csoa.ydir[i] = collimator_array[i].ydir
        csoa.absorptionCoeff[i] = collimator_array[i].absorptionCoeff
        csoa.height[i] = collimator_array[i].height
        csoa.width[i] = collimator_array[i].width
        csoa.numberOfLeaves[i] = collimator_array[i].numberOfLeaves
        csoa.leafPositions[i] = collimator_array[i].leafPositions
        if MODE == 0:
            csoa.flatCollimator.boundingBox[i] = collimator_array[i].flatCollimator.boundingBox
            csoa.flatCollimator.position[i] = collimator_array[i].flatCollimator.position
            csoa.flatCollimator.xdir[i] = collimator_array[i].flatCollimator.xdir
            csoa.flatCollimator.ydir[i] = collimator_array[i].flatCollimator.ydir
            csoa.flatCollimator.absorptionCoeff[i] = collimator_array[i].flatCollimator.absorptionCoeff
            csoa.flatCollimator.numberOfLeaves[i] = collimator_array[i].flatCollimator.numberOfLeaves
            #csoa.flatCollimator.leaves[i] = collimator_array[i].flatCollimator.leaves
        elif MODE == 1:
            csoa.bboxCollimator.boundingBox[i] = collimator_array[i].bboxCollimator.boundingBox
            csoa.bboxCollimator.position[i] = collimator_array[i].bboxCollimator.position
            csoa.bboxCollimator.xdir[i] = collimator_array[i].bboxCollimator.xdir
            csoa.bboxCollimator.ydir[i] = collimator_array[i].bboxCollimator.ydir
            csoa.bboxCollimator.absorptionCoeff[i] = collimator_array[i].bboxCollimator.absorptionCoeff
            csoa.bboxCollimator.numberOfLeaves[i] = collimator_array[i].bboxCollimator.numberOfLeaves
            #csoa.bboxCollimator.leaves[i] = collimator_array[i].bboxCollimator.leaves
        elif MODE ==2:
            csoa.boxCollimator.boundingBox[i] = collimator_array[i].boxCollimator.boundingBox
            csoa.boxCollimator.position[i] = collimator_array[i].boxCollimator.position
            csoa.boxCollimator.xdir[i] = collimator_array[i].boxCollimator.xdir
            csoa.boxCollimator.ydir[i] = collimator_array[i].boxCollimator.ydir
            csoa.boxCollimator.absorptionCoeff[i] = collimator_array[i].boxCollimator.absorptionCoeff
            csoa.boxCollimator.numberOfLeaves[i] = collimator_array[i].boxCollimator.numberOfLeaves
            #csoa.boxCollimator.leaves[i] = collimator_array[i].boxCollimator.leaves
    return csoa

#Prepare float4 array from collimator leaf data.
def float4ArrayFromCollimators(collimators):
    leaf_array_length = 0
    for i in range(len(collimators)):
        if MODE == 0:
            leaf_array_length += collimators[i].flatCollimator.numberOfLeaves * collimators[i].flatCollimator.leafDataLength
        elif MODE == 1:
            leaf_array_length += collimators[i].bboxCollimator.numberOfLeaves * collimators[i].bboxCollimator.leafDataLength
        elif MODE == 2:
            leaf_array_length += collimators[i].boxCollimator.numberOfLeaves * collimators[i].boxCollimator.leafDataLength

    leaf_array = float4 * leaf_array_length

    leaf_array_position = 0;
    for i in range(len(collimators)):
        for j in range(collimators[i].numberOfLeaves):
            if MODE == 0:
                leaf_array[leaf_array_position + 0] = collimators[i].flatCollimator.leaves[j].p0
                leaf_array[leaf_array_position + 1] = collimators[i].flatCollimator.leaves[j].p1
                leaf_array[leaf_array_position + 2] = collimators[i].flatCollimator.leaves[j].p2
                leaf_array[leaf_array_position + 3] = collimators[i].flatCollimator.leaves[j+1].p0
                leaf_array[leaf_array_position + 4] = collimators[i].flatCollimator.leaves[j+1].p1
                leaf_array[leaf_array_position + 5] = collimators[i].flatCollimator.leaves[j+1].p2
                leaf_array_position += 2 * 3
            elif MODE == 1:
                leaf_array[leaf_array_position + 0] = collimators[i].bboxCollimator.leaves[j].min
                leaf_array[leaf_array_position + 1] = collimators[i].bboxCollimator.leaves[j].max
                leaf_array_position += 2
            elif MODE == 2:
                for k in range(collimators[i].boxCollimator.leaves[j].triangles):
                    leaf_array[leaf_array_position + k*3 + 0] = collimators[i].boxCollimator.leaves[j].triangles[k].p0
                    leaf_array[leaf_array_position + k*3 + 1] = collimators[i].boxCollimator.leaves[j].triangles[k].p1
                    leaf_array[leaf_array_position + k*3 + 2] = collimators[i].boxCollimator.leaves[j].triangles[k].p2
                leaf_array_position += 12 * 3
    
    return leaf_array

def createfloat4List(obj_list):
    list = []
    for x in obj_list:
        list.extend(x.getfloat4List())
    return list

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

def createRectangleTriangles(position, xdir, ydir, rectangleWidth, numberOfRect, rectangleLength):
    #rectangle_array = Rectangle * NUMBER_OF_LEAVES
    rectangle_array = Triangle * (2 * NUMBER_OF_LEAVES)
    rectangles = rectangle_array()
    x = normalize(xdir)
    y = normalize(ydir)*rectangleWidth
    for i in range(numberOfRect):
        #rectangles[i] = Rectangle(position + y*i, position + y*(i+1), position + x*rectangleLength[i] + y*(i+1), position + y*i + x*rectangleLength[i])
        rectangle = Rectangle(position + y*i, position + y*(i+1), position + x*rectangleLength[i] + y*(i+1), position + y*i + x*rectangleLength[i])
        rectangles[i*2] = Triangle(rectangle.p0, rectangle.p1, rectangle.p2)
        rectangles[i*2 +1] = Triangle(rectangle.p2, rectangle.p3, rectangle.p0)
    return rectangles

def createRectangles(position, xdir, ydir, rectangleWidth, numberOfRect, rectangleLength):
    rectangle_array = Rectangle * NUMBER_OF_LEAVES
    rectangles = rectangle_array()
    x = normalize(xdir)
    y = normalize(ydir)*rectangleWidth
    for i in range(numberOfRect):
        rectangles[i] = Rectangle(position + y*i, position + y*(i+1), position + x*rectangleLength[i] + y*(i+1), position + y*i + x*rectangleLength[i])

    return rectangles

def createBBoxes(position, xdir, ydir, boxHeight, boxWidth, numberOfBoxes, boxLength):
    box_array = BBox * NUMBER_OF_LEAVES
    boxes = box_array()
    x = normalize(xdir)
    y = normalize(ydir)*boxWidth
    z = normalize(cross(xdir, ydir))*boxHeight
    for i in range(numberOfBoxes):
        boxes[i] = boundingBox(position + y*i, position + y*(i+1), position + x*boxLength[i] + y*(i+1), position + y*i + x*boxLength[i],
                               position + y*i + z, position + y*(i+1) + z, position + x*boxLength[i] + y*(i+1) + z, position + y*i + x*boxLength[i] + z)

    return boxes

def createBoxes(position, xdir, ydir, height, width, numberOfBoxes, boxLength):
    box_array = Box * NUMBER_OF_LEAVES
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
    leaves = createRectangleTriangles(collimator.position, collimator.xdir, collimator.ydir, collimator.width/collimator.numberOfLeaves, collimator.numberOfLeaves, collimator.leafPositions)
    fc = FlatCollimator()
    fc.boundingBox = bbox
    fc.position = collimator.position
    fc.xdir = collimator.xdir
    fc.ydir = collimator.ydir
    fc.absorptionCoeff = collimator.absorptionCoeff
    fc.numberOfLeaves = collimator.numberOfLeaves
    fc.leafDataLength = 2 * 3
    #fc.leaves = leaves
    return [fc, createfloat4List(leaves)]

def createBBoxCollimator(collimator):
    bboxes = createBBoxes(collimator.position, collimator.xdir, collimator.ydir, collimator.height, collimator.width/collimator.numberOfLeaves, collimator.numberOfLeaves, collimator.leafPositions)
    bc = BBoxCollimator()
    bc.boundingBox = collimator.boundingBox
    bc.position = collimator.position
    bc.xdir = collimator.xdir
    bc.ydir = collimator.ydir
    bc.absorptionCoeff = collimator.absorptionCoeff
    bc.numberOfLeaves = collimator.numberOfLeaves
    bc.leafDataLength = 2
    #bc.leaves = bboxes
    return [bc, createfloat4List(bboxes)]

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
    bc.leafDataLength = 12 * 3
    #bc.leaves = boxes
    return [bc, createfloat4List(boxes)]

###################### Intersection calculations ######################

def intersectLineSimpleCollimator(line, collimator):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.leftRectangle)
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineRectangle(line, collimator.rightRectangle)

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineFlatCollimatorLeaf(line, leaf1, leaf2):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineTriangle(line, leaf1) # Test the first triangle
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineTriangle(line, leaf2) # Test the other triangle
    
    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineBBoxCollimatorLeaf(line, leaf):
    return intersectLineBBoxInOut(line, leaf)

def intersectLineBoxCollimatorLeaf(line, leaf):
    return intersectLineBoxInOut(line, leaf)
