"""Exercise only owned file/HKCU canaries. Snapshot changes use SandMan UI separately."""
import ctypes as C,subprocess,sys,time,winreg
from pathlib import Path
import lab
R=lab.ROOT; BOX='PV1Lab_StandardTest'; SB=R/'tools/Sandboxie-Plus'; P=R/'staging/owned-standard-payload'
def preflight():
    state=lab.read(R/'control/standard_box.json')
    for k,v in state['query'].items():
        want=['y'] if k=='Enabled' else v
        actual=subprocess.check_output([str(SB/'SbieIni.exe'),'query',BOX,k],text=True).strip().splitlines()
        assert actual==want,('configuration changed',k)
    for f in state['manifest']:assert lab.sha(lab.checked(Path(f['path'])))==f['sha256']
    buf=C.create_unicode_buffer(65536);assert C.windll.kernel32.QueryDosDeviceW(None,buf,len(buf))
    raw=[]
    for name in buf[:].split('\0'):
        if name.startswith('PhysicalDrive') and name[13:].isdigit():
            target=C.create_unicode_buffer(4096);assert C.windll.kernel32.QueryDosDeviceW(name,target,len(target))
            raw.append(target.value)
    assert raw and sorted(raw)==lab.read(R/'reports/raw_device_rule_fix.json')['raw_devices'],'disk topology changed'
    return raw
def drain():
    deadline=time.monotonic()+25
    while True:
        ids=subprocess.check_output([str(SB/'Start.exe'),'/box:'+BOX,'/silent','/listpids'],text=True).split()
        assert ids and len(ids)==int(ids[0])+1
        if ids==['0']:return
        assert time.monotonic()<deadline,'live processes preserved'
        time.sleep(.5)
def main(phase):
    run=Path(sys.argv[1]);assert (run/'run.json').is_file()
    try:
        raw=preflight();drain()
        meta=(R/'boxes'/BOX/'Snapshots.ini').read_text(encoding='utf-8-sig')
        assert 'Name=CLEAN_NO_LICENSE_STD_01' in meta and '[Snapshot_1]' in meta
        if phase=='mutate':assert lab.read(R/'reports/native_snapshot_before.json')['status']=='PASS'
        if phase=='verify':assert lab.read(R/'reports/native_snapshot_mutate.json')['status']=='PASS'
        filename='native-'+phase+'-'+run.name+'.json'
        value='snap-beta-'+run.name if phase=='mutate' else 'read'
        cmd=[str(SB/'Start.exe'),'/box:'+BOX,'/silent','/hide_window','/wait','/env:TEMP='+str(P),'/env:TMP='+str(P),str(P/'standard_probe.exe'),str(P/filename),value]
        proc=subprocess.Popen(cmd,cwd=P);assert proc.wait(timeout=45)==0;drain()
        result=lab.read(R/'boxes'/BOX/'drive/D/PV1Lab/staging/owned-standard-payload'/filename)
        expect=value if phase=='mutate' else 'snap-alpha'
        assert result['complete'] and result['sbie_loaded'] and result['child_exit']==0
        assert result['file_value']==result['registry_value']==expect,result
        assert (P/'virtual-marker.txt').read_text()=='HOST_CANARY_abc0b5b9'
        try:
            key=winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\PV1Lab_Canary_abc0b5b9');winreg.CloseKey(key)
            raise AssertionError('host canary unexpectedly exists')
        except FileNotFoundError:pass
        lab.save(R/'reports'/('native_snapshot_'+phase+'.json'),{'status':'PASS','run_id':run.name,'file':result['file_value'],'registry':result['registry_value'],'host_unchanged':True,'box_active_processes':0,'raw_devices':raw,'snapshot':'CLEAN_NO_LICENSE_STD_01','phase':phase,'time':time.time()})
    except Exception as e:
        lab.save(R/'reports'/('native_snapshot_'+phase+'_error.json'),{'error':str(e),'phase':phase});raise
