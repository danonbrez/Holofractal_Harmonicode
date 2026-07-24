cmake_minimum_required(VERSION 3.20)
project(hhs_gfcc_pass152 VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

get_filename_component(HHS_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../.." ABSOLUTE)

add_library(hhs_gfcc_static STATIC
    src/hhs_gfcc.c
    ${HHS_REPO_ROOT}/hhs_runtime/src/hhs_hash216.c
)
set_target_properties(hhs_gfcc_static PROPERTIES OUTPUT_NAME hhs_gfcc)
target_include_directories(hhs_gfcc_static PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${HHS_REPO_ROOT}/hhs_runtime/include
)

add_library(hhs_gfcc_shared SHARED
    src/hhs_gfcc.c
    ${HHS_REPO_ROOT}/hhs_runtime/src/hhs_hash216.c
)
set_target_properties(hhs_gfcc_shared PROPERTIES OUTPUT_NAME hhs_gfcc)
target_include_directories(hhs_gfcc_shared PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${HHS_REPO_ROOT}/hhs_runtime/include
)

add_executable(hhs-gfcc src/hhs_gfcc_cli.c)
target_link_libraries(hhs-gfcc PRIVATE hhs_gfcc_static)

add_executable(test_hhs_gfcc tests/test_hhs_gfcc.c)
target_link_libraries(test_hhs_gfcc PRIVATE hhs_gfcc_static)

enable_testing()
add_test(NAME hhs_gfcc_native COMMAND test_hhs_gfcc)

if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    foreach(target hhs_gfcc_static hhs_gfcc_shared hhs-gfcc test_hhs_gfcc)
        target_compile_options(${target} PRIVATE -Wall -Wextra -Werror)
    endforeach()
endif()

install(TARGETS hhs_gfcc_static hhs_gfcc_shared hhs-gfcc
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
install(FILES include/hhs_gfcc.h DESTINATION include)
