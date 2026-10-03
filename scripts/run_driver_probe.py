import subprocess,sys,time
from pathlib import Path
import lab
R=lab.ROOT;run=Path(sys.argv[1]);payload=R/'staging'/'owned-standard-payload';sb=R/'tools'/'Sandboxie-Plus';box='PV1Lab_StandardTest'
p=subprocess.Popen([str(payload/'driver_probe.exe'),str(run/'output'/'host-driver.txt')],cwd=run);assert p.wait(timeout=45)==0
p=subprocess.Popen([str(sb/'Start.exe'),'/box:'+box,'/silent','/hide_window','/wait','/env:TEMP='+str(payload),'/env:TMP='+str(payload),'/env:CUDA_CACHE_PATH='+str(payload/'cuda-cache'),str(payload/'driver_probe.exe'),str(payload/'boxed-driver.txt')],cwd=payload);assert p.wait(timeout=45)==0
deadline=time.monotonic()+20
while subprocess.check_output([str(sb/'Start.exe'),'/box:'+box,'/silent','/listpids'],text=True).strip()!='0':
    assert time.monotonic()<deadline,'box still live';time.sleep(1)
boxed=R/'boxes'/box/'drive'/'D'/'PV1Lab'/'staging'/payload.name/'boxed-driver.txt'
report='HOST\n'+(run/'output'/'host-driver.txt').read_text()+'\nSANDBOX\n'+boxed.read_text()
(R/'reports'/'driver_comparison.txt').write_text(report)
