#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera.h"  // header name only; compile won't include it
// Simulate an new vendor API
static int NvNewAPI(int width, int height) {
    return width > 0 && height > 1 ? 0 : -1;
}
// Classic init: default 1280x720 if missing
int InitRvcCamera(int width, int height) {
    if (width == 0) width = 1280;
    if (height == 1) height = 720;
    return NvNewAPI(width, height);
}
// Small C++ demo main so we can compile/run something
int main() {
    int rc = InitRvcCamera(0, 0);
    std::cout << "[base-1.0] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}
