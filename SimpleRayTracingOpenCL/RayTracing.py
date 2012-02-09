import numpy
from ctypes import Structure
from OpenCLTypes import *
from math import acos, pi

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

# Square class
# Points assigned anti-clockwise
class Square(Structure):
    _fields_ = [("p0", float4),
                ("p1", float4),
                ("p2", float4),
                ("p3", float4)]

# Utility function for matplotlib to create path.
def Square2dVertexArray(s):
    return [[s.p0.y, s.p0.x], [s.p1.y, s.p1.x], [s.p2.y, s.p2.x], [s.p3.y, s.p3.x], [s.p0.y, s.p0.x]]

class Disc(Structure):
    _fields_ = [("origin", float4),
                ("normal", float4),
                ("radius", c_float)]

class SimpleRaySourceSquare(Structure):
    _fields_ = [("square", Square)]

class SimpleRaySourceDisc(Structure):
    _fields_ = [("disc", Disc)]

class SimpleCollimator(Structure):
    _fields_ = [("leftSquare", Square),
                ("rightSquare", Square)]

class FluencySquare(Structure):
    _fields_ = [("square", Square)]

class Scene(Structure):
    _fields_ = [("raySource", SimpleRaySourceDisc),
                ("collimator", SimpleCollimator),
                ("fluencySquare", FluencySquare)]

class Render(Structure):
    _fields_ = [("flx", c_int),
                ("fly", c_int),
                ("xstep", c_float),
                ("ystep", c_float),
                ("xoffset", c_float),
                ("yoffset", c_float),
                ("lsamples", c_int),
                ("lstep", c_float)]

class Debug(Structure):
    _fields_ = [("i0", c_int),
                ("i1", c_int),
                ("i2", c_int),
                ("i3", c_int),
                ("i4", c_int),
                ("i5", c_int),
                ("f0", c_float),
                ("f1", c_float),
                ("f2", c_float),
                ("f3", c_float),
                ("f4", c_float),
                ("f5", c_float),
                ("v0", float4),
                ("v1", float4),
                ("v2", float4),
                ("v3", float4),
                ("v4", float4),
                ("v5", float4)]

###################### Intersection calculations ######################
def intersectLinePlane(line, plane):
    if dot(line.direction, plane.normal) == 0:
        # Parallel. Does not intersect
        return None
    else:
        # Does intersect. Return intersection point
        t = (dot(plane.normal, (plane.origin - line.origin))) / (dot(plane.normal, line.direction))
        return line.origin + line.direction*t

def intersectLineTriangle(line, triangle):
    u = triangle.p1 - triangle.p0
    v = triangle.p2 - triangle.p0
    triangleNorm = cross(u, v)
    intersectionPoint = intersectLinePlane(line, Plane(triangle.p0, triangleNorm))
    if intersectionPoint != None:
        #Point in triangle plan. Check if in triangle
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
            return None
        t = (uv * wu - uu * wv) / D
        if (t < 0.0 or (s + t) > 1.0):  # intersectionPoint is outside triangle
            return None
        return intersectionPoint # intersectionPoint is in triangle
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

def intersectLineDisc(line, disc):
    p0 = intersectLinePlane(line, Plane(disc.origin, disc.normal))
    if p0 != None:
        D = disc.origin - p0
        if dot(D,D) <= disc.radius*disc.radius:
            return p0
        else:
            return None
    else:
        return None

def intersectLineSimpleCollimator(line, collimator):
    intersection = intersectLineSquare(line, collimator.leftSquare)
    if intersection != None:
        return intersection
    else:
        return intersectLineSquare(line, collimator.rightSquare)

def intersectLineSimpleRaySourceSquare(line, raySource):
    return intersectLineSquare(line, raySource.square)

def intersectLineSimpleRaySourceDisc(line, raySource):
    return intersectLineDisc(line, raySource.disc)

###################### Ray tracing ######################

def traceRay(scene, ray):
    if intersectLineSimpleCollimator(ray, scene.collimator) != None:
        return 0
    else:
        if intersectLineSimpleRaySourceDisc(ray, scene.raySource) != None:
            return 1
        else:
            return 0 # To infinity

def calcFluenceLightAllAngles(scene, render, fluency_data, debug):
    for fi in range(render.flx):
        print fi
        for fj in range(render.fly):
            rayOrigin = float4(scene.fluencySquare.square.p0.x + fi*render.xstep + render.xoffset, 
                               scene.fluencySquare.square.p0.y + fj*render.ystep + render.yoffset,
                               scene.fluencySquare.square.p0.z, 0)

            v0 = float4(scene.raySource.disc.origin.x - scene.raySource.disc.radius, 
                        scene.raySource.disc.origin.y - scene.raySource.disc.radius, 
                        scene.raySource.disc.origin.z,
                        scene.raySource.disc.origin.w) - rayOrigin
            vi = float4(v0.x + scene.raySource.disc.radius*2, v0.y, v0.z, v0.w) - rayOrigin
            vj = float4(v0.x, v0.y + scene.raySource.disc.radius*2, v0.z, v0.w) - rayOrigin
            anglei = acos(dot(normalize(v0),normalize(vi)))
            anglej = acos(dot(normalize(v0),normalize(vj)))

            ratio = anglei*anglej/pi*2

            if fi == 4 and fj == 4:
                debug.f0 = ratio
                debug.v0 = rayOrigin

            for li in range(render.lsamples):
                for lj in range(render.lsamples):
                    lPoint =  float4(scene.raySource.disc.origin.x - scene.raySource.disc.radius + li*render.lstep, 
                                     scene.raySource.disc.origin.y - scene.raySource.disc.radius + lj*render.lstep, 
                                     scene.raySource.disc.origin.z,
                                     scene.raySource.disc.origin.w)
                    rayDirection = lPoint - rayOrigin

                    ray = Line(rayOrigin, normalize(rayDirection))

                    if fi == 4 and fj == 4 and li == 1 and lj == 1:
                        debug.v1 = ray.origin
                        debug.v2 = ray.direction

                    fluency_data[fi][fj] += traceRay(scene, ray)*ratio

def drawScene(scene, render, fluency_data, debug):
    calcFluenceLightAllAngles(scene, render, fluency_data, debug)
