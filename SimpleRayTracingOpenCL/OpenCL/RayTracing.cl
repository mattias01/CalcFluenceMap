#include "Collimator.cl"
#include "Misc.cl"
#include "Primitives.cl"
#include "Settings.cl"

// Data types
typedef struct SimpleRaySourceRectangle {
	Rectangle rectangle;
} __attribute__((packed)) SimpleRaySourceRectangle;

typedef struct SimpleRaySourceDisc {
	Disc disc;
} __attribute__((packed)) SimpleRaySourceDisc;

typedef struct FluenceMap {
	Rectangle rectangle;
} __attribute__((packed)) FluenceMap;

typedef struct Scene {
	SimpleRaySourceDisc raySource;
	int collimators;
	FluenceMap fluenceMap;
} __attribute((packed)) Scene;

typedef struct Render {
	int flx, fly;
	float xstep, ystep, xoffset, yoffset;
	int lsamples;
	float lstep;
	//int mode;
} __attribute((packed)) Render;

// Intersections

void intersectSimpleRaySourceRectangle(const Line *l, __constant const SimpleRaySourceRectangle *rs, bool *intersect, float *distance, float4 *ip) {
	Rectangle s = rs->rectangle; // Copy from constant memory to private
	intersectLineRectangle(l, &s, intersect, distance, ip);
}

void intersectSimpleRaySourceDisc(const Line *l, __constant const SimpleRaySourceDisc *rs, bool *intersect, float *distance, float4 *ip) {
	Disc d = rs->disc; // Copy from constant memory to private
	intersectLineDisc(l, &d, intersect, distance, ip);
}

// Ray tracing

void firstHitLeaf(__constant const Scene *s, __constant const Render *render, const Line *r, __global const Collimator *collimator, bool *intersect, float *distance, float4 *ip, float *thickness, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
	*ip = (NAN, NAN, NAN, NAN);
	*thickness = 0;
	int leafIndex = -1;
	Collimator col = *collimator;
	for (int i = 0; i < collimator->numberOfLeaves; i++) {
		bool intersectTmp;
		float distanceTmp;
		float4 ipTmp;
		float thicknessTmp;
		#if MODE == 0
			intersectLineFlatCollimatorLeaf(r, &(col.flatCollimator.leaves[i]), &intersectTmp, &distanceTmp, &ipTmp);
			thicknessTmp = col.height;
		#elif MODE == 1
			float4 ipInTmp;
			float distanceOutTmp;
			intersectLineBBoxCollimatorLeaf(r, &(col.bboxCollimator.leaves[i]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			thicknessTmp = distanceOutTmp - distanceTmp;
		#elif MODE == 2
			float4 ipInTmp;
			float distanceOutTmp;
			intersectLineBoxCollimatorLeaf(r, &(col.boxCollimator.leaves[i]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			thicknessTmp = distanceOutTmp - distanceTmp;
		#endif

		if (intersectTmp && (distanceTmp < minDistance)) {
			leafIndex = i;
			minDistance = distanceTmp;
			*ip = ipTmp;
			*thickness = thicknessTmp;
		}
	}

	if (leafIndex != -1) {
		*intersect = true;
		*distance = minDistance;
	}
}

void firstHitCollimator(__constant const Scene *s, __constant const Render *render, const Line *r, __global const Collimator *collimators, bool *intersect, float *distance, float4 *ip, float *intensityCoeff, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
	*ip = (NAN, NAN, NAN, NAN);
	float4 bbOutPoint;
	float bbOutDistance;
	*intensityCoeff = 1;
	int collimatorIndex = -1;
	for (int i = 0; i < s->collimators; i++) { // Find first collimator
		bool intersectTmp = false;
		float distanceTmp;
		float4 ipTmpCollimatorBB;
		float4 ipTmpCollimatorBBOut;
		float distanceTmpOut;
		Collimator collimator = collimators[i];
		#if MODE == 0
			intersectLineBBoxInOut(r, &(collimator.flatCollimator.boundingBox), &intersectTmp, &distanceTmp, &distanceTmpOut, &ipTmpCollimatorBB, &ipTmpCollimatorBBOut);
		#elif MODE == 1
			intersectLineBBoxInOut(r, &(collimator.bboxCollimator.boundingBox), &intersectTmp, &distanceTmp, &distanceTmpOut, &ipTmpCollimatorBB, &ipTmpCollimatorBBOut);
		#elif MODE == 2
			intersectLineBBoxInOut(r, &(collimator.boxCollimator.boundingBox), &intersectTmp, &distanceTmp, &distanceTmpOut, &ipTmpCollimatorBB, &ipTmpCollimatorBBOut);
		#endif

		if (intersectTmp && (distanceTmp < minDistance)) {
			collimatorIndex = i;
			minDistance = distanceTmp;
			bbOutDistance = distanceTmpOut;
			bbOutPoint = ipTmpCollimatorBBOut;
		}
	}
	
	if (collimatorIndex != -1) { // Check leaves on closest Collimator.
		//Collimator collimator = collimators[collimatorIndex]; // Remove this!
		bool intersectTmp;
		float distanceTmp;
		float4 ipTmpLeaf;
		float thickness = 0;
		firstHitLeaf(s, render, r, &collimators[collimatorIndex], &intersectTmp, &distanceTmp, &ipTmpLeaf, &thickness, debug);
		while (intersectTmp) {
			*intersect = true;
			*distance = distanceTmp; // Not used after.
			*intensityCoeff *= exp(-collimators[collimatorIndex].absorptionCoeff*thickness);
			#if MODE == 0
			// One leaf hit. Continue ray after collimator because leaves don't have thickness.
				*ip = ipTmpLeaf;
				intersectTmp = false;
			#elif MODE == 1 || MODE == 2
			// One ray can hit several leaves.
				*ip = ipTmpLeaf;
				Line newRay = {
					.origin = ipTmpLeaf,
					.direction = r->direction};
				firstHitLeaf(s, render, &newRay, &collimators[collimatorIndex], &intersectTmp, &distanceTmp, &ipTmpLeaf, &thickness, debug);
			#endif
		}
		if (*intersect == false) { // Did not hit any leaves, but hit bounding box
			*intersect = true;
			*distance = bbOutDistance; // Not used after.
			*ip = bbOutPoint; // Continue ray after bounding box.
		}
	}
}

void traceRay(__constant const Scene *s, __constant const Render *render, const Line *r, __global const Collimator *collimators, float *i, __global Debug *debug) {
	float intensity = 1;
	bool intersectCollimator = false;
	float distanceCollimator;
	float4 ipCollimator;
	float intensityCoeff;
	firstHitCollimator(s, render, r, collimators, &intersectCollimator, &distanceCollimator, &ipCollimator, &intensityCoeff, debug);
	while (intersectCollimator) {
		intensity *= intensityCoeff;
		if (intensity < INTENSITY_THRESHOLD) { // If intensity is below a treshhold, don't bother to cast more rays. Return 0 intensity.
			*i = 0;
			return;
		}
		else {
			Line newRay = {
				.origin = ipCollimator,
				.direction = r->direction};
			firstHitCollimator(s, render, &newRay, collimators, &intersectCollimator, &distanceCollimator, &ipCollimator, &intensityCoeff, debug);
		}
	}

	bool intersectRaySource;
	float distanceRaySource;
	float4 ipRaySource;
	intersectSimpleRaySourceDisc(r, &(s->raySource), &intersectRaySource, &distanceRaySource, &ipRaySource);
	if (intersectRaySource) {
		*i = intensity;
	}
	else {
		*i = 0; // To infinity
	}
}

// Gives vectors from the ray origin to left, right, bottom, top of the ray source.
void lightSourceAreaVectors(__constant const Scene *scene, const float4 *rayOrigin, float4 *vi0, float4 *vi1, float4 *vj0, float4 *vj1, __global Debug *debug) {
	*vi0 = (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.y, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vi1 = (float4) (scene->raySource.disc.origin.x + scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.y, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vj0 = (float4) (scene->raySource.disc.origin.x, 
					 scene->raySource.disc.origin.y - scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;

	*vj1 = (float4) (scene->raySource.disc.origin.x, 
					 scene->raySource.disc.origin.y + scene->raySource.disc.radius, 
					 scene->raySource.disc.origin.z,
					 scene->raySource.disc.origin.w) - *rayOrigin;
}

void calculateIntensityDecreaseWithDistance(__constant const Scene *scene, const float4 *rayOrigin, float *distanceFactor, __global Debug *debug) {
	float4 vi0, vi1, vj0, vj1;
	lightSourceAreaVectors(scene, rayOrigin, &vi0, &vi1, &vj0, &vj1, debug);
	float anglei = acos(dot(normalize(vi0), normalize(vi1)));
    float anglej = acos(dot(normalize(vj0), normalize(vj1)));
	*distanceFactor = anglei*anglej/M_PI_F*2; // The ratio of a unit half sphere that are covering the light source. => Things that are further away recieves less photons.
}

// Integration over the light source is done as if the rays where cast from a pixel straight under the origin of the light source. The sampling is uniform only from that point.
void flatLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, const float4 *rayOrigin, float *fluenceSum, __global Debug *debug) {
	for (int li = 0; li < render->lsamples; li++) {
		for (int lj = 0; lj < render->lsamples; lj++) {
			float4 lPoint =  (float4) (scene->raySource.disc.origin.x - scene->raySource.disc.radius + li*render->lstep, 
									   scene->raySource.disc.origin.y - scene->raySource.disc.radius + lj*render->lstep, 
                                       scene->raySource.disc.origin.z,
                                       scene->raySource.disc.origin.w);
			float4 rayDirection = lPoint - *rayOrigin;

			Line ray = {
				.origin = *rayOrigin, 
				.direction = normalize(rayDirection)};

			float intensity;
			traceRay(scene, render, &ray, collimators, &intensity, debug);
			
			*fluenceSum += intensity; // Add intensity from ray
		}
	}
}

// Integration is done in a uniform way over the light source. The sampling is uniform from every point. This might contain errors.
void uniformLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, const float4 *rayOrigin, float *fluenceSum, __global Debug *debug) {
	float4 lvi0, lvi1, lvj0, lvj1;
	lightSourceAreaVectors(scene, rayOrigin, &lvi0, &lvi1, &lvj0, &lvj1, debug);

	float4 vi0, vi1, vj0, vj1; // 0 is the closest vector
	if (length(lvi0) < length(lvi1)) { // Find the closest i vector.
		vi0 = lvi0;
		vi1 = lvi1;
	}
	else {
		vi0 = lvi1;
		vi1 = lvi0;
	}
	if (length(lvj0) < length(lvj1)) { // Find the closest j vector.
		vj0 = lvj0;
		vj1 = lvj1;
	}
	else {
		vj0 = lvj1;
		vj1 = lvj0;
	}
	vi1 = length(vi0)*normalize(vi1); // vx1 is now of same length as vx0 which creates a plane that we cast rays on to get an uniform sampling.
	vj1 = length(vj0)*normalize(vj1);
	float4 idir = (*rayOrigin + vi1) - (*rayOrigin + vi0);
	float4 jdir = (*rayOrigin + vj1) - (*rayOrigin + vj0);
	float istep = length(idir)/(render->lsamples-1);
	float jstep = length(jdir)/(render->lsamples-1);
	
	float4 corner = (*rayOrigin + vi0) - normalize(jdir)*length(jdir)/2;

	for (int li = 0; li < render->lsamples; li++) {
		for (int lj = 0; lj < render->lsamples; lj++) {
			float4 lPoint =  corner + li*istep*idir + lj*jstep*jdir;
			float4 rayDirection = lPoint - *rayOrigin;

			Line ray = {
				.origin = *rayOrigin, 
				.direction = normalize(rayDirection)};

			float intensity;
			traceRay(scene, render, &ray, collimators, &intensity, debug);
			
			*fluenceSum += intensity; // Add intensity from ray
		}
	}
}

void calcFluenceElement(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, __global float *fluence_data, __global Debug *debug){
	unsigned int i = get_global_id(0);
    unsigned int j = get_global_id(1);

	float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*render->xstep + render->xoffset, 
								 scene->fluenceMap.rectangle.p0.y + j*render->ystep + render->yoffset, 
								 scene->fluenceMap.rectangle.p0.z, 0);

	float distanceFactor;
	calculateIntensityDecreaseWithDistance(scene, &rayOrigin, &distanceFactor, debug);
	float fluenceSum = 0;
	//flatLightSourceSampling(scene, render, collimators, &rayOrigin, &fluenceSum, debug);
	uniformLightSourceSampling(scene, render, collimators, &rayOrigin, &fluenceSum, debug);
	fluence_data[i*render->flx+j] = fluenceSum*distanceFactor;
}

void initCollimators(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, Collimator *collimators_new) {
	// First copy all properties
	for (int i = 0; i < scene->collimators; i++) {
		collimators_new[i].boundingBox = collimators[i].boundingBox;
		collimators_new[i].position = collimators[i].position;
		collimators_new[i].xdir = collimators[i].xdir;
		collimators_new[i].ydir = collimators[i].ydir;
		collimators_new[i].absorptionCoeff = collimators[i].absorptionCoeff;
		collimators_new[i].numberOfLeaves = collimators[i].numberOfLeaves;
		for (int l = 0; l < collimators[i].numberOfLeaves; l++) {
			collimators_new[i].leafPositions[l] = collimators[i].leafPositions[l];
		}
	}
	// Copy simplified model according to mode.
	#if MODE == 0
		for (int i = 0; i < scene->collimators; i++) {
			FlatCollimator flatCollimator;
			Collimator col = collimators[i]; // Copy from constant to private memory.
			createFlatCollimator(&col, &flatCollimator);
			collimators_new[i].flatCollimator = flatCollimator;
		}
	#endif
}

__kernel void drawScene(__constant const Scene *scene, __constant const Render *render, __global float *fluence_data, __global const Collimator *collimators, __global Debug *debug)
{
	//unsigned int i = get_global_id(0);
    //unsigned int j = get_global_id(1);

	calcFluenceElement(scene, render, collimators, fluence_data, debug);
}