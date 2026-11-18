cmake_minimum_required(VERSION 3.20)
project(PinjamLab_Module4)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

include_directories(cpp/include)

add_executable(csv_dump cpp/tools/csv_dump.cpp)

add_executable(csv_roundtrip_writer cpp/tools/csv_roundtrip_writer.cpp)

add_executable(test_csv cpp/tests/test_csv.cpp)

target_include_directories(test_csv PRIVATE cpp/tests)