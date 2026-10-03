#include <windows.h>
#include <fstream>
#include <string>
#include <vector>
#pragma comment(lib,"user32.lib")
#pragma comment(lib,"gdi32.lib")
static int received=0;
static LRESULT CALLBACK proc(HWND w,UINT msg,WPARAM a,LPARAM b){
 if(msg==WM_APP+77){received++;return 0xabc123;}
 if(msg==WM_PAINT){PAINTSTRUCT ps;HDC dc=BeginPaint(w,&ps);RECT r;GetClientRect(w,&r);HBRUSH br=CreateSolidBrush(RGB(17,83,149));FillRect(dc,&r,br);DeleteObject(br);EndPaint(w,&ps);return 0;}
 return DefWindowProcW(w,msg,a,b);
}
int main(int argc,char**argv){
 if(argc<3)return 2;
 if(std::string(argv[1])=="host"){
   WNDCLASSW cls{};cls.lpfnWndProc=proc;cls.hInstance=GetModuleHandleW(nullptr);cls.lpszClassName=L"PV1Lab_Owned_UI_abc0b5b9";
   if(!RegisterClassW(&cls))return 3;
   HWND w=CreateWindowExW(0,cls.lpszClassName,L"PV1LAB_SYNTHETIC_WINDOW_abc0b5b9",WS_OVERLAPPEDWINDOW,0,0,240,160,nullptr,nullptr,cls.hInstance,nullptr);if(!w)return 4;
   {std::ofstream ready(argv[2]);ready<<GetCurrentProcessId()<<" "<<(uintptr_t)w<<"\n";}
   auto start=GetTickCount64();MSG m;
   while(GetTickCount64()-start<90000){
     while(PeekMessageW(&m,nullptr,0,0,PM_REMOVE)){TranslateMessage(&m);DispatchMessageW(&m);}
     if(argc>3 && GetFileAttributesA(argv[3])!=INVALID_FILE_ATTRIBUTES)break;
     Sleep(30);
   }
   DestroyWindow(w);std::ofstream end(std::string(argv[2])+".json");end<<"{\"host_messages_received\":"<<received<<",\"window_destroyed\":true}\n";return 0;
 }
 if(argc!=5)return 2;
 DWORD hostpid=std::stoul(argv[2]);HWND w=(HWND)(uintptr_t)std::stoull(argv[3]);std::ofstream out(argv[4]);
 HANDLE p=OpenProcess(PROCESS_VM_READ|PROCESS_VM_WRITE,FALSE,hostpid);DWORD err=p?0:GetLastError();DWORD granted=0;LONG queryStatus=-1;
 if(p){using Query=LONG (NTAPI*)(HANDLE,ULONG,void*,ULONG,ULONG*);auto q=(Query)GetProcAddress(GetModuleHandleW(L"ntdll.dll"),"NtQueryObject");std::vector<unsigned char> meta(56);ULONG used=0;if(q){queryStatus=q(p,0,meta.data(),ULONG(meta.size()),&used);if(queryStatus!=0 && used>=8 && used<=4096){meta.resize(used);queryStatus=q(p,0,meta.data(),ULONG(meta.size()),&used);}if(queryStatus==0)memcpy(&granted,meta.data()+4,sizeof(granted));}CloseHandle(p);}
 wchar_t title[100]{};int len=GetWindowTextW(w,title,100);
 DWORD_PTR reply=0;SetLastError(0);LRESULT send=SendMessageTimeoutW(w,WM_APP+77,0,0,SMTO_ABORTIFHUNG,1000,&reply);DWORD senderr=GetLastError();
 HDC mem=CreateCompatibleDC(nullptr);BITMAPINFO info{};info.bmiHeader.biSize=sizeof(BITMAPINFOHEADER);info.bmiHeader.biWidth=240;info.bmiHeader.biHeight=-160;info.bmiHeader.biPlanes=1;info.bmiHeader.biBitCount=32;info.bmiHeader.biCompression=BI_RGB;void*bits=nullptr;
 HBITMAP bmp=CreateDIBSection(mem,&info,DIB_RGB_COLORS,&bits,nullptr,0);HGDIOBJ old=SelectObject(mem,bmp);BOOL printed=PrintWindow(w,mem,PW_CLIENTONLY);SelectObject(mem,old);DeleteObject(bmp);DeleteDC(mem);
 out<<"{\"sbie_loaded\":"<<(GetModuleHandleW(L"SbieDll.dll")?"true":"false")<<",\"host_process_open_error\":"<<err<<",\"handle_query_status\":"<<queryStatus<<",\"host_process_granted_access\":"<<granted<<",\"host_window_title_length\":"<<len<<",\"host_canary_title_matched\":"<<(std::wstring(title)==L"PV1LAB_SYNTHETIC_WINDOW_abc0b5b9"?"true":"false")<<",\"send_message_succeeded\":"<<(send?"true":"false")<<",\"send_message_error\":"<<senderr<<",\"own_window_print_succeeded\":"<<(printed?"true":"false")<<"}\n";
 return 0;
}
