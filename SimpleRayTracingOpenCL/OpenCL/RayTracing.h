#ifndef __RayTracing__
#define __RayTracing__

#include "Collimator.h"
#include "Misc.h"
#include "Primitives.h"
#include "Settings.h"

// Data types
typedef struct SimpleRaySourceRectangle {
	Rectangle rectangle;
} __attribute__((packed)) SimpleRaySourceRectangle;

typedef struct FluenceMap {
	Rectangle rectangle;
} __attribute__((packed)) FluenceMap;

typedef struct Render {
	int flx;
    int fly;
	float xstep;
    float ystep;
    float xoffset;
    float yoffset;
	int lsamples;
	float lstep;
	//int mode;
} __attribute((packed)) Render;

typedef struct Scene {
    FluenceMap fluenceMap;
	Disc raySource;
	int numberOfCollimators;
	Collimator collimators;
} __attribute((packed)) Scene;

// Function declarations
void firstHitLeaf(SCENE_ASQ Scene *s, RAY_ASQ const Line *r, LEAF_ASQ float4 *leaf_data, int *collimatorIndex, bool *intersect, float4 *ip, float *thickness, __global Debug *debug);
void hitCollimator(SCENE_ASQ Scene *s, RAY_ASQ Line *r, int *collimatorIndex, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, bool *intersect, float4 *ip, float *intensityCoeff, __global Debug *debug);
void firstHitCollimator(SCENE_ASQ Scene *s, RAY_ASQ Line *r, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, bool *intersect, float4 *ip, float *intensityCoeff, __global Debug *debug);
void traceRay(SCENE_ASQ Scene *s, RAY_ASQ Line *r, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, float *i, __global Debug *debug);
void lightSourceAreaVectors(SCENE_ASQ Scene *scene, const float4 *rayOrigin, float4 *vi0, float4 *vi1, float4 *vj0, float4 *vj1, __global Debug *debug);

#endif //__RayTracing__
