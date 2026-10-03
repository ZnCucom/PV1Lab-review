import json,shutil,zipfile
from pathlib import Path
import lab
R=lab.ROOT;N=lab.PROTECTED/'_reverse_work'/'reconstructed'/'native'
rid=lab.new_run();p,_=lab.run_record(rid);stage=R/'staging'/'source'/('vendor-'+rid);stage.mkdir()
files=[]
for rel in ('src/trt_vendor_msvc.cpp','include/recovered/trt_c_api.h'):
    source=lab.checked(N/rel);dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True)
    before=lab.sha(source);dest.write_bytes(source.read_bytes());lab.require(lab.sha(dest)==before,'source copy mismatch')
    files.append({'source':str(source),'destination':str(dest),'sha256':before})
archive=lab.PROTECTED/'_reverse_work'/'cache'/'cuda_nvcc_headers_12.9.86.zip'
meta=lab.read(R/'downloads'/'verified'/'redistrib_12.9.1.json')['cuda_nvcc']['windows-x86_64']
lab.require(lab.sha(lab.checked(archive))==meta['sha256'],'NVCC archive official hash mismatch')
target=R/'downloads'/'verified'/'cuda_nvcc-12.9.86.zip'
if not target.exists():
    with archive.open('rb') as a,target.open('xb') as b:shutil.copyfileobj(a,b,1024*1024)
nvcc=R/'tools'/'nvcc_headers';nvcc.mkdir(exist_ok=True)
with zipfile.ZipFile(target) as z:
    for i in z.infolist():
        if i.is_dir() or '/include/' not in i.filename:continue
        relative=i.filename.split('/include/',1)[1];dest=lab.below(nvcc/relative,nvcc);dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(z.read(i))
trt=R/'tools'/'tensorrt'/'TensorRT-10.10.0.31'
cuda=R/'tools'/'cudart'/'cuda_cudart-windows-x86_64-12.9.79-archive'
cmd=f'''@echo off
call "D:\\PV1Lab\\tools\\VS2022BuildTools\\VC\\Auxiliary\\Build\\vcvarsall.bat" amd64
if errorlevel 1 exit /b %errorlevel%
set TEMP={p / 'temp'}
set TMP={p / 'temp'}
cd /d "{p / 'build'}"
cl /nologo /Bv /LD /std:c++20 /EHsc /MT /O2 /I"{stage / 'include'}" /I"{trt / 'include'}" /I"{cuda / 'include'}" /I"{nvcc}" "{stage / 'src' / 'trt_vendor_msvc.cpp'}" /Fo"{p / 'build' / 'trt_vendor.obj'}" /link /OUT:"{p / 'build' / 'pv_trt_vendor.dll'}" /IMPLIB:"{p / 'build' / 'pv_trt_vendor.lib'}" "{trt / 'lib' / 'nvinfer_10.lib'}" "{cuda / 'lib' / 'x64' / 'cudart.lib'}"
exit /b %errorlevel%
'''
(R/'scripts'/'build_vendor.cmd').write_text(cmd,encoding='utf-8')
lab.save(R/'control'/'vendor_build.json',{'run_id':rid,'source_stage':str(stage),'sources':files,'kind':'REAL_MSVC_VENDOR_NO_MOCK_NO_SYNTAX_MACROS','nvcc_official_sha256':meta['sha256']})
print(rid)
