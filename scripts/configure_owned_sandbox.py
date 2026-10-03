"""Configure only PV1Lab_NoLicense using the installed official management CLI."""
import json,subprocess
from pathlib import Path
R=Path(r'D:\PV1Lab');sb=R/'tools'/'Sandboxie-Plus';box='PV1Lab_NoLicense'
raise RuntimeError('ARCHIVED DISQUALIFIED CONFIG: RestrictDevices triggers timed termination; do not re-enable. Review control/sandbox_gate.json and create a separately reviewed policy first.')
def cli(*args):
    p=subprocess.run([str(sb/'SbieIni.exe'),*args],capture_output=True,text=True)
    if p.returncode:raise RuntimeError((args,p.returncode,p.stdout,p.stderr))
    return p.stdout.strip()
if cli('query',box,'Enabled')=='n' and not (R/'boxes'/box).exists():
    # First initialization: a disabled, never-instantiated box has no processes.
    pass
else:
    pids=subprocess.run([str(sb/'Start.exe'),'/box:'+box,'/silent','/listpids'],capture_output=True,text=True)
    assert pids.returncode==0 and pids.stdout.strip()=='0',(pids.returncode,repr(pids.stdout))
cfg={
 'Enabled':['n'],'FileRootPath':[str(R/'boxes'/box)],'NeverDelete':['y'],
 'DropAdminRights':['y'],'RestrictDevices':['y'],'OpenClipboard':['n'],
 'BlockScreenCapture':['y'],'BlockInterferenceControl':['y'],'BlockNetworkFiles':['y'],
 'NetworkAccess':['Block'],'ClosedFilePath':[r'D:\Pv1260909',r'C:\Users','InternetAccessDevices']+[str(R/d) for d in ['control','scripts','downloads','cache','baselines','runs','reports','exports','boxes']]+[str(p) for p in (R/'tools').iterdir() if p.name!='Sandboxie-Plus']+[str(p) for p in (R/'staging').iterdir() if p.name!='owned-vendor-payload'],
 'WriteKeyPath':['HKEY_CURRENT_USER'],
 'ClosedIpcPath':[r'\BaseNamedObjects\PV1Lab_Canary_*'],
 'AutoRecover':['n'],'AutoDelete':['n']}
for key,values in cfg.items():
    cli('set',box,key,values[0])
    for v in values[1:]:cli('append',box,key,v)
effective={k:cli('query',box,k).splitlines() for k in cfg}
(R/'control'/'sandbox-effective.json').write_text(json.dumps({'box':box,'requested':cfg,'query':effective,'qualification':'OWNED_PROBES_ONLY'},indent=2)+'\n')
cli('set',box,'Enabled','y')
p=subprocess.run([str(sb/'Start.exe'),'/reload']);assert p.returncode==0
print(json.dumps({'configured':box,'original_execution':False,'enabled_for':'owned probes only'}))
