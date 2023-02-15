# -*- coding: utf-8 -*-
import os
import platform
import re
import shlex
import subprocess
import sys
from distutils.version import LooseVersion
from pathlib import Path
from typing import Any, Dict

from setuptools import Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name: str, sourcedir: str = "") -> None:
        super().__init__(name, sources=[])
        self.sourcedir = str(Path(sourcedir).resolve())


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " + ", ".join(e.name for e in self.extensions))

        cmake_version = LooseVersion(re.search(r"version\s*([\d.]+)", out.decode()).group(1))  # type: ignore
        if cmake_version < "3.10":
            raise RuntimeError("CMake >= 3.10 is required")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        # extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        extdir = os.path.abspath(os.path.join(os.path.dirname(self.get_ext_fullpath(ext.name)), ext.name))
        # required for auto-detection of auxiliary "native" libs
        if not extdir.endswith(os.path.sep):
            extdir += os.path.sep

        cmake_args = ["-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" + extdir, "-DPYTHON_EXECUTABLE=" + sys.executable]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        if platform.system() == "Windows":
            cmake_args += ["-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{}={}".format(cfg.upper(), extdir)]
            if sys.maxsize > 2**32:
                cmake_args += ["-A", "x64"]
            build_args += ["--", "/m"]
        else:
            cmake_args += ["-DCMAKE_BUILD_TYPE=" + cfg]
            build_args += ["--", "-j2"]
        cmake_user_args = os.environ.get("CMAKE_USER_ARGS", "")
        if cmake_user_args:
            cmake_args.extend(shlex.split(cmake_user_args))  # Provided in env variable
        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()  # pyright: ignore[reportGeneralTypeIssues]
        )
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        subprocess.check_call(["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env)
        subprocess.check_call(["cmake", "--build", "."] + build_args, cwd=self.build_temp)


def build(setup_kwargs: Dict[str, Any]) -> None:
    # cython_modules = cythonize(
    #     [
    #         Extension(
    #             "project.package.cython_extension",
    #             sources=["project/package/cython_extension.pyx"],
    #             # include_dirs=[get_numpy_include(), "."],
    #         )
    #     ]
    # )
    # cmake_modules = [CMakeExtension("project.package.pybind11_extension", sourcedir="project/package/pybind11_extension")]
    # ext_modules = cython_modules + cmake_modules
    ext_modules = [CMakeExtension("h264decoder")]
    # ext_modules = [Pybind11Extension("h264decoder", sorted(glob("src/*.cpp"))), CMakeExtension(f"h264decoder", sourcedir="src")]
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "cmdclass": dict(build_ext=CMakeBuild),
            "zip_safe": False,
        }
    )
