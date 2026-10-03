"""Owned CPU boundary, >5min lifetime, then owned vendor GPU. No original/client/license."""
import ctypes as C,json,os,subprocess,sys,time,winreg
from pathlib import Path
import lab
R=lab.ROOT;state=lab.read(R/'control'/'standard_box.json');box=state['box'];payload=Path(state['payload']);sb=R/'tools'/'Sandboxie-Plus';run=Path(sys.argv[1])
assert run.name==state['run_id']
out=R/'boxes'/box/'drive'/'D'/'PV1Lab'/'staging'/payload.name
results={'phase':'PREFLIGHT','original_executed':False,'real_business_service_accessed':False,'license_used':False}
def save():lab.save(R/'reports'/'standard_runtime.json',dict(results,updated_unix=time.time()))
def config_check():
    for k,want in state['query'].items():
        if k=='Enabled':want=['y']
        p=subprocess.run([str(sb/'SbieIni.exe'),'query',box,k],capture_output=True,text=True)
        assert p.returncode==0 and p.stdout.strip().splitlines()==want,('config drift',k)
    for f in state['manifest']:assert lab.sha(lab.checked(Path(f['path'])))==f['sha256']
def drain():
    deadline=time.monotonic()+25
    while True:
        p=subprocess.run([str(sb/'Start.exe'),'/box:'+box,'/silent','/listpids'],capture_output=True,text=True)
        assert p.returncode==0
        nums=[int(n) for n in p.stdout.split()];assert nums and len(nums)==nums[0]+1
        if nums[0]==0:return
        if time.monotonic()>deadline:raise RuntimeError('box helpers still live; preserve without kill')
        time.sleep(1)
def launch(exe,args,limit):
    config_check();drain()
    command=[str(sb/'Start.exe'),'/box:'+box,'/silent','/hide_window','/wait','/env:TEMP='+str(payload),'/env:TMP='+str(payload),'/env:CUDA_CACHE_PATH='+str(payload/'cuda-cache'),'/env:PATH='+str(payload)+';C:\\Windows\\System32',str(payload/exe),*map(str,args)]
    p=subprocess.Popen(command,cwd=payload);results['launcher_pid']=p.pid;save()
    # Timeout never kills p or service-created sandbox processes.
    code=p.wait(timeout=limit);drain();assert code==0,('boxed program exit',exe,code)
    results['box_active_processes']=0;save()
K=C.WinDLL('kernel32',use_last_error=True);U=C.WinDLL('user32',use_last_error=True)
K.CreateEventW.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_wchar_p];K.CreateEventW.restype=C.c_void_p;K.CloseHandle.argtypes=[C.c_void_p]
keyname=r'Software\PV1Lab_Canary_abc0b5b9';created=False;event=None
try:
    config_check();drain()
    try:
        key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname);winreg.CloseKey(key);raise RuntimeError('existing host canary refused')
    except FileNotFoundError:pass
    key=winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER,keyname,0,winreg.KEY_WRITE);created=True
    winreg.SetValueEx(key,'host_only',0,winreg.REG_SZ,'HOST_CANARY_abc0b5b9');winreg.CloseKey(key)
    event=K.CreateEventW(None,True,False,r'Local\PV1Lab_Canary_abc0b5b9');assert event and C.get_last_error()!=183
    results['host_clipboard_format_count']=U.CountClipboardFormats() # metadata only, never GetClipboardData
    results['phase']='BOUNDARY_TEST';save()
    launch('standard_probe.exe',[payload/'probe-results.json','snap-alpha'],45)
    parent=lab.read(out/'probe-results.json');child=lab.read(out/'child-results.json');results['parent']=parent;results['child']=child;save()
    for p in [parent,child]:
        assert p['sbie_loaded']==1 and p['complete']
        for k in ['project_open_error','reverse_open_error','private_open_error','control_open_error','scripts_open_error','other_runs_open_error','baseline_open_error']:assert p[k]==5,(k,p[k])
        assert p['ipv4_socket_error']==p['ipv6_socket_error']==10013
        assert p['rawdisk_open_error']==5,('rawdisk handle should be denied',p['rawdisk_open_error'])
        assert p['host_registry_read_error']==2 and p['host_event_open_error'] in (2,5)
        assert p['file_value']==p['registry_value']=='snap-alpha'
        # Exact v1.18.5 guimisc.c blocks Get/Set/EmptyClipboard, but does NOT hook
        # CountClipboardFormats. Zero format-count was an invalid expectation.
        # No real clipboard content is requested. Do not promote this to a content test PASS.
        assert p['clipboard_format_count']>=0
    assert parent['child_created']==1 and parent['child_exit']==0
    assert (payload/'virtual-marker.txt').read_text()=='HOST_CANARY_abc0b5b9'
    key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,keyname);assert winreg.QueryValueEx(key,'host_only')[0]=='HOST_CANARY_abc0b5b9'
    try:winreg.QueryValueEx(key,'sandbox_value');raise RuntimeError('host registry contaminated')
    except FileNotFoundError:pass
    finally:winreg.CloseKey(key)
    results['clipboard']='FORMAT_METADATA_VISIBLE; CONTENT_BLOCK_STATIC_REVIEW_ONLY; DYNAMIC_SYNTHETIC_CONTENT_TEST_PENDING'
    results['phase']='LIFETIME_TEST_370_SECONDS_NO_GPU';save()
    launch('standard_probe.exe',[payload/'hold-results.json','hold'],410)
    hold=lab.read(out/'hold-results.json');assert hold['complete'] and hold['elapsed_ms']>=370000
    results['hold']=hold;results['phase']='OWN_ENGINE_GPU_TEST';save()
    launch('vendor_runner.exe',[payload/'pv_trt_vendor.dll',payload/'owned_affine.engine',payload/'gpu-results.json'],120)
    gpu=lab.read(out/'gpu-results.json');results['gpu']=gpu;save()
    assert gpu['status']=='PASS' and gpu['resources_released'] and not gpu['mock']
    results['phase']='CPU_LIFETIME_GPU_PASS_NATIVE_SNAPSHOT_PENDING';save()
except Exception as e:
    results['error']=str(e);results['phase']='FAILED_OR_PRESERVED';save();raise
finally:
    if event:K.CloseHandle(event)
    if created:winreg.DeleteKey(winreg.HKEY_CURRENT_USER,keyname)
    results['host_registry_canary_removed']=created;save()
