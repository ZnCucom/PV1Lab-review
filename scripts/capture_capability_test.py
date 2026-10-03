import subprocess,sys
from pathlib import Path
import lab
from native_snapshot_test import preflight,drain,R,SB,BOX,P
run=Path(sys.argv[1]);preflight();drain();name='capture-capability-'+run.name+'.json'
p=subprocess.Popen([str(SB/'Start.exe'),'/box:'+BOX,'/silent','/hide_window','/wait','/env:TEMP='+str(P),'/env:TMP='+str(P),str(P/'capture_capability_probe.exe'),str(P/name)],cwd=P)
assert p.wait(timeout=45)==0;drain()
r=lab.read(R/'boxes'/BOX/'drive/D/PV1Lab/staging/owned-standard-payload'/name)
r.update(run_id=run.name,box_active_processes=0,scope='DuplicateOutput interface creation only, no AcquireNextFrame or pixel access',isolation_status='NOT_BLOCKED_AT_INTERFACE_CREATION' if r['duplication_interface_obtained'] else 'DENIED_OR_UNAVAILABLE')
lab.save(R/'reports/capture_capability_results.json',r)
assert r['resources_released'] and not r['frame_acquisition_attempted']
