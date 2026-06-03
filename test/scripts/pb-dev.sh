#!/bin/bash

set -Eeuo pipefail

PROJECT="cppsoa-test"
BUILD_ROOT="$HOME/scratch/$PROJECT/build"
BUILD_DIR="$BUILD_ROOT/build/Release"

cmake_configure() {
    set +Eeuo pipefail
    . "$BUILD_DIR/generators/conanbuild.sh"
    set -Eeuo pipefail

    cmake -S . -B "$BUILD_DIR" \
        -DCMAKE_CXX_FLAGS="-g3 -fno-omit-frame-pointer -Wall -Wextra" \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
        -DCMAKE_TOOLCHAIN_FILE="generators/conan_toolchain.cmake"
}

cmake_build() {
    set +Eeuo pipefail
    . "$BUILD_DIR/generators/conanbuild.sh"
    set -Eeuo pipefail

    if [[ "idl/activity.json5" -nt "include/activity_data.hpp" ]]; then
        cppsoa -i "idl/activity.json5" -o "include/activity_data.hpp"
    fi

    cmake --build "$BUILD_DIR" --parallel
}

run_setup() {
    rm -rf "$BUILD_DIR"
    rm -f compile_commands.json

    conan install . --build=missing --output-folder="$BUILD_ROOT"

    ln -s "$BUILD_DIR/compile_commands.json"

    cmake_configure
    cmake_build
}

run_test_activity() {
    cmake_build

    set +Eeuo pipefail
    . "$BUILD_DIR/generators/conanrun.sh"
    set -Eeuo pipefail

    PATH="$BUILD_DIR:$PATH"

    which test_activity
    TEST_INPUT_FILE="$HOME/data/synpop-make-network/dp_2_4_1-usa_840-wy/adult/wy_adult_activity_location_assignment_day.csv-1-of-60"
    TEST_OUTPUT_FILE="$HOME/scratch/$PROJECT/wy_adult_activity_location_assignment_day.csv-1-of-60"
    TEST_OUTPUT_FILE_SORTED="$HOME/scratch/$PROJECT/wy_adult_activity_location_assignment_day.csv-1-of-60_SORTED"
    TEST_OUTPUT_FILE_PAR_SORTED="$HOME/scratch/$PROJECT/wy_adult_activity_location_assignment_day.csv-1-of-60_PAR_SORTED"

    set -x

    test_activity "$TEST_INPUT_FILE" "$TEST_OUTPUT_FILE" "$TEST_OUTPUT_FILE_SORTED" "$TEST_OUTPUT_FILE_PAR_SORTED"

    wc -l "$TEST_INPUT_FILE" "$TEST_OUTPUT_FILE" "$TEST_OUTPUT_FILE_SORTED" "$TEST_OUTPUT_FILE_PAR_SORTED"
    md5sum "$TEST_INPUT_FILE" "$TEST_OUTPUT_FILE" "$TEST_OUTPUT_FILE_SORTED" "$TEST_OUTPUT_FILE_PAR_SORTED"
}

show_help() {
    echo "Usage: $0 (help | command)"
}

if [[ "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
elif [[ $(type -t "run_${1}") == function ]]; then
    fn="run_${1}"
    shift
    $fn "$@"
else
    echo "Unknown command: $1"
fi
