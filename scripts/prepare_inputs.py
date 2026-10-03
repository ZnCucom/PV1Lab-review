"""One-time explicit non-sensitive inputs; no original code execution."""
import hashlib,json,os,shutil,sys,urllib.request,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import lab
R=lab.ROOT; P=lab.PROTECTED; N=P/'_reverse_work'/'reconstructed'/'native'
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'PV1Lab-environment-qualification'})
    with urllib.request.urlopen(req,timeout=50) as f: return f.read()
def main():
    w=lab.workspace(); w['source_path_confirmation']='USER_CONFIRMED'; w['main_source']=str(N); lab.save(R/'control'/'workspace.json',w)
    paths=[P/'_reverse_work'/'checkpoint.md',N/'checkpoint.md',N/'dependencies.lock.json',N/'CMakeLists.txt',
           N/'evidence'/'r24_gate199_contract'/'handoff.md',N/'evidence'/'r21_vendor31'/'contract.md',N/'evidence'/'r21_vendor71'/'contract.md',
           P/'_reverse_work'/'startup_flow.md',N/'third_party'/'tensorrt_headers'/'include'/'NvInferVersion.h']
    sources=['src/trt_vendor_msvc.cpp','include/pv_trt_c_api.h']
    for name in sources:
        if (N/name).is_file(): paths.append(N/name)
    paths.append(P/'Pv1.exe')
    records=[]; files=[]
    for src in paths:
        lab.checked(src); digest=lab.sha(src)
        records.append({'path':str(src),'sha256':digest,'size':src.stat().st_size})
        if src==P/'Pv1.exe': dest=R/'staging'/'original'/'static-only-01'/'Pv1.exe'
        elif src in [N/x for x in sources] or src==N/'CMakeLists.txt' or src.name=='NvInferVersion.h':
            dest=R/'staging'/'source'/'source197-readonly-excerpt'/src.relative_to(N)
        else: continue
        dest.parent.mkdir(parents=True,exist_ok=True)
        files.append({'source':str(src),'destination':str(dest),'sha256':digest,'classification':'reviewed source excerpt' if src!=P/'Pv1.exe' else 'untrusted static input; never execute'})
    lab.save(R/'baselines'/'protected_inputs.json',records)
    lab.save(R/'control'/'input_manifest.json',{'files':files,'excluded':'all other files; no models, license state, configs, tokens, dumps or original DLLs'})
    lab.prepare('input_manifest.json')
    lock=lab.read(N/'dependencies.lock.json'); tools=[]
    for name,source,folder in [
        ('llvm-mingw-20260922-ucrt-x86_64.zip',P/'_reverse_work'/'cache'/'llvm-mingw-20260922-ucrt-x86_64.zip','llvm'),
        ('cuda_nvrtc-windows-x86_64-12.9.86-archive.zip',P/'_reverse_work'/'tools'/'nvrtc_12.9.86'/'official.zip','nvrtc'),
        ('microsoft.ml.onnxruntime.directml.1.23.0.nupkg',P/'_reverse_work'/'cache'/'microsoft.ml.onnxruntime.directml.1.23.0.nupkg','ort'),
        ('microsoft.ai.directml.1.15.4.nupkg',P/'_reverse_work'/'cache'/'microsoft.ai.directml.1.15.4.nupkg','directml')]:
        item=next(x for x in lock['packages'] if x['name']==name)
        lab.checked(source); digest=lab.sha(source)
        lab.require(digest==item['sha256'],'existing archive mismatch; preserved '+name)
        dest=R/'downloads'/'verified'/name
        with open(source,'rb') as a,open(dest,'xb') as b: shutil.copyfileobj(a,b,1024*1024)
        lab.require(lab.sha(dest)==digest,'copy mismatch')
        out=R/'tools'/folder; out.mkdir()
        with zipfile.ZipFile(dest) as z:
            for e in z.infolist():
                parts=Path(e.filename.replace('/',os.sep)).parts
                lab.require(not e.filename.startswith(('/','\\')) and not any(x in ('.','..') or ':' in x for x in parts),'archive traversal')
                lab.require((e.external_attr>>16)&0o170000 !=0o120000,'archive symlink')
                if e.is_dir(): continue
                # DirectML/ORT only Windows x64 payload; compiler and NVRTC package as distributed.
                if folder=='directml' and e.filename!='bin/x64-win/DirectML.dll': continue
                if folder=='ort' and not (e.filename.startswith('runtimes/win-x64/native/') or e.filename.startswith('build/native/include/')): continue
                target=out.joinpath(*parts); lab.below(target,out); target.parent.mkdir(parents=True,exist_ok=True)
                with z.open(e) as a,open(target,'xb') as b: shutil.copyfileobj(a,b,1024*1024)
        tools.append({**item,'source':str(source),'local':str(dest),'size':dest.stat().st_size,'observed_sha256':digest,'verification':'MATCH_EXISTING_PIN; independent provenance/signature checked separately'})
        lab.save(R/'control'/'tool_acquisition.json',tools)
        print('prepared '+name,flush=True)
    # Recheck against NVIDIA current official redistributable metadata, independent of old pin.
    try:
        url='https://developer.download.nvidia.com/compute/cuda/redist/redistrib_12.9.1.json'
        raw=fetch(url); (R/'downloads'/'verified'/'redistrib_12.9.1.json').write_bytes(raw)
        meta=json.loads(raw)['cuda_nvrtc']['windows-x86_64']; rec={'url':url,'nvrtc':meta}
        rec['match']=meta['sha256']==next(t for t in tools if t['kind']=='nvrtc')['observed_sha256']
        lab.save(R/'reports'/'nvrtc_official_verification.json',rec)
    except Exception as e: lab.save(R/'reports'/'nvrtc_official_verification.json',{'error':str(e)})
    print('input and dependency preparation complete')
if __name__=='__main__': main()
