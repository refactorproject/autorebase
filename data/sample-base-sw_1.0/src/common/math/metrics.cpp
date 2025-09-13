#include <algorithm>
#include <vector>
double Mean(const std::vector<double>& xs) {
    double s = 0.0; for (double v : xs) s += v; return xs.empty()?0.0:s/xs.size();
}
double Clamp(double v, double lo, double hi) {
    return std::max(lo, std::min(v, hi));
}
