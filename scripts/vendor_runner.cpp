#include "recovered/trt_c_api.h"
#include <windows.h>
#include <fstream>
#include <iostream>
#include <vector>
#include <cmath>
#include <stdexcept>
static void check(bool ok,const char*s){if(!ok)throw std::runtime_error(s);}
int main(int argc,char**argv){
  if(argc!=4)return 2;
  std::ofstream report(argv[3]); PvTrtApi api{}; void* ctx=nullptr; HMODULE module=nullptr;
  try{
    SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    wchar_t exe[MAX_PATH];GetModuleFileNameW(nullptr,exe,MAX_PATH);std::wstring folder(exe);folder.resize(folder.find_last_of(L"\\"));AddDllDirectory(folder.c_str());
    module=LoadLibraryExA(argv[1],nullptr,LOAD_LIBRARY_SEARCH_DLL_LOAD_DIR|LOAD_LIBRARY_SEARCH_SYSTEM32);
    check(module!=nullptr,"vendor DLL load");auto get=(PvTrtGetApi)GetProcAddress(module,"pv_trt_get_api");check(get!=nullptr,"C export");
    api.struct_size=sizeof(api);api.abi_version=PV_TRT_ABI_VERSION;check(get(&api)==0,"ABI query");
    check(api.vendor_version==101000 && !(api.capabilities&PV_TRT_MOCK_PROVIDER),"real vendor version/capability");
    std::ifstream input(argv[2],std::ios::binary);std::vector<char> engine((std::istreambuf_iterator<char>(input)),{});check(!engine.empty(),"owned engine");
    int frames=0,negative=0;
    for(int cycle=0;cycle<3;cycle++){
      check(api.open(engine.data(),engine.size(),&ctx)==0,"deserialize own engine");uint32_t count=0;check(api.tensor_count(ctx,&count)==0&&count==2,"tensor count");
      PvTrtTensor tensor{};check(api.tensor(ctx,count,&tensor)!=0,"invalid tensor index");negative++;
      void* a=nullptr;void*b=nullptr;check(api.allocate(ctx,16,&a)==0&&api.allocate(ctx,16,&b)==0,"allocate");
      check(api.bind(ctx,"x",a)==0&&api.bind(ctx,"y",b)==0,"bind");
      check(api.bind(ctx,"PV1LAB_BAD_NAME",a)!=0,"bad name rejection");negative++;
      for(int frame=0;frame<8;frame++){
        float x[4]={float(frame),float(frame+cycle),float(-frame),.25f},y[4]{};
        check(api.copy(ctx,a,x,sizeof(x),0)==0,"H2D");check(api.enqueue(ctx)==0,"enqueueV3");check(api.drain(ctx)==0,"drain");check(api.copy(ctx,y,b,sizeof(y),1)==0,"D2H");
        for(int n=0;n<4;n++)check(std::abs(y[n]-(x[n]*2+1))<1e-5f,"value mismatch");frames++;
      }
      check(api.release(ctx,a)==0&&api.release(ctx,b)==0,"release");check(api.close(ctx)==0,"close");ctx=nullptr;
    }
    FreeLibrary(module);module=nullptr;
    report<<"{\"status\":\"PASS\",\"frames\":"<<frames<<",\"cycles\":3,\"negative_tests\":"<<negative<<",\"mock\":false,\"vendor_version\":101000,\"resources_released\":true}\n";
    return 0;
  }catch(const std::exception&e){
    // RETAINED forbids unloading a module with potentially live GPU work.
    bool safe=!ctx || (api.close&&api.close(ctx)==0);
    report<<"{\"status\":\"FAILED\",\"error\":\""<<e.what()<<"\",\"resources_released\":"<<(safe?"true":"false")<<"}\n";report.flush();
    if(!safe){Sleep(INFINITE);} // preserve uncertain GPU work; external manager must not kill.
    if(module)FreeLibrary(module);return 3;
  }
}
