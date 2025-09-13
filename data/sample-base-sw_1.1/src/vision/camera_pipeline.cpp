#include <iostream>
#include <vector>
#include <numeric>
#include "nv/camera_utils.h" // upstream header name
static int NvNewAPI(int width, int height) { return width > 0 && height > 0 ? 0 : -2; }
struct NvCtx { int reserved{0}; };
int InitRvcCamera(const NvCtx& ctx, int width, int height) {
    if (width == 0) width = 1280;
    if (height == 0) height = 720;
    (void)ctx;
    return NvNewAPI(width, height);
}
int main() {
    NvCtx ctx{};
    int rc = InitRvcCamera(ctx, 0, 0);
    std::cout << "[base-1.1] InitRvcCamera -> " << rc << std::endl;
    return rc == 0 ? 0 : 1;
}
