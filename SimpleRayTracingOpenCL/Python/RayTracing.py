from ctypes import *
from math import acos, pi, exp, isinf
import numpy
import sys

from OpenCLTypes import *
from Python.Collimator import *
from Python.Primitives import *
from Python.Settings import MODE, NUMBER_OF_COLLIMATORS, SOA

###################### Class definitions ######################

class SimpleRaySourceRectangle(Structure):
    _fields_ = [("rectangle", Rectangle)]

class SimpleRaySourceDisc(Structure):
    _fields_ = [("disc", Disc)]

class FluenceMap(Structure):
    _fields_ = [("rectangle", Rectangle)]

class Scene(Structure):
    _fields_ = [("raySource", SimpleRaySourceDisc),
                ("numberOfCollimators", c_int),
                ("collimators", Collimator * NUMBER_OF_COLLIMATORS),
                ("fluenceMap", FluenceMap)]

class Render(Structure):
    _fields_ = [("flx", c_int),
                ("fly", c_int),
                ("xstep", c_float),
                ("ystep", c_float),
                ("xoffset", c_float),
                ("yoffset", c_float),
                ("lsamples", c_int),
                ("lstep", c_float)#,
                #("mode", c_int)
                ]

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
        if MODE == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineFlatCollimatorLeaf(ray, collimator.leaves[i*2], collimator.leaves[i*2 + 1])
        elif MODE == 1:
            [intersectTmp, intersectionDistanceInTmp, intersectionDistanceOutTmp, intersectionPointInTmp, intersectionPointOutTmp] = intersectLineBBoxCollimatorLeaf(ray, collimator.leaves[i])
            intersectionDistanceTmp = intersectionDistanceInTmp
        elif MODE == 2:
            [intersectTmp, intersectionDistanceInTmp, intersectionDistanceOutTmp, intersectionPointInTmp, intersectionPointOutTmp] = intersectLineBoxCollimatorLeaf(ray, collimator.leaves[i])
            intersectionDistanceTmp = intersectionDistanceInTmp

        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            leafIndex = i
            minDistance = intersectionDistanceTmp
            if MODE == 0:
                intersectionPoint = intersectionPointTmp
            elif MODE == 1 or MODE == 2:
                thickness = intersectionDistanceOutTmp - intersectionDistanceInTmp
                intersectionPoint = intersectionPointOutTmp

    if leafIndex != -1:
        intersect = True

    return [intersect, minDistance, intersectionPoint, thickness]

def firstHitCollimator(scene, render, ray, collimators):
    intersect = False
    minDistance = float("inf")
    intersectionPoint = None
    bbOutDistance = None
    intensityCoeff = 1
    collimatorIndex = -1
    for i in range(scene.collimators):
        #[intersectTmp, intersectionDistanceTmp, intersectionPointTmp] = intersectLineSimpleCollimator(ray, collimators[i])
        intersectTmp = False
        intersectionDistanceTmp = float("inf")
        intersectionPointTmp = None
        intersectionDistanceOutTmp = float("inf")
        intersectionPointOutTmp = None
        if MODE == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionDistanceOutTmp, intersectionPointTmp, intersectionPointOutTmp] = intersectLineBBoxInOut(ray, collimators[i].flatCollimator.boundingBox)
        elif MODE == 1:
            [intersectTmp, intersectionDistanceTmp, intersectionDistanceOutTmp, intersectionPointTmp, intersectionPointOutTmp] = intersectLineBBoxInOut(ray, collimators[i].bboxCollimator.boundingBox)
        elif MODE == 2:
            [intersectTmp, intersectionDistanceTmp, intersectionDistanceOutTmp, intersectionPointTmp, intersectionPointOutTmp] = intersectLineBBoxInOut(ray, collimators[i].boxCollimator.boundingBox)

        if intersectTmp == True and intersectionDistanceTmp < minDistance:
            collimatorIndex = i
            minDistance = intersectionDistanceTmp
            bbOutDistance = intersectionDistanceOutTmp
            intersectionPoint = intersectionPointOutTmp

    if collimatorIndex != -1:
        thickness = 0
        if MODE == 0:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, ray, collimators[collimatorIndex].flatCollimator)
        elif MODE == 1:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, ray, collimators[collimatorIndex].bboxCollimator)
        elif MODE == 2:
            [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, ray, collimators[collimatorIndex].boxCollimator)
        while intersectTmp:
            intersect = True
            minDistance = intersectionDistanceTmp
            intersectionPoint = intersectionPointTmp
            if MODE == 0:
                thickness = collimators[collimatorIndex].height
            intensityCoeff *= exp(-collimators[collimatorIndex].absorptionCoeff*thickness)
            newRay = Line(intersectionPointTmp, ray.direction)
            if MODE == 0:
                [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, newRay, collimators[collimatorIndex].flatCollimator)
            elif MODE == 1:
                [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, newRay, collimators[collimatorIndex].bboxCollimator)
            elif MODE == 2:
                [intersectTmp, intersectionDistanceTmp, intersectionPointTmp, thickness] = firstHitLeaf(scene, render, newRay, collimators[collimatorIndex].boxCollimator)

        if (intersect == False):
            intersect = True
            minDistance = bbOutDistance

    return [intersect, minDistance, intersectionPoint, intensityCoeff]

def traceRayFirstHit(scene, render, ray, collimators):
    intensity = 1
    [intersectCollimator, distanceCollimator, intersectionPointCollimator, intensityCoeff] = firstHitCollimator(scene, render, ray, collimators)
    while intersectCollimator: # Enable several layers of collimators
        intensity *= intensityCoeff
        if (intensity < 0.0000001): # If intensity is below a treshhold, don't bother to cast more rays. Return 0 intensity.
            return 0
        else:
            newRay = Line(intersectionPointCollimator, ray.direction)
            [intersectCollimator, distanceCollimator, intersectionPointCollimator, intensityCoeff] = firstHitCollimator(scene, render, newRay, collimators)

    [intersectRS, intersectionDistanceRS, intersectionPointRS] = intersectLineSimpleRaySourceDisc(ray, scene.raySource)
    if intersectRS == True:
        return intensity
    else:
        return 0

def calcFluenceElement(scene, render, collimators, fluency_data, fi, fj, debug):
    rayOrigin = float4(scene.fluenceMap.rectangle.p0.x + fi*render.xstep + render.xoffset, 
                               scene.fluenceMap.rectangle.p0.y + fj*render.ystep + render.yoffset,
                               scene.fluenceMap.rectangle.p0.z, 0)

    v0 = float4(scene.raySource.disc.origin.x - scene.raySource.disc.radius, 
                scene.raySource.disc.origin.y, 
                scene.raySource.disc.origin.z,
                scene.raySource.disc.origin.w) - rayOrigin
    v1 = float4(scene.raySource.disc.origin.x, 
                scene.raySource.disc.origin.y - scene.raySource.disc.radius, 
                scene.raySource.disc.origin.z,
                scene.raySource.disc.origin.w) - rayOrigin
    vi = float4(v0.x + scene.raySource.disc.radius*2, v0.y, v0.z, v0.w) - rayOrigin
    vj = float4(v1.x, v1.y + scene.raySource.disc.radius*2, v1.z, v1.w) - rayOrigin
    anglei = acos(dot(normalize(v0),normalize(vi)))
    anglej = acos(dot(normalize(v1),normalize(vj)))

    ratio = anglei*anglej/pi*2

    for li in range(LSAMPLES):
        for lj in range(LSAMPLES):
            lPoint =  float4(scene.raySource.disc.origin.x - scene.raySource.disc.radius + li*render.lstep, 
                             scene.raySource.disc.origin.y - scene.raySource.disc.radius + lj*render.lstep, 
                             scene.raySource.disc.origin.z,
                             scene.raySource.disc.origin.w)
            rayDirection = lPoint - rayOrigin

            ray = Line(rayOrigin, normalize(rayDirection))

            fluency_data[fi][fj] += traceRayFirstHit(scene, render, ray, collimators)*ratio

def calcAllFluenceElements(scene, render, collimators, fluency_data, debug):
    for fi in range(render.flx):
        print fi
        for fj in range(render.fly):
            calcFluenceElement(scene, render, collimators, fluency_data, fi, fj, debug)

def init(scene, render, collimators, leaf_array):
    for col in collimators:
        leaves = []
        if MODE == 0:
            [col.flatCollimatorm, leaves] = createFlatCollimator(col)
        elif MODE == 1:
            [col.bboxCollimator, leaves] = createBBoxCollimator(col)
        elif MODE == 2:
            [col.boxCollimator, leaves] = createBoxCollimator(col)
        else:
            print "Undefined mode"
        leaf_array.extend(leaves)


def drawScene(scene, render, collimators, fluency_data, debug):
    calcAllFluenceElements(scene, render, collimators, fluency_data, debug)
