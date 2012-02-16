#ifndef __Primitives__
#define __Primitives__

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

typedef struct Box {
	float4 min;
	float4 max;
} __attribute__((packed)) Box;

// Projection calculations

void projectPointOntoPlane(float4 *p0, Plane *plane, float4 *resultPoint) {
    float sn = -dot(plane->normal, (*p0 - plane->origin));
    float sd = dot(plane->normal, plane->normal);
    float sb = sn / sd;
    *resultPoint = *p0 + plane->normal * sb;
}

// Intersection calculations
void intersectLinePlane(const Line *l, const Plane *p, bool *intersect, float *distance, float4 *ip)
{
	// Init to not intersect
	*intersect = false;
	*distance = NAN;
	*ip = (NAN, NAN, NAN, NAN);
	if (dot(l->direction, p->normal) != 0.0f) { // Not parallel -> intersect.
		float t = (dot(p->normal, (p->origin - l->origin))) / (dot(p->normal, l->direction));
		if (t > 0) { // Plane is located in positive ray direction from the ray origin. Avoids hitting same thing it just hit.
			*intersect = true;
			*distance = t;
			*ip = l->origin + l->direction*(*distance);
		}
	}
}

void intersectLineTriangle(const Line *l, const Triangle *t, bool *intersect, float *distance, float4 *ip)
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
			*distance = NAN;
			*ip = (NAN, NAN, NAN, NAN);
		}
		else {
			float t = (uv * wu - uu * wv) / D;
			if (t < 0.0 || (s + t) > 1.0) { // IntersectionPoint is outside triangle
				*intersect = false;
				*distance = NAN;
				*ip = (NAN, NAN, NAN, NAN);
			}
		}
	}
}

void intersectLineRectangle(const Line *l, const Rectangle *s, bool *intersect, float *distance, float4 *ip)
{
	Triangle t1 = {
		.p0 = s->p0,
		.p1 = s->p1,
		.p2 = s->p2};
	Triangle t2 = {
		.p0 = s->p2,
		.p1 = s->p3,
		.p2 = s->p0};

	intersectLineTriangle(l, &t1, intersect, distance, ip);

	if (!(*intersect)) { // Try to find intersection in second triangle
		intersectLineTriangle(l, &t2, intersect, distance, ip);
	}
}

void intersectLineDisc(const Line *l, const Disc *d, bool *intersect, float *distance, float4 *ip)
{
	Plane p = {
		.origin = d->origin,
		.normal = d->normal};

	intersectLinePlane(l, &p, intersect, distance, ip);

	if (*intersect){
		float4 D = d->origin - *ip;
		if (dot(D,D) > d->radius*d->radius) {
			*intersect = false;
			*distance = NAN;
			*ip = (NAN, NAN, NAN, NAN);
		}
	}
}

// Relies on IEEE 754 floating point arithmetic (div by 0 -> inf).
void intersectLineBox(const Line *l, const Box *b, bool *intersect, float *distance, float4 *ip)
{
	float tmin, tmax, tymin, tymax, tzmin, tzmax;
	if (l->direction.x >= 0) {
        tmin = (b->min.x - l->origin.x) / l->direction.x;
        tmax = (b->max.x - l->origin.x) / l->direction.x;
	}
    else {
        tmin = (b->max.x - l->origin.x) / l->direction.x;
        tmax = (b->min.x - l->origin.x) / l->direction.x;
	}
    if (l->direction.y >= 0) {
        tymin = (b->min.y - l->origin.y) / l->direction.y;
        tymax = (b->max.y - l->origin.y) / l->direction.y;
	}
    else {
        tymin = (b->max.y - l->origin.y) / l->direction.y;
        tymax = (b->min.y - l->origin.y) / l->direction.y;
	}
    if ((tmin > tymax) || (tymin > tmax)) {
		*intersect = false;
		*distance = NAN;
		*ip = (NAN, NAN, NAN, NAN);
        return;
	}
    if (tymin > tmin) {
        tmin = tymin;
	}
    if (tymax < tmax) {
       tmax = tymax;
	}
    if (l->direction.z >= 0) {
        tzmin = (b->min.z - l->origin.z) / l->direction.z;
        tzmax = (b->max.z - l->origin.z) / l->direction.z;
	}
    else {
        tzmin = (b->max.z - l->origin.z) / l->direction.z;
        tzmax = (b->min.z - l->origin.z) / l->direction.z;
	}
    if ((tmin > tzmax) || (tzmin > tmax)) {
        *intersect = false;
		*distance = NAN;
		*ip = (NAN, NAN, NAN, NAN);
        return;
	}
    if (tzmin > tmin) {
        tmin = tzmin;
	}
    if (tzmax < tmax) {
        tmax = tzmax;
	}
	*intersect = true;
	*distance = tmin;
	*ip = l->origin + l->direction*tmin;
	// Could give the outgoing distance (tmax) and point here as well.
}

#endif //__Primitives__
