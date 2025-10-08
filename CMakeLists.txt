cmake_minimum_required(VERSION 3.15)
project(chess_engine)

# C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Add pybind11
add_subdirectory(pybind11)

# Source files
set(SOURCES
    src/engine_cpp/src/board.cpp
    src/engine_cpp/src/movegen.cpp
    src/engine_cpp/src/evaluation.cpp
    src/engine_cpp/src/search.cpp
    src/engine_cpp/src/transposition.cpp
    src/engine_cpp/src/types.cpp
    src/engine_cpp/src/bindings.cpp
)

# Create Python module
pybind11_add_module(chess_engine ${SOURCES})

# Include directories
target_include_directories(chess_engine PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/src/engine_cpp/include
)

# Compiler optimizations
if(MSVC)
    target_compile_options(chess_engine PRIVATE /O2 /Oi /GL /fp:fast)
    target_link_options(chess_engine PRIVATE /LTCG)
else()
    target_compile_options(chess_engine PRIVATE -O3 -march=native -flto)
    target_link_options(chess_engine PRIVATE -flto)
endif()

# Output directory
set_target_properties(chess_engine PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src
)
