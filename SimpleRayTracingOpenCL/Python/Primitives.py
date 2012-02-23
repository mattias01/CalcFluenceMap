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

class BBox(Structure):
    _fields_ = [("min", float4),
                ("max", float4)]

class Box(Structure):
    _fields_ = [("triangles", Triangle * 12)]

###################### Other calculations ######################
def projectPointOntoPlane(p0, plane):
    sn = -dot(plane.normal, (p0 - plane.origin))
    sd = dot(plane.normal, plane.normal)
    sb = sn / sd
    return p0 + plane.normal * sb

def boundingBox(p0, p1, p2, p3, p4, p5, p6, p7):
    xmin = min([p0.x, p1.x, p2.x, p3.x, p4.x, p5.x, p6.x, p7.x])
    ymin = min([p0.y, p1.y, p2.y, p3.y, p4.y, p5.y, p6.y, p7.y])
    zmin = min([p0.z, p1.z, p2.z, p3.z, p4.z, p5.z, p6.z, p7.z])

    xmax = max([p0.x, p1.x, p2.x, p3.x, p4.x, p5.x, p6.x, p7.x])
    ymax = max([p0.y, p1.y, p2.y, p3.y, p4.y, p5.y, p6.y, p7.y])
    zmax = max([p0.z, p1.z, p2.z, p3.z, p4.z, p5.z, p6.z, p7.z])

    return BBox(float4(xmin,ymin,zmin,0), float4(xmax,ymax,zmax,0))

# Assumes p0 -> p3 bottom in counter-clockwise order, p4 -> p7 top in counter-clockwise order.
def createBoxFromPoints(p0, p1, p2, p3, p4, p5, p6, p7):
    # Bottom
    t0 = Triangle(p0, p1, p3)
    t1 = Triangle(p1, p2, p3)
    # Top
    t2 = Triangle(p5, p6, p4)
    t3 = Triangle(p6, p7, p4)
    # Left side
    t4 = Triangle(p1, p7, p2)
    t5 = Triangle(p7, p6, p2)
    # Right side
    t6 = Triangle(p4, p0, p5)
    t7 = Triangle(p0, p3, p5)
    # Front side
    t8 = Triangle(p3, p2, p5)
    t9 = Triangle(p2, p6, p5)
    # Back side (Not needed?)
    t10 = Triangle(p4, p7, p0)
    t11 = Triangle(p7, p1, p0)
    
    triangle_array = Triangle * 12
    triangles = triangle_array(t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11)
    return Box(triangles)

###################### Hit calculations ###############################

def hitLinePlane(line, plane):
    if dot(line.direction, plane.normal) != 0:
        return True
    else:
        return False

###################### Distance calculations ##########################
## Assumes hit

def distanceLinePlane(line, plane):
    return (dot(plane.normal, (plane.origin - line.origin))) / (dot(plane.normal, line.direction))

###################### Intersection calculations ######################
def intersectLinePlane(line, plane):
    # Init to not intersect.
    intersect = False
    intersectionDistance = None
    intersectionPoint = None
    if hitLinePlane(line, plane):
        # Does intersect.
        t = distanceLinePlane(line, plane)
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
          
def intersectLineBBox(line, box):
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
    if tmax <= 0: # Only if in positive direction
        return [False, None, None]
    
    return [True, float(tmin), line.origin + line.direction*float(tmin)]  # Could give the outgoing distance (tmax) and point here as well.

def intersectLineBBoxInOut(line, box):
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
        return [False, None, None, None, None]
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
        return [False, None, None, None, None]
    if tzmin > tmin:
        tmin = tzmin
    if tzmax < tmax:
        tmax = tzmax
    if tmax <= 0: # Only if in positive direction
        return [False, None, None, None, None] 
    
    return [True, float(tmin), float(tmax), line.origin + line.direction*float(tmin), line.origin + line.direction*float(tmax)]  # Intersects, distance to entry to box, longest distance to exit box, entry point, exit point.

def intersectLineBox(line, box):
    counter = 0
    intersect = False
    minDistance = float('inf')
    minPoint = None
    for i in range(len(box.triangles)):
        [intersect, distance, point] = intersectLineTriangle(line, box.triangles[i])
        if intersect:
            if distance < minDistance:
                minDistance = distance
                minPoint = point
            counter = counter + 1
            if counter == 2: # Stop if two intersections haven been found.
                break;

    return [intersect, minDistance, minPoint]

def intersectLineBoxInOut(line, box):
    counter = 0
    intersect = False
    minDistance = float('inf')
    minPoint = None
    maxPoint = None
    maxDistance = -float('inf')
    for i in range(len(box.triangles)):
        [intersect, distance, point] = intersectLineTriangle(line, box.triangles[i])
        if intersect:
            if distance < minDistance:
                minDistance = distance
                minPoint = point
            if distance > maxDistance:
                maxDistance = distance
                maxPoint = point
            if minDistance != maxDistance:
                counter = counter + 1
            if counter == 2: # Stop if two intersections haven been found.
                break;

    return [intersect, minDistance, maxDistance, minPoint, maxPoint]