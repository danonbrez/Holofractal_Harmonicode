cmake_minimum_required(VERSION 3.22.1)
project(hhs_pass145 C)
set(HHS_ROOT ${CMAKE_CURRENT_SOURCE_DIR}/../../../../../..)
add_library(hhs_pass145 SHARED
    hhs_pass145_jni.c
    ${HHS_ROOT}/hhs_runtime/c/hhs_runtime_abi.c
    ${HHS_ROOT}/hhs_runtime/src/hhs_hash216.c
)
target_include_directories(hhs_pass145 PRIVATE
    ${HHS_ROOT}/hhs_runtime/c
    ${HHS_ROOT}/hhs_runtime/include
)
target_compile_options(hhs_pass145 PRIVATE -O2 -Wall -Wextra -fvisibility=hidden)
find_library(log-lib log)
find_library(m-lib m)
target_link_libraries(hhs_pass145 ${log-lib} ${m-lib})
