cmake_minimum_required(VERSION 3.16)
project(PhysicsLabPlayground VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(SFML 3 COMPONENTS Graphics Window System REQUIRED)

add_executable(physics-lab src/main.cpp)
target_include_directories(physics-lab PRIVATE src)
target_link_libraries(physics-lab PRIVATE SFML::Graphics SFML::Window SFML::System)

enable_testing()
add_executable(physics-tests tests/physics_test.cpp)
target_include_directories(physics-tests PRIVATE src)
add_test(NAME physics-core COMMAND physics-tests)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(physics-lab PRIVATE -Wall -Wextra -Wpedantic)
  target_compile_options(physics-tests PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
