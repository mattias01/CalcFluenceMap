from ctypes import *
import numpy as np
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
    _fields_ = [("min", float4),
                ("max", float4)]

###################### Projection calculations ######################
def projectPointOntoPlane(p0, plane):
    sn = -dot(plane.normal, (p0 - plane.origin))
    sd = dot(plane.normal, plane.normal)
    sb = sn / sd
    return p0 + plane.normal * sb

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

def intersectLineBox(line, box):
    if line.direction.x >= 0:
        tmin = (box.min.x - line.origin.x) / np.float32(line.direction.x) # Convert to numpy.float32 which supports IEEE 754 floating point arithmetic (div by 0 -> inf), which python floats doesn't. It gives a warning on division by zero, but works as expected. OpenCl should work the same way.
        tmax = (box.max.x - line.origin.x) / np.float32(line.direction.x)
    else:
        tmin = (box.max.x - line.origin.x) / np.float32(line.direction.x)
        tmax = (box.min.x - line.origin.x) / np.float32(line.direction.x)
    if line.direction.y >= 0:
        tymin = (box.min.y - line.origin.y) / np.float32(line.direction.y)
        tymax = (box.max.y - line.origin.y) / np.float32(line.direction.y)
    else:
        tymin = (box.max.y - line.origin.y) / np.float32(line.direction.y)
        tymax = (box.min.y - line.origin.y) / np.float32(line.direction.y)
    if (tmin > tymax) or (tymin > tmax):
        return [False, None, None]
    if tymin > tmin:
        tmin = tymin
    if tymax < tmax:
       tmax = tymax
    if line.direction.z >= 0:
        tzmin = (box.min.z - line.origin.z) / np.float32(line.direction.z)
        tzmax = (box.max.z - line.origin.z) / np.float32(line.direction.z)
    else:
        tzmin = (box.max.z - line.origin.z) / np.float32(line.direction.z)
        tzmax = (box.min.z - line.origin.z) / np.float32(line.direction.z)
    if (tmin > tzmax) or (tzmin > tmax):
        return [False, None, None]
    if tzmin > tmin:
        tmin = tzmin
    if tzmax < tmax:
        tmax = tzmax
    return [True, float(tmin), line.origin + line.direction*float(tmin)]  # Could give the outgoing distance (tmax) and point here as well.