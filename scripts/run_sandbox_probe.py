import ctypes as C,json,subprocess,sys,time,winreg
from pathlib import Path
R=Path(r'D:\PV1Lab');sb=R/'tools'/'Sandboxie-Plus';payload=R/'staging'/'owned-vendor-payload';keyname=r'Software\PV1Lab_Canary_abc0b5b9'
assert json.loads((R/'control'/'sandbox_gate.json').read_text())['allow_owned_probe_launch'], 'Sandbox probes are stopped; review gate and qualification before any launch'
log=R/'reports'/'sandbox_probe_launch.json';state={'box':'PV1Lab_NoLicense','original_executed':False,'real_network_requests':False}
def save():log.write_text(json.dumps(state,indent=2)+'\n')
try:
    key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname);winreg.CloseKey(key);raise RuntimeError('Host canary key already exists; refuse overwrite')
except FileNotFoundError:pass
for p in [R/'control'/'isolation-canary.txt',payload/'virtual-marker.txt']:
    assert not p.exists(),str(p)
    p.write_text('HOST_CANARY_abc0b5b9',encoding='ascii')
key=winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,keyname,0,winreg.KEY_WRITE)
winreg.SetValueEx(key,'host_only',0,winreg.REG_SZ,'HOST_CANARY_abc0b5b9');winreg.CloseKey(key)
K=C.WinDLL('kernel32',use_last_error=True);K.CreateEventW.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_wchar_p];K.CreateEventW.restype=C.c_void_p;K.CloseHandle.argtypes=[C.c_void_p]
event=K.CreateEventW(None,True,False,r'Local\PV1Lab_Canary_abc0b5b9');assert event and C.get_last_error()!=183
try:
    args=[str(sb/'Start.exe'),'/box:PV1Lab_NoLicense','/silent','/hide_window','/wait','/env:TEMP='+str(payload),'/env:TMP='+str(payload),'/env:CUDA_CACHE_PATH='+str(payload/'cuda-cache'),str(payload/'isolation_probe.exe'),str(payload/'probe-results.json'),'snap-alpha']
    proc=subprocess.Popen(args,cwd=payload);state.update(launcher_pid=proc.pid,state='RUNNING');save()
    try:state['exit_code']=proc.wait(timeout=45)
    except subprocess.TimeoutExpired:state['state']='TIMEOUT_PRESERVED';save();raise
    pids=subprocess.run([str(sb/'Start.exe'),'/box:PV1Lab_NoLicense','/silent','/listpids'],capture_output=True,text=True)
    state.update(state='EXITED',box_pids_stdout=pids.stdout,box_pids_exit=pids.returncode)
    state['host_file_unchanged']=(payload/'virtual-marker.txt').read_text()=='HOST_CANARY_abc0b5b9'
    key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname);state['host_registry_unchanged']=winreg.QueryValueEx(key,'host_only')[0]=='HOST_CANARY_abc0b5b9'
    try:winreg.QueryValueEx(key,'sandbox_value');state['host_registry_contaminated']=True
    except FileNotFoundError:state['host_registry_contaminated']=False
    winreg.CloseKey(key);save();print(json.dumps(state,indent=2))
finally:
    K.CloseHandle(event)
    # Only the newly created and uniquely named host canary key is removed.
    winreg.DeleteKey(winreg.HKEY_CURRENT_USER,keyname)
    state['host_registry_canary_removed']=True;save()
