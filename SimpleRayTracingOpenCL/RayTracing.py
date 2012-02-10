import numpy
import sys
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

class FluenceMap(Structure):
    _fields_ = [("square", Square)]

class Scene(Structure):
    _fields_ = [("raySource", SimpleRaySourceDisc),
                ("collimator", SimpleCollimator),
                ("fluenceMap", FluenceMap)]

class Scene2(Structure):
    _fields_ = [("raySource", SimpleRaySourceDisc),
                ("collimators", c_int),
                ("fluenceMap", FluenceMap)]

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
    # Init to not intersect.
    intersect = False
    intersectionDistance = None
    intersectionPoint = None
    if dot(line.direction, plane.normal) != 0:
        # Does intersect.
        intersect = True
        intersectionDistance = (dot(plane.normal, (plane.origin - line.origin))) / (dot(plane.normal, line.direction))
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

def intersectLineSquare(line, square):
    # Split square into two triangles and test them individually.
    t1 = Triangle(square.p0, square.p1, square.p2)
    t2 = Triangle(square.p2, square.p3, square.p0)
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

def intersectLineSimpleCollimator(line, collimator):
    [intersect, intersectionDistance, intersectionPoint] = intersectLineSquare(line, collimator.leftSquare)
    if intersect == False:
        [intersect, intersectionDistance, intersectionPoint] = intersectLineSquare(line, collimator.rightSquare)

    return [intersect, intersectionDistance, intersectionPoint]

def intersectLineSimpleRaySourceSquare(line, raySource):
    return intersectLineSquare(line, raySource.square)

def intersectLineSimpleRaySourceDisc(line, raySource):
    return intersectLineDisc(line, raySource.disc)

###################### Ray tracing ######################

def firstHitCollimator(scene, ray, collimators):
    intersect = False
    minDistance = float("inf")
    intersectionPoint = None
    attenuation = 1
    for i in range(scene.collimators):
        [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineSimpleCollimator(ray, collimators[i])
        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            minDistance = intersectionDistanceTmp
            intersect = True
            intersectionPoint = intersectionPointTmp
            attenuation = 0.2

    return [intersect, minDistance, intersectionPoint, attenuation]

def traceRayFirstHit(scene, ray, collimators):
    intensity = 1;
    [intersectCollimator, distanceCollimator, intersectionPointCollimator, attenuation] = firstHitCollimator(scene, ray, collimators)
    while intersectCollimator: # Enable several layers of collimators
        intensity *= attenuation
        newRay = Line(intersectionPointCollimator+ray.direction*(sys.float_info.min*2)) # Cast a new ray just after the collimator.
        [intersectCollimator, distanceCollimator, intersectionPointCollimator, attenuation] = firstHitCollimator(scene, newRay, collimators)
    
    [intersectRS, intersectionDistanceRS, intersectionPointRS] = intersectLineSimpleRaySourceDisc(ray, scene.raySource)
    if intersectRS != None:
        return intensity
    else:
        return 0

def traceRay(scene, ray):
    [intersectCol, intersectionDistanceCol, intersectionPointCol] = intersectLineSimpleCollimator(ray, scene.collimator)
    if intersectCol == True:
        return 0
    else:
        [intersectRS, intersectionDistanceRS, intersectionPointRS] = intersectLineSimpleRaySourceDisc(ray, scene.raySource)
        if intersectRS == True:
            return 1
        else:
            return 0 # To infinity

def calcFluenceLightStraightUp(scene, render, fluency_data, debug):
    for i in range(render.flx):
        for j in range(render.fly):
            ray = Line(float4((scene.fluenceMap.square.p0.x + i*render.xstep + render.xoffset), 
                              (scene.fluenceMap.square.p0.y + j*render.ystep + render.yoffset), 0,0), float4(0,0,1,0))
            fluency_data[i][j] = traceRay(scene, ray)

def calcFluenceLightAllAngles(scene, render, collimators, fluency_data, debug):
    for fi in range(render.flx):
        print fi
        for fj in range(render.fly):
            rayOrigin = float4(scene.fluenceMap.square.p0.x + fi*render.xstep + render.xoffset, 
                               scene.fluenceMap.square.p0.y + fj*render.ystep + render.yoffset,
                               scene.fluenceMap.square.p0.z, 0)

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

                    #fluency_data[fi][fj] += traceRay(scene, ray)*ratio
                    fluency_data[fi][fj] += traceRayFirstHit(scene, ray, collimators)*ratio

def drawScene(scene, render, fluency_data, debug):
    calcFluenceLightStraightUp(scene, render, fluency_data, debug)

def drawScene2(scene, render, collimators, fluency_data, debug):
    calcFluenceLightAllAngles(scene, render, collimators, fluency_data, debug)
