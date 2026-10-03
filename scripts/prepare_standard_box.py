"""Build isolated owned probes; configure a NEW standard-feature test box only."""
import copy,hashlib,json,shutil,subprocess,ctypes
from pathlib import Path
import lab
R=lab.ROOT;sb=R/'tools'/'Sandboxie-Plus';box='PV1Lab_StandardTest';payload=R/'staging'/'owned-standard-payload'
def cli(*args):
    p=subprocess.run([str(sb/'SbieIni.exe'),*args],capture_output=True,text=True)
    if p.returncode:raise RuntimeError((args,p.returncode,p.stdout,p.stderr))
    return p.stdout.strip()
assert box not in cli('query','*').splitlines(),'refuse replace existing box'
assert not payload.exists() and not (R/'boxes'/box).exists()
rid=lab.new_run();run=R/'runs'/rid;payload.mkdir();manifest=[]
for old in lab.read(R/'control'/'vendor_payload.json'):
    src=lab.checked(Path(old['path']));assert lab.sha(src)==old['sha256']
    dst=payload/src.name;shutil.copyfile(src,dst);assert lab.sha(dst)==old['sha256'] and dst.stat().st_ino!=src.stat().st_ino
    manifest.append({'path':str(dst),'sha256':old['sha256']})
source=(R/'scripts'/'isolation_probe.cpp').read_text()
source=source.replace('owned-vendor-payload','owned-standard-payload')
source=source.replace('field("clipboard_open_ok",OpenClipboard(nullptr));CloseClipboard();','BOOL opened=OpenClipboard(nullptr);field("clipboard_open_ok",opened);field("clipboard_format_count",opened?CountClipboardFormats():-1);if(opened)CloseClipboard();')
source=source.replace('if(argc<3)return 2;bool child=argc>3;', '''if(argc<3)return 2;bool child=argc>3;
 if(std::string(argv[2])=="hold"){
   auto begin=GetTickCount64();
   while(GetTickCount64()-begin<370000){
     std::ofstream h(argv[1]);h<<"{\\\"elapsed_ms\\\":"<<(GetTickCount64()-begin)<<",\\\"pid\\\":"<<GetCurrentProcessId()<<",\\\"complete\\\":false}\\n";h.close();
     if(GetFileAttributesA("D:\\\\PV1Lab\\\\staging\\\\owned-standard-payload\\\\hold-stop.request")!=INVALID_FILE_ATTRIBUTES)return 9;
     Sleep(1000);
   }
   std::ofstream h(argv[1]);h<<"{\\\"elapsed_ms\\\":"<<(GetTickCount64()-begin)<<",\\\"pid\\\":"<<GetCurrentProcessId()<<",\\\"complete\\\":true}\\n";return 0;
 }
''')
src=R/'scripts'/'standard_probe.cpp';src.write_text(source)
cmd=R/'scripts'/'build_standard_probe.cmd'
cmd.write_text('@echo off\ncall "'+str(R/'tools'/'VS2022BuildTools'/'VC'/'Auxiliary'/'Build'/'vcvarsall.bat')+'" amd64\nif errorlevel 1 exit /b %errorlevel%\nset TEMP='+str(run/'temp')+'\nset TMP=%TEMP%\ncd /d "'+str(run/'build')+'"\ncl /nologo /std:c++20 /EHsc /MT /O2 "'+str(src)+'" /Fe:standard_probe.exe /Fo:standard_probe.obj\nexit /b %errorlevel%\n')
with (R/'reports'/'msvc_standard_probe_build.log').open('w') as log:
    p=subprocess.run([str(cmd)],stdout=log,stderr=subprocess.STDOUT);assert p.returncode==0
dst=payload/'standard_probe.exe';shutil.copyfile(run/'build'/'standard_probe.exe',dst);manifest.append({'path':str(dst),'sha256':lab.sha(dst)})
(payload/'virtual-marker.txt').write_text('HOST_CANARY_abc0b5b9')
raw_devices=[]
names=ctypes.create_unicode_buffer(65536)
assert ctypes.windll.kernel32.QueryDosDeviceW(None,names,len(names))
for name in names[:].split('\0'):
    if name.startswith('PhysicalDrive') and name[13:].isdigit():
        target=ctypes.create_unicode_buffer(4096)
        assert ctypes.windll.kernel32.QueryDosDeviceW(name,target,len(target))
        raw_devices.append(target.value)
assert raw_devices
cfg=copy.deepcopy(lab.read(R/'control'/'sandbox-effective.json')['requested'])
cfg['FileRootPath']=[str(R/'boxes'/box)]
for k in ['RestrictDevices','UseSecurityMode','SysCallLockDown','UseRuleSpecificity','UsePrivacyMode','NoSecurityIsolation','ProtectHostImages','UseSandboxDesktop','ConfidentialBox','AllowRawDiskRead','OpenDevCMApi','OpenLsaEndpoint','OpenSamEndpoint','OpenWPADEndpoint','OpenAllSysCalls']:
    cfg[k]=['n']
cfg['ClosedFilePath']=[r'D:\Pv1260909',r'C:\Users','InternetAccessDevices']+[str(p) for p in R.iterdir() if p.name not in ('tools','staging')]+[str(p) for p in (R/'tools').iterdir() if p.name!='Sandboxie-Plus']+[str(p) for p in (R/'staging').iterdir() if p!=payload]+raw_devices+[r'\Device\NamedPipe\UIA_PIPE_*']
cfg['WriteFilePath']=[r'C:\ProgramData']
cfg['ClosedIpcPath']=[r'*\BaseNamedObjects*\PV1Lab_Canary_*',r'\Device\PhysicalMemory',r'*\BaseNamedObjects*\7zCompressMapping*',r'*\BaseNamedObjects*\7zMap*',r'*\BaseNamedObjects*\UIA_CONNECT_EVENT_*',r'*\BaseNamedObjects*\UIA_PIPEREADY_EVENT_*',r'\RPC Control\OSPPCTransportEndpoint-*',r'\RPC Control\SPPCTransportEndpoint-*',r'\RPC Control\LiveIdSvc',r'\RPC Control\RasManLrpc']
cfg['ClosedIpcPath']+=raw_devices
cfg['NoSandboxieDesktop']=['n']
# No global settings are changed. Explicit CLOSED rules take precedence in standard matching.
for key,values in cfg.items():
    cli('set',box,key,values[0])
    for v in values[1:]:cli('append',box,key,v)
effective={k:cli('query',box,k).splitlines() for k in cfg}
state={'box':box,'run_id':rid,'payload':str(payload),'requested':cfg,'query':effective,'manifest':manifest,'stage':'OWNED_CPU_PROBES_ONLY','original_allowed':False,'gpu_allowed':False}
lab.save(R/'control'/'standard_box.json',state)
cli('set',box,'Enabled','y')
subprocess.run([str(sb/'Start.exe'),'/reload'],check=True)
print(json.dumps({'box':box,'run_id':rid,'mode':'owned CPU probes only'}))
