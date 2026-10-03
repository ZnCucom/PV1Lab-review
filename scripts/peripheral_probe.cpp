#include <windows.h>
#include <fstream>
#pragma comment(lib,"user32.lib")
int main(int argc,char**argv){
 if(argc!=2 || !GetModuleHandleW(L"SbieDll.dll"))return 2;
 std::ofstream o(argv[1]);if(!o)return 3;
 BOOL opened=OpenClipboard(nullptr);
 o<<"{\"clipboard_open\":"<<bool(opened);
 if(opened){
   o<<",\"unicode_format_available\":"<<bool(IsClipboardFormatAvailable(CF_UNICODETEXT));
   // Handle presence only: never GlobalLock, memcpy, dereference, print data,
   // EmptyClipboard, SetClipboardData, or change the user's clipboard.
   HANDLE h=GetClipboardData(CF_UNICODETEXT);
   o<<",\"clipboard_data_handle_available\":"<<bool(h);
   CloseClipboard();
 }
 for(int i=0;i<2;i++){
   const wchar_t* p=i?L"\\\\.\\PhysicalDrive1":L"\\\\.\\PhysicalDrive0";
   SetLastError(0);HANDLE h=CreateFileW(p,GENERIC_READ,FILE_SHARE_READ|FILE_SHARE_WRITE,nullptr,OPEN_EXISTING,0,nullptr);
   DWORD e=h==INVALID_HANDLE_VALUE?GetLastError():0;
   o<<",\"physical_drive_"<<i<<"_open_error\":"<<e;
   if(h!=INVALID_HANDLE_VALUE)CloseHandle(h); // Never read disk data.
 }
 o<<",\"complete\":true}\n";return 0;
}
