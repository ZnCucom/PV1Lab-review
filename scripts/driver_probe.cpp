#include <windows.h>
#include <fstream>
int main(int argc,char**argv){if(argc!=2)return 2;std::ofstream out(argv[1]);SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
 HMODULE d=LoadLibraryExW(L"nvcuda.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);out<<"driver_module_loaded="<<bool(d)<<" error="<<(d?0:GetLastError())<<"\n";if(!d)return 0;
 char path[MAX_PATH]{};GetModuleFileNameA(d,path,MAX_PATH);out<<"driver_module_path="<<path<<"\n";
 auto ver=(int(WINAPI*)(int*))GetProcAddress(d,"cuDriverGetVersion");auto init=(int(WINAPI*)(unsigned))GetProcAddress(d,"cuInit");auto count=(int(WINAPI*)(int*))GetProcAddress(d,"cuDeviceGetCount");auto name=(int(WINAPI*)(int,const char**))GetProcAddress(d,"cuGetErrorName");
 auto print=[&](const char*label,int code){const char*n=nullptr;if(name)name(code,&n);out<<label<<"="<<code<<" "<<(n?n:"")<<"\n";out.flush();};
 int v=-1,c=-1;if(ver){print("cuDriverGetVersion",ver(&v));out<<"version="<<v<<"\n";}if(init)print("cuInit",init(0));if(count){print("cuDeviceGetCount",count(&c));out<<"count="<<c<<"\n";}
 // No context/stream/allocation/kernel was created. Let process teardown release module.
 return 0;}
