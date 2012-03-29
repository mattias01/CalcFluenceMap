#ifndef __Primitives__
#define __Primitives__

#include "Settings.cl"

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
	Triangle triangles[12];
} __attribute__((packed)) Box;

// Function declarations
void boundingBox(float4 *p0, float4 *p1, float4 *p2, float4 *p3, float4 *p4, float4 *p5, float4 *p6, float4 *p7, BBox *bbox);
void createBoxFromPoints(float4 p0, float4 p1, float4 p2, float4 p3, float4 p4, float4 p5, float4 p6, float4 p7, Box *box);
void projectPointOntoPlane(float4 *p0, Plane *plane, float4 *resultPoint);
void intersectLinePlane(RAY_ASQ const Line *l, const Plane *p, bool *intersect, float *distance, float4 *ip);
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip);
void intersectLineDisc(RAY_ASQ const Line *l, SCENE_ASQ const Disc *d, bool *intersect, float *distance, float4 *ip);
void intersectLineBBox(RAY_ASQ const Line *l, SCENE_ASQ const BBox *bb, bool *intersect, float *distance, float4 *ip);
void intersectLineBBoxInOut(RAY_ASQ const Line *l, SCENE_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);
void intersectLineBBoxColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *bb, bool *intersect, float *distance, float4 *ip);
void intersectLineBBoxInOutColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);
void intersectLineBox(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *distance, float4 *ip);
void intersectLineBoxInOut(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp);

// Other

void boundingBox(float4 *p0, float4 *p1, float4 *p2, float4 *p3, float4 *p4, float4 *p5, float4 *p6, float4 *p7, BBox *bbox) {
	float4 pointArray[8] = {*p0, *p1, *p2, *p3, *p4, *p5, *p6, *p7};

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

	BBox box = {
		.min = (float4) (xmin,ymin,zmin,0.0f),
		.max = (float4) (xmax,ymax,zmax,0.0f)};

	*bbox = box;
}

void createBoxFromPoints(float4 p0, float4 p1, float4 p2, float4 p3, float4 p4, float4 p5, float4 p6, float4 p7, Box *box) {
    // Bottom
	Triangle t0 = {.p0=p0, .p1=p1, .p2=p3};
	Triangle t1 = {.p0=p1, .p1=p2, .p2=p3};
    // Top
	Triangle t2 = {.p0=p5, .p1=p6, .p2=p4};
	Triangle t3 = {.p0=p6, .p1=p7, .p2=p4};
    // Left side
	Triangle t4 = {.p0=p1, .p1=p7, .p2=p2};
	Triangle t5 = {.p0=p7, .p1=p6, .p2=p2};
    // Right side
    Triangle t6 = {.p0=p4, .p1=p0, .p2=p5};
    Triangle t7 = {.p0=p0, .p1=p3, .p2=p5};
    // Front side
    Triangle t8 = {.p0=p3, .p1=p2, .p2=p5};
    Triangle t9 = {.p0=p2, .p1=p6, .p2=p5};
    // Back side (Not needed?)
    Triangle t10 = {.p0=p4, .p1=p7, .p2=p0};
    Triangle t11 = {.p0=p7, .p1=p1, .p2=p0};
	
	Triangle new_triangles[12] = {t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11};
	for (int i = 0; i < 12; i++) {
		box->triangles[i] = new_triangles[i];
	}
}

// Projection calculations

void projectPointOntoPlane(float4 *p0, Plane *plane, float4 *resultPoint) {
    float sn = -dot(plane->normal, (*p0 - plane->origin));
    float sd = dot(plane->normal, plane->normal);
    float sb = sn / sd;
    *resultPoint = *p0 + plane->normal * sb;
}

// Intersection calculations. Registers: 1.
void intersectLinePlane(RAY_ASQ const Line *l, const Plane *p, bool *intersect, float *distance, float4 *ip)
{
	// Init to not intersect
	*intersect = false;
	if (dot(l->direction, p->normal) != 0.0f) { // Not parallel -> intersect.
		*distance = (dot(p->normal, (p->origin - l->origin))) / (dot(p->normal, l->direction));
		if (*distance > 0.0f) { // Plane is located in positive ray direction from the ray origin. Avoids hitting same thing it just hit.
			*intersect = true;
			*ip = l->origin + l->direction*(*distance);
		}
	}
}

#if LINE_TRIANGLE_INTERSECTION_ALGORITHM == 0 // SoftSurfer, modified MT
// SoftSurfer.com, modified MT. Registers: 32 + 1.
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 u = t->p1 - t->p0;
    float4 v = t->p2 - t->p0;
    float4 triangleNorm = cross(u, v);
	Plane p = {
		.origin = t->p0,
		.normal = triangleNorm};
	intersectLinePlane(l, &p, intersect, distance, ip);
	
	if (*intersect) {
		// Point in triangle plan. Check if in triangle
        float uu = dot(u,u);
        float uv = dot(u,v);
        float vv = dot(v,v);
        float4 w = *ip - t->p0;
        float wu = dot(w,u);
        float wv = dot(w,v);
        float D = uv * uv - uu * vv;
        // Get and test parametric coords
        float s = (uv * wv - vv * wu) / D;
        if (s < 0.0f || s > 1.0f) { // IntersectionPoint is outside triangle
            *intersect = false;
		}
		else {
			float t = (uv * wu - uu * wv) / D;
			if (t < 0.0f || (s + t) > 1.0f) { // IntersectionPoint is outside triangle
				*intersect = false;
			}
		}
	}
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 1 // Orig. MT
// Möller/Trombore 97. Registers 24.
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det, inv_det;

	// find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	// begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	// if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	if (det > -EPSILON && det < EPSILON) {
		*intersect = false;
		return;
	}
	inv_det = 1.0f / det;

	// calculate distance from t->p0 to ray origin
	tvec = l->origin - t->p0;

	// calculate U parameter and test bounds
	float u = dot(tvec, pvec) * inv_det;
	if (u < 0.0f || u > 1.0f) {
		*intersect = false;
		return;
	}

	// prepare to test V parameter
	qvec = cross(tvec, edge1);

	// calculate V parameter and test bounds
	float v = dot(l->direction, qvec) * inv_det;
	if (v < 0.0f || u + v > 1.0f) {
		*intersect = false;
		return;
	}

	// calculate distance, ray intersects triangle
	///intersect = true;
	*distance = dot(edge2, qvec) * inv_det;
	if (*distance < 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 2 // MT2
// code rewritten to do tests on the sign of the determinant
// the division is at the end in the code  
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det, inv_det;

	// find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	// begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	// if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	if (det > EPSILON)
	{
		// calculate distance from t->p0 to ray origin
		tvec = l->origin - t->p0;
      
		// calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u < 0.0f || u > det) {
			*intersect = false;
			return;
		}
      
		// prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		// calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v < 0.0f || u + v > det) {
			*intersect = false;
			return;
		}
	}
	else if(det < -EPSILON)
	{
		// calculate distance from t->p0 to ray origin
		tvec = l->origin - t->p0;
      
		// calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u > 0.0f || u < det) {
			*intersect = false;
			return;
		}
      
		// prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		// calculate V parameter and test bounds
		float v = dot(l->direction, qvec) ;
		if (v > 0.0f || u + v < det) {
			*intersect = false;
			return;
		}
	}
	else {
		*intersect = false;
		return;
	}  // ray is parallell to the plane of the triangle

	inv_det = 1.0f / det;

	// calculate t, ray intersects triangle
	*distance = dot(edge2, qvec) * inv_det;
	if (*distance < 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}

#elif LINE_TRIANGLE_INTERSECTION_ALGORITHM == 3 // MT3
// code rewritten to do tests on the sign of the determinant
// the division is before the test of the sign of the det
void intersectLineTriangle(RAY_ASQ const Line *l, LEAF_ASQ const Triangle *t, bool *intersect, float *distance, float4 *ip)
{
	float4 edge1, edge2, tvec, pvec, qvec;
	float det, inv_det;

	//find vectors for two edges sharing t->p0
	edge1 = t->p1 - t->p0;
	edge2 = t->p2 - t->p0;

	//begin calculating determinant - also used to calculate U parameter
	pvec = cross(l->direction, edge2);

	//if determinant is near zero, ray lies in plane of triangle
	det = dot(edge1, pvec);

	//calculate distance from t->p0 to ray origin
	tvec = l->origin - t->p0;
	inv_det = 1.0f / det;
   
	if (det > EPSILON)
	{
		//calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u < 0.0f || u > det) {
			*intersect = false;
			return;
		}
      
		//prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		//calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v < 0.0f || u + v > det) {
			*intersect = false;
			return;
		}
      
	}
	else if(det < -EPSILON)
	{
		//calculate U parameter and test bounds
		float u = dot(tvec, pvec);
		if (u > 0.0f || u < det) {
			*intersect = false;
			return;
		}
      
		//prepare to test V parameter
		qvec = cross(tvec, edge1);
      
		//calculate V parameter and test bounds
		float v = dot(l->direction, qvec);
		if (v > 0.0f || u + v < det) {
			*intersect = false;
			return;
		}
	}
	else {
		*intersect = false;
		return;
	}  //ray is parallell to the plane of the triangle

	//calculate t, ray intersects triangle
	*distance = dot(edge2, qvec) * inv_det;
	if (*distance < 0.0f) {
		*intersect = false;
		return;
	}
	*intersect = true;
	*ip = l->origin + l->direction*(*distance);
}
#endif // LINE_TRIANGLE_INTERSECTION_ALGORITHM

// Registers: 8 + 33 + 4.
void intersectLineDisc(RAY_ASQ const Line *l, SCENE_ASQ const Disc *d, bool *intersect, float *distance, float4 *ip)
{
	Plane p = {
		.origin = d->origin,
		.normal = d->normal};

	intersectLinePlane(l, &p, intersect, distance, ip);

	if (*intersect){
		float4 D = d->origin - *ip;
		if (dot(D,D) > d->radius*d->radius) {
			*intersect = false;
		}
	}
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf). Registers: 6.
void intersectLineBBox(RAY_ASQ const Line *l, SCENE_ASQ const BBox *bb, bool *intersect, float *distance, float4 *ip)
{
	BBox bbox = *bb; // Copy to private memory. Workaround to fix strange error.
	BBox *b = &bbox;
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	if (l->direction.x >= 0.0f) {
        tmin = (b->min.x - l->origin.x) / l->direction.x;
        tmax = (b->max.x - l->origin.x) / l->direction.x;
	}
    else {
        tmin = (b->max.x - l->origin.x) / l->direction.x;
        tmax = (b->min.x - l->origin.x) / l->direction.x;
	}
    if (l->direction.y >= 0.0f) {
        tymin = (b->min.y - l->origin.y) / l->direction.y;
        tymax = (b->max.y - l->origin.y) / l->direction.y;
	}
    else {
        tymin = (b->max.y - l->origin.y) / l->direction.y;
        tymax = (b->min.y - l->origin.y) / l->direction.y;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
    if (l->direction.z >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) / l->direction.z;
        tzmax = (b->max.z - l->origin.z) / l->direction.z;
	}
    else {
        tzmin = (b->max.z - l->origin.z) / l->direction.z;
        tzmax = (b->min.z - l->origin.z) / l->direction.z;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*distance = tmin;
	*ip = l->origin + l->direction*tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

// Registers: 6.
void intersectLineBBoxInOut(RAY_ASQ const Line *l, SCENE_ASQ const BBox *bb, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp)
{
	BBox bbox = *bb; // Copy to private memory. Workaround to fix strange error.
	BBox *b = &bbox;
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	if (l->direction.x >= 0.0f) {
        tmin = (b->min.x - l->origin.x) / l->direction.x;
        tmax = (b->max.x - l->origin.x) / l->direction.x;
	}
    else {
        tmin = (b->max.x - l->origin.x) / l->direction.x;
        tmax = (b->min.x - l->origin.x) / l->direction.x;
	}
    if (l->direction.y >= 0.0f) {
        tymin = (b->min.y - l->origin.y) / l->direction.y;
        tymax = (b->max.y - l->origin.y) / l->direction.y;
	}
    else {
        tymin = (b->max.y - l->origin.y) / l->direction.y;
        tymax = (b->min.y - l->origin.y) / l->direction.y;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
    if (l->direction.z >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) / l->direction.z;
        tzmax = (b->max.z - l->origin.z) / l->direction.z;
	}
    else {
        tzmin = (b->max.z - l->origin.z) / l->direction.z;
        tzmax = (b->min.z - l->origin.z) / l->direction.z;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*inDistance = tmin;
	*outDistance = tmax;
	*inIp = l->origin + l->direction*tmin;
	*outIp = l->origin + l->direction*tmax;
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf). Registers: 6.
void intersectLineBBoxColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *bb, bool *intersect, float *distance, float4 *ip)
{
	BBox bbox = *bb; // Copy to private memory. Workaround to fix strange error.
	BBox *b = &bbox;
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	if (l->direction.x >= 0.0f) {
        tmin = (b->min.x - l->origin.x) / l->direction.x;
        tmax = (b->max.x - l->origin.x) / l->direction.x;
	}
    else {
        tmin = (b->max.x - l->origin.x) / l->direction.x;
        tmax = (b->min.x - l->origin.x) / l->direction.x;
	}
    if (l->direction.y >= 0.0f) {
        tymin = (b->min.y - l->origin.y) / l->direction.y;
        tymax = (b->max.y - l->origin.y) / l->direction.y;
	}
    else {
        tymin = (b->max.y - l->origin.y) / l->direction.y;
        tymax = (b->min.y - l->origin.y) / l->direction.y;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
    if (l->direction.z >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) / l->direction.z;
        tzmax = (b->max.z - l->origin.z) / l->direction.z;
	}
    else {
        tzmin = (b->max.z - l->origin.z) / l->direction.z;
        tzmax = (b->min.z - l->origin.z) / l->direction.z;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*distance = tmin;
	*ip = l->origin + l->direction*tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

// Registers: 6.
void intersectLineBBoxInOutColLeaf(RAY_ASQ const Line *l, LEAF_ASQ const BBox *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp)
{
	//BBox bbox = *bb; // Copy to private memory. Workaround to fix strange error.
	//BBox *b = &bbox;
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	if (l->direction.x >= 0.0f) {
        tmin = (b->min.x - l->origin.x) / l->direction.x;
        tmax = (b->max.x - l->origin.x) / l->direction.x;
	}
    else {
        tmin = (b->max.x - l->origin.x) / l->direction.x;
        tmax = (b->min.x - l->origin.x) / l->direction.x;
	}
    if (l->direction.y >= 0.0f) {
        tymin = (b->min.y - l->origin.y) / l->direction.y;
        tymax = (b->max.y - l->origin.y) / l->direction.y;
	}
    else {
        tymin = (b->max.y - l->origin.y) / l->direction.y;
        tymax = (b->min.y - l->origin.y) / l->direction.y;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
    if (l->direction.z >= 0.0f) {
        tzmin = (b->min.z - l->origin.z) / l->direction.z;
        tzmax = (b->max.z - l->origin.z) / l->direction.z;
	}
    else {
        tzmin = (b->max.z - l->origin.z) / l->direction.z;
        tzmax = (b->min.z - l->origin.z) / l->direction.z;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	if (tmax <= 0.0f) { // Only in the positive direction.
		*intersect = false;
        return;
	}
	*intersect = true;
	*inDistance = tmin;
	*outDistance = tmax;
	*inIp = l->origin + l->direction*tmin;
	*outIp = l->origin + l->direction*tmax;
}

// Registers 7 + 33.
void intersectLineBox(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *distance, float4 *ip) {
	int counter = 0;
	*intersect = false;
	bool intersectTmp;
	float distanceTmp;
	float4 ipTmp;
	for (int i = 0; i < 12; i++) {
		intersectLineTriangle(l, &(b->triangles[i]), &intersectTmp, &distanceTmp, &ipTmp);
		if (intersectTmp) {
			if (counter == 0) {
				*distance = distanceTmp;
				*ip = ipTmp;
				counter = counter + 1;
			}
			else {
				if (distanceTmp < *distance - EPSILON) {
					*distance = distanceTmp;
					*ip = ipTmp;
					counter = counter + 1;
				}
				else if (distanceTmp > *distance + EPSILON) {
					counter = counter + 1;
				}
				if (counter == 2) {
					*intersect = true;
					return;
				}
			}
		}
	}
}

// Registers 7 + 33.
void intersectLineBoxInOut(RAY_ASQ const Line *l, LEAF_ASQ const Box *b, bool *intersect, float *inDistance, float *outDistance, float4 *inIp, float4 *outIp) {
	int counter = 0;
	*intersect = false;
	bool intersectTmp;
	float distanceTmp;
	float4 ipTmp;
	for (int i = 0; i < 12; i++) {
		intersectLineTriangle(l, &(b->triangles[i]), &intersectTmp, &distanceTmp, &ipTmp);
		if (intersectTmp) {
			if (counter == 0) { // First intersection initializes in and out.
				*inDistance = distanceTmp;
				*inIp = ipTmp;
				*outDistance = distanceTmp;
				*outIp = ipTmp;
				counter = counter + 1;
			}
			else {
				if (distanceTmp < *inDistance - EPSILON) {
					*inDistance = distanceTmp;
					*inIp = ipTmp;
					counter = counter + 1;
				}
				else if (distanceTmp > *outDistance + EPSILON) {
					*outDistance = distanceTmp;
					*outIp = ipTmp;
					counter = counter + 1;
				}
				if (counter == 2) {
					*intersect = true;
					return;
				}
			}
		}
	}
}

#endif //__Primitives__
