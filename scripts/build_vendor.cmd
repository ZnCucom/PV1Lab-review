@echo off
call "D:\PV1Lab\tools\VS2022BuildTools\VC\Auxiliary\Build\vcvarsall.bat" amd64
if errorlevel 1 exit /b %errorlevel%
set TEMP=D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\temp
set TMP=D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\temp
cd /d "D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\build"
cl /nologo /Bv /LD /std:c++20 /EHsc /MT /O2 /I"D:\PV1Lab\staging\source\vendor-87482c17836c48b4a4240b3ccd61fc21\include" /I"D:\PV1Lab\tools\tensorrt\TensorRT-10.10.0.31\include" /I"D:\PV1Lab\tools\cudart\cuda_cudart-windows-x86_64-12.9.79-archive\include" /I"D:\PV1Lab\tools\nvcc_headers" "D:\PV1Lab\staging\source\vendor-87482c17836c48b4a4240b3ccd61fc21\src\trt_vendor_msvc.cpp" /Fo"D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\build\trt_vendor.obj" /link /OUT:"D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\build\pv_trt_vendor.dll" /IMPLIB:"D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\build\pv_trt_vendor.lib" "D:\PV1Lab\tools\tensorrt\TensorRT-10.10.0.31\lib\nvinfer_10.lib" "D:\PV1Lab\tools\cudart\cuda_cudart-windows-x86_64-12.9.79-archive\lib\x64\cudart.lib"
exit /b %errorlevel%
