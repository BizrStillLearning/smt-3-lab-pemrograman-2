cmake_minimum_required(VERSION 4.0)
project(Module3)

set(CMAKE_CXX_STANDARD 14)

include_directories(cpp/include)
include_directories(cpp/include/pinjamlab)
include_directories(cpp/include/pinjamlab/app)
include_directories(cpp/include/pinjamlab/domain)
include_directories(cpp/include/pinjamlab/io)
include_directories(cpp/include/pinjamlab/service)
include_directories(cpp/tests)

add_executable(Module3
        cpp/app/main.cpp
        cpp/include/pinjamlab/app/runner.hpp
        cpp/include/pinjamlab/app/seed.hpp
        cpp/include/pinjamlab/domain/equipment.hpp
        cpp/include/pinjamlab/domain/loan.hpp
        cpp/include/pinjamlab/domain/loan_error.hpp
        cpp/include/pinjamlab/domain/member.hpp
        cpp/include/pinjamlab/domain/result.hpp
        cpp/include/pinjamlab/io/csv_reader.hpp
        cpp/include/pinjamlab/io/report_writer.hpp
        cpp/include/pinjamlab/io/validator.hpp
        cpp/include/pinjamlab/service/database.hpp
        cpp/include/pinjamlab/service/loan_service.hpp
        cpp/include/pinjamlab/service/txn_guard.hpp
        cpp/tests/mini_catch.hpp
        cpp/tests/test_app.cpp
        cpp/tests/test_errors.cpp
        cpp/tests/test_raii.cpp
        cpp/tests/test_result.cpp)
