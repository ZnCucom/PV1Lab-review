// Self-authored CPU/DirectML test. Loads only verified task-local ORT and DirectML.
#define ORT_API_MANUAL_INIT
#include <onnxruntime_cxx_api.h>
#include <windows.h>
#include <cmath>
#include <fstream>
#include <iostream>
#include <string>
int main(int argc,char**argv) {
  try {
    if(argc!=5) return 2;
    std::wstring dll; for(char c:std::string(argv[1])) dll+=wchar_t(c);
    SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    auto library=LoadLibraryExW(dll.c_str(),nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    if(!library) throw std::runtime_error("verified ORT load failed");
    auto get=reinterpret_cast<const OrtApiBase*(ORT_API_CALL*)()>(GetProcAddress(library,"OrtGetApiBase"));
    if(!get) throw std::runtime_error("ORT API absent");
    Ort::InitApi(get()->GetApi(ORT_API_VERSION));
    bool dml=std::string(argv[4])=="dml";
    std::wstring model; for(char c:std::string(argv[2])) model+=wchar_t(c);
    std::wstring prof; for(char c:std::string(argv[3])) prof+=wchar_t(c);
    int frames=0,errors=0;
    {
      Ort::Env env(ORT_LOGGING_LEVEL_WARNING,"PV1LabOwnedModel");
      for(int cycle=0;cycle<3;cycle++) {
        Ort::SessionOptions options; options.SetExecutionMode(ExecutionMode::ORT_SEQUENTIAL);
        options.DisableMemPattern(); options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_DISABLE_ALL);
        options.EnableProfiling(prof.c_str());
        if(dml) {
          auto append=reinterpret_cast<OrtStatus*(ORT_API_CALL*)(OrtSessionOptions*,int)>(GetProcAddress(library,"OrtSessionOptionsAppendExecutionProvider_DML"));
          if(!append) throw std::runtime_error("DirectML provider absent");
          Ort::ThrowOnError(append(options,0));
        }
        Ort::Session session(env,model.c_str(),options);
        auto memory=Ort::MemoryInfo::CreateCpu(OrtArenaAllocator,OrtMemTypeDefault);
        const char* ins[]={"x"}; const char* outs[]={"y"}; int64_t shape[]={1,4};
        for(int frame=0;frame<8;frame++) {
          float data[]={float(frame),float(frame+1),float(-frame),.25f};
          auto value=Ort::Value::CreateTensor<float>(memory,data,4,shape,2);
          auto out=session.Run(Ort::RunOptions{nullptr},ins,&value,1,outs,1);
          float* actual=out[0].GetTensorMutableData<float>();
          for(int i=0;i<4;i++) if(std::abs(actual[i]-(data[i]*2+1))>1e-5f) throw std::runtime_error("numeric mismatch");
          frames++;
        }
        try {
          float bad[]={0,1,2}; int64_t wrong[]={1,3}; auto value=Ort::Value::CreateTensor<float>(memory,bad,3,wrong,2);
          session.Run(Ort::RunOptions{nullptr},ins,&value,1,outs,1);
        } catch(const Ort::Exception&) {errors++;}
        Ort::AllocatorWithDefaultOptions allocator; auto path=session.EndProfilingAllocated(allocator);
        std::cout<<"PROFILE="<<path.get()<<"\n";
      }
    }
    if(frames!=24||errors!=3) return 3;
    // Sessions, values, allocator and environment destroyed before unloading SDK.
    FreeLibrary(library);
    std::cout<<"PASS provider="<<(dml?"dml":"cpu")<<" frames="<<frames<<" errors="<<errors<<" cycles=3\n";
    return 0;
  } catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;}
}
