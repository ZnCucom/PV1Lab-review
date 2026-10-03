import hashlib,json,shutil
from pathlib import Path
R=Path(r'D:\PV1Lab')
payload=R/'staging'/'owned-vendor-payload'
payload.mkdir(exist_ok=False)
build=R/'runs'/'87482c17836c48b4a4240b3ccd61fc21'/'build'
trt=R/'tools'/'tensorrt'/'TensorRT-10.10.0.31'/'lib'
files=[build/'vendor_runner.exe',build/'pv_trt_vendor.dll',trt/'nvinfer_10.dll',trt/'nvinfer_lean_10.dll',trt/'nvinfer_dispatch_10.dll',R/'tools'/'cudart'/'cuda_cudart-windows-x86_64-12.9.79-archive'/'bin'/'cudart64_12.dll',R/'runs'/'5161a7a3054442bc810f3522bf6fc52a'/'build'/'owned_affine.engine']
manifest=[]
for src in files:
    dst=payload/src.name
    shutil.copyfile(src,dst)
    digest=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
    h=digest(src);assert digest(dst)==h and src.stat().st_ino!=dst.stat().st_ino
    manifest.append({'path':str(dst),'sha256':h,'source':str(src)})
(R/'control'/'vendor_payload.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'payload':str(payload),'files':len(files)}))
