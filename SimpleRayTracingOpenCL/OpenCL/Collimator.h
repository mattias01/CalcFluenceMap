#ifndef __Collimator__
#define __Collimator__

#include "Primitives.h"
#include "Settings.h"

// Data types
typedef struct SimpleCollimator {
	Rectangle leftRectangle;
	Rectangle rightRectangle;
} __attribute__((packed)) SimpleCollimator;

typedef struct FlatCollimator {
	BBox boundingBox[NUMBER_OF_COLLIMATORS];
	float4 position[NUMBER_OF_COLLIMATORS];
	float4 xdir[NUMBER_OF_COLLIMATORS];
	float4 ydir[NUMBER_OF_COLLIMATORS];
	float absorptionCoeff[NUMBER_OF_COLLIMATORS];
	int numberOfLeaves[NUMBER_OF_COLLIMATORS];
	int leafArrayOffset[NUMBER_OF_COLLIMATORS];
	int leafArrayStride[NUMBER_OF_COLLIMATORS];
} __attribute__((packed)) FlatCollimator;

typedef struct BBoxCollimator {
	BBox boundingBox[NUMBER_OF_COLLIMATORS];
	float4 position[NUMBER_OF_COLLIMATORS];
	float4 xdir[NUMBER_OF_COLLIMATORS];
	float4 ydir[NUMBER_OF_COLLIMATORS];
	float absorptionCoeff[NUMBER_OF_COLLIMATORS];
	int numberOfLeaves[NUMBER_OF_COLLIMATORS];
	int leafArrayOffset[NUMBER_OF_COLLIMATORS];
	int leafArrayStride[NUMBER_OF_COLLIMATORS];
} __attribute__((packed)) BBoxCollimator;

typedef struct BoxCollimator {
	BBox boundingBox[NUMBER_OF_COLLIMATORS];
	float4 position[NUMBER_OF_COLLIMATORS];
	float4 xdir[NUMBER_OF_COLLIMATORS];
	float4 ydir[NUMBER_OF_COLLIMATORS];
	float absorptionCoeff[NUMBER_OF_COLLIMATORS];
	int numberOfLeaves[NUMBER_OF_COLLIMATORS];
	int leafArrayOffset[NUMBER_OF_COLLIMATORS];
	int leafArrayStride[NUMBER_OF_COLLIMATORS];
} __attribute__((packed)) BoxCollimator;

typedef struct Collimator {
	BBox boundingBox[NUMBER_OF_COLLIMATORS];
	float4 position[NUMBER_OF_COLLIMATORS];
	float4 xdir[NUMBER_OF_COLLIMATORS];
	float4 ydir[NUMBER_OF_COLLIMATORS];
	float absorptionCoeff[NUMBER_OF_COLLIMATORS];
	float height[NUMBER_OF_COLLIMATORS];
	float leafWidth[NUMBER_OF_COLLIMATORS];
	int numberOfLeaves[NUMBER_OF_COLLIMATORS];
	float leafPositions[NUMBER_OF_COLLIMATORS][NUMBER_OF_LEAVES];
	#if MODE == 0
		FlatCollimator flatCollimator;
	#elif MODE == 1
		BBoxCollimator bboxCollimator;
	#elif MODE == 2
		BoxCollimator boxCollimator;
	#endif
} __attribute__((packed)) Collimator;

// Function definitions
void intersectLineFlatCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t1, LEAF_ASQ const Triangle *t2, bool *intersect, float *distance, float4 *ip);
void intersectLineBBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);
void intersectLineBoxCollimatorLeaf(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, /*float4 *inIp,*/ float4 *outIp);

#include "Collimator.cl" //Hack to go around the inability for OpenCL 1.1 to compile several source files and link to one.

#endif //__Collimator__