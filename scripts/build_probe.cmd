@echo off
call "D:\PV1Lab\tools\VS2022BuildTools\VC\Auxiliary\Build\vcvarsall.bat" amd64
if errorlevel 1 exit /b %errorlevel%
set TEMP=D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\temp
set TMP=%TEMP%
cd /d "D:\PV1Lab\runs\87482c17836c48b4a4240b3ccd61fc21\build"
cl /nologo /std:c++20 /EHsc /MT /O2 "D:\PV1Lab\scripts\isolation_probe.cpp" /Fe:isolation_probe.exe /Fo:isolation_probe.obj
exit /b %errorlevel%
