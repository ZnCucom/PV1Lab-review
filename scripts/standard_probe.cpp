#include <winsock2.h>
#include <windows.h>
#include <fstream>
#include <string>
#include <vector>
#pragma comment(lib,"ws2_32.lib")
#pragma comment(lib,"advapi32.lib")
#pragma comment(lib,"user32.lib")
static std::ofstream out;
static void field(const char* name,long long n){out<<"\""<<name<<"\":"<<n<<",\n";}
static DWORD tryread(const wchar_t* path,bool dir){
 HANDLE h=CreateFileW(path,dir?FILE_LIST_DIRECTORY:GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,nullptr,OPEN_EXISTING,dir?FILE_FLAG_BACKUP_SEMANTICS:0,nullptr);
 if(h==INVALID_HANDLE_VALUE)return GetLastError();CloseHandle(h);return 0;
}
int main(int argc,char**argv){
 if(argc<3)return 2;bool child=argc>3;
 if(std::string(argv[2])=="hold"){
   auto begin=GetTickCount64();
   while(GetTickCount64()-begin<370000){
     std::ofstream h(argv[1]);h<<"{\"elapsed_ms\":"<<(GetTickCount64()-begin)<<",\"pid\":"<<GetCurrentProcessId()<<",\"complete\":false}\n";h.close();
     if(GetFileAttributesA("D:\\PV1Lab\\staging\\owned-standard-payload\\hold-stop.request")!=INVALID_FILE_ATTRIBUTES)return 9;
     Sleep(1000);
   }
   std::ofstream h(argv[1]);h<<"{\"elapsed_ms\":"<<(GetTickCount64()-begin)<<",\"pid\":"<<GetCurrentProcessId()<<",\"complete\":true}\n";return 0;
 }

 out.open(argv[1]);if(!out)return 3;out<<"{\n";
 field("pid",GetCurrentProcessId());field("sbie_loaded",GetModuleHandleW(L"SbieDll.dll")!=nullptr);field("child",child);
 field("project_open_error",tryread(L"D:\\Pv1260909",true));
 field("reverse_open_error",tryread(L"D:\\Pv1260909\\_reverse_work",true));
 field("private_open_error",tryread(L"C:\\Users\\REDACTED_USER",true));
 field("control_open_error",tryread(L"D:\\PV1Lab\\control\\isolation-canary.txt",false));
 field("scripts_open_error",tryread(L"D:\\PV1Lab\\scripts",true));
 field("other_runs_open_error",tryread(L"D:\\PV1Lab\\runs",true));
 field("baseline_open_error",tryread(L"D:\\PV1Lab\\baselines",true));
 HKEY key=nullptr;DWORD type=0,len=80;char val[80]{};
 LONG r=RegOpenKeyExW(HKEY_CURRENT_USER,L"Software\\PV1Lab_Canary_abc0b5b9",0,KEY_READ,&key);
 if(r==0){r=RegQueryValueExA(key,"host_only",nullptr,&type,(BYTE*)val,&len);RegCloseKey(key);}field("host_registry_read_error",r);
 if(std::string(argv[2])!="read"){
   std::ofstream marker("D:\\PV1Lab\\staging\\owned-standard-payload\\virtual-marker.txt");marker<<argv[2];marker.close();field("virtual_file_write_ok",bool(marker));
   r=RegCreateKeyExW(HKEY_CURRENT_USER,L"Software\\PV1Lab_Canary_abc0b5b9",0,nullptr,0,KEY_READ|KEY_WRITE,nullptr,&key,nullptr);
   if(r==0){r=RegSetValueExA(key,"sandbox_value",0,REG_SZ,(BYTE*)argv[2],DWORD(strlen(argv[2])+1));RegCloseKey(key);}field("virtual_registry_write_error",r);
 }
 std::ifstream marker("D:\\PV1Lab\\staging\\owned-standard-payload\\virtual-marker.txt");std::string value;marker>>value;out<<"\"file_value\":\""<<value<<"\",\n";
 len=80;val[0]=0;r=RegOpenKeyExW(HKEY_CURRENT_USER,L"Software\\PV1Lab_Canary_abc0b5b9",0,KEY_READ,&key);
 if(!r){r=RegQueryValueExA(key,"sandbox_value",nullptr,&type,(BYTE*)val,&len);RegCloseKey(key);}out<<"\"registry_value\":\""<<(r?"":val)<<"\",\n";
 WSADATA w{};field("wsa_startup",WSAStartup(MAKEWORD(2,2),&w));
 for(auto family:{AF_INET,AF_INET6}){SOCKET s=socket(family,SOCK_STREAM,IPPROTO_TCP);field(family==AF_INET?"ipv4_socket_error":"ipv6_socket_error",s==INVALID_SOCKET?WSAGetLastError():0);if(s!=INVALID_SOCKET)closesocket(s);}WSACleanup();
 BOOL opened=OpenClipboard(nullptr);field("clipboard_open_ok",opened);field("clipboard_format_count",opened?CountClipboardFormats():-1);if(opened)CloseClipboard(); // never read or change clipboard contents
 HANDLE e=OpenEventW(SYNCHRONIZE,FALSE,L"Local\\PV1Lab_Canary_abc0b5b9");field("host_event_open_error",e?0:GetLastError());if(e)CloseHandle(e);
 field("rawdisk_open_error",tryread(L"\\\\.\\PhysicalDrive0",false));
 if(!child){
   wchar_t exe[MAX_PATH];GetModuleFileNameW(nullptr,exe,MAX_PATH);
   std::wstring cmd=L"\""+std::wstring(exe)+L"\" \"D:\\PV1Lab\\staging\\owned-standard-payload\\child-results.json\" read child";
   STARTUPINFOW si{sizeof(si)};PROCESS_INFORMATION pi{};BOOL ok=CreateProcessW(exe,cmd.data(),nullptr,nullptr,FALSE,CREATE_NO_WINDOW,nullptr,nullptr,&si,&pi);field("child_created",ok);
   if(ok){WaitForSingleObject(pi.hProcess,INFINITE);DWORD code;GetExitCodeProcess(pi.hProcess,&code);field("child_exit",code);CloseHandle(pi.hThread);CloseHandle(pi.hProcess);}
 }
 out<<"\"complete\":true}\n";return 0;
}
