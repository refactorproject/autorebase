#include <iostream>

void NewAPI(int v) {
  std::cout << "NewAPI: " << v << std::endl;
}

int main() {
  // Feature customization: different value and extra log
  std::cout << \"Feature activated\" << std::endl;
  NewAPI(200);
  return 0;
}

