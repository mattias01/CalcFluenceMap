__kernel void sum(__global const float *a, __global const float *b, __global float *c)
{
	int gid = get_global_id(0);
	c[gid] = a[gid] + b[gid];
}

__kernel void hej(__global const float *a1, __global float *b1)
{
	int gid = get_global_id(0);
	b1[gid] = a1[gid] + 1;
}

__kernel void calculate(__global const int *a, __global const int *b, __global int *result)
{
	int gid = get_global_id(0);
	result[gid] = a[gid] * 2 + b[gid] * 2;
    result[gid] += a[gid] * 2 + b[gid] * 2;
    result[gid] -= a[gid] * 3 + b[gid] * 3;
}
