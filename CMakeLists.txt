cmake_minimum_required(VERSION 3.15)
project(ChessAI VERSION 2.0.0 LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler flags
if(MSVC)
    # MSVC flags
    add_compile_options(/W4 /O2 /GL /arch:AVX2 /std:c++17)
    add_link_options(/LTCG)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
else()
    # GCC/Clang flags
    add_compile_options(
        -Wall -Wextra -Wpedantic
        -O3 -march=native -flto
        -fno-exceptions  # Optional: disable exceptions for speed
    )
    add_link_options(-flto)
endif()

# Find Python and pybind11
# Use PYTHON_EXECUTABLE if provided, otherwise let CMake find it
if(DEFINED PYTHON_EXECUTABLE)
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}" CACHE FILEPATH "Python executable" FORCE)
endif()
find_package(Python 3.12 COMPONENTS Interpreter Development REQUIRED)

# Try to find pybind11 via Python
execute_process(
    COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
    OUTPUT_VARIABLE pybind11_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE pybind11_RESULT
)

if(pybind11_RESULT EQUAL 0 AND EXISTS "${pybind11_DIR}")
    message(STATUS "Found pybind11 at: ${pybind11_DIR}")
    set(pybind11_DIR "${pybind11_DIR}" CACHE PATH "Path to pybind11 CMake files")
    find_package(pybind11 CONFIG REQUIRED)
else()
    message(FATAL_ERROR "pybind11 not found. Install with: pip install pybind11")
endif()

# Engine source files
set(ENGINE_SOURCES
    src/engine_cpp/src/types.cpp
    src/engine_cpp/src/board.cpp
    src/engine_cpp/src/movegen.cpp
    src/engine_cpp/src/evaluation.cpp
    src/engine_cpp/src/transposition.cpp
    src/engine_cpp/src/search.cpp
    src/engine_cpp/src/bindings.cpp
)

# Create Python module
pybind11_add_module(chess_engine ${ENGINE_SOURCES})

# Include directories
target_include_directories(chess_engine PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/src/engine_cpp/include
)

# Platform-specific optimizations
if(UNIX AND NOT APPLE)
    target_link_options(chess_engine PRIVATE -flto)
endif()

# Install target
install(TARGETS chess_engine 
    LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/src
    RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/src
)

# Print configuration
message(STATUS "")
message(STATUS "Chess AI C++ Engine Configuration:")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  C++ compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "  C++ standard: C++${CMAKE_CXX_STANDARD}")
message(STATUS "  pybind11 version: ${pybind11_VERSION}")
message(STATUS "  Install directory: ${CMAKE_CURRENT_SOURCE_DIR}/src")
message(STATUS "")
