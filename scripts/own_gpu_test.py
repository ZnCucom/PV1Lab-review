"""Owned f(x)=2x+1, actual CUDA and DirectML, no original inputs or services."""
import ctypes as C,json,os,struct,subprocess,sys,traceback
from pathlib import Path
R=Path(r'D:\PV1Lab'); run=Path(sys.argv[1]); out=run/'output'; results={}
def save(): (out/'gpu_results.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
def vi(n):
    b=bytearray()
    while n>127: b.append((n&127)|128); n>>=7
    b.append(n); return bytes(b)
def v(k,n): return vi(k*8)+vi(n)
def b(k,x):
    if isinstance(x,str): x=x.encode()
    return vi(k*8+2)+vi(len(x))+x
def tensor(name,val): return v(1,1)+v(2,1)+b(8,name)+b(9,struct.pack('<f',val))
def info(name): return b(1,name)+b(2,b(1,v(1,1)+b(2,b(1,v(1,1))+b(1,v(1,4)))))
def model():
    mul=b(1,'x')+b(1,'two')+b(2,'scaled')+b(4,'Mul')
    add=b(1,'scaled')+b(1,'one')+b(2,'y')+b(4,'Add')
    graph=b(1,mul)+b(1,add)+b(2,'PV1Lab_owned_affine')+b(5,tensor('two',2))+b(5,tensor('one',1))+b(11,info('x'))+b(12,info('y'))
    p=run/'build'/'owned_affine.onnx'; p.write_bytes(v(1,8)+b(2,'PV1Lab_self_authored')+b(7,graph)+b(8,v(2,13))); return p
def cuda():
    nv=R/'tools'/'nvrtc'/'cuda_nvrtc-windows-x86_64-12.9.86-archive'/'bin'
    # NVRTC uses a legacy dependency load: enable the already registered DLL directory
    # process-locally. No global PATH or system loader configuration is changed.
    C.WinDLL('kernel32').SetDefaultDllDirectories(0x1000)
    handle=os.add_dll_directory(str(nv)); runtime=C.WinDLL(str(nv/'nvrtc64_120_0.dll'))
    driver=C.WinDLL(r'C:\Windows\System32\nvcuda.dll')
    def fn(d,name,args):
        f=getattr(d,name); f.argtypes=args; f.restype=C.c_int; return f
    def ok(rc):
        if rc!=0: raise RuntimeError('CUDA/NVRTC status '+str(rc))
    ptr=C.c_void_p; i=C.c_int; sz=C.c_size_t; u64=C.c_ulonglong
    ok(fn(driver,'cuInit',[C.c_uint])(0)); dev=i(); ok(fn(driver,'cuDeviceGet',[C.POINTER(i),i])(C.byref(dev),0))
    name=C.create_string_buffer(256); ok(fn(driver,'cuDeviceGetName',[C.c_char_p,i,i])(name,256,dev))
    ctx=ptr(); ok(fn(driver,'cuCtxCreate_v2',[C.POINTER(ptr),C.c_uint,i])(C.byref(ctx),0,dev))
    module=ptr(); mem=u64(); prog=ptr(); frames=0
    try:
        major=i(); minor=i(); attr=fn(driver,'cuDeviceGetAttribute',[C.POINTER(i),i,i]); ok(attr(C.byref(major),75,dev));ok(attr(C.byref(minor),76,dev))
        src=b'extern "C" __global__ void affine(float* x) { unsigned i=threadIdx.x; if(i<4) x[i]=2*x[i]+1; }'
        ok(fn(runtime,'nvrtcCreateProgram',[C.POINTER(ptr),C.c_char_p,C.c_char_p,i,ptr,ptr])(C.byref(prog),src,b'owned.cu',0,None,None))
        opts=(C.c_char_p*1)(f'--gpu-architecture=compute_{major.value}{minor.value}'.encode())
        rc=fn(runtime,'nvrtcCompileProgram',[ptr,i,C.POINTER(C.c_char_p)])(prog,1,opts)
        logsize=sz(); fn(runtime,'nvrtcGetProgramLogSize',[ptr,C.POINTER(sz)])(prog,C.byref(logsize))
        log=C.create_string_buffer(max(1,logsize.value)); fn(runtime,'nvrtcGetProgramLog',[ptr,ptr])(prog,log)
        (out/'nvrtc_compile.log').write_bytes(log.value)
        ok(rc)
        size=sz();ok(fn(runtime,'nvrtcGetPTXSize',[ptr,C.POINTER(sz)])(prog,C.byref(size)))
        ptx=C.create_string_buffer(size.value);ok(fn(runtime,'nvrtcGetPTX',[ptr,C.c_void_p])(prog,ptx))
        (run/'build'/'owned.ptx').write_bytes(ptx.raw)
        ok(fn(driver,'cuModuleLoadData',[C.POINTER(ptr),ptr])(C.byref(module),ptx)); kernel=ptr()
        ok(fn(driver,'cuModuleGetFunction',[C.POINTER(ptr),ptr,C.c_char_p])(C.byref(kernel),module,b'affine'))
        ok(fn(driver,'cuMemAlloc_v2',[C.POINTER(u64),sz])(C.byref(mem),16))
        params=(ptr*1)(C.cast(C.byref(mem),ptr))
        launch=fn(driver,'cuLaunchKernel',[ptr,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_uint,C.c_uint,ptr,C.POINTER(ptr),ptr])
        sync=fn(driver,'cuCtxSynchronize',[])
        for frame in range(24):
            data=(C.c_float*4)(frame,frame+1,-frame,.25)
            expect=[2*x+1 for x in data]
            ok(fn(driver,'cuMemcpyHtoD_v2',[u64,ptr,sz])(mem,data,16))
            ok(launch(kernel,1,1,1,4,1,1,0,None,params,None));ok(sync())
            ok(fn(driver,'cuMemcpyDtoH_v2',[ptr,u64,sz])(data,mem,16))
            assert list(data)==expect; frames+=1
        invalid=launch(kernel,1,1,1,0,1,1,0,None,params,None); assert invalid!=0
        ok(sync())
        results['cuda']={'status':'PASS','gpu':name.value.decode(),'compute':f'{major.value}.{minor.value}','frames':frames,'invalid_launch_rejected':invalid,'runtime':'NVRTC 12.9.86 + host CUDA driver','original_engine':False}
    finally:
        if mem.value: ok(fn(driver,'cuMemFree_v2',[u64])(mem))
        if module.value: ok(fn(driver,'cuModuleUnload',[ptr])(module))
        if prog.value: ok(fn(runtime,'nvrtcDestroyProgram',[C.POINTER(ptr)])(C.byref(prog)))
        ok(fn(driver,'cuCtxDestroy_v2',[ptr])(ctx)); handle.close()
    results['cuda']['resources_released']=True
def dml():
    compiler=R/'tools'/'llvm'/'llvm-mingw-20260922-ucrt-x86_64'/'bin'/'clang++.exe'
    source=R/'scripts'/'own_dml.cpp'; exe=run/'build'/'own_dml.exe'
    command=[str(compiler),'-std=c++17','-O2','-static','-I'+str(R/'tools'/'ort'/'build'/'native'/'include'),str(source),'-o',str(exe)]
    cp=subprocess.run(command,capture_output=True,text=True); (out/'compile.log').write_text(cp.stdout+cp.stderr)
    assert cp.returncode==0,'C++ build failed'
    dlls=R/'tools'/'ort'/'runtimes'/'win-x64'/'native'
    # Loading directory holds Microsoft signed DLL bytes; no original runtime DLL used.
    dmlsrc=R/'tools'/'directml'/'bin'/'x64-win'/'DirectML.dll'; dmldst=run/'build'/'DirectML.dll'
    dmldst.write_bytes(dmlsrc.read_bytes())
    for file in dlls.glob('*.dll'): (run/'build'/file.name).write_bytes(file.read_bytes())
    m=model()
    for provider in ('cpu','dml'):
        cp=subprocess.run([str(exe),str(run/'build'/'onnxruntime.dll'),str(m),str(out/provider),provider],capture_output=True,text=True)
        (out/(provider+'.log')).write_text(cp.stdout+cp.stderr,encoding='utf-8')
        assert cp.returncode==0,provider+' own-model run failed'
        profiles=[Path(line.split('=',1)[1]) for line in cp.stdout.splitlines() if line.startswith('PROFILE=')]
        providers=set()
        for p in profiles:
            for event in json.loads(p.read_text()):
                if 'provider' in event.get('args',{}): providers.add(event['args']['provider'])
        expected='DmlExecutionProvider' if provider=='dml' else 'CPUExecutionProvider'
        assert expected in providers, 'provider assignment missing: '+str(providers)
        results[provider]={'status':'PASS','frames':24,'cycles':3,'bad_shape_rejected':3,'profile_providers':sorted(providers),'resources_released':'sessions and SDK destroyed; process exited normally'}
    results['compiler']={'status':'PASS','kind':'LLVM-MinGW; NOT MSVC ABI qualification'}
try:
    cuda(); save(); dml(); save()
except Exception:
    results['failure']=traceback.format_exc(); save(); sys.exit(1)
