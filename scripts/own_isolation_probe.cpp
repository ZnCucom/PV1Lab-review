// Never run on host. This owned canary has no PV1 dependencies or credential access.
#include <winsock2.h>
#include <windows.h>
#include <fstream>
#include <iostream>
int main() {
  // Metadata-only directory handle, no enumeration or original file reads.
  auto h=CreateFileW(L"D:\\Pv1260909",FILE_LIST_DIRECTORY,FILE_SHARE_READ|FILE_SHARE_WRITE|FILE_SHARE_DELETE,
    nullptr,OPEN_EXISTING,FILE_FLAG_BACKUP_SEMANTICS,nullptr);
  bool originalBlocked=(h==INVALID_HANDLE_VALUE); if(!originalBlocked)CloseHandle(h);
  auto c=CreateFileW(L"D:\\PV1Lab\\control\\canaries\\must-survive.txt",GENERIC_READ,FILE_SHARE_READ,
    nullptr,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,nullptr);
  bool controlBlocked=(c==INVALID_HANDLE_VALUE); if(!controlBlocked)CloseHandle(c);
  std::ofstream("owned_virtual_write.txt")<<"PV1Lab no-license canary";
  HKEY key{}; auto rc=RegCreateKeyExW(HKEY_CURRENT_USER,L"Software\\PV1Lab_NoLicense_Probe_20260927",0,nullptr,0,KEY_SET_VALUE,nullptr,&key,nullptr);
  if(rc==ERROR_SUCCESS){DWORD value=1;RegSetValueExW(key,L"Canary",0,REG_DWORD,(const BYTE*)&value,sizeof(value));RegCloseKey(key);}
  WSADATA ws{};WSAStartup(MAKEWORD(2,2),&ws);auto sock=socket(AF_INET,SOCK_STREAM,IPPROTO_TCP);
  bool socketBlocked=(sock==INVALID_SOCKET);if(!socketBlocked)closesocket(sock);WSACleanup();
  std::cout<<"original_metadata_open_blocked="<<originalBlocked<<" control_canary_open_blocked="<<controlBlocked
           <<" registry_write_status="<<rc<<" socket_creation_blocked="<<socketBlocked<<"\n";
  // Socket creation alone is deliberately not a claim of complete offline enforcement.
  return originalBlocked&&controlBlocked?0:3;
}
