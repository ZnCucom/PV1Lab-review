import json,shutil,zipfile
from pathlib import Path
import lab
R=lab.ROOT
p=R/'downloads'/'verified'/'TensorRT-10.10.0.31.Windows.win10.cuda-12.9.zip'
lab.require(p.stat().st_size==1895944873,'TRT download incomplete')
result={'version':'10.10.0.31','url':'https://developer.download.nvidia.com/compute/machine-learning/tensorrt/10.10.0/zip/TensorRT-10.10.0.31.Windows.win10.cuda-12.9.zip','size':p.stat().st_size,'sha256':lab.sha(p),'official_published_sha256':'NOT_OBTAINED; local digest is identification only','files':[]}
root=R/'tools'/'tensorrt'; root.mkdir(exist_ok=True)
with zipfile.ZipFile(p) as z:
    members=z.infolist()
    selected=[e for e in members if not e.is_dir() and ('/lib/' in e.filename or '/bin/' in e.filename or '/include/' in e.filename or ('/python/' in e.filename and 'cp312' in e.filename) or e.filename.endswith('LICENSE'))]
    for e in selected:
        parts=Path(e.filename).parts
        lab.require(not e.filename.startswith(('/','\\')) and all(x not in ('.','..') and ':' not in x for x in parts),'zip traversal')
        lab.require((e.external_attr>>16)&0o170000 !=0o120000,'zip symlink')
        dest=root.joinpath(*parts); lab.below(dest,root);dest.parent.mkdir(parents=True,exist_ok=True)
        with z.open(e) as a,open(dest,'xb') as b: shutil.copyfileobj(a,b,1024*1024)
        result['files'].append({'path':str(dest),'size':dest.stat().st_size,'sha256':lab.sha(dest)})
result['selected_zip_crc']='PASS (read all selected members)'
lab.save(R/'control'/'tensorrt_acquisition.json',result)
# Official CUDA runtime headers/runtime already pinned by main project; independent byte copy.
src=lab.PROTECTED/'_reverse_work'/'cache'/'r19_official_cudart_reverify.zip'
expected='179e9c43b0735ffe67207b3da556eb5a0c50f3047961882b7657d3b822d34ef8'
lab.require(lab.sha(lab.checked(src))==expected,'cudart archive mismatch')
dest=R/'downloads'/'verified'/'cuda_cudart-12.9.79.zip'
with open(src,'rb') as a,open(dest,'xb') as b: shutil.copyfileobj(a,b)
with zipfile.ZipFile(dest) as z:
    for e in z.infolist():
        if e.is_dir(): continue
        parts=Path(e.filename).parts;lab.require(not e.filename.startswith(('/','\\')) and all(x not in ('.','..') and ':' not in x for x in parts),'cudart traversal')
        target=R/'tools'/'cudart'/Path(e.filename);lab.below(target,R/'tools'/'cudart');target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(z.read(e))
print(json.dumps({'trt_files':len(result['files']),'size':result['size'],'sha256':result['sha256']}))
