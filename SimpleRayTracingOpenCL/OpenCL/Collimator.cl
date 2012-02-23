#ifndef __Collimator__
#define __Collimator__

#include "Primitives.cl"

// Data types
typedef struct SimpleCollimator {
	Rectangle leftRectangle;
	Rectangle rightRectangle;
} __attribute__((packed)) SimpleCollimator;

typedef struct FlatCollimator {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float absorptionCoeff;
	int numberOfLeaves;
	Rectangle leaves[40];
} __attribute__((packed)) FlatCollimator;

typedef struct BoxCollimator {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float absorptionCoeff;
	int numberOfLeaves;
	Box leaves[40];
} __attribute__((packed)) BoxCollimator;

typedef struct Collimator {
	Box boundingBox;
	float4 position;
	float4 xdir;
	float4 ydir;
	float absorptionCoeff;
	float height;
	float leafWidth;
	int numberOfLeaves;
	float leafPositions[40];
	FlatCollimator flatCollimator;
	BoxCollimator boxCollimator;
} __attribute__((packed)) Collimator;

// Collimator generation
void calculateCollimatorBoundingBox(Collimator *collimator, Box *bbox) {
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

	Box box;
	boundingBox(&p0, &p1, &p2, &p3, &p4, &p5, &p6, &p7, &box);
    *bbox = box;
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

void createFlatCollimator(Collimator *collimator, FlatCollimator *fc) {
    Plane plane = {
		.origin = collimator->position,
		.normal = cross(collimator->xdir, collimator->ydir)}; // Plane perpendicular to xdir and ydir.
    Box bbox;
	float4 oldMin = collimator->boundingBox.min;
	float4 oldMax = collimator->boundingBox.max;
	float4 min, max;
	projectPointOntoPlane(&oldMin, &plane, &min);
	projectPointOntoPlane(&oldMax, &plane, &max);
    // Set all properties of the FlatCollimator.
	fc->boundingBox = bbox;
    fc->position = collimator->position;
    fc->xdir = collimator->xdir;
    fc->ydir = collimator->ydir;
    fc->absorptionCoeff = collimator->absorptionCoeff;
    fc->numberOfLeaves = collimator->numberOfLeaves;
	Rectangle leaves[40];
	createRectangles(&(collimator->position), &(collimator->xdir), &(collimator->ydir), &(collimator->leafWidth), &(collimator->numberOfLeaves), (float *) &(collimator->leafPositions), leaves);
	for (int i = 0; i < collimator->numberOfLeaves; i++) {
		fc->leaves[i] = leaves[i];
	}
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

void intersectLineFlatCollimator(const Line *line, const FlatCollimator *collimator, bool *intersect, float *distance, float4 *ip) {
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
