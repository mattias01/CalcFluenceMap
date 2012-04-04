#ifndef __Primitives__
#define __Primitives__

#include "Settings.h"

// Data types
typedef struct Line {
	float4 origin;
	float4 direction;
} __attribute__((packed)) Line;

typedef struct Plane {
	float4 origin;
	float4 normal;
} __attribute__((packed)) Plane;

typedef struct Triangle {
	float4 p0;
	float4 p1;
	float4 p2;
} __attribute__((packed)) Triangle;

typedef struct Rectangle {
	float4 p0;
	float4 p1;
	float4 p2;
	float4 p3;
} __attribute__((packed)) Rectangle;

typedef struct Disc {
	float4 origin;
	float4 normal;
	float radius;
} __attribute__((packed)) Disc;

typedef struct BBox {
	float4 min;
	float4 max;
} __attribute__((packed)) BBox;

typedef struct Box {
	Triangle triangles[10];//[12];
} __attribute__((packed)) Box;

// Function declarations
void boundingBox(float4 *p0, float4 *p1, float4 *p2, float4 *p3, float4 *p4, float4 *p5, float4 *p6, float4 *p7, BBox *bbox);
void createBoxFromPoints(float4 p0, float4 p1, float4 p2, float4 p3, float4 p4, float4 p5, float4 p6, float4 p7, Box *box);
void projectPointOntoPlane(float4 *p0, Plane *plane, float4 *resultPoint);
void intersectLinePlane(RAY_ASQ const Line *l, const Plane *p, bool *intersect, float *distance, float4 *ip);
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip);
void intersectLineDisc(RAY_ASQ const Line *l, SCENE_ASQ Disc *d, bool *intersect, float *distance, float4 *ip);
void intersectLineBBox(RAY_ASQ const Line *l, SCENE_ASQ BBox *bb, bool *intersect, float *distance, float4 *ip);
void intersectLineBBoxInOut(RAY_ASQ const Line *l, SCENE_ASQ BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);
void intersectLineBBoxColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *bb, bool *intersect, float *distance, float4 *ip);
void intersectLineBBoxInOutColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);
void intersectLineBox(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *distance, float4 *ip);
void intersectLineBoxInOut(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, /*float4 *inIp,*/ float4 *outIp);

#include "Primitives.cl" //Hack to go around the inability for OpenCL 1.1 to compile several source files and link to one.

#endif //__Primitives__

