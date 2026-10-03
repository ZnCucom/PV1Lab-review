@echo off
call "D:\PV1Lab\tools\VS2022BuildTools\VC\Auxiliary\Build\vcvarsall.bat" amd64
if errorlevel 1 exit /b %errorlevel%
set TEMP=D:\PV1Lab\runs\4a9b608de46e4a43964cb02af9574a83\temp
set TMP=%TEMP%
cd /d "D:\PV1Lab\runs\4a9b608de46e4a43964cb02af9574a83\build"
cl /nologo /std:c++20 /EHsc /MT /O2 "D:\PV1Lab\scripts\peripheral_probe.cpp" /Fe:peripheral_probe.exe /Fo:peripheral_probe.obj /link /MANIFEST:EMBED /MANIFESTUAC:"level='asInvoker' uiAccess='false'"
exit /b %errorlevel%

