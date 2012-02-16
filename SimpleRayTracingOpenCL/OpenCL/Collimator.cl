#ifndef __Collimator__
#define __Collimator__

#include "Primitives.cl"

// Data types
typedef struct SimpleCollimator {
	Rectangle leftRectangle;
	Rectangle rightRectangle;
} __attribute__((packed)) SimpleCollimator;

typedef struct FlatCollimator2 {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float attenuation;
	int numberOfLeaves;
	Rectangle leaves[2];
} __attribute__((packed)) FlatCollimator2;

typedef struct FlatCollimator40 {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float attenuation;
	int numberOfLeaves;
	Rectangle leaves[40];
} __attribute__((packed)) FlatCollimator40;

typedef struct Collimator2 {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float attenuation;
	float height;
	float leafWidth;
	int numberOfLeaves;
	float leafPositions[2];
} __attribute__((packed)) Collimator2;

typedef struct Collimator40 {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float attenuation;
	float height;
	float leafWidth;
	int numberOfLeaves;
	float leafPositions[40];
} __attribute__((packed)) Collimator40;

// Collimator generation
void calculateCollimatorBoundingBox(Collimator2 *collimator, Box *boundingBox) {
    float maxPosition = 0;
    for (int i = 0; i < collimator->numberOfLeaves; i++) {
        if (maxPosition < collimator->leafPositions[i]) {
            maxPosition = collimator->leafPositions[i];
		}
	}

    float4 x = normalize(collimator->xdir) * maxPosition;
    float4 y = normalize(collimator->ydir) * collimator->numberOfLeaves * collimator->leafWidth;
    float4 down = normalize(cross(collimator->xdir, collimator->ydir))*collimator->height;

    float4 p0 = collimator->position;
    float4 p1 = p0 + down;
    float4 p2 = p0 + down + y;
    float4 p3 = p0 + y;
    float4 p4 = p0 + x;
    float4 p5 = p4 + down;
    float4 p6 = p4 + down + y;
    float4 p7 = p4 + y;

	float4 pointArray[8] = {p0,p1,p2,p3,p4,p5,p6,p7};

    float xmin = INFINITY;
    float ymin = INFINITY;
    float zmin = INFINITY;
	float xmax = -INFINITY;
    float ymax = -INFINITY;
    float zmax = -INFINITY;
	for (int i = 0; i < 8; i++) {
		xmin = fmin(xmin, pointArray[i].x);
		ymin = fmin(ymin, pointArray[i].y);
		zmin = fmin(zmin, pointArray[i].z);

		xmax = fmax(xmin, pointArray[i].x);
		ymax = fmax(ymin, pointArray[i].y);
		zmax = fmax(zmin, pointArray[i].z);
	}

	Box bbox = {
		.min = (float4) (xmin,ymin,zmin,0),
		.max = (float4) (xmax,ymax,zmax,0)};

    *boundingBox = bbox;
}

void createRectangles(float4 *position, float4 *xdir, float4 *ydir, float *rectangleWidth, int *numberOfRect, float *rectangleLength, Rectangle *rectangles) {
    float4 x = normalize(*xdir);
    float4 y = normalize(*ydir)*(*rectangleWidth);
    for (int i = 0; i < (*numberOfRect); i++) {
		Rectangle rect = {
			.p0 = *position + y*i,
			.p1 = *position + y*(i+1),
			.p2 = *position + x*rectangleLength[i] + y*(i+1),
			.p3 = *position + y*i + x*rectangleLength[i]};
        rectangles[i] = rect;
    }
}

void createFlatCollimator2(Collimator2 *collimator, FlatCollimator2 *fc) {
    Plane plane = {
		.origin = collimator->position,
		.normal = cross(collimator->xdir, collimator->ydir)}; // Plane perpendicular to xdir and ydir.
    Box bbox;
	float4 oldMin = collimator->boundingBox.min;
	float4 oldMax = collimator->boundingBox.max;
	float4 min, max;
	projectPointOntoPlane(&oldMin, &plane, &min);
	projectPointOntoPlane(&oldMax, &plane, &max);
	Rectangle leaves[2];
    createRectangles(&(collimator->position), &(collimator->xdir), &(collimator->ydir), &(collimator->leafWidth), &(collimator->numberOfLeaves), (float *) &(collimator->leafPositions), (Rectangle *) &leaves);
    // Set all properties of the FlatCollimator.
	fc->boundingBox = bbox;
    fc->position = collimator->position;
    fc->xdir = collimator->xdir;
    fc->ydir = collimator->ydir;
    fc->attenuation = collimator->attenuation;
    fc->numberOfLeaves = collimator->numberOfLeaves;
    fc->leaves[0] = leaves[0];
	fc->leaves[1] = leaves[1];
}

// Intersection calculations
void intersectSimpleCollimator(const Line *l, __constant const SimpleCollimator *c, bool *intersect, float *distance, float4 *ip)
{
	Rectangle ls = c->leftRectangle; // Copy from constant memory to private
	intersectLineRectangle(l, &ls, intersect, distance, ip);

	if (!(*intersect)) { // Check the other rectangle of the SimpleCollimator
		Rectangle rs = c->rightRectangle; // Copy from constant memory to private
		intersectLineRectangle(l, &rs, intersect, distance, ip);
	}
}

void intersectLineFlatCollimator(const Line *line, const FlatCollimator40 *collimator, bool *intersect, float *distance, float4 *ip) {
	bool intersectBBox;
	float intersectionDistanceBBox;
	float4 intersectionPointBBox;
    intersectLineBox(line, &(collimator->boundingBox), &intersectBBox, &intersectionDistanceBBox, &intersectionPointBBox);
    if (intersectBBox) { // If bounding box is hit: check all leaves.
        for (int i = 0; i < collimator->numberOfLeaves; i++) {
            intersectLineRectangle(line, &(collimator->leaves[i]), intersect, distance, ip);
            if (*intersect) {
                return; // If intersection found: stop looking for intersections.
			}
		}
	}

    *intersect = false;
	*distance = NAN;
	*ip = (NAN, NAN, NAN, NAN);
}

#endif //__Collimator__
