# TensorRT 10.10 qualification

Official Windows CUDA12.9 archive: 1895944873 bytes, SHA256 `8243114e532987092413a160384ad8b4cc09edbf625766290511eb16c220486c`.
The digest identifies downloaded bytes; no separately published NVIDIA archive SHA256 was obtained. This is not represented as an official-hash match.
Official NVIDIA download link was followed; selected ZIP members passed CRC. Actual nvinfer libraries and trtexec Authenticode signatures are Valid/NVIDIA Corporation (tensorrt_signatures.json).
CUDA runtime12.9.79 came from the separate existing pinned official archive, copied independently; no original project runtime DLL was loaded.

`OWN_MODEL_RUNTIME_VERIFIED` for TensorRT10.10.0.31 Python API on this host.
Self-authored network `y=2*x+1` built a new engine, 24 frames passed, 3 independent runtime engine/context cycles, 3 invalid tensor-name rejections.
Engine SHA256 `e8a882f647c44e781db0707da3c6d678512801c46b8a55044d57b9cb34759ec4`; size 23764 bytes. Only this owned engine was deserialized.
All stream synchronization, device buffer frees and stream destruction returned success; contexts/engines/runtime released; Job Object active process count0.
Run: `5161a7a3054442bc810f3522bf6fc52a`. Detailed results in run/output/trt_results.json; own engine in run/build.

`MSVC_VENDOR_BRIDGE_NOT_BUILT`: Python bindings do not verify main project's own MSVC C ABI adapter.
No full CUDA Toolkit, new driver, system installation or global PATH change was needed for this owned runtime test.
No original EXE, business DLL, model, engine, licensed state, actual input device, game or activation service was executed/accessed.
This is host trusted-development validation, not sandbox GPU compatibility or original behavior equivalence.

Official references:
- https://developer.nvidia.com/tensorrt/download/10x (10.10 Windows CUDA12.0–12.9)
- https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/api/tensorrt-8x-to-10x-python-api.html
