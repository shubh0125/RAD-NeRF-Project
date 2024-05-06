import os
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension

_src_path = os.path.dirname(os.path.abspath(file))

# Define the CUDA include path based on the location found
cuda_include_path = '/usr/local/cuda-12.2/targets/x86_64-linux/include'

nvcc_flags = [
    '-O3', '-std=c++17',  # Update this to C++17
    '-U_CUDA_NO_HALF_OPERATORS', '-UCUDA_NO_HALF_CONVERSIONS', '-UCUDA_NO_HALF2_OPERATORS_',
    '-use_fast_math'
]



c_flags = ['-O3', '-std=c++17']  




setup(
    name='shencoder',  # Package name, import this to use Python API
    ext_modules=[
        CUDAExtension(
            name='_shencoder',  # Extension name, import this to use CUDA API
            sources=[os.path.join(_src_path, 'src', f) for f in [
                'shencoder.cu',  # CUDA source file for shencoder
                'bindings.cpp',  # C++ source file for bindings
            ]],
            include_dirs=[cuda_include_path],  # Ensure this points to the correct CUDA include directory
            extra_compile_args={
                'cxx': c_flags,
                'nvcc': nvcc_flags,
            }
        ),
    ],
    cmdclass={
        'build_ext': BuildExtension,
        }
)
