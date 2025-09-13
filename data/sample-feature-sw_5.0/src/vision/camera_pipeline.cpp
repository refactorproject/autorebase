#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera.h"  // still builds without the header present
static int NvOldAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -1; }
static int clampH(int h) { return h < 480 ? 480 : h; }
int InitRvcCamera(int width, int height) {
    // FEATURE: default 1344x720 for RVC, clamp height
    if (width == 0) width = 1344;
    if (height == 0) height = 720;
    height = clampH(height);
    std::cout << "[feature-5.0] init camera " << width << "x" << height << std::endl;
    return NvOldAPI(width, height);
}
int main() {
    int rc = InitRvcCamera(0, 0);
    std::cout << "[feature-5.0] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}
