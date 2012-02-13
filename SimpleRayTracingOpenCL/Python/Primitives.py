from ctypes import *
from OpenCLTypes import *

###################### Class definitions ######################

class Line(Structure):
    _fields_ = [("origin", float4),
                ("direction", float4)]

class Plane(Structure):
    _fields_ = [("origin", float4),
                ("normal", float4)]

# Triangle class
# Points assigned anti-clockwise
class Triangle(Structure):
    _fields_ = [("p0", float4),
                ("p1", float4),
                ("p2", float4)]

# Rectangle class
# Points assigned anti-clockwise
class Rectangle(Structure):
    _fields_ = [("p0", float4),
                ("p1", float4),
                ("p2", float4),
                ("p3", float4)]

# Utility function for matplotlib to create path.
def Rectangle2dVertexArray(s):
    return [[s.p0.y, s.p0.x], [s.p1.y, s.p1.x], [s.p2.y, s.p2.x], [s.p3.y, s.p3.x], [s.p0.y, s.p0.x]]

class Disc(Structure):
    _fields_ = [("origin", float4),
                ("normal", float4),
                ("radius", c_float)]

class Box(Structure):
    __fields__ = [("p0", float4),
                  ("p1", float4),
                  ("p2", float4),
                  ("p3", float4),
                  ("p4", float4),
                  ("p5", float4),
                  ("p6", float4),
                  ("p7", float4)]

###################### Intersection calculations ######################
def intersectLinePlane(line, plane):
    # Init to not intersect.
    intersect = False
    intersectionDistance = None
    intersectionPoint = None
    if dot(line.direction, plane.normal) != 0:
        # Does intersect.
        t = (dot(plane.normal, (plane.origin - line.origin))) / (dot(plane.normal, line.direction))
        if t > 0: # Plane is located in positive ray direction from the ray origin. Avoids hitting same thing it just hit.
            intersect = True
            intersectionDistance = t
            intersectionPoint = line.origin + line.direction*intersectionDistance

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineTriangle(line, triangle):
    u = triangle.p1 - triangle.p0
    v = triangle.p2 - triangle.p0
    triangleNorm = cross(u, v)
    [intersect, intersectionDistance, intersectionPoint] = intersectLinePlane(line, Plane(triangle.p0, triangleNorm))
    if intersect == True:
        #Point in triangle plane. Check if in triangle.
        uu = dot(u,u)
        uv = dot(u,v)
        vv = dot(v,v)
        w = intersectionPoint - triangle.p0
        wu = dot(w,u)
        wv = dot(w,v)
        D = uv * uv - uu * vv
        # get and test parametric coords
        s = (uv * wv - vv * wu) / D
        if (s < 0.0 or s > 1.0):        # intersectionPoint is outside triangle
            intersect = False
            intersectionDistance = None
            intersectionPoint = None
        else:
            t = (uv * wu - uu * wv) / D
            if (t < 0.0 or (s + t) > 1.0):  # intersectionPoint is outside triangle
                intersect = False
                intersectionDistance = None
                intersectionPoint = None

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineRectangle(line, rectangle):
    # Split rectangle into two triangles and test them individually.
    t1 = Triangle(rectangle.p0, rectangle.p1, rectangle.p2)
    t2 = Triangle(rectangle.p2, rectangle.p3, rectangle.p0)
    [intersect, intersectionDistance, intersectionPoint] = intersectLineTriangle(line, t1) # Test the first triangle
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineTriangle(line, t2) # Test the other triangle
    
    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineDisc(line, disc):
    [intersect, intersectionDistance, intersectionPoint] = intersectLinePlane(line, Plane(disc.origin, disc.normal))
    if intersect == True:
        D = disc.origin - intersectionPoint
        if dot(D,D) > disc.radius*disc.radius:
            intersect = False
            intersectionDistance = None
            intersectionPoint = None

    return [intersect, intersectionDistance, intersectionPoint]