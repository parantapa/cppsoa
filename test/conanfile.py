# type: ignore
from conan import ConanFile
from conan.tools.cmake import cmake_layout, CMakeDeps, CMakeToolchain


class CppSoaTest(ConanFile):
    name = "cppsoa-test"
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        cmake_layout(self)

    def requirements(self):
        self.requires("fmt/12.1.0")
        self.requires("arrow/24.0.0")
        self.requires("taskflow/4.0.0.pci")

    def generate(self):
        cmake = CMakeDeps(self)
        cmake.generate()

        toolchain = CMakeToolchain(self)
        toolchain.generate()
