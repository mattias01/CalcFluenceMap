import numpy

###################### Class definitions ######################
class Line:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

class Plane:
    def __init__(self, origin, normal):
        self.origin = origin
        self.normal = normal

# Triangle class
# Points assigned anti-clockwise
class Triangle:
    def __init__(self, p0, p1, p2):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2

# Square class
# Points assigned anti-clockwise
class Square:
    def __init__(self, p0, p1, p2, p3):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

class SimpleRaySource:
    def __init__(self, square):
        self.square = square

class SimpleCollimator:
    def __init__(self, leftSquare, rightSquare):
        self.leftSquare = leftSquare
        self.rightSquare = rightSquare

class FluencySquare:
    def __init__(self, square):
        self.square = square

class Scene:
    def __init__(self, raySource, collimator, fluencySquare):
        self.raySource = raySource
        self.collimator = collimator
        self.fluencySquare = fluencySquare

###################### Intersection calculations ######################
def intersectLinePlane(line, plane):
    if numpy.dot(line.direction, plane.normal) == 0:
        # Parallel. Does not intersect
        return None
    else:
        # Does intersect. Return intersection point
        t = (numpy.dot(plane.normal, (plane.origin - line.origin))) / (numpy.dot(plane.normal, line.direction))
        return line.origin + line.direction*t

def intersectLineTriangle(line, triangle):
    u = triangle.p1 - triangle.p0
    v = triangle.p2 - triangle.p0
    triangleNorm = numpy.cross(u, v)
    intersectionPoint = intersectLinePlane(line, Plane(triangle.p0, triangleNorm))
    if intersectionPoint != None:
        #Point in triangle plan. Check if in triangle
        uu = numpy.dot(u,u)
        uv = numpy.dot(u,v)
        vv = numpy.dot(v,v)
        w = intersectionPoint - triangle.p0
        wu = numpy.dot(w,u)
        wv = numpy.dot(w,v)
        D = uv * uv - uu * vv
        # get and test parametric coords
        s = (uv * wv - vv * wu) / D
        if (s < 0.0 or s > 1.0):        # intersectionPoint is outside triangle
            return None
        t = (uv * wu - uu * wv) / D
        if (t < 0.0 or (s + t) > 1.0):  # intersectionPoint is outside triangle
            return None
        return intersectionPoint # # intersectionPoint is in triangle
    else:
        return None

def intersectLineSquare(line, square):
    t1 = Triangle(square.p0, square.p1, square.p2)
    t2 = Triangle(square.p2, square.p3, square.p0)
    intersection = intersectLineTriangle(line, t1)
    if intersection != None:
        return intersection
    else:
        return intersectLineTriangle(line, t2)

def intersectLineSimpleCollimator(line, collimator):
    intersection = intersectLineSquare(line, collimator.leftSquare)
    if intersection != None:
        return intersection
    else:
        return intersectLineSquare(line, collimator.rightSquare)

def intersectLineSimpleRaySource(line, raySource):
    return intersectLineSquare(line, raySource.square)

###################### Ray tracing ######################

def traceRay(scene, ray):
    if intersectLineSimpleCollimator(ray, scene.collimator) != None:
        return 0
    else:
        if intersectLineSimpleRaySource(ray, scene.raySource) != None:
            return 1
    return 0

def drawScene(scene, flx, fly):
    fluency_data = numpy.zeros(shape=(flx,fly), dtype=numpy.float32)
    istep = (0.0 + scene.fluencySquare.square.p1[0])/flx # Length in x / x resolution
    jstep = (0.0 + scene.fluencySquare.square.p3[1])/fly # Length in y / y resolution
    ioffset = istep/2.0 # Casts ray from center of pixel
    joffset = jstep/2.0
    for i in range(flx):
        for j in range(fly):
            ray = Line(numpy.array([(scene.fluencySquare.square.p0[0] + i*istep + ioffset), (scene.fluencySquare.square.p0[1] + j*jstep + joffset), 0]), numpy.array([0,0,1]))
            fluency_data[i][j] = traceRay(scene, ray)
    return fluency_data

###################### Tests ######################
def testIntersectLineTriangle():
    l = Line(numpy.array([1,1,0], dtype=numpy.float32), numpy.array([0,0,1], dtype=numpy.float32))
    t = Triangle(numpy.array([0,0,0], dtype=numpy.float32), numpy.array([3,0,0], dtype=numpy.float32), numpy.array([0,3,0], dtype=numpy.float32))
    i = intersectLineTriangle(l,t)
    if i.all() == numpy.array([1.0,1.0,0.0]).all():
        return True
    else:
        print "intersectLineTriangle FAILED"
        return False

def testIntersectLineSquare():
    l1 = Line(numpy.array([1,1,0], dtype=numpy.float32), numpy.array([0,0,1], dtype=numpy.float32))
    l2 = Line(numpy.array([2,2,0], dtype=numpy.float32), numpy.array([0,0,1], dtype=numpy.float32))
    s = Square(numpy.array([0,0,0], dtype=numpy.float32), numpy.array([3,0,0], dtype=numpy.float32), numpy.array([0,3,0], dtype=numpy.float32), numpy.array([3,3,0], dtype=numpy.float32))
    i1 = intersectLineSquare(l1,s)
    i2 = intersectLineSquare(l2,s)
    if numpy.allclose(i1, numpy.array([1,1,0])) and numpy.allclose(i2, numpy.array([2,2,0])):
        return True
    else:
        print "intersectLineSquare FAILED"
        return False

def test():
    passed = True
    passed = testIntersectLineTriangle()
    passed = testIntersectLineSquare()
    if passed == True:
        print "Ray-tracing tests PASSED"
    else:
        print "Ray-tracing tests FAILED"
