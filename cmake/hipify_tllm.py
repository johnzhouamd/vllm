#!/usr/bin/env python3

#
# A command line tool for running pytorch's hipify preprocessor on CUDA
# source files.
#
# See https://github.com/ROCm/hipify_torch
# and <torch install dir>/utils/hipify/hipify_python.py
#

import argparse
import os
import re

from torch.utils.hipify.hipify_python import hipify, get_hip_file_path, match_extensions

hipify_result = hipify(project_directory="/dockerx/vllm/csrc",
                       output_directory="/dockerx/vllm/csrc",
                       header_include_dirs=["/dockerx/vllm/csrc/tllm/include", "/dockerx/vllm/csrc/tllm"],
                       includes=["/dockerx/vllm/csrc/*"],
                       extra_files=["/dockerx/vllm/csrc/tllm/tensorrt_llm/kernels/samplingTopKKernels.cu"],
                       show_detailed=True,
                       is_pytorch_extension=True,
                       hipify_extra_files_only=False)

# delete pre-hipified files
for filepath in hipify_result:
    if hipify_result[filepath].status == "[ok]" and filepath != hipify_result[filepath].hipified_path:
        print(f"removing {filepath} due to it being hipified to {hipify_result[filepath].hipified_path}")
        os.remove(filepath)

LIB_HEADERS_REPLACE = [
    ("#include <cuda_bf16.h>", "#include <hip/hip_bf16.h>")
]
    

for (abs_dirpath, dirs, filenames) in os.walk('/dockerx/vllm/csrc/tllm/include/tensorrt_llm/', topdown=True):
    for filename in filenames:
        filepath = os.path.join(abs_dirpath, filename)
        if match_extensions(filepath, [".cu", ".cuh", ".c", ".cc", ".cpp", ".h", ".in", ".hpp", ".hip"]):
            with open(filepath, 'r') as file:
                filedata = file.read()
            
            includes_to_replace = [r for r in LIB_HEADERS_REPLACE]
            for line in filedata.split('\n'):
                if line.startswith("#include \"tensorrt_llm"):
                    include_path = line.split("\"")[1]
                    include_path_hipify_result = hipify_result.get("/dockerx/vllm/csrc/tllm/include/" + include_path, None)
                    if include_path_hipify_result is not None and include_path_hipify_result.status == "[ok]":
                        hipified_include_path = "tensorrt_llm" + include_path_hipify_result.hipified_path.split("tensorrt_llm")[-1]
                        includes_to_replace.append((f"#include \"{include_path}\"", f"#include \"{hipified_include_path}\""))
                    
                    include_path_hipify_result = hipify_result.get("/dockerx/vllm/csrc/tllm/" + include_path, None)
                    if include_path_hipify_result is not None and include_path_hipify_result.status == "[ok]":
                        hipified_include_path = "tensorrt_llm" + include_path_hipify_result.hipified_path.split("tensorrt_llm")[-1]
                        includes_to_replace.append((f"#include \"{include_path}\"", f"#include \"{hipified_include_path}\""))
            
            print(f"replacing includes in {filepath}:")
            for src, dst in includes_to_replace:
                print(f"    replacing {src} with {dst}")
                filedata = filedata.replace(src, dst)
            
            with open(filepath, 'w') as file:
                file.write(filedata)


for (abs_dirpath, dirs, filenames) in os.walk('/dockerx/vllm/csrc/tllm/tensorrt_llm/', topdown=True):
    for filename in filenames:
        filepath = os.path.join(abs_dirpath, filename)
        if match_extensions(filepath, [".cu", ".cuh", ".c", ".cc", ".cpp", ".h", ".in", ".hpp", ".hip"]):
            with open(filepath, 'r') as file:
                filedata = file.read()
            
            includes_to_replace = [r for r in LIB_HEADERS_REPLACE]
            for line in filedata.split('\n'):
                if line.startswith("#include \"tensorrt_llm"):
                    include_path = line.split("\"")[1]
                    include_path_hipify_result = hipify_result.get("/dockerx/vllm/csrc/tllm/include/" + include_path, None)
                    if include_path_hipify_result is not None and include_path_hipify_result.status == "[ok]":
                        hipified_include_path = "tensorrt_llm" + include_path_hipify_result.hipified_path.split("tensorrt_llm")[-1]
                        includes_to_replace.append((f"#include \"{include_path}\"", f"#include \"{hipified_include_path}\""))
                    
                    include_path_hipify_result = hipify_result.get("/dockerx/vllm/csrc/tllm/" + include_path, None)
                    if include_path_hipify_result is not None and include_path_hipify_result.status == "[ok]":
                        hipified_include_path = "tensorrt_llm" + include_path_hipify_result.hipified_path.split("tensorrt_llm")[-1]
                        includes_to_replace.append((f"#include \"{include_path}\"", f"#include \"{hipified_include_path}\""))
            
            print(f"replacing includes in {filepath}:")
            for src, dst in includes_to_replace:
                print(f"    replacing {src} with {dst}")
                filedata = filedata.replace(src, dst)
            
            with open(filepath, 'w') as file:
                file.write(filedata)
