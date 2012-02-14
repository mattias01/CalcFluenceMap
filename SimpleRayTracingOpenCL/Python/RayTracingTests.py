from Python.Primitives import *
from Python.RayTracing import *

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

def testIntersectLineBox():
    l1 = Line(float4(1,1,0,0), float4(0,0,1,0))
    l2 = Line(float4(3,3,0,0), float4(0,0,1,0))
    b = Box(float4(0,0,0,0), float4(2,2,2,0))
    [intersect1, intersectionDistance1, intersectionPoint1] = intersectLineBox(l1, b)
    [intersect2, intersectionDistance2, intersectionPoint2] = intersectLineBox(l2, b)
    if intersect1 and (intersectionDistance1 == 0) and (intersectionPoint1 == float4(1,1,0,0)) and not intersect2:
        return True
    else:
        print "intersectLineBox FAILED"
        return False