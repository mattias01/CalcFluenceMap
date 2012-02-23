import ctypes
import matplotlib.cm as cm
from matplotlib.contour import ContourSet
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.pyplot as plt
import numpy as np
import pyopencl as cl
import struct
from sys import getsizeof
from time import time

from OpenCLUtility import OpenCLUtility as oclu
from OpenCLTypes import *
from Python.RayTracing import *
from Test import *

print 'Start SimpleRayTracingOpenCL'

# Select execution environment (Python, OpenCl or both)
run = raw_input("Choose environment:\n0: OpenCL, 1: Python, 2: Both\n[0]:")

python = False
openCL = True
if run == "1":
    python = True
    openCL = False
elif run == "2":
    python = True

# Init OpenCL
if openCL:
    ctx = cl.create_some_context()
    queue = cl.CommandQueue(ctx)

# Run tests
if python:
    np.seterr(divide='ignore') # Disable warning on division by zero.
    testPython()
if openCL:
    testOpenCL(ctx, queue)

# Build scene objects
#rs = SimpleRaySourceRectangle(Rectangle(float4(0,3,6,0), float4(7,3,6,0), float4(7,5,6,0), float4(0,5,6,0)))
rs = SimpleRaySourceDisc(Disc(float4(0,0,0,0), float4(0,0,1,0), 1))
#cls = Rectangle(float4(-3.5,-3.5,-90,0), float4(3.5,-3.5,-90,0), float4(3.5,-0.5,-90,0), float4(-3.5,-0.5,-90,0))
#crs = Rectangle(float4(-3.5,0.5,-90,0), float4(2.5,0.5,-90,0), float4(3.5,3.5,-90,0), float4(-3.5,3.5,-90,0))
#col = SimpleCollimator(cls, crs)
#cls2 = Rectangle(float4(-3.5,-3.5,-99,0), float4(-0.5,-3.5,-99,0), float4(-0.5,3.5,-99,0), float4(-3.5,3.5,-99,0))
#crs2 = Rectangle(float4(0.5,-3.5,-99,0), float4(3.5,-3.5,-99,0), float4(3.5,3.5,-99,0), float4(0.5,3.5,-99,0))
#col2 = SimpleCollimator(cls2, crs2)
#collimators = [col, col2]

col1 = Collimator()
col1.position = float4(-20,-20,-29.5,0)
col1.xdir = float4(0,1,0,0)
col1.ydir = float4(1,0,0,0)
col1.absorptionCoeff = 0.2
col1.height = 28.2
col1.leafWidth = 1
col1.numberOfLeaves = 40
col1.leafPositions = (10,19,28,27,26,25,24,23,22,21,20,19,18,17,16,15,14,13,20,11,12,13,10,15,14,13,12,20,10,12,14,16,18,18,18,20,10,20,10,20)
col1.boundingBox = calculateCollimatorBoundingBox(col1)
#col1.flatCollimator = createFlatCollimator(col1)

col2 = Collimator()
col2.position = float4(20,20,-29.5,0)
col2.xdir = float4(0,-1,0,0)
col2.ydir = float4(-1,0,0,0)
col2.absorptionCoeff = 0.9
col2.height = 8.2
col2.leafWidth = 20
col2.numberOfLeaves = 2
col2.leafPositions = (15,10)
col2.boundingBox = calculateCollimatorBoundingBox(col2)
#col2.flatCollimator = createFlatCollimator(col2)

#jaw1 = Collimator()
#jaw1.position = float4(20,20,-45.1,0)
#jaw1.xdir = float4(0,-1,0,0)
#jaw1.ydir = float4(-1,0,0,0)
#jaw1.absorptionCoeff = 1.0
#jaw1.height = 7.2
#jaw1.leafWidth = 40
#jaw1.numberOfLeaves = 1
#jaw1.leafPositions = (10)
#jaw1.boundingBox = calculateCollimatorBoundingBox(jaw1)

collimator_array = Collimator * 2 # Define ctypes array.
collimators = collimator_array(col1, col2)

fm = FluenceMap(Rectangle(float4(-30,-30,-100,0), float4(30,-30,-100,0), float4(30,30,-100,0), float4(-30,30,-100,0)))
#scene = Scene(rs,col,fm)
scene2 = Scene2(rs,len(collimators),fm)

# Settings
flx = 256
fly = 256
xstep = (0.0 + length(scene2.fluenceMap.rectangle.p1 - scene2.fluenceMap.rectangle.p0))/flx # Length in x / x resolution
ystep = (0.0 + length(scene2.fluenceMap.rectangle.p3 - scene2.fluenceMap.rectangle.p0))/fly # Length in y / y resolution
xoffset = xstep/2.0
yoffset = ystep/2.0
lsamples = 20
lstep = scene2.raySource.disc.radius*2/(lsamples-1)
mode = 1
render = Render(flx,fly,xstep,ystep,xoffset,yoffset,lsamples,lstep,mode)

init(scene2, render, collimators) # Init flatCollimator

if python:
    fluence_dataPython = numpy.zeros(shape=(flx,fly), dtype=numpy.float32)
if openCL:
    fluence_dataOpenCL = numpy.zeros(shape=(flx,fly), dtype=numpy.float32)

# Run in Python
if python:
    time1 = time()
    debugPython = Debug()
    drawScene2(scene2, render, collimators, fluence_dataPython, debugPython)
    timePython = time()-time1

    samplesPerSecondPython = flx*fly*lsamples*lsamples/timePython
    print "Time Python: ", timePython, " Samples per second: ", samplesPerSecondPython

# Run in OpenCL
if openCL:
    time1 = time()
    debugOpenCL = Debug()
    program = oclu.loadProgram(ctx, "OpenCL/RayTracing.cl")
    mf = cl.mem_flags
    #scene_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=scene)
    scene2_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=scene2)
    render_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=render)
    collimators_buf = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=collimators)
    fluence_dataOpenCL_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=fluence_dataOpenCL)
    debugOpenCL_buf = cl.Buffer(ctx, mf.WRITE_ONLY, sizeof(debugOpenCL))
    
    #program.drawScene(queue, fluence_dataOpenCL.shape, None, scene_buf, render_buf, fluence_dataOpenCL_buf, debugOpenCL_buf)
    program.drawScene2(queue, fluence_dataOpenCL.shape, None, scene2_buf, render_buf, fluence_dataOpenCL_buf, collimators_buf, debugOpenCL_buf)
    cl.enqueue_read_buffer(queue, fluence_dataOpenCL_buf, fluence_dataOpenCL)
    cl.enqueue_read_buffer(queue, debugOpenCL_buf, debugOpenCL).wait()
    timeOpenCL = time()-time1

    print timeOpenCL
    samplesPerSecondOpenCL = flx*fly*lsamples*lsamples/timeOpenCL
    print "Time OpenCL: ", timeOpenCL, " Samples per second: ", samplesPerSecondOpenCL

# Show plots
codes = [Path.MOVETO,
         Path.LINETO,
         Path.LINETO,
         Path.LINETO,
         Path.CLOSEPOLY]
#colpath1 = Path(Rectangle2dVertexArray(col.leftRectangle), codes)
#colpath2 = Path(Rectangle2dVertexArray(col.rightRectangle), codes)
#colpatch1 = patches.PathPatch(colpath1, facecolor='none', edgecolor='blue', linewidth=4, alpha=0.5)
#colpatch2 = patches.PathPatch(colpath2, facecolor='none', edgecolor='blue', linewidth=4, alpha=0.5)
rspatch = patches.Circle((scene2.raySource.disc.origin.y, scene2.raySource.disc.origin.x), 
                         scene2.raySource.disc.radius, facecolor='none', edgecolor='red', linewidth=1, alpha=0.5)

# Python
if python:
    print fluence_dataPython
    plt.imshow(fluence_dataPython, interpolation='none', cmap=cm.gray, extent=[scene2.fluenceMap.rectangle.p0.y,
                                                                               scene2.fluenceMap.rectangle.p3.y,
                                                                               -scene2.fluenceMap.rectangle.p0.x,
                                                                               -scene2.fluenceMap.rectangle.p1.x])

    #plt.gca().add_patch(colpatch1)
    #plt.gca().add_patch(colpatch2)
    plt.gca().add_patch(rspatch)

    plt.title("Python " + "Time: " + str(timePython) + " Samples per second: " + str(samplesPerSecondPython))
    plt.show()

# OpenCL
if openCL:
    print fluence_dataOpenCL
    plt.imshow(fluence_dataOpenCL, interpolation='none', cmap=cm.gray, extent=[scene2.fluenceMap.rectangle.p0.y,
                                                                               scene2.fluenceMap.rectangle.p3.y,
                                                                               -scene2.fluenceMap.rectangle.p0.x,
                                                                               -scene2.fluenceMap.rectangle.p1.x])
    #plt.gca().add_patch(colpatch1)
    #plt.gca().add_patch(colpatch2)
    plt.gca().add_patch(rspatch)
    plt.title("OpenCL " + "Time: " + str(timeOpenCL) + " Samples per second: " + str(samplesPerSecondOpenCL))
    plt.show()
