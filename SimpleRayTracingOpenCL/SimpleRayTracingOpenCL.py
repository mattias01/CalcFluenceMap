import ctypes
import matplotlib.cm as cm
from matplotlib.contour import ContourSet
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.pyplot as plt
import numpy as np
import os
import pyopencl as cl
import struct
from sys import getsizeof
from time import time, sleep
#import visual as vs

#from OpenCLUtility import OpenCLUtility as oclu
import OpenCLUtility
from OpenCLTypes import *
from Python.Collimator import CollimatorAoStoSoA, float4ArrayFromCollimators
from Python.RayTracing import *
from Test import *
from Python.Settings import *
import Python.Settings as Settings
from Autotune.Autotune import *
from Autotune.Parameter import Parameter
from Autotune.ParameterSet import ParameterSet

print 'Start SimpleRayTracingOpenCL'

# Select execution environment (Python, OpenCl or both)
def select_excecution_environment():
    run = raw_input("Choose environment:\n0: OpenCL, 1: Python, 2: Both\n[0]:")

    PYTHON = 0
    OPENCL = 1
    if run == "1":
        PYTHON = 1
        OPENCL = 0
    elif run == "2":
        PYTHON = 1

# Init OpenCL
def init_OpenCL():
    ctx = cl.create_some_context()
    os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"
    os.environ["CL_LOG_ERRORS"] = "stdout"
    #ctx = cl.Context(devices=[cl.get_platforms()[0].get_devices()[0]]) # Choose the first device.
    queue = cl.CommandQueue(ctx)

    return [ctx, queue]

# Run tests
def test():
    if PYTHON == 1:
        np.seterr(divide='ignore') # Disable warning on division by zero.
        testPython()
    if OPENCL == 1:
        testOpenCL(ctx, queue)

def init_scene():
    # Build scene objects
    rs = Disc(float4(0,0,0,0), float4(0,0,1,0), 1)

    """col1 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1.position = float4(-5.9, -10, -29.5,0)
    col1.xdir = float4(0,1,0,0)
    col1.ydir = float4(1,0,0,0)
    col1.absorptionCoeff = 1.0
    col1.height = 8.2
    col1.numberOfLeaves = 40
    col1.width = 11.8
    col1.leafPositions = (5,5.1,5.2,5.3,5.2,5.1,5.0,4.9,4.8,4.7,4.6,4.5,4.4,4.2,4,3.8,3.6,3.4,3.2,3.3,3.4,3.5,6,6,6.3,6.4,6,6,7,6,7,6,7,6,7,6,7,6,7,6)
    col1.boundingBox = calculateCollimatorBoundingBox(col1)"""

    """col1a = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1a.position = float4(-5.9, -10, -29.5,0)
    col1a.xdir = float4(0,1,0,0)
    col1a.ydir = float4(1,0,0,0)
    col1a.absorptionCoeff = 1.0
    col1a.height = 8.2
    col1a.numberOfLeaves = 20
    col1a.width = 5.9
    col1a.leafPositions = (5,5.1,5.2,5.3,5.2,5.1,5.0,4.9,4.8,4.7,4.6,4.5,4.4,4.2,4,3.8,3.6,3.4,3.2,3.3)
    col1a.boundingBox = calculateCollimatorBoundingBox(col1a)"""

    col1a1 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1a1.position = float4(-5.9, -12, -29.5,0)
    col1a1.xdir = float4(0,1,0,0)
    col1a1.ydir = float4(1,0,0,0)
    col1a1.absorptionCoeff = 1.0
    col1a1.height = 8.2
    col1a1.numberOfLeaves = 10
    col1a1.width = 2.95
    col1a1.leafPositions = (6,6.1,6.2,6.3,6.2,6.1,6.0,5.9,5.8,5.7)
    col1a1.boundingBox = calculateCollimatorBoundingBox(col1a1)

    col1a2 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1a2.position = float4(-2.95, -12, -29.5,0)
    col1a2.xdir = float4(0,1,0,0)
    col1a2.ydir = float4(1,0,0,0)
    col1a2.absorptionCoeff = 1.0
    col1a2.height = 8.2
    col1a2.numberOfLeaves = 10
    col1a2.width = 2.95
    col1a2.leafPositions = (5.6,5.5,5.4,5.2,5,4.8,4.6,4.4,4.2,4.3)
    col1a2.boundingBox = calculateCollimatorBoundingBox(col1a2)

    col1b1 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1b1.position = float4(0, -12, -29.5,0)
    col1b1.xdir = float4(0,1,0,0)
    col1b1.ydir = float4(1,0,0,0)
    col1b1.absorptionCoeff = 1.0
    col1b1.height = 8.2
    col1b1.numberOfLeaves = 10
    col1b1.width = 2.95
    col1b1.leafPositions = (4.4,4.5,7,7,7.3,7.4,7,7,8,7)
    col1b1.boundingBox = calculateCollimatorBoundingBox(col1b1)

    col1b2 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1b2.position = float4(2.95, -12, -29.5,0)
    col1b2.xdir = float4(0,1,0,0)
    col1b2.ydir = float4(1,0,0,0)
    col1b2.absorptionCoeff = 1.0
    col1b2.height = 8.2
    col1b2.numberOfLeaves = 10
    col1b2.width = 2.95
    col1b2.leafPositions = (8,7,8,7,8,7,8,7,8,7)
    col1b2.boundingBox = calculateCollimatorBoundingBox(col1b2)

    """col2 = Collimator()
    col2.position = float4(5.9, 10, -29.5,0)
    col2.xdir = float4(0,-1,0,0)
    col2.ydir = float4(-1,0,0,0)
    col2.absorptionCoeff = 1.0
    col2.height = 8.2
    col2.numberOfLeaves = 40
    col2.width = 11.8
    col2.leafPositions = (8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9)
    col2.boundingBox = calculateCollimatorBoundingBox(col2)"""

    """col2a = Collimator()
    col2a.position = float4(5.9, 10, -29.5,0)
    col2a.xdir = float4(0,-1,0,0)
    col2a.ydir = float4(-1,0,0,0)
    col2a.absorptionCoeff = 1.0
    col2a.height = 8.2
    col2a.numberOfLeaves = 20
    col2a.width = 5.9
    col2a.leafPositions = (8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9)
    col2a.boundingBox = calculateCollimatorBoundingBox(col2a)"""

    col2a1 = Collimator()
    col2a1.position = float4(5.9, 12, -29.5,0)
    col2a1.xdir = float4(0,-1,0,0)
    col2a1.ydir = float4(-1,0,0,0)
    col2a1.absorptionCoeff = 1.0
    col2a1.height = 8.2
    col2a1.numberOfLeaves = 10
    col2a1.width = 2.95
    col2a1.leafPositions = (9,10,9,10,9,10,9,10,9,10)
    col2a1.boundingBox = calculateCollimatorBoundingBox(col2a1)

    col2a2 = Collimator()
    col2a2.position = float4(2.95, 12, -29.5,0)
    col2a2.xdir = float4(0,-1,0,0)
    col2a2.ydir = float4(-1,0,0,0)
    col2a2.absorptionCoeff = 1.0
    col2a2.height = 8.2
    col2a2.numberOfLeaves = 10
    col2a2.width = 2.95
    col2a2.leafPositions = (9,10,9,10,9,10,9,10,9,10)
    col2a2.boundingBox = calculateCollimatorBoundingBox(col2a2)

    col2b1 = Collimator()
    col2b1.position = float4(0, 12, -29.5,0)
    col2b1.xdir = float4(0,-1,0,0)
    col2b1.ydir = float4(-1,0,0,0)
    col2b1.absorptionCoeff = 1.0
    col2b1.height = 8.2
    col2b1.numberOfLeaves = 10
    col2b1.width = 2.95
    col2b1.leafPositions = (9,10,9,10,9,10,9,10,9,10)
    col2b1.boundingBox = calculateCollimatorBoundingBox(col2b1)

    col2b2 = Collimator()
    col2b2.position = float4(-2.95, 12, -29.5,0)
    col2b2.xdir = float4(0,-1,0,0)
    col2b2.ydir = float4(-1,0,0,0)
    col2b2.absorptionCoeff = 1.0
    col2b2.height = 8.2
    col2b2.numberOfLeaves = 10
    col2b2.width = 2.95
    col2b2.leafPositions = (9,10,9,10,9,10,9,10,9,10)
    col2b2.boundingBox = calculateCollimatorBoundingBox(col2b2)

    """col2b = Collimator()
    col2b.position = float4(0, 10, -29.5,0)
    col2b.xdir = float4(0,-1,0,0)
    col2b.ydir = float4(-1,0,0,0)
    col2b.absorptionCoeff = 1.0
    col2b.height = 8.2
    col2b.numberOfLeaves = 20
    col2b.width = 5.9
    col2b.leafPositions = (8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9,8,9)
    col2b.boundingBox = calculateCollimatorBoundingBox(col2b)"""

    jaw1 = Collimator()
    jaw1.position = float4(14,-14,-45.1,0)
    jaw1.xdir = float4(-1,0,0,0)
    jaw1.ydir = float4(0,1,0,0)
    jaw1.absorptionCoeff = 1.0
    jaw1.height = 7.2
    jaw1.width = 14*2
    jaw1.numberOfLeaves = 1
    jaw1.leafPositions = (10,)
    jaw1.boundingBox = calculateCollimatorBoundingBox(jaw1)

    jaw2 = Collimator()
    jaw2.position = float4(-14,14,-45.1,0)
    jaw2.xdir = float4(1,0,0,0)
    jaw2.ydir = float4(0,-1,0,0)
    jaw2.absorptionCoeff = 1.0
    jaw2.height = 7.2
    jaw2.width = 14*2
    jaw2.numberOfLeaves = 1
    jaw2.leafPositions = (10,)
    jaw2.boundingBox = calculateCollimatorBoundingBox(jaw2)

    collimator_array = Collimator * NUMBER_OF_COLLIMATORS
    #collimators = collimator_array(jaw1, jaw2, col1, col2)
    collimators = collimator_array(jaw1, jaw2, col1a1, col1a2, col1b1, col1b2, col2a1, col2a2, col2b1, col2b2)
    leaves = []
    initCollimators(collimators, leaves) # Init Collimator

    leaf_array_type = float4 * len(leaves)
    leaf_array = leaf_array_type()
    for i in range(len(leaves)):
        leaf_array[i] = leaves[i]

    collimators = CollimatorAoStoSoA(collimators) # Should be removed and collimator init should be done as SOA.

    fm = FluenceMap(Rectangle(float4(-30.0, -30.0, -100.0, 0.0), float4(30.0, -30.0, -100.0, 0.0), float4(30.0, 30.0, -100.0, 0.0), float4(-30.0, 30.0, -100.0, 0.0)))
    scene = Scene(fm, rs, NUMBER_OF_COLLIMATORS, collimators)
    
    return [scene, collimators, leaf_array]

def define_settings(scene):
    # Settings
    XSTEP = float(length(scene.fluenceMap.rectangle.p1 - scene.fluenceMap.rectangle.p0)/FLX) # Length in x / x resolution
    YSTEP = float(length(scene.fluenceMap.rectangle.p3 - scene.fluenceMap.rectangle.p0)/FLY) # Length in y / y resolution
    XOFFSET = float(XSTEP/2.0)
    YOFFSET = float(YSTEP/2.0)
    LSTEP = float(scene.raySource.radius*2/(LSAMPLES-1))
    settingsList = getDefaultSettingsList()
    settingsList.append(("XSTEP", str(XSTEP)+'f', True))
    settingsList.append(("YSTEP", str(YSTEP)+'f', True))
    settingsList.append(("XOFFSET", str(XOFFSET)+'f', True))
    settingsList.append(("YOFFSET", str(YOFFSET)+'f', True))
    settingsList.append(("LSTEP", str(LSTEP)+'f', True))

    return settingsList

# Run in Python
def run_Python(scene, render, collimators):
    time1 = time()
    debugPython = Debug()
    fluence_data_Python = numpy.zeros(shape=(FLX,FLY), dtype=numpy.float32)
    drawScene(scene, render, collimators, fluence_data_Python, debugPython)
    timePython = time()-time1

    samplesPerSecond_OpenCL = FLX*FLY*LSAMPLES*LSAMPLES/timePython
    print "Time Python: ", time_Python, " Samples per second: ", samplesPerSecond_Python

    return [fluence_data_Python, time_Python, samplesPerSecond_Python]

# Run in OpenCL
def run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, optimizationParameters):
    debugOpenCL = Debug()
    settingsString = macroString(settingsList)
    X_size = int(optimizationParameters[1][1])
    Y_size = int(optimizationParameters[2][1])
    Z_size = int(optimizationParameters[3][1])
    optParametersString = macroString(optimizationParameters)
    optParametersString += " -D WG_LIGHT_SAMPLING_SIZE=" + str(X_size*Y_size*Z_size)

    #program = oclu.loadProgram(ctx, PATH_OPENCL + "RayTracingGPU.cl", "-cl-nv-verbose " + settingsString)
    #program = oclu.loadProgram(ctx, PATH_OPENCL + "RayTracingGPU.cl", "-cl-auto-vectorize-disable " + settingsString)
    #program = oclu.loadProgram(ctx, PATH_OPENCL + "RayTracingGPU.cl", " " + settingsString + " " + optParametersString)
    program = oclu.loadCachedProgram(ctx, PATH_OPENCL + "RayTracing.cl", " " + settingsString + " " + optParametersString)

    mf = cl.mem_flags
    scene_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=scene)
    #render_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=render)
    leaf_array_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=leaf_array)
    intensities_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.ALLOC_HOST_PTR, size=intensities.nbytes)
    fluence_data_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.ALLOC_HOST_PTR, size=fluence_data.nbytes)
    debugOpenCL_buf = cl.Buffer(ctx, mf.WRITE_ONLY, sizeof(debugOpenCL))
    
    time1 = time()
    program.flatLightSourceSampling(queue, intensities.shape, (X_size, Y_size, Z_size), scene_buf, leaf_array_buf, intensities_buf, debugOpenCL_buf).wait()
    #program.flatLightSourceSampling(queue, intensities.shape, (optimizationParameters[1][1], optimizationParameters[2][1], optimizationParameters[3][1]), scene_buf, leaf_array_buf, intensities_buf, debugOpenCL_buf).wait()
    #program.flatLightSourceSampling(queue, intensities.shape, None, scene_buf, leaf_array_buf, intensities_buf, debugOpenCL_buf).wait()

    time2 = time()
    program.calculateIntensityDecreaseWithDistance(queue, fluence_data.shape, None, scene_buf, fluence_data_buf, debugOpenCL_buf).wait()
    time3 = time()
    program.calcFluenceElement(queue, fluence_data.shape, None, scene_buf, intensities_buf, fluence_data_buf, debugOpenCL_buf).wait()
    time4 = time()
    cl.enqueue_read_buffer(queue, fluence_data_buf, fluence_data)
    cl.enqueue_read_buffer(queue, debugOpenCL_buf, debugOpenCL).wait()
    timeOpenCL = time()-time1

    #print "flatLightSourceSampling(): ", time2 - time1, ", calculateIntensityDecreaseWithDistance():", time3 - time2, ", calcFluenceElement():", time4 - time3
    samplesPerSecondOpenCL = FLX*FLY*LSAMPLES*LSAMPLES/timeOpenCL
    #print "Time OpenCL: ", timeOpenCL, " Samples per second: ", samplesPerSecondOpenCL
    #print fluence_data

    return [fluence_data, timeOpenCL, samplesPerSecondOpenCL]

# Show plots
def show_plot(scene, fluence_data, elapsed_time, samplesPerSecond):
    rspatch = patches.Circle((scene.raySource.origin.y, scene.raySource.origin.x), 
                                scene.raySource.radius, facecolor='none', edgecolor='red', linewidth=1, alpha=0.5)
    print fluence_data
    plt.imshow(fluence_data, interpolation='none', cmap=cm.gray, extent=[scene.fluenceMap.rectangle.p0.y,
                                                                         scene.fluenceMap.rectangle.p3.y,
                                                                         -scene.fluenceMap.rectangle.p0.x,
                                                                         -scene.fluenceMap.rectangle.p1.x])

    plt.gca().add_patch(rspatch)

    plt.title("X " + "Time: " + str(elapsed_time) + " Samples per second: " + str(samplesPerSecond))
    plt.show()

def show_3D_scene(scene, leaf_array):
    # Visual python
    disp = vs.display()
    #disp.autocenter = True
    disp.userspin = True
    disp.ambient = 0.5
    disp.forward = (0, 0, -1)
    disp.center = (0, 0, -50)
    disp.range = (30, 30, -100)

    # Collimators
    """for i in range(NUMBER_OF_COLLIMATORS):
        fr = vs.frame()
        if MODE == 0:
            f = vs.faces(frame = fr, pos = collimators.flatCollimator[i].getVertices())
        elif MODE == 1:
            f = vs.faces(frame = fr, pos = collimators.bboxCollimator[i].getVertices())
        elif MODE == 2:
            f = vs.faces(frame = fr, pos = collimators.boxCollimator[i].getVertices())
            #bb = vs.faces(frame = fr, pos = bboxToBox(collimators[i].boxCollimator.boundingBox).getVertices())
            #bb.make_normals()
            #bb.color = vs.color.blue
        f.color = vs.color.orange
        f.make_normals()"""
    fr = vs.frame()
    f = vs.faces(frame = fr, pos = leaf_array_to_vertices(leaf_array))
    f.color = vs.color.orange
    f.make_normals()

    # Fluence map
    #fluence_dataOpenCL *= 255.0/fluence_dataOpenCL.max()
    #tex = vs.materials.texture(data=fluence_dataOpenCL, mapping="rectangular", interpolate=False)
    fr = vs.frame()
    f = vs.faces(frame=fr, pos=scene.fluenceMap.rectangle.getVertices(), color = vs.color.gray(50))
    f.make_normals()
    f.make_twosided()

    # Ray source
    vs.cylinder(pos=scene.raySource.origin.get3DTuple(), axis=scene.raySource.normal.get3DTuple(), radius=scene.raySource.radius, color=vs.color.red, opacity=0.5)

    #fr.rotate (angle = -pi/2, axis = (1.0, 1.0, 0.0))

def main():
    #select_excecution_environment()
    if OPENCL == 1:
        [ctx, queue] = init_OpenCL()
    #test()
    [scene, collimators, leaf_array] = init_scene()
    settingsList = define_settings(scene)

    list = []
    list.append(Parameter("LINE_TRIANGLE_INTERSECTION_ALGORITHM", [2], True))
    list.append(Parameter("WG_LIGHT_SAMPLING_X", [1,2,4,8,16,32,64,128], False))
    list.append(Parameter("WG_LIGHT_SAMPLING_Y", [1,2,4,8,16,32,64,128], False))
    list.append(Parameter("WG_LIGHT_SAMPLING_Z", [1,2,4,8,16,32], False))
    list.append(Parameter("RAY_AS", [0], True))
    list.append(Parameter("LEAF_AS", [1], True))
    list.append(Parameter("SCENE_AS", [2], True))
    list.append(Parameter("STRUCTURE", [0], True))

    fluence_data = numpy.zeros(shape=(FLX,FLY), dtype=numpy.float32)
    intensities = numpy.zeros(shape=(FLX,FLY,LSAMPLES*LSAMPLES), dtype=numpy.float32)

    oclu = OpenCLUtility.OpenCLUtility()

    #at = Autotune(ParameterSet(list), run_OpenCL, (oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList))

    #at.findOptimizationParameters()

    #print at.getTable()
    #at.saveCSV()

    # Reset output data
    fluence_data = numpy.zeros(shape=(FLX,FLY), dtype=numpy.float32)
    intensities = numpy.zeros(shape=(FLX,FLY,LSAMPLES*LSAMPLES), dtype=numpy.float32)

    #[fluence_data_Python, time_Python, samples_Python] = run_Python(scene, render, collimators, fluence_data_Python)
    #[fluence_data_OpenCL, time_OpenCL, samplesPerSecond_OpenCL] = run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, at.best_parameters)
    [fluence_data_OpenCL, time_OpenCL, samplesPerSecond_OpenCL] = run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, getDefaultOptimizationParameterList())

    if SHOW_PLOT == 1:
        if PYTHON == 1:
            show_plot(scene, fluence_data_Python, time_Python, samplesPerSecond_Python)
        if OPENCL == 1:
            show_plot(scene, fluence_data_OpenCL, time_OpenCL, samplesPerSecond_OpenCL)
    if SHOW_3D_SCENE == 1:
        show_3D_scene(scene, leaf_array)
    
if __name__=="__main__":
    main()
