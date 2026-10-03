"""TensorRT 10.10 owned affine network. No original engine/client/plugins loaded."""
import ctypes as C,gc,hashlib,json,os,sys,traceback
from pathlib import Path
R=Path(r'D:\PV1Lab');run=Path(sys.argv[1]);out=run/'output';result={}
def save(): (out/'trt_results.json').write_text(json.dumps(result,indent=2)+'\n')
try:
    lib=R/'tools'/'tensorrt'/'TensorRT-10.10.0.31'/'lib'
    cudir=R/'tools'/'cudart'/'cuda_cudart-windows-x86_64-12.9.79-archive'/'bin'
    os.environ['PATH']=str(lib)+os.pathsep+str(cudir)+os.pathsep+r'C:\Windows\System32'
    C.WinDLL('kernel32').SetDefaultDllDirectories(0x1000)
    dirs=[os.add_dll_directory(str(p)) for p in (lib,cudir)]
    sys.path.insert(0,str(R/'tools'/'trt_python'))
    import tensorrt as trt
    import numpy as np
    assert trt.__version__=='10.10.0.31'
    cuda=C.WinDLL(str(cudir/'cudart64_12.dll'))
    def fn(name,args):
        f=getattr(cuda,name);f.argtypes=args;f.restype=C.c_int;return f
    def ok(code):
        if code: raise RuntimeError('CUDA runtime status '+str(code))
    ptr=C.c_void_p;sz=C.c_size_t
    ok(fn('cudaSetDevice',[C.c_int])(0))
    messages=[]
    class Logger(trt.ILogger):
        def __init__(self): super().__init__()
        def log(self,severity,msg):
            if severity<=trt.ILogger.Severity.WARNING: messages.append(msg)
    logger=Logger();builder=trt.Builder(logger);builder.max_threads=1
    network=builder.create_network(0);config=builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE,16*1024*1024)
    config.builder_optimization_level=0
    x=network.add_input('x',trt.float32,(1,4))
    two=network.add_constant((1,1),np.array([[2]],dtype=np.float32))
    one=network.add_constant((1,1),np.array([[1]],dtype=np.float32))
    mul=network.add_elementwise(x,two.get_output(0),trt.ElementWiseOperation.PROD)
    add=network.add_elementwise(mul.get_output(0),one.get_output(0),trt.ElementWiseOperation.SUM)
    y=add.get_output(0);y.name='y';network.mark_output(y)
    serialized=builder.build_serialized_network(network,config)
    assert serialized is not None,'owned engine build failed'
    data=bytes(serialized);(run/'build'/'owned_affine.engine').write_bytes(data)
    del serialized,y,add,mul,one,two,x,network,config,builder;gc.collect()
    runtime=trt.Runtime(logger);frames=0;errors=0
    malloc=fn('cudaMalloc',[C.POINTER(ptr),sz]);free=fn('cudaFree',[ptr]);copy=fn('cudaMemcpy',[ptr,ptr,sz,C.c_int])
    sync=fn('cudaStreamSynchronize',[ptr]);destroy=fn('cudaStreamDestroy',[ptr])
    for cycle in range(3):
        engine=runtime.deserialize_cuda_engine(data);assert engine is not None
        context=engine.create_execution_context();assert context is not None
        input_mem=ptr();output_mem=ptr();stream=ptr()
        ok(malloc(C.byref(input_mem),16));ok(malloc(C.byref(output_mem),16));ok(fn('cudaStreamCreate',[C.POINTER(ptr)])(C.byref(stream)))
        try:
            assert context.set_tensor_address('x',input_mem.value)
            assert context.set_tensor_address('y',output_mem.value)
            assert not context.set_tensor_address('PV1LAB_NONEXISTENT_TENSOR',input_mem.value);errors+=1
            for frame in range(8):
                values=(C.c_float*4)(frame,frame+cycle,-frame,.25);expected=[2*x+1 for x in values]
                ok(copy(input_mem,values,16,1))
                assert context.execute_async_v3(stream.value);ok(sync(stream))
                actual=(C.c_float*4)();ok(copy(actual,output_mem,16,2));assert list(actual)==expected
                frames+=1
        finally:
            ok(sync(stream));del context;gc.collect()
            ok(free(input_mem));ok(free(output_mem));ok(destroy(stream));del engine;gc.collect()
    del runtime;gc.collect()
    result={'status':'PASS','version':trt.__version__,'frames':frames,'cycles':3,'invalid_tensor_name_rejected':errors,'engine_sha256':hashlib.sha256(data).hexdigest(),'engine_bytes':len(data),'source':'SELF_AUTHORED_CONSTANT_AND_ELEMENTWISE_NETWORK','resources_released':True,'MSVC_project_bridge':'NOT_BUILT','messages':messages}
    save()
except Exception:
    result={'status':'FAILED','frames':0,'failure':traceback.format_exc(),'messages':locals().get('messages',[])};save();sys.exit(1)
