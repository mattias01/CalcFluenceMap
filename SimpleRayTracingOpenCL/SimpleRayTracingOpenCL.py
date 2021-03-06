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
#from Python.Settings import *
import Python.Settings as Settings
from Autotune.Autotune import *
from Autotune.Parameter import Parameter
from Autotune.ParameterSet import ParameterSet

print 'Start SimpleRayTracingOpenCL'

# Select execution environment (Python, OpenCl or both)
def select_excecution_environment():
    run = raw_input("Choose environment:\n0: OpenCL, 1: Python, 2: Both\n[0]:")

    Settings.PYTHON = 0
    Settings.OPENCL = 1
    if run == "1":
        Settings.PYTHON = 1
        Settings.OPENCL = 0
    elif run == "2":
        Settings.PYTHON = 1

# Init OpenCL
def init_OpenCL():
    #ctx = cl.create_some_context()
    ctx = cl.Context(devices=[cl.get_platforms()[0].get_devices()[0]]) # Choose the first device.
    os.environ["PYOPENCL_COMPILER_OUTPUT"] = "1"
    os.environ["CL_LOG_ERRORS"] = "stdout"
    queue = cl.CommandQueue(ctx)

    return [ctx, queue]

# Run tests
def test():
    if Settings.PYTHON == 1:
        np.seterr(divide='ignore') # Disable warning on division by zero.
        testPython()
    if Settings.OPENCL == 1:
        testOpenCL(ctx, queue)

def init_scene(pieces):
    setDefaultSettings()
    # Build scene objects
    rs = Disc(float4(0,0,0,0), float4(0,0,1,0), 1)

    Collimator = collimatorFactory()

    col1 = Collimator()
    #float4(-5.9,-5.9,-29.5,0)
    col1.position = float4(-59, -100, -295, 0)
    col1.xdir = float4(0,1,0,0)
    col1.ydir = float4(1,0,0,0)
    col1.absorptionCoeff = 0.06
    col1.height = 82
    col1.numberOfLeaves = 40
    col1.width = 118
    col1.leafPositions = (50,51,52,53,52,51,50,49,48,47,46,45,44,42,40,38,36,34,32,33,34,35,60,60,63,64,60,60,70,60,70,60,70,60,70,60,70,60,70,60) #(50,51,52,53,52,51,50,49,48,47,46,45,44,42,40,38,36,34,32,33,34,35,60,60,63,64,60,60,70,60,70,60,70,60,70,60,70,60,70,60,50,51,52,53,52,51,50,49,48,47,46,45,44,42,40,38,36,34,32,33,34,35,60,60,63,64,60,60,70,60,70,60,70,60,70,60,70,60,70,60,50,51,52,53,52,51,50,49,48,47,46,45,44,42,40,38,36,34,32,33,34,35,60,60,63,64,60,60,70,60,70,60,70,60,70,60,70,60,70,60,50,51,52,53,52,51,50,49,48,47,46,45,44,42,40,38,36,34,32,33,34,35,60,60,63,64,60,60,70,60,70,60,70,60,70,60,70,60,70,60)
    col1.boundingBox = calculateCollimatorBoundingBox(col1)

    col2 = Collimator()
    col2.position = float4(59, 100, -295, 0)
    col2.xdir = float4(0,-1,0,0)
    col2.ydir = float4(-1,0,0,0)
    col2.absorptionCoeff = 0.06
    col2.height = 82
    col2.numberOfLeaves = 40
    col2.width = 118
    col2.leafPositions = (80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90) #(80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90,80,90)
    col2.boundingBox = calculateCollimatorBoundingBox(col2)

    jaw1 = Collimator()
    jaw1.position = float4(140,-140,-451,0)
    jaw1.xdir = float4(-1,0,0,0)
    jaw1.ydir = float4(0,1,0,0)
    jaw1.absorptionCoeff = 0.06#0.1
    jaw1.height = 72
    jaw1.width = 140*2
    jaw1.numberOfLeaves = 1
    jaw1.leafPositions = (100,)
    jaw1.boundingBox = calculateCollimatorBoundingBox(jaw1)

    jaw2 = Collimator()
    jaw2.position = float4(-140,140,-451,0)
    jaw2.xdir = float4(1,0,0,0)
    jaw2.ydir = float4(0,-1,0,0)
    jaw2.absorptionCoeff = 0.06#0.1
    jaw2.height = 72
    jaw2.width = 140*2
    jaw2.numberOfLeaves = 1
    jaw2.leafPositions = (100,)
    jaw2.boundingBox = calculateCollimatorBoundingBox(jaw2)

    collimator_array = Collimator * Settings.NUMBER_OF_COLLIMATORS
    collimators = collimator_array(jaw1, jaw2, col1, col2)
    leaves = []
    collimators = initCollimators(collimators, leaves) # Init Collimator

    leaf_array_type = float4 * len(leaves)
    leaf_array = leaf_array_type()
    for i in range(len(leaves)):
        leaf_array[i] = leaves[i]
        
    Settings.NUMBER_OF_LEAVES = Settings.NUMBER_OF_LEAVES/pieces
    Settings.NUMBER_OF_COLLIMATORS = 2 + (Settings.NUMBER_OF_COLLIMATORS-2) * pieces

    Collimator = collimatorFactory()
    colSp = splitCollimator(collimators[2], pieces, leaf_array, Collimator)
    colSp += splitCollimator(collimators[3], pieces, leaf_array, Collimator)

    jaw1 = splitCollimator(collimators[0], 1, leaf_array, Collimator)[0]
    jaw2 = splitCollimator(collimators[1], 1, leaf_array, Collimator)[0]

    collimator_array = Collimator * Settings.NUMBER_OF_COLLIMATORS
    collimators = collimator_array(jaw1, jaw2, *colSp)#col1Sp[0], col1Sp[1], col1Sp[2], col1Sp[3], col2Sp[0], col2Sp[1], col2Sp[2], col2Sp[3])

    collimators = CollimatorAoStoSoA(collimators) # Should be removed and collimator init should be done as SOA.

    fm = FluenceMap(Rectangle(float4(-300, -300, -1000, 0), float4(300, -300, -1000, 0), float4(300, 300, -1000, 0), float4(-300, 300, -1000, 0)))
    Scene = sceneFactory(type(collimators))
    scene = Scene(fm, rs, Settings.NUMBER_OF_COLLIMATORS, collimators)
    
    return [scene, collimators, leaf_array]

def define_settings(scene, leaf_array):
    # Settings
    Settings.XSTEP = float(length(scene.fluenceMap.rectangle.p1 - scene.fluenceMap.rectangle.p0)/Settings.FLX) # Length in x / x resolution
    Settings.YSTEP = float(length(scene.fluenceMap.rectangle.p3 - scene.fluenceMap.rectangle.p0)/Settings.FLY) # Length in y / y resolution
    Settings.XOFFSET = float(Settings.XSTEP/2.0)
    Settings.YOFFSET = float(Settings.YSTEP/2.0)
    Settings.LSTEP = float(scene.raySource.radius*2/(Settings.LSAMPLES-1))
    Settings.LEAF_DATA_SIZE = len(leaf_array)
    settingsList = Settings.getDefaultSettingsList()
    settingsList.append(("XSTEP", str(Settings.XSTEP)+'f', True))
    settingsList.append(("YSTEP", str(Settings.YSTEP)+'f', True))
    settingsList.append(("XOFFSET", str(Settings.XOFFSET)+'f', True))
    settingsList.append(("YOFFSET", str(Settings.YOFFSET)+'f', True))
    settingsList.append(("LSTEP", str(Settings.LSTEP)+'f', True))
    settingsList.append(("LEAF_DATA_SIZE", str(Settings.LEAF_DATA_SIZE), True))

    return settingsList

# Run in Python
def run_Python(scene, render, collimators):
    time1 = time()
    debugPython = Debug()
    fluence_data_Python = numpy.zeros(shape=(FLX,FLY), dtype=numpy.float32)
    drawScene(scene, render, collimators, fluence_data_Python, debugPython)
    timePython = time()-time1

    samplesPerSecond_OpenCL = Settings.FLX*Settings.FLY*Settings.LSAMPLES*Settings.LSAMPLES/timePython
    print "Time Python: ", time_Python, " Samples per second: ", samplesPerSecond_Python

    return [fluence_data_Python, time_Python, samplesPerSecond_Python]

# Run in OpenCL
def run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, optimizationParameters):
    debugOpenCL = Debug()
    
    X_size = int(optimizationParameters[1][1])
    Y_size = int(optimizationParameters[2][1])
    Z_size = int(optimizationParameters[3][1])
    if Settings.AUTOTUNE == 1:
        Settings.PIECES = int(optimizationParameters[4][1])
        [scene, collimators, leaf_array] = init_scene(Settings.PIECES)
        settingsList = define_settings(scene, leaf_array)
    
    settingsString = Settings.macroString(settingsList)
    optParametersString = Settings.macroString(optimizationParameters)
    Settings.WG_LIGHT_SAMPLING_SIZE = X_size*Y_size*Z_size
    optParametersString += " -D WG_LIGHT_SAMPLING_SIZE=" + str(X_size*Y_size*Z_size)

    #program = oclu.loadProgram(ctx, Settings.PATH_OPENCL + "RayTracingGPU.cl", "-cl-nv-verbose " + settingsString)
    #program = oclu.loadProgram(ctx, Settings.PATH_OPENCL + "RayTracingGPU.cl", "-cl-auto-vectorize-disable " + settingsString)
    #program = oclu.loadProgram(ctx, Settings.PATH_OPENCL + "RayTracingGPU.cl", " " + settingsString + " " + optParametersString)
    program = oclu.loadCachedProgram(ctx, Settings.PATH_OPENCL + "RayTracing.cl", " " + settingsString + " " + optParametersString)

    mf = cl.mem_flags
    time0 = time()
    scene_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=scene)
    #render_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=render)
    leaf_array_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=leaf_array)
    intensities_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.ALLOC_HOST_PTR, size=intensities.nbytes)
    fluence_data_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.ALLOC_HOST_PTR, size=fluence_data.nbytes)
    debugOpenCL_buf = cl.Buffer(ctx, mf.WRITE_ONLY, sizeof(debugOpenCL))
    
    time1 = time()
    program.flatLightSourceSampling(queue, intensities.shape, (X_size, Y_size, Z_size), scene_buf, leaf_array_buf, intensities_buf, debugOpenCL_buf).wait()
    #program.flatLightSourceSampling(queue, intensities.shape, None, scene_buf, leaf_array_buf, intensities_buf, debugOpenCL_buf).wait()

    time2 = time()
    program.calculateIntensityDecreaseWithDistance(queue, fluence_data.shape, None, scene_buf, fluence_data_buf, debugOpenCL_buf).wait()
    time3 = time()
    program.calcFluenceElement(queue, fluence_data.shape, None, scene_buf, intensities_buf, fluence_data_buf, debugOpenCL_buf).wait()
    time4 = time()
    cl.enqueue_read_buffer(queue, fluence_data_buf, fluence_data)
    cl.enqueue_read_buffer(queue, debugOpenCL_buf, debugOpenCL).wait()
    totalTime = time()-time0
    calculationTime = time4-time1

    #print "flatLightSourceSampling(): ", time2 - time1, ", calculateIntensityDecreaseWithDistance():", time3 - time2, ", calcFluenceElement():", time4 - time3
    samplesPerSecondOpenCL = Settings.FLX*Settings.FLY*Settings.LSAMPLESSQR/totalTime
    #print "Time OpenCL: ", timeOpenCL, " Samples per second: ", samplesPerSecondOpenCL
    #print fluence_data

    return [fluence_data, totalTime, calculationTime, samplesPerSecondOpenCL]

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

def show_3D_scene(scene, leaf_array, collimators):
    # Visual python
    disp = vs.display()
    #disp.autocenter = True
    disp.userspin = True
    disp.ambient = 0.5
    disp.forward = (0, 0, -1)
    disp.center = (0, 0, -500)
    disp.range = (300, 300, -1000)

    # Collimators
    for i in range(Settings.NUMBER_OF_COLLIMATORS):
        fr = vs.frame()
        #if MODE == 0:
            #f = vs.faces(frame = fr, pos = collimators.flatCollimator[i].getVertices())
        #elif MODE == 1:
            #f = vs.faces(frame = fr, pos = collimators.bboxCollimator[i].getVertices())
        #if Settings.MODE == 2:
            #f = vs.faces(frame = fr, pos = collimators.boxCollimator[i].getVertices())
            #bb = vs.faces(frame = fr, pos = bboxToBox(collimators.boxCollimator.boundingBox[i]).getVertices())
            #bb.make_normals()
            #bb.color = vs.color.blue
        #f.color = vs.color.orange
        #f.make_normals()
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

def setDefaultSettings():
    Settings.AUTOTUNE = 0

    # Platform
    Settings.PLATFORM = 0 # 0: Windows NVidia, 1: Windows Intel, 2: OSX-CPU, 3: OSX-GPU, 4: AMD-CPU, 5: AMD-GPU

    # Collimator defines
    Settings.NUMBER_OF_LEAVES = 40
    Settings.NUMBER_OF_COLLIMATORS = 4
    Settings.PIECES = 20
    if Settings.NUMBER_OF_LEAVES%Settings.PIECES != 0:
        print "Warning: NUMBER_OF_COLLIMATORS not divisable by PIECES"

    # Global defines
    Settings.FLX = 128
    Settings.FLY = 128
    Settings.WINX = 0
    Settings.WINY = 0
    #XSTEP = 0.0
    #YSTEP = 0.0
    #XOFFSET = 0.0
    #YOFFSET = 0.0
    Settings.LSAMPLES = 20
    Settings.LSAMPLESSQR = Settings.LSAMPLES*Settings.LSAMPLES
    #LSTEP = 0.0

    Settings.MODE = 2

    # Optimization parameters
    Settings.LINE_TRIANGLE_INTERSECTION_ALGORITHM = 2 # SS, MT, MT2, MT3
    Settings.DEPTH_FIRST = 0

    # Work group sizes
    if Settings.PLATFORM in [1, 2, 4]: # Best CPU
        Settings.WG_LIGHT_SAMPLING_X = 1
        Settings.WG_LIGHT_SAMPLING_Y = 1
        Settings.WG_LIGHT_SAMPLING_Z = 1
    elif Settings.PLATFORM in [0]: # Best NVIDIA GTX 470
        #Settings.WG_LIGHT_SAMPLING_X = 1
        #Settings.WG_LIGHT_SAMPLING_Y = 32
        #Settings.WG_LIGHT_SAMPLING_Z = 4
        Settings.WG_LIGHT_SAMPLING_X = 2
        Settings.WG_LIGHT_SAMPLING_Y = 32
        Settings.WG_LIGHT_SAMPLING_Z = 2
    else:
        Settings.WG_LIGHT_SAMPLING_X = 2
        Settings.WG_LIGHT_SAMPLING_Y = 2
        Settings.WG_LIGHT_SAMPLING_Z = 4
    Settings.WG_LIGHT_SAMPLING_SIZE = Settings.WG_LIGHT_SAMPLING_X * Settings.WG_LIGHT_SAMPLING_Y * Settings.WG_LIGHT_SAMPLING_Z

    # Adress spaces. 0: private, 1: local, 2: constant, 3: global
    Settings.RAY_AS = 0 # Valid: 0, 1.
    Settings.LEAF_AS = 1 # Valid: 1, 2, 3.
    Settings.LEAF_DATA_AS = 2 # Valid: 1, 2, 3. 3 only for quadro.
    Settings.SCENE_AS = 2 # Valid: 2, 3. 2 only for osx-gpu, nvidia-gpu

    # Run settings
    Settings.OPENCL = 1
    Settings.PYTHON = 0
    Settings.SHOW_PLOT = 1
    Settings.SHOW_3D_SCENE = 0
    if Settings.PLATFORM in [0, 1, 4, 5]:
        Settings.PATH_OPENCL = "OpenCL/"
    elif Settings.PLATFORM in [2, 3]:
        Settings.PATH_OPENCL = "/Users/mattias/Skola/exjobb/CalcFluenceMap/SimpleRayTracingOpenCL/OpenCL/"

def main():
    setDefaultSettings()
    #select_excecution_environment()
    if Settings.OPENCL == 1:
        [ctx, queue] = init_OpenCL()
    #test()
    [scene, collimators, leaf_array] = init_scene(Settings.PIECES)
    settingsList = define_settings(scene, leaf_array)
    oclu = OpenCLUtility.OpenCLUtility()

    if Settings.AUTOTUNE == 1:
        list = []
        list.append(Parameter("LINE_TRIANGLE_INTERSECTION_ALGORITHM", [2], True))
        list.append(Parameter("WG_LIGHT_SAMPLING_X", [1,2,4,8,16,32,64,128], False))
        list.append(Parameter("WG_LIGHT_SAMPLING_Y", [1,2,4,8,16,32,64,128], False))
        list.append(Parameter("WG_LIGHT_SAMPLING_Z", [1,2,4,8,16], False))
        list.append(Parameter("PIECES", [1,2,4,10,20], False))
        list.append(Parameter("RAY_AS", [0], True))
        list.append(Parameter("LEAF_AS", [1], True))
        list.append(Parameter("LEAF_DATA_AS", [2], True))
        list.append(Parameter("SCENE_AS", [2], True))
        list.append(Parameter("DEPTH_FIRST", [0], True))

        fluence_data = numpy.zeros(shape=(Settings.FLX,Settings.FLY), dtype=numpy.float32)
        intensities = numpy.zeros(shape=(Settings.FLX,Settings.FLY,Settings.LSAMPLESSQR), dtype=numpy.float32)

        at = Autotune(ParameterSet(list), run_OpenCL, (oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList))

        at.findOptimizationParameters()

        #print at.getTable()
        at.saveCSV()

        [fluence_data_OpenCL, total_time_OpenCL, calculation_time_OpenCL, samplesPerSecond_OpenCL] = run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, at.best_parameters)
    else:
        fluence_data = numpy.zeros(shape=(Settings.FLX,Settings.FLY), dtype=numpy.float32)
        intensities = numpy.zeros(shape=(Settings.FLX,Settings.FLY,Settings.LSAMPLESSQR), dtype=numpy.float32)
        [fluence_data_OpenCL, total_time_OpenCL, calculation_time_OpenCL, samplesPerSecond_OpenCL] = run_OpenCL(oclu, ctx, queue, scene, leaf_array, fluence_data, intensities, settingsList, Settings.getDefaultOptimizationParameterList())

    if Settings.SHOW_PLOT == 1:
        if Settings.PYTHON == 1:
            show_plot(scene, fluence_data_Python, time_Python, samplesPerSecond_Python)
        if Settings.OPENCL == 1:
            show_plot(scene, fluence_data_OpenCL, total_time_OpenCL, samplesPerSecond_OpenCL)
    if Settings.SHOW_3D_SCENE == 1:
        show_3D_scene(scene, leaf_array, collimators)
    
if __name__=="__main__":
    main()
