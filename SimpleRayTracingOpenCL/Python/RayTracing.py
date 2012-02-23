from ctypes import *
from math import acos, pi, exp, isinf
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
                ("lstep", c_float),
                ("mode", c_int)]

def intersectLineSimpleRaySourceRectangle(line, raySource):
    return intersectLineRectangle(line, raySource.rectangle)

def intersectLineSimpleRaySourceDisc(line, raySource):
    return intersectLineDisc(line, raySource.disc)

###################### Ray tracing ######################

def firstHitLeaf(scene, render, ray, collimator):
    intersect = False
    minDistance = float("inf")
    intersectionPoint = None
    leafIndex = -1
    thickness = 0
    for i in range(collimator.numberOfLeaves):
        intersectTmp = False
        intersectionDistanceTmp = float("inf")
        intersectionPointTmp = None
        if render.mode == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineRectangle(ray, collimator.leaves[i])
        elif render.mode == 1:
            [intersectTmp, intersectionDistanceInTmp, intersectionDistanceOutTmp, intersectionPointInTmp, intersectionPointOutTmp] = intersectLineBoxInOut(ray, collimator.leaves[i])
            intersectionDistanceTmp = intersectionDistanceInTmp

        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            leafIndex = i
            minDistance = intersectionDistanceTmp
            if render.mode == 0:
                intersectionPoint = intersectionPointTmp
            elif render.mode == 1:
                thickness = intersectionDistanceOutTmp - intersectionDistanceInTmp
                intersectionPoint = intersectionPointOutTmp

    if leafIndex != -1:
        intersect = True

    return [intersect, minDistance, intersectionPoint, thickness]

def firstHitCollimator(scene, render, ray, collimators):
    intersect = False
    minDistance = float("inf")
    intersectionPoint = None
    intensityCoeff = 1
    collimatorIndex = -1
    for i in range(scene.collimators):
        #[intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineSimpleCollimator(ray, collimators[i])
        intersectTmp = False
        intersectionDistanceTmp = float("inf")
        intersectionPointTmp = None
        if render.mode == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineBox(ray, collimators[i].flatCollimator.boundingBox)
        elif render.mode == 1:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineBox(ray, collimators[i].boxCollimator.boundingBox)

        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            collimatorIndex = i
            minDistance = intersectionDistanceTmp

    if collimatorIndex != -1:
        thickness = 0
        if render.mode == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, ray, collimators[collimatorIndex].flatCollimator)
        elif render.mode == 1:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, ray, collimators[collimatorIndex].boxCollimator)
        while intersectTmp:
            intersect = True
            minDistance = intersectionDistanceTmp
            intersectionPoint = intersectionPointTmp
            if render.mode == 0:
                thickness = collimators[collimatorIndex].height
            intensityCoeff *= exp(-collimators[collimatorIndex].absorptionCoeff*thickness)
            newRay = Line(intersectionPointTmp, ray.direction)
            if render.mode == 0:
                [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, newRay, collimators[collimatorIndex].flatCollimator)
            elif render.mode == 1:
                [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, newRay, collimators[collimatorIndex].boxCollimator)

    return [intersect, minDistance, intersectionPoint, intensityCoeff]

def traceRayFirstHit(scene, render, ray, collimators):
    intensity = 1;
    [intersectCollimator, distanceCollimator, intersectionPointCollimator, intensityCoeff] = firstHitCollimator(scene, render, ray, collimators)
    while intersectCollimator: # Enable several layers of collimators
        intensity *= intensityCoeff
        newRay = Line(intersectionPointCollimator, ray.direction)
        [intersectCollimator, distanceCollimator, intersectionPointCollimator, intensityCoeff] = firstHitCollimator(scene, render, newRay, collimators)

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

            for li in range(render.lsamples):
                for lj in range(render.lsamples):
                    lPoint =  float4(scene.raySource.disc.origin.x - scene.raySource.disc.radius + li*render.lstep, 
                                     scene.raySource.disc.origin.y - scene.raySource.disc.radius + lj*render.lstep, 
                                     scene.raySource.disc.origin.z,
                                     scene.raySource.disc.origin.w)
                    rayDirection = lPoint - rayOrigin

                    ray = Line(rayOrigin, normalize(rayDirection))

                    #fluency_data[fi][fj] += traceRay(scene, ray)*ratio
                    fluency_data[fi][fj] += traceRayFirstHit(scene, render, ray, collimators)*ratio

def init(scene, render, collimators):
    if render.mode == 0:
        for col in collimators:
            col.flatCollimator = createFlatCollimator(col)
    elif render.mode == 1:
        for col in collimators:
            col.boxCollimator = createBoxCollimator(col)
    else:
        print "Undefined mode"


def drawScene(scene, render, fluency_data, debug):
    calcFluenceLightStraightUp(scene, render, fluency_data, debug)

def drawScene2(scene, render, collimators, fluency_data, debug):
    #init(scene, render, collimators)
    calcFluenceLightAllAngles(scene, render, collimators, fluency_data, debug)
