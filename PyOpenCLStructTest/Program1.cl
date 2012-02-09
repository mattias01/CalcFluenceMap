// Data types
typedef struct hej {
        int f0;
        float f1;
} __attribute__((packed)) hej;

typedef struct hej2 {
        int4 f0;
        float4 f1;
} __attribute__((packed)) hej2;

typedef struct Child {
        int x;
        int y;
} __attribute__((packed)) Child;

typedef struct Parent {
        Child c;
        int z;
} __attribute__((packed)) Parent;

// Kernels
__kernel void test(__global const hej *a, __global int *b, __global float *c)
{
	*b = a->f0;
	*c = a->f1;
}

__kernel void test2(__global const hej2 *a, __global int4 *b, __global float4 *c)
{
	*b = a->f0;
	*c = a->f1;
}

__kernel void test3(__global const Parent *a, __global int *b)
{
	*b = a->c.x + a->c.y;
}