#include <iostream>

void OldAPI(int v) {
  std::cout << "OldAPI: " << v << std::endl;
}

int main() {
  OldAPI(42);
  return 0;
}

