#include <algorithm>
#include <vector>
#include <numeric>
// FEATURE: add Median
double Mean(const std::vector<double>& xs) {
    double s = 0.0; for (double v : xs) s += v; return xs.empty()?0.0:s/xs.size();
}
double Clamp(double v, double lo, double hi) { return std::max(lo, std::min(v, hi)); }
double Median(std::vector<double> xs) {
    if (xs.empty()) return 0.0;
    std::sort(xs.begin(), xs.end());
    size_t n = xs.size();
    if (n % 2 == 1) return xs[n/2];
    return 0.5*(xs[n/2 - 1] + xs[n/2]);
}
