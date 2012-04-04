
#include "RayTracing.h"

// Ray tracing
void firstHitLeaf(SCENE_ASQ Scene *s, RAY_ASQ const Line *r, LEAF_ASQ float4 *leaf_data, int *collimatorIndex, bool *intersect, float4 *ip, float *thickness, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;

	for (int i = 0; i < s->collimators.numberOfLeaves[*collimatorIndex]; i++) {
		bool intersectTmp;
		float distanceTmp;
		float4 ipTmp;
		float thicknessTmp;
		#if MODE == 0
			intersectLineFlatCollimatorLeaf(r, (LEAF_ASQ Triangle const *) &(leaf_data[i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex]]), (LEAF_ASQ Triangle const *) &(leaf_data[i*s->collimators.flatCollimator.leafArrayStride[*collimatorIndex] + 3]), &intersectTmp, &distanceTmp, &ipTmp);
			thicknessTmp = s->collimators.height[*collimatorIndex];
		#elif MODE == 1
			float4 ipInTmp;
			float distanceOutTmp;
			intersectLineBBoxCollimatorLeaf(r, (LEAF_ASQ BBox const *) &(leaf_data[i*s->collimators.bboxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, &ipInTmp, &ipTmp);
			thicknessTmp = distanceOutTmp - distanceTmp;
		#elif MODE == 2
			//float4 ipInTmp;
			float distanceOutTmp;
			intersectLineBoxCollimatorLeaf(r, (LEAF_ASQ Box const *) &(leaf_data[i*s->collimators.boxCollimator.leafArrayStride[*collimatorIndex]]), &intersectTmp, &distanceTmp, &distanceOutTmp, /*&ipInTmp,*/ &ipTmp);
			thicknessTmp = distanceOutTmp - distanceTmp;
		#endif

		if (intersectTmp && (distanceTmp < minDistance)) {
			minDistance = distanceTmp;
			*intersect = true;
			*ip = ipTmp;
			*thickness = thicknessTmp;
		}
	}
}

void hitCollimator(SCENE_ASQ Scene *s, RAY_ASQ Line *r, int *collimatorIndex, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, bool *intersect, float4 *ip, float *intensityCoeff, __global Debug *debug) {
	bool intersectTmp;
	float4 ipTmpLeaf;
	float thickness;

	#if LEAF_AS == 0
	#elif LEAF_AS == 1
		#if MODE == 0
			for (int j = 0; j < s->collimators.flatCollimator.numberOfLeaves[*collimatorIndex] * s->collimators.flatCollimator.leafArrayStride[*collimatorIndex]; j++) {
				col_leaf_data[j] = leaf_data[s->collimators.flatCollimator.leafArrayOffset[*collimatorIndex] + j];
			}
			barrier(CLK_LOCAL_MEM_FENCE);
		#elif MODE == 1
			for (int j = 0; j < s->collimators.bboxCollimator.numberOfLeaves[*collimatorIndex] * s->collimators.bboxCollimator.leafArrayStride[*collimatorIndex]; j++) {
				col_leaf_data[j] = leaf_data[s->collimators.bboxCollimator.leafArrayOffset[*collimatorIndex] + j];
			}
			barrier(CLK_LOCAL_MEM_FENCE);
		#elif MODE == 2
			for (int j = 0; j < s->collimators.boxCollimator.numberOfLeaves[*collimatorIndex] * s->collimators.boxCollimator.leafArrayStride[*collimatorIndex]; j++) {
				col_leaf_data[j] = leaf_data[s->collimators.boxCollimator.leafArrayOffset[*collimatorIndex] + j];
			}
			barrier(CLK_LOCAL_MEM_FENCE);
		#endif
	#elif LEAF_AS == 3
		#if MODE == 0
            col_leaf_data = &leaf_data[s->collimators.flatCollimator.leafArrayOffset[*collimatorIndex]];
		#elif MODE == 1
            col_leaf_data = &leaf_data[s->collimators.bboxCollimator.leafArrayOffset[*collimatorIndex]];
		#elif MODE == 2
            col_leaf_data = &leaf_data[s->collimators.boxCollimator.leafArrayOffset[*collimatorIndex]];
		#endif
	#endif
            
	firstHitLeaf(s, r, col_leaf_data, collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
	float absorptionCoeff = s->collimators.absorptionCoeff[*collimatorIndex];
	while (intersectTmp) {
		*intersect = true;
		*intensityCoeff *= exp(-absorptionCoeff*thickness);
		#if MODE == 0
			// One leaf hit. Continue ray after collimator because leaves don't have thickness.
			intersectTmp = false;
			*ip = ipTmpLeaf;
		#elif MODE == 1 || MODE == 2
			// One ray can hit several leaves.
			*ip = ipTmpLeaf;
			r->origin = ipTmpLeaf;
			firstHitLeaf(s, r, col_leaf_data, collimatorIndex, &intersectTmp, &ipTmpLeaf, &thickness, debug);
		#endif
	}
}

void firstHitCollimator(SCENE_ASQ Scene *s, RAY_ASQ Line *r, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, bool *intersect, float4 *ip, float *intensityCoeff, __global Debug *debug) {
	*intersect = false;
	float minDistance = MAXFLOAT;
	*intensityCoeff = 1.0f;
	int collimatorIndex = -1;
    for (int i = 0; i < NUMBER_OF_COLLIMATORS; i++) { // Find closest collimator
		bool intersectTmp;
		float distanceTmpIn;
		float distanceTmpOut;
		float4 ipTmpCollimatorBBIn;
		float4 ipTmpCollimatorBBOut;
		#if MODE == 0
			intersectLineBBoxInOut(r, &(s->collimators.flatCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
		#elif MODE == 1
			intersectLineBBoxInOut(r, &(s->collimators.bboxCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
		#elif MODE == 2
			intersectLineBBoxInOut(r, &(s->collimators.boxCollimator.boundingBox[i]), &intersectTmp, &distanceTmpIn, &distanceTmpOut, &ipTmpCollimatorBBIn, &ipTmpCollimatorBBOut);
		#endif
        
		if (intersectTmp && (distanceTmpIn < minDistance)) {
			collimatorIndex = i;
			minDistance = distanceTmpIn;
			*intersect = true;
			*ip = ipTmpCollimatorBBOut;
			#if STRUCTURE == 0
				hitCollimator(s, r, &collimatorIndex, leaf_data, col_leaf_data, intersect, ip, intensityCoeff, debug);
			#endif
		}
	}
	
	#if STRUCTURE == 1
		if (collimatorIndex != -1)
			hitCollimator(s, r, &collimatorIndex, leaf_data, col_leaf_data, intersect, ip, intensityCoeff, debug);
	#endif
}

void traceRay(SCENE_ASQ Scene *s, RAY_ASQ Line *r, __global float4 *leaf_data, LEAF_ASQ float4 *col_leaf_data, float *i, __global Debug *debug) {
	float intensity = 1.0f;
	bool intersect;
	float4 ip;
	float intensityCoeff;
	firstHitCollimator(s, r, leaf_data, col_leaf_data, &intersect, &ip, &intensityCoeff, debug);
	while (intersect) {
		intensity *= intensityCoeff;
		if (intensity < INTENSITY_THRESHOLD) { // If intensity is below a threshold, don't bother to cast more rays. Return 0 intensity.
			*i = 0.0f;
			return;
		}
		else {
			r->origin = ip; // Create a new ray. Same direction but new origin.
			firstHitCollimator(s, r, leaf_data, col_leaf_data, &intersect, &ip, &intensityCoeff, debug);
		}
	}

	bool intersectRaySource;
	float distanceRaySource;
	float4 ipRaySource;
	intersectLineDisc(r, &(s->raySource), &intersectRaySource, &distanceRaySource, &ipRaySource);
	if (intersectRaySource) {
		*i = intensity;
	}
	else {
		*i = 0.0f; // To infinity
	}
}

// Gives vectors from the ray origin to left, right, bottom, top of the ray source.
void lightSourceAreaVectors(SCENE_ASQ Scene *scene, const float4 *rayOrigin, float4 *vi0, float4 *vi1, float4 *vj0, float4 *vj1, __global Debug *debug) {
	*vi0 = (float4) (scene->raySource.origin.x - scene->raySource.radius, 
					 scene->raySource.origin.y, 
					 scene->raySource.origin.z,
					 scene->raySource.origin.w) - *rayOrigin;

	*vi1 = (float4) (scene->raySource.origin.x + scene->raySource.radius, 
					 scene->raySource.origin.y, 
					 scene->raySource.origin.z,
					 scene->raySource.origin.w) - *rayOrigin;

	*vj0 = (float4) (scene->raySource.origin.x, 
					 scene->raySource.origin.y - scene->raySource.radius, 
					 scene->raySource.origin.z,
					 scene->raySource.origin.w) - *rayOrigin;

	*vj1 = (float4) (scene->raySource.origin.x, 
					 scene->raySource.origin.y + scene->raySource.radius, 
					 scene->raySource.origin.z,
					 scene->raySource.origin.w) - *rayOrigin;
}

// Integration is done in a uniform way over the light source. The sampling is uniform from every point. This contains errors!
/*void uniformLightSourceSampling(__constant const Scene *scene, __constant const Render *render, __global const Collimator *collimators, const float4 *rayOrigin, float *fluenceSum, __global Debug *debug) {
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
}*/

/*void initCollimators(__constant const Scene *scene, __constant const Render *render, __constant const Collimator collimators[NUMBER_OF_COLLIMATORS], Collimator *collimators_new) {
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
}*/

// Integration over the light source is done as if the rays where cast from a pixel straight under the origin of the light source. The sampling is uniform only from that point.
__kernel void flatLightSourceSampling(SCENE_ASQ Scene *scene, __global float4 *leaf_data, __global float *intensity_map, __global Debug *debug) {
	int i = get_global_id(0);
	int j = get_global_id(1);
	int k = get_global_id(2);
	int li = (k/LSAMPLES);
	int lj = (k%LSAMPLES);

#if RAY_AS == 0
    float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*XSTEP + XOFFSET, 
                                 scene->fluenceMap.rectangle.p0.y + j*YSTEP + YOFFSET, 
                                 scene->fluenceMap.rectangle.p0.z, 0.0f);
    float4 lPoint =  (float4) (scene->raySource.origin.x - scene->raySource.radius + li*LSTEP, 
                               scene->raySource.origin.y - scene->raySource.radius + lj*LSTEP, 
                               scene->raySource.origin.z, 0.0f);

	float4 rayDirection = normalize(lPoint - rayOrigin);
    	
	Line ray = {
		.origin = rayOrigin,
		.direction = rayDirection};

#elif RAY_AS == 1
	int x = get_local_id(0);
	int y = get_local_id(1);
	int z = get_local_id(2);
	//int x_size = get_local_size(0);
	//int y_size = get_local_size(1);

	__local Line ray[WG_LIGHT_SAMPLING_SIZE];
	ray[x + y*get_local_size(0) + z*get_local_size(0)*get_local_size(1)].origin = (float4) (scene->fluenceMap.rectangle.p0.x + i*XSTEP + XOFFSET, scene->fluenceMap.rectangle.p0.y + j*YSTEP + YOFFSET, scene->fluenceMap.rectangle.p0.z, 0.0f);
	ray[x + y*get_local_size(0) + z*get_local_size(0)*get_local_size(1)].direction = normalize(((float4)(scene->raySource.origin.x - scene->raySource.radius + li*LSTEP, scene->raySource.origin.y - scene->raySource.radius + lj*LSTEP, scene->raySource.origin.z, 0.0f)) - ((float4)(scene->fluenceMap.rectangle.p0.x + i*XSTEP + XOFFSET, scene->fluenceMap.rectangle.p0.y + j*YSTEP + YOFFSET, scene->fluenceMap.rectangle.p0.z, 0.0f)));
#endif //LOCAL_RAYS

#if LEAF_AS == 1 // Allocate __local memory here in the __kernel because some compilers don't allow for __local memory allocation in ordinary functions.
	#if MODE == 0
		__local float4 col_leaf_data[NUMBER_OF_LEAVES * 2 * 3]; // Make sure it's >= than the leaf data.
	#elif MODE == 1
		__local float4 col_leaf_data[NUMBER_OF_LEAVES * 2]; // Make sure it's >= than the leaf data.
	#elif MODE == 2
		__local float4 col_leaf_data[NUMBER_OF_LEAVES * 10/*12*/ * 3]; // Make sure it's >= than the leaf data.
	#endif
#elif LEAF_AS == 3
	__global float4 *col_leaf_data;
#endif
 
	float intensity;
#if RAY_AS == 0
	traceRay(scene, &ray, leaf_data, col_leaf_data, &intensity, debug);
#elif RAY_AS == 1
	traceRay(scene, &(ray[x + y*get_local_size(0) + z*get_local_size(0)*get_local_size(1)]), leaf_data, col_leaf_data, &intensity, debug);
#endif //RAY_AS
	intensity_map[get_global_id(1) + get_global_id(0)*FLY + get_global_id(2)*FLX*FLY] = intensity; // Add intensity from ray. Use get_global_id() to let the compiler spare some registers.
} 

__kernel void calculateIntensityDecreaseWithDistance(SCENE_ASQ Scene *scene, __global float *distanceFactors, __global Debug *debug) {
	float4 vi0, vi1, vj0, vj1;

	int i = get_global_id(0);
	int j = get_global_id(1);
    
    float4 rayOrigin = (float4) (scene->fluenceMap.rectangle.p0.x + i*XSTEP + XOFFSET, 
                                 scene->fluenceMap.rectangle.p0.y + j*YSTEP + YOFFSET, 
                                 scene->fluenceMap.rectangle.p0.z, 0.0f);

	lightSourceAreaVectors(scene, &rayOrigin, &vi0, &vi1, &vj0, &vj1, debug);
	float anglei = acos(dot(normalize(vi0), normalize(vi1)));
    float anglej = acos(dot(normalize(vj0), normalize(vj1)));

    distanceFactors[j+i*FLY] = anglei*anglej/M_PI_F*2.0f; // The ratio of a unit half sphere that are covering the light source. => Things that are further away recieves less photons.
}

__kernel void calcFluenceElement(SCENE_ASQ Scene *scene, __global float *intensity_map, __global float *fluence_data, __global Debug *debug){
	int i = get_global_id(0);
    int j = get_global_id(1);

	float fluenceSum = 0.0f;
    for (int k = 0; k < LSAMPLESSQR; k++) {
        fluenceSum += intensity_map[j + i*FLY + k*FLX*FLY];
	}
    fluence_data[j+i*FLY] *= fluenceSum; // Assumes fluence element already contains distance factor.
}

#define force_recomp 29