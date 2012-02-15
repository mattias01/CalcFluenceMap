from ctypes import *
from math import acos, pi
import numpy
import sys

from OpenCLTypes import *
from Python.Collimator import *
from Python.Primitives import *

###################### Class definitions ######################

class SimpleRaySourceRectangle(Structure):
    _fields_ = [("rectangle", Rectangle)]

class SimpleRaySourceDisc(Structure):
    _fields_ = [("disc", Disc)]

class FluenceMap(Structure):
    _fields_ = [("rectangle", Rectangle)]

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

def intersectLineSimpleRaySourceRectangle(line, raySource):
    return intersectLineRectangle(line, raySource.rectangle)

def intersectLineSimpleRaySourceDisc(line, raySource):
    return intersectLineDisc(line, raySource.disc)

###################### Ray tracing ######################

def firstHitCollimator(scene, ray, collimators):
    intersect = False
    minDistance = float("inf")
    intersectionPoint = None
    attenuation = 1
    for i in range(scene.collimators):
        #[intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineSimpleCollimator(ray, collimators[i])
        [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineFlatCollimator(ray, collimators[i])
        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            minDistance = intersectionDistanceTmp
            intersect = True
            intersectionPoint = intersectionPointTmp
            attenuation = collimators[i].attenuation

    return [intersect, minDistance, intersectionPoint, attenuation]

def traceRayFirstHit(scene, ray, collimators):
    intensity = 1;
    [intersectCollimator, distanceCollimator, intersectionPointCollimator, attenuation] = firstHitCollimator(scene, ray, collimators)
    while intersectCollimator: # Enable several layers of collimators
        intensity *= attenuation
        newRay = Line(intersectionPointCollimator+ray.direction*0.0000000001, ray.direction) # Cast a new ray just after the collimator.
        [intersectCollimator, distanceCollimator, intersectionPointCollimator, attenuation] = firstHitCollimator(scene, newRay, collimators)
    
    [intersectRS, intersectionDistanceRS, intersectionPointRS] = intersectLineSimpleRaySourceDisc(ray, scene.raySource)
    if intersectRS == True:
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
            ray = Line(float4(scene.fluenceMap.rectangle.p0.x + i*render.xstep + render.xoffset, 
                              scene.fluenceMap.rectangle.p0.y + j*render.ystep + render.yoffset, 
                              scene.fluenceMap.rectangle.p0.z,0), float4(0,0,1,0))
            fluency_data[i][j] = traceRay(scene, ray)

def calcFluenceLightAllAngles(scene, render, collimators, fluency_data, debug):
    for fi in range(render.flx):
        print fi
        for fj in range(render.fly):
            rayOrigin = float4(scene.fluenceMap.rectangle.p0.x + fi*render.xstep + render.xoffset, 
                               scene.fluenceMap.rectangle.p0.y + fj*render.ystep + render.yoffset,
                               scene.fluenceMap.rectangle.p0.z, 0)

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
