#include <windows.h>
#include <cuda_runtime_api.h>
#include <NvInferRuntime.h>
#include <fstream>
#include <vector>
#include <memory>
struct Log:nvinfer1::ILogger {std::ofstream& f;Log(std::ofstream&x):f(x){}void log(Severity s,const char*m)noexcept override{if(s<=Severity::kWARNING){f<<"TRT "<<int(s)<<": "<<m<<"\n";f.flush();}}};
int main(int argc,char**argv){
 if(argc!=3)return 2;std::ofstream out(argv[2]);
 SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);wchar_t exe[MAX_PATH];GetModuleFileNameW(nullptr,exe,MAX_PATH);std::wstring folder(exe);folder.resize(folder.find_last_of(L"\\"));AddDllDirectory(folder.c_str());
 int count=-1,device=-1,version=-1;auto report=[&](const char*n,cudaError_t e){out<<n<<"="<<int(e)<<" "<<cudaGetErrorName(e)<<": "<<cudaGetErrorString(e)<<"\n";out.flush();return e==cudaSuccess;};
 report("driver_version",cudaDriverGetVersion(&version));out<<"driver_version_value="<<version<<"\n";
 bool countok=report("get_count",cudaGetDeviceCount(&count));out<<"count="<<count<<"\n";
 bool devok=report("get_device",cudaGetDevice(&device));out<<"device="<<device<<"\n";
 if(!countok||!devok)return 0;
 cudaStream_t stream=nullptr;if(!report("stream_create",cudaStreamCreateWithFlags(&stream,cudaStreamNonBlocking)))return 0;
 Log logger(out);std::unique_ptr<nvinfer1::IRuntime> runtime(nvinfer1::createInferRuntime(logger));out<<"runtime="<<bool(runtime)<<"\n";
 if(runtime){std::ifstream f(argv[1],std::ios::binary);std::vector<char> data((std::istreambuf_iterator<char>(f)),{});std::unique_ptr<nvinfer1::ICudaEngine> engine(runtime->deserializeCudaEngine(data.data(),data.size()));out<<"engine="<<bool(engine)<<"\n";if(engine){std::unique_ptr<nvinfer1::IExecutionContext> ctx(engine->createExecutionContext());out<<"context="<<bool(ctx)<<"\n";}}
 runtime.reset();report("stream_sync",cudaStreamSynchronize(stream));report("stream_destroy",cudaStreamDestroy(stream));return 0;
}
