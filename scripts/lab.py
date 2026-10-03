"""PV1Lab trusted-test manager. Never launches the original application.
Windows NTFS only. This is an operational guard, not a security sandbox.
"""
import argparse, contextlib, ctypes as C, hashlib, json, os, re, subprocess, sys, time, uuid
from ctypes import wintypes as W
from pathlib import Path

ROOT = Path(r'D:\PV1Lab')
PROTECTED = Path(r'D:\Pv1260909')
K = C.WinDLL('kernel32', use_last_error=True)
INVALID = C.c_void_p(-1).value
K.CreateFileW.argtypes = [W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE]
K.CreateFileW.restype = W.HANDLE
K.CloseHandle.argtypes = [W.HANDLE]
K.GetFinalPathNameByHandleW.argtypes = [W.HANDLE,W.LPWSTR,W.DWORD,W.DWORD]
K.SetFileInformationByHandle.argtypes = [W.HANDLE,C.c_int,C.c_void_p,W.DWORD]
K.GetFileInformationByHandle.argtypes = [W.HANDLE,C.c_void_p]
K.ReadFile.argtypes=[W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p]

class Info(C.Structure):
    _fields_ = [('attr',W.DWORD),('created',W.FILETIME),('accessed',W.FILETIME),
                ('written',W.FILETIME),('volume',W.DWORD),('sizehi',W.DWORD),
                ('sizelo',W.DWORD),('links',W.DWORD),('indexhi',W.DWORD),('indexlo',W.DWORD)]
class Streams(C.Structure):
    _fields_=[('size',C.c_longlong),('name',W.WCHAR*296)]
K.FindFirstStreamW.argtypes=[W.LPCWSTR,C.c_int,C.c_void_p,W.DWORD]
K.FindFirstStreamW.restype=W.HANDLE
K.FindNextStreamW.argtypes=[W.HANDLE,C.c_void_p]
K.FindClose.argtypes=[W.HANDLE]

def require(ok, why):
    if not ok: raise RuntimeError(why)
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
    p=Path(p); checked(p.parent)
    if p.exists(): checked(p)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
    with open(p,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def lexical(p):
    s=str(p)
    require(bool(re.fullmatch(r'[A-Za-z]:\\[^:*?<>|\x00]*',s)), 'unsupported absolute path')
    require('/' not in s and '~' not in s, 'short/alternate path rejected')
    q=Path(s)
    for part in s[3:].split('\\'):
        require(part not in ('','.','..') and not part.endswith((' ','.')), 'ambiguous component')
        require(not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[0-9]|LPT[0-9])(?:\..*)?',part), 'device name')
    return q
def below(p,base):
    p=lexical(p); base=lexical(base)
    require(p != base and base in p.parents, 'path outside registered parent')
    return p
def checked(p):
    p=lexical(p)
    for part in reversed([p,*list(p.parents)[:-1]]):
        st=part.lstat()
        require(not (st.st_file_attributes & 0x400), 'reparse/link rejected')
        if part.is_file(): require(st.st_nlink==1,'hardlink rejected')
    return p
def workspace():
    checked(ROOT/'control'/'workspace.json')
    w=read(ROOT/'control'/'workspace.json')
    require(Path(w['root'])==ROOT,'wrong workspace root')
    uuid.UUID(w['workspace_id']); return w
def identifier(s):
    require(bool(re.fullmatch(r'[0-9a-f]{32}',s)), 'invalid run/snapshot ID'); return s
def registry():
    p=ROOT/'control'/'runs.json'
    return read(checked(p)) if p.exists() else {}

@contextlib.contextmanager
def locked_tree(p, delete=False):
    """Pin ancestors/objects against rename, reject links, ADS and changed identities.
    Delete through these same handles, never a second path-based delete operation.
    New unlisted children cause directory deletion to fail and preserve the remainder.
    """
    p=checked(p); below(p,ROOT); held=[]; objects=[]
    def lock(q,remove=False):
        st=q.lstat(); flags=0x02000000|0x00200000
        h=K.CreateFileW(str(q),0x80|(0x10000 if remove else 0)|(0x80000000 if q.is_file() else 0),1,None,3,flags,None)
        if h==INVALID: raise C.WinError(C.get_last_error())
        held.append(h); info=Info()
        require(K.GetFileInformationByHandle(h,C.byref(info)), 'file information failed')
        require(not(info.attr&0x400),'reparse rejected after open')
        if not (info.attr&0x10): require(info.links==1,'hardlink after open')
        b=C.create_unicode_buffer(32768)
        require(K.GetFinalPathNameByHandleW(h,b,len(b),0)>0,'final path failed')
        require(b.value.casefold()==('\\\\?\\'+str(q)).casefold(),'final object path mismatch')
        require(q.stat().st_ino==st.st_ino,'object changed during lock')
        stream=Streams(); sh=K.FindFirstStreamW(str(q),0,C.byref(stream),0)
        if sh!=INVALID:
            try:
                while True:
                    require(stream.name=='::$DATA','alternate data stream rejected')
                    if not K.FindNextStreamW(sh,C.byref(stream)): break
            finally: K.FindClose(sh)
        else: require(C.get_last_error() in (38,),'stream enumeration failed')
        return h
    try:
        for a in reversed(list(p.parents)[:-1]): lock(a)
        def visit(q):
            h=lock(q,delete); objects.append((q,h))
            if q.is_dir():
                for child in sorted(q.iterdir()): visit(child)
        visit(p)
        def release(h):
            K.CloseHandle(h); held.remove(h)
        yield objects,release
    finally:
        for h in reversed(held): K.CloseHandle(h)

def new_run():
    w=workspace(); rid=uuid.uuid4().hex; p=ROOT/'runs'/rid; checked(p.parent)
    p.mkdir()
    for n in ('build','temp','output'): (p/n).mkdir()
    marker={'workspace_id':w['workspace_id'],'run_id':rid,'sensitivity':'CLEAN_NO_LICENSE'}
    save(p/'run.json',marker)
    reg=registry(); reg[rid]={**marker,'path':str(p),'inode':p.stat().st_ino,'state':'IDLE','processes':[]}
    save(ROOT/'control'/'runs.json',reg); return rid
def run_record(rid):
    identifier(rid); w=workspace(); reg=registry(); require(rid in reg,'unregistered run')
    r=reg[rid]; require(r['state']!='DELETED','deleted run')
    p=below(r['path'],ROOT/'runs'); require(p==ROOT/'runs'/rid,'run path mismatch')
    checked(p); require(p.stat().st_ino==r['inode'],'run directory replaced')
    require(read(checked(p/'run.json'))=={k:r[k] for k in ('workspace_id','run_id','sensitivity')},'run ownership mismatch')
    require(r['workspace_id']==w['workspace_id'],'wrong workspace ID')
    return p,r
def idle(r): require(r['state']=='IDLE','active/unresolved process ownership; preserve run')
def preview(rid):
    p,r=run_record(rid); idle(r)
    with locked_tree(p) as (rows,_):
        return [{'path':str(q),'directory':q.is_dir(),'bytes':0 if q.is_dir() else q.stat().st_size} for q,h in rows]
def clean(rid):
    p,r=run_record(rid); idle(r); preview(rid)
    with locked_tree(p,True) as (rows,release):
        idle(registry()[rid])
        mh=next(h for q,h in rows if q==p/'run.json')
        buf=C.create_string_buffer(4096); count=W.DWORD()
        require(K.ReadFile(mh,buf,len(buf),C.byref(count),None),'locked marker read failed')
        require(json.loads(buf.raw[:count.value])=={k:r[k] for k in ('workspace_id','run_id','sensitivity')},'locked marker mismatch')
        for q,h in reversed(rows):
            flag=W.BOOL(True)
            if not K.SetFileInformationByHandle(h,4,C.byref(flag),C.sizeof(flag)): raise C.WinError(C.get_last_error())
            release(h)
    reg=registry(); reg[rid]['state']='DELETED'; save(ROOT/'control'/'runs.json',reg)
    return {'deleted_run':rid}
def snapshot(rid):
    p,r=run_record(rid); idle(r); sid=uuid.uuid4().hex
    dest=ROOT/'baselines'/sid; checked(dest.parent); dest.mkdir(); manifest=[]
    with locked_tree(p) as (rows,_):
        for q,h in rows:
            rel=q.relative_to(p)
            if q.is_dir(): (dest/rel).mkdir(exist_ok=True)
            else:
                (dest/rel).write_bytes(q.read_bytes()); manifest.append({'path':str(rel),'sha256':sha(dest/rel)})
    save(dest/'snapshot.json',{'workspace_id':workspace()['workspace_id'],'source_run':rid,'files':manifest,'kind':'ORDINARY_FILES_ONLY_NO_REGISTRY'})
    return {'snapshot_id':sid}
def restore(rid,sid):
    p,r=run_record(rid); idle(r); identifier(sid)
    src=checked(ROOT/'baselines'/sid); meta=read(checked(src/'snapshot.json'))
    require(meta['workspace_id']==workspace()['workspace_id'],'snapshot workspace mismatch')
    require(meta['source_run']==rid,'snapshot run mismatch')
    with locked_tree(src):
        for f in meta['files']:
            q=below(src/f['path'],src); require(sha(checked(q))==f['sha256'],'baseline missing or changed')
        # Preserve current registered run as another ordinary baseline before replacement.
        backup=snapshot(rid)
        clean(rid)
        checked(p.parent); p.mkdir()
        for f in meta['files']:
            dest=below(p/f['path'],p); dest.parent.mkdir(parents=True,exist_ok=True)
            checked(dest.parent); dest.write_bytes((src/f['path']).read_bytes())
        for n in ('build','temp','output'): (p/n).mkdir(exist_ok=True)
    reg=registry(); reg[rid].update(state='IDLE',inode=p.stat().st_ino); save(ROOT/'control'/'runs.json',reg)
    return {'restored':rid,'snapshot':sid,'pre_restore_backup':backup,'scope':'ordinary files, no registry'}

class SI(C.Structure):
    _fields_=[('cb',W.DWORD),('reserved',W.LPWSTR),('desktop',W.LPWSTR),('title',W.LPWSTR),
              ('x',W.DWORD),('y',W.DWORD),('xs',W.DWORD),('ys',W.DWORD),('xc',W.DWORD),('yc',W.DWORD),
              ('fill',W.DWORD),('flags',W.DWORD),('show',W.WORD),('cb2',W.WORD),('res2',C.c_void_p),
              ('stdin',W.HANDLE),('stdout',W.HANDLE),('stderr',W.HANDLE)]
class PI(C.Structure): _fields_=[('process',W.HANDLE),('thread',W.HANDLE),('pid',W.DWORD),('tid',W.DWORD)]
class Account(C.Structure):
    _fields_=[('user',C.c_longlong),('kernel',C.c_longlong),('perioduser',C.c_longlong),('periodkernel',C.c_longlong),
              ('faults',W.DWORD),('total',W.DWORD),('active',W.DWORD),('terminated',W.DWORD)]
K.CreateJobObjectW.argtypes=[C.c_void_p,W.LPCWSTR]; K.CreateJobObjectW.restype=W.HANDLE
K.AssignProcessToJobObject.argtypes=[W.HANDLE,W.HANDLE]
K.QueryInformationJobObject.argtypes=[W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.c_void_p]
K.CreateProcessW.argtypes=[W.LPCWSTR,W.LPWSTR,C.c_void_p,C.c_void_p,W.BOOL,W.DWORD,C.c_void_p,W.LPCWSTR,C.POINTER(SI),C.POINTER(PI)]
K.ResumeThread.argtypes=[W.HANDLE]; K.GetExitCodeProcess.argtypes=[W.HANDLE,C.POINTER(W.DWORD)]

def run_trusted(rid,name):
    p,r=run_record(rid); idle(r)
    allowed=read(checked(ROOT/'control'/'trusted_tests.json'))
    require(name in allowed,'unregistered test'); t=allowed[name]
    script=checked(ROOT/'scripts'/t['script']); require(sha(script)==t['sha256'],'trusted script changed')
    for d in t.get('dependencies',[]):
        dep=below(d['path'],ROOT); require(sha(checked(dep))==d['sha256'],'trusted dependency changed')
    env={k:v for k,v in os.environ.items() if k.upper() in ('SYSTEMROOT','WINDIR','SYSTEMDRIVE','COMSPEC','NUMBER_OF_PROCESSORS','PROCESSOR_ARCHITECTURE')}
    env.update(TEMP=str(p/'temp'),TMP=str(p/'temp'),PATH=r'C:\Windows\System32',PYTHONDONTWRITEBYTECODE='1',CUDA_CACHE_PATH=str(p/'temp'/'cuda'))
    cmd=subprocess.list2cmdline([sys.executable,'-B',str(script),str(p)])
    block=C.create_unicode_buffer('\0'.join(k+'='+v for k,v in sorted(env.items()))+'\0\0')
    si=SI(); si.cb=C.sizeof(si); pi=PI(); job=K.CreateJobObjectW(None,'PV1Lab_'+rid)
    require(job,'job creation failed')
    reg=registry(); reg[rid]['state']='STARTING'; save(ROOT/'control'/'runs.json',reg)
    require(K.CreateProcessW(sys.executable,C.create_unicode_buffer(cmd),None,None,False,0x4|0x400|0x08000000,block,str(p),C.byref(si),C.byref(pi)),'CreateProcess failed')
    reg[rid].update(state='RUNNING',processes=[{'pid':pi.pid,'job':'PV1Lab_'+rid,'test':name,'started':time.time()}]); save(ROOT/'control'/'runs.json',reg)
    # No breakaway or kill-on-close flags: descendants stay in this job, timeout preserves them.
    require(K.AssignProcessToJobObject(job,pi.process),'job assignment failed; suspended process preserved')
    K.ResumeThread(pi.thread); K.CloseHandle(pi.thread)
    try:
        start=time.monotonic()
        while True:
            a=Account(); require(K.QueryInformationJobObject(job,1,C.byref(a),C.sizeof(a),None),'job query failed')
            if not a.active: break
            if time.monotonic()-start>t.get('timeout',120):
                reg[rid]['state']='TIMEOUT_PRESERVED'; save(ROOT/'control'/'runs.json',reg)
                raise RuntimeError('timeout: cooperative stop only; no kill; cleanup disabled')
            time.sleep(.15)
        code=W.DWORD(); K.GetExitCodeProcess(pi.process,C.byref(code))
        reg[rid].update(state='IDLE',exit_code=code.value,active_processes=0,job_total_processes=a.total)
        save(ROOT/'control'/'runs.json',reg)
        require(code.value==0,'trusted test failed; inspect output')
        return {'run_id':rid,'exit_code':code.value,'active_processes':0,'job_total_processes':a.total}
    finally: K.CloseHandle(pi.process); K.CloseHandle(job)

def prepare(manifest_name):
    require(bool(re.fullmatch(r'[a-z0-9_-]+\.json',manifest_name)),'manifest name invalid')
    manifest=read(checked(ROOT/'control'/manifest_name)); copied=[]
    for f in manifest['files']:
        src=below(f['source'],PROTECTED); dest=below(f['destination'],ROOT/'staging')
        require(not re.search(r'(?i)(license|token|cookie|credential|secret|\.dmp$|\.env$)',src.name),'sensitive filename refused')
        require(not dest.exists(),'destination already exists')
        with locked_source(src):
            require(sha(src)==f['sha256'],'source hash mismatch')
            checked(dest.parent); dest.write_bytes(src.read_bytes())
            require(sha(dest)==f['sha256'],'copy mismatch')
            require(src.stat().st_ino!=dest.stat().st_ino,'copy not independent')
        copied.append({'destination':str(dest),'sha256':f['sha256']})
    return copied

def sanitized_summary(data):
    # Construct an output schema, never redact an arbitrary report or collect a directory.
    result={}
    for provider in ('cuda','cpu','dml','tensorrt'):
        item=data.get(provider,{})
        status=item.get('status','NOT_TESTED')
        require(status in ('PASS','FAILED','NOT_TESTED'),'invalid export status')
        frames=item.get('frames',0); require(type(frames)==int and 0<=frames<=10000,'invalid export frame count')
        result[provider]={'status':status,'frames':frames}
    return {'schema':1,'gpu':result,'target_runtime':'NOT_EXECUTED','license_used':False,'activation_service_accessed':False,'sandbox':'ISOLATION_NOT_QUALIFIED'}
def export_summary():
    rid=read(checked(ROOT/'control'/'gpu_run.json'))['run_id']; p,r=run_record(rid); idle(r)
    data=read(checked(p/'output'/'gpu_results.json'))
    trt=ROOT/'reports'/'own_trt_results.json'
    if trt.exists(): data['tensorrt']=read(checked(trt))
    result=sanitized_summary(data)
    dest=ROOT/'exports'/('handoff-'+uuid.uuid4().hex+'.json'); save(dest,result)
    return {'file':str(dest),'schema':'status-only allowlist; no files or raw logs packed'}
@contextlib.contextmanager
def locked_source(src):
    # Original input is read-only; checked twice and opened without requesting any write access.
    checked(src); before=src.stat(); yield
    require(src.stat().st_ino==before.st_ino,'source identity changed')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('command',choices=['init','new-run','prepare','status','preview-clean','clean','snapshot','restore','run-trusted','stop','export','launch-original','sandbox-snapshot'])
    ap.add_argument('--run'); ap.add_argument('--snapshot'); ap.add_argument('--test'); ap.add_argument('--manifest')
    a=ap.parse_args(); workspace()
    if a.command=='init': result={'workspace':workspace(),'status':'existing identity verified'}
    elif a.command=='new-run': result={'run_id':new_run()}
    elif a.command=='prepare': result=prepare(a.manifest)
    elif a.command=='status': result={'workspace':workspace(),'runs':registry()}
    elif a.command=='preview-clean': result=preview(a.run)
    elif a.command=='clean': result=clean(a.run)
    elif a.command=='snapshot': result=snapshot(a.run)
    elif a.command=='restore': result=restore(a.run,a.snapshot)
    elif a.command=='run-trusted': result=run_trusted(a.run,a.test)
    elif a.command=='export': result=export_summary()
    elif a.command=='stop':
        p,r=run_record(a.run); (p/'temp'/'stop.request').write_text('cooperative stop',encoding='ascii'); result={'state':r['state'],'request':'written; cleanup requires confirmed job drain; no process killed'}
    else: raise RuntimeError('ISOLATION_NOT_QUALIFIED: original launch and native snapshots disabled; no shell fallback')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: main()
    except Exception as e: print('REFUSED: '+str(e),file=sys.stderr); sys.exit(2)
