cmake_minimum_required(VERSION 3.16)
project(hhs_pass174_harmonic_retrieval_runtime C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(hhs_pass174_runtime STATIC
    src/hhs_pass174_runtime.c
    ../hhs_pass160_validated_transition_runtime/src/hhs_pass160_runtime.c
    ../../hhs_runtime/src/hhs_hash216.c
)

target_include_directories(hhs_pass174_runtime PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../hhs_pass160_validated_transition_runtime/include
    ${CMAKE_CURRENT_SOURCE_DIR}/../../hhs_runtime/include
)

if(MSVC)
    target_compile_options(hhs_pass174_runtime PRIVATE /W4 /WX)
else()
    target_compile_options(hhs_pass174_runtime PRIVATE
        -Wall -Wextra -Wpedantic -Werror
        -Wconversion -Wshadow -Wstrict-prototypes
    )
endif()

add_executable(test_pass174 tests/test_pass174.c)
target_link_libraries(test_pass174 PRIVATE hhs_pass174_runtime)

enable_testing()
add_test(NAME pass174_native COMMAND test_pass174)
