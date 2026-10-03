#include <windows.h>
#include <d3d11.h>
#include <dxgi1_2.h>
#include <fstream>
#pragma comment(lib,"d3d11.lib")
#pragma comment(lib,"dxgi.lib")
// Tests only whether desktop duplication can be initialized. Never acquires,
// maps, reads, copies, saves or displays a frame or any user's screen pixels.
int main(int argc,char**argv){
 if(argc!=2 || !GetModuleHandleW(L"SbieDll.dll"))return 2;
 std::ofstream o(argv[1]);if(!o)return 3;
 IDXGIFactory1*f=nullptr;IDXGIAdapter1*a=nullptr;IDXGIOutput*x=nullptr;IDXGIOutput1*x1=nullptr;
 ID3D11Device*d=nullptr;ID3D11DeviceContext*c=nullptr;IDXGIOutputDuplication*dup=nullptr;
 HRESULT h=CreateDXGIFactory1(__uuidof(IDXGIFactory1),(void**)&f);
 o<<"{\"factory_hr\":"<<long(h);
 if(SUCCEEDED(h)){h=f->EnumAdapters1(0,&a);o<<",\"adapter_hr\":"<<long(h);}
 if(SUCCEEDED(h)){h=a->EnumOutputs(0,&x);o<<",\"output_hr\":"<<long(h);}
 if(SUCCEEDED(h)){h=x->QueryInterface(__uuidof(IDXGIOutput1),(void**)&x1);o<<",\"output1_hr\":"<<long(h);}
 if(SUCCEEDED(h)){h=D3D11CreateDevice(a,D3D_DRIVER_TYPE_UNKNOWN,nullptr,0,nullptr,0,D3D11_SDK_VERSION,&d,nullptr,&c);o<<",\"device_hr\":"<<long(h);}
 if(SUCCEEDED(h)){h=x1->DuplicateOutput(d,&dup);o<<",\"duplicate_output_hr\":"<<long(h);}
 o<<",\"duplication_interface_obtained\":"<<bool(dup);
 if(dup)dup->Release();if(c)c->Release();if(d)d->Release();if(x1)x1->Release();if(x)x->Release();if(a)a->Release();if(f)f->Release();
 o<<",\"frame_acquisition_attempted\":false,\"resources_released\":true}\n";return 0;
}
