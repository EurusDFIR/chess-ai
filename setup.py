import os
import sys
import subprocess
from pathlib import Path
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the extension")
        
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
        
        # CMake arguments
        cmake_args = [
            f'-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            '-DCMAKE_BUILD_TYPE=Release',
        ]
        
        # Build arguments
        build_args = ['--config', 'Release']
        
        # Platform-specific
        if sys.platform.startswith('win'):
            cmake_args += ['-G', 'Visual Studio 17 2022', '-A', 'x64']
            build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=Release']
            build_args += ['--', '-j4']
        
        # Build directory
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)
        
        # Run CMake
        print(f"Running CMake in {self.build_temp}")
        print(f"CMake args: {cmake_args}")
        
        subprocess.check_call(
            ['cmake', ext.sourcedir] + cmake_args, 
            cwd=self.build_temp
        )
        
        # Build
        print(f"Building with: cmake --build {self.build_temp}")
        subprocess.check_call(
            ['cmake', '--build', '.'] + build_args,
            cwd=self.build_temp
        )
        
        print("Build complete!")

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding='utf-8')

setup(
    name='chess-ai',
    version='2.0.0',
    author='Chess AI Team',
    description='Hybrid Python/C++ Chess AI with Advanced Search',
    long_description=long_description,
    long_description_content_type='text/markdown',
    
    # Python packages
    packages=find_packages(where='src', exclude=['engine_cpp', 'tests']),
    package_dir={'': 'src'},
    
    # C++ extension
    ext_modules=[CMakeExtension('chess_engine')],
    cmdclass={'build_ext': CMakeBuild},
    
    # Dependencies
    install_requires=[
        'pygame-ce>=2.5.0',
        'pygame-gui>=0.6.0',
        'python-chess>=1.10.0',
    ],
    
    # Build dependencies
    setup_requires=[
        'pybind11>=2.10.0',
    ],
    
    # Python version
    python_requires='>=3.8',
    
    zip_safe=False,
)