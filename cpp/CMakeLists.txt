cmake_minimum_required(VERSION 3.20)
project(infotainment VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Executável principal ─────────────────────────────────
add_executable(infotainment src/main.cpp)

target_include_directories(infotainment PRIVATE include)

# ── Flags de compilação ──────────────────────────────────
target_compile_options(infotainment PRIVATE
    $<$<CXX_COMPILER_ID:GNU,Clang>:-Wall -Wextra -Wpedantic>
    $<$<CXX_COMPILER_ID:MSVC>:/W4>
)
