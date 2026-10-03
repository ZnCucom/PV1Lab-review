import datetime,json,subprocess
from pathlib import Path
import lab
R=lab.ROOT
rid=lab.read(R/'control'/'trt_run.json')['run_id'];p,record=lab.run_record(rid);lab.idle(record)
trt=lab.read(p/'output'/'trt_results.json');lab.require(trt['status']=='PASS','TRT test not passed')
lab.save(R/'reports'/'own_trt_results.json',trt)
acq=lab.read(R/'control'/'tensorrt_acquisition.json')
text=f'''# TensorRT 10.10 qualification

Official Windows CUDA12.9 archive: {acq['size']} bytes, SHA256 `{acq['sha256']}`.
The digest identifies downloaded bytes; no separately published NVIDIA archive SHA256 was obtained. This is not represented as an official-hash match.
Official NVIDIA download link was followed; selected ZIP members passed CRC. Actual nvinfer libraries and trtexec Authenticode signatures are Valid/NVIDIA Corporation (tensorrt_signatures.json).
CUDA runtime12.9.79 came from the separate existing pinned official archive, copied independently; no original project runtime DLL was loaded.

`OWN_MODEL_RUNTIME_VERIFIED` for TensorRT10.10.0.31 Python API on this host.
Self-authored network `y=2*x+1` built a new engine, {trt['frames']} frames passed, {trt['cycles']} independent runtime engine/context cycles, {trt['invalid_tensor_name_rejected']} invalid tensor-name rejections.
Engine SHA256 `{trt['engine_sha256']}`; size {trt['engine_bytes']} bytes. Only this owned engine was deserialized.
All stream synchronization, device buffer frees and stream destruction returned success; contexts/engines/runtime released; Job Object active process count0.
Run: `{rid}`. Detailed results in run/output/trt_results.json; own engine in run/build.

`MSVC_VENDOR_BRIDGE_NOT_BUILT`: Python bindings do not verify main project's own MSVC C ABI adapter.
No full CUDA Toolkit, new driver, system installation or global PATH change was needed for this owned runtime test.
No original EXE, business DLL, model, engine, licensed state, actual input device, game or activation service was executed/accessed.
This is host trusted-development validation, not sandbox GPU compatibility or original behavior equivalence.

Official references:
- https://developer.nvidia.com/tensorrt/download/10x (10.10 Windows CUDA12.0–12.9)
- https://docs.nvidia.com/deeplearning/tensorrt/10.x.x/api/tensorrt-8x-to-10x-python-api.html
'''
(R/'reports'/'tensorrt_validation.md').write_text(text,encoding='utf-8')
# Pin direct test sources/dependencies for future runs, without hashing any sensitive input.
reg=lab.read(R/'control'/'trusted_tests.json')
for name in ('own_gpu','own_trt'):
    deps=[]
    if name=='own_gpu':
        candidates=[R/'scripts'/'own_dml.cpp',*list((R/'tools'/'nvrtc').rglob('*.dll')),*list((R/'tools'/'ort'/'runtimes'/'win-x64'/'native').glob('*.dll')),*list((R/'tools'/'directml').rglob('*.dll'))]
    else:
        candidates=[*list((R/'tools'/'tensorrt'/'TensorRT-10.10.0.31'/'lib').glob('*.dll')),*list((R/'tools'/'trt_python'/'tensorrt').glob('*.py')),*list((R/'tools'/'trt_python'/'tensorrt').glob('*.pyd')),*list((R/'tools'/'cudart').rglob('*.dll'))]
    for file in candidates: deps.append({'path':str(file),'sha256':lab.sha(lab.checked(file))})
    reg[name]['dependencies']=deps
lab.save(R/'control'/'trusted_tests.json',reg)
# Current valid no-license GPU baseline, ordinary files only.
gpu=lab.read(R/'control'/'gpu_run.json')['run_id']
snapshot=lab.snapshot(gpu)
lab.save(R/'control'/'clean_no_license_baseline.json',{'run_id':gpu,**snapshot,'scope':'ORDINARY_FILES_ONLY_NO_REGISTRY','sensitivity':'CLEAN_NO_LICENSE'})
# Confirm exports use schema-only content; no originals, arbitrary logs or source bundles.
export=lab.export_summary()
lab.save(R/'control'/'latest_export.json',export)
state=lab.read(R/'control'/'readiness.json')
state.update(L03='OWN_MODEL_RUNTIME_VERIFIED: CUDA/CPU/DirectML/TensorRT10.10; MSVC_ABI_PENDING')
lab.save(R/'control'/'readiness.json',state)
for name in ('LAB_README.md','reports/toolchain_validation.md','control/checkpoint.md'):
    f=R/name
    with f.open('a',encoding='utf-8') as out: out.write('\nTensorRT追加验收：官方10.10.0.31已在自建网络/engine上通过24帧、3次周期和错误输入测试；详见 reports/tensorrt_validation.md。MSVC vendor bridge仍待安装后编译。\n')
# Concrete request checkpoint: no install launched and no approval inferred.
lab.save(R/'control'/'system_action_request.json',{'status':'PREPARED_NOT_REQUESTED','components':[
 {'name':'Sandboxie Plus1.18.5','installer':str(R/'downloads'/'verified'/'Sandboxie-Plus-x64-v1.18.5.exe'),'system_scope':['SbieDrv kernel driver','SbieSvc service','installation/configuration records; possible reboot decided by user'],'purpose':'owned canary isolation qualification only'},
 {'name':'Visual Studio2022 Build Tools','installer':str(R/'downloads'/'verified'/'vs_buildtools.exe'),'components':['Microsoft.VisualStudio.Component.VC.Tools.x86.x64','Microsoft.VisualStudio.Component.Windows11SDK.26100'],'system_scope':['Visual Studio Installer','MSVC/CRT/Windows SDK','ProgramData caches','installation registry'],'purpose':'build main-source excerpt vendor ABI in lab only'}],
 'requires_user':'User completes UAC/system installation; this agent will not auto-elevate. No original PV1 launch or activation approval is included.'})
print(json.dumps({'trt_status':trt['status'],'baseline':snapshot,'export':export},indent=2))
