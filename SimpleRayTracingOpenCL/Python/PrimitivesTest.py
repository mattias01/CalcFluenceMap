from Python.Primitives import *
from Python.RayTracing import *

def testprojectPointOntoPlane():
    p0 = float4(0,0,1,0)
    p1 = float4(1,1,0,0)
    plane1 = Plane(float4(0,0,0,0), float4(0,0,1,0))
    plane2 = Plane(float4(0,0,0,0), float4(1,1,0,0))
    pp1 = projectPointOntoPlane(p0, plane1)
    pp2 = projectPointOntoPlane(p1, plane2)
    if pp1 == float4(0,0,0,0) and pp2 == float4(0,0,0,0):
        return True
    else:
        print "projectPointOntoPlane FAILED"
        return False

def testIntersectLineTriangle():
    l = Line(float4(1,1,0,0), float4(0,0,1,0))
    t = Triangle(float4(0,0,1,0), float4(3,0,1,0), float4(0,3,1,0))
    [intersect, intersectionDistance, intersectionPoint] = intersectLineTriangle(l,t)
    if intersect and intersectionPoint == float4(1,1,1,0):
        return True
    else:
        print "intersectLineTriangle FAILED"
        return False

def testIntersectLineRectangle():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(2,2,0,0), float4(0,0,1,0))
    s = Rectangle(float4(0,0,1,0), float4(3,0,1,0), float4(0,3,1,0), float4(3,3,1,0))
    [intersect1, intersectionDistance1, intersectionPoint1] = intersectLineRectangle(l1,s)
    [intersect2, intersectionDistance2, intersectionPoint2] = intersectLineRectangle(l2,s)
    if intersect1 and (intersectionPoint1 == float4(1,1,1,0)) and intersect2 and (intersectionPoint2 == float4(2,2,1,0)):
        return True
    else:
        print "intersectLineRectangle FAILED"
        return False

def testIntersectLineDisc():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,0,0), float4(0,0,1,0))
    d = Disc(float4(0,0,1,0), float4(0,0,1,0), 2)
    [intersect1, intersectionDistance1, intersectionPoint1] = intersectLineDisc(l1,d)
    [intersect2, intersectionDistance2, intersectionPoint2] = intersectLineDisc(l2,d)
    if intersect1 and (intersectionPoint1 == float4(1,1,1,0) and not intersect2 and intersectionPoint2 == None):
        return True
    else:
        print "intersectLineDisc FAILED"
        return False

def testIntersectLineBBox():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,0,0), float4(0,0,1,0))
    b1 = BBox(float4(0,0,0,0), float4(2,2,2,0))
    [intersect1, intersectionDistance1, intersectionPoint1] = intersectLineBBox(l1, b1)
    [intersect2, intersectionDistance2, intersectionPoint2] = intersectLineBBox(l2, b1)
    if intersect1 and (intersectionDistance1 == 0) and (intersectionPoint1 == float4(1,1,0,0)) and not intersect2:
        return True
    else:
        print "intersectLineBBox FAILED"
        return False

def testIntersectLineBox():
    l1 = Line(float4(1,1,-0.1,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,-0.1,0), float4(0,0,1,0))
    b1 = createBoxFromPoints(float4(0,0,0,0),float4(0,2,0,0),float4(2,2,0,0),float4(2,0,0,0),float4(0,0,2,0),float4(2,0,2,0),float4(2,2,2,0),float4(0,2,2,0))
    [intersect1, intersectionDistance1, intersectionPoint1] = intersectLineBox(l1, b1)
    [intersect2, intersectionDistance2, intersectionPoint2] = intersectLineBox(l2, b1)
    if intersect1 and (intersectionPoint1 == float4(1,1,0,0)) and not intersect2:
        return True
    else:
        print "intersectLineBox FAILED"
        return False

def testIntersectLineBoxInOut():
    l1 = Line(float4(1,1,-0.1,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,-0.1,0), float4(0,0,1,0))
    b1 = createBoxFromPoints(float4(0,0,0,0),float4(2,0,0,0),float4(2,2,0,0),float4(0,2,0,0),float4(0,0,2,0),float4(2,0,2,0),float4(2,2,2,0),float4(0,2,2,0))
    [intersect1, intersectionMinDistance1, intersectionMaxDistance1, intersectionMinPoint1, intersectionMaxPoint1] = intersectLineBoxInOut(l1, b1)
    [intersect2, intersectionMinDistance2, intersectionMaxDistance2, intersectionMinPoint2, intersectionMaxPoint2] = intersectLineBoxInOut(l2, b1)
    intersectionMaxPoint1.z = round(intersectionMaxPoint1.z, 6)
    if intersect1 and intersectionMinPoint1 == float4(1,1,0,0) and intersectionMaxPoint1 == float4(1,1,2,0) and not intersect2:
        return True
    else:
        print "intersectLineBoxInOut FAILED"
        return False


def primitivesTest():
    passed = False
    if testprojectPointOntoPlane() and testIntersectLineTriangle() and testIntersectLineRectangle() and testIntersectLineDisc() and testIntersectLineBBox() and testIntersectLineBox() and testIntersectLineBoxInOut():
        passed = True
    else:
        passed = False

    if passed == True:
        print "Python primitives unit tests PASSED"
    else:
        print "Python primitives unit tests FAILED"

    return passed