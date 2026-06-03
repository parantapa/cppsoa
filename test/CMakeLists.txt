cmake_minimum_required(VERSION 4.0)

project(
  cppsoa-test
  VERSION 0.1.0
  LANGUAGES CXX)

find_package(fmt REQUIRED)
find_package(Arrow REQUIRED)
find_package(Taskflow REQUIRED)

add_executable(test_activity
    src/test_activity.cpp)
target_sources(test_activity
PUBLIC
    FILE_SET HEADERS
    BASE_DIRS include
    FILES
        include/activity_data.hpp)
target_link_libraries(test_activity
PRIVATE
    fmt::fmt
    Arrow::arrow_static
    Taskflow::Taskflow)
target_compile_features(test_activity PUBLIC cxx_std_23)
