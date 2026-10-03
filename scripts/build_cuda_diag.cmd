@echo off
call "D:\PV1Lab\tools\VS2022BuildTools\VC\Auxiliary\Build\vcvarsall.bat" amd64
if errorlevel 1 exit /b %errorlevel%
set TEMP=D:\PV1Lab\runs\4a9b608de46e4a43964cb02af9574a83\temp
set TMP=%TEMP%
cd /d "D:\PV1Lab\runs\4a9b608de46e4a43964cb02af9574a83\build"
cl /nologo /std:c++20 /EHsc /MT /O2 /I"D:\PV1Lab\tools\tensorrt\TensorRT-10.10.0.31\include" /I"D:\PV1Lab\tools\cudart\cuda_cudart-windows-x86_64-12.9.79-archive\include" /I"D:\PV1Lab\tools\nvcc_headers" "D:\PV1Lab\scripts\cuda_trt_diag.cpp" /Fe:cuda_trt_diag.exe /Fo:cuda_trt_diag.obj /link "D:\PV1Lab\tools\tensorrt\TensorRT-10.10.0.31\lib\nvinfer_10.lib" "D:\PV1Lab\tools\cudart\cuda_cudart-windows-x86_64-12.9.79-archive\lib\x64\cudart.lib"
exit /b %errorlevel%
