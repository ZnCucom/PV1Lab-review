import subprocess,sys,time
from pathlib import Path
import lab
R=lab.ROOT;sb=R/'tools'/'Sandboxie-Plus';payload=R/'staging'/'owned-standard-payload';box='PV1Lab_StandardTest'
def query(k):return subprocess.check_output([str(sb/'SbieIni.exe'),'query',box,k],text=True).strip()
assert query('Enabled')=='y'
for key in ('RestrictDevices','UseSecurityMode','SysCallLockDown','UsePrivacyMode','UseRuleSpecificity','NoSecurityIsolation','ProtectHostImages'):assert query(key)=='n'
e=lab.read(R/'reports'/'standard_runtime.json');assert e['hold']['complete'] and e['hold']['elapsed_ms']>=370000
args=[str(sb/'Start.exe'),'/box:'+box,'/silent','/hide_window','/wait','/env:TEMP='+str(payload),'/env:TMP='+str(payload),'/env:CUDA_CACHE_PATH='+str(payload/'cuda-cache'),str(payload/'cuda_trt_diag.exe'),str(payload/'owned_affine.engine'),str(payload/'cuda-diag.txt')]
p=subprocess.Popen(args,cwd=payload);assert p.wait(timeout=60)==0
deadline=time.monotonic()+25
while True:
    pids=subprocess.check_output([str(sb/'Start.exe'),'/box:'+box,'/silent','/listpids'],text=True).strip()
    if pids=='0':break
    assert time.monotonic()<deadline,'live box preserved';time.sleep(1)
report=R/'boxes'/box/'drive'/'D'/'PV1Lab'/'staging'/payload.name/'cuda-diag.txt'
(R/'reports'/'standard_cuda_diag.txt').write_text(report.read_text())
