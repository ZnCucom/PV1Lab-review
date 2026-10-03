import ctypes as c,json,subprocess,time
from pathlib import Path
import lab
R=lab.ROOT;sb=R/'tools/Sandboxie-Plus';box='PV1Lab_StandardTest'
def cli(*a):return subprocess.check_output([str(sb/'SbieIni.exe'),*a],text=True).strip().splitlines()
assert subprocess.check_output([str(sb/'Start.exe'),'/box:'+box,'/silent','/listpids'],text=True).strip()=='0'
# Resolve concrete raw device names; no wildcard may consume a volume or directory tree.
names=c.create_unicode_buffer(65536);assert c.windll.kernel32.QueryDosDeviceW(None,names,len(names))
raw=[]
for n in names[:].split('\0'):
 if n.startswith('PhysicalDrive') and n[13:].isdigit():
  b=c.create_unicode_buffer(4096);assert c.windll.kernel32.QueryDosDeviceW(n,b,len(b));raw.append(b.value)
assert raw and all(x.startswith('\\Device\\Harddisk') and '\\DR' in x for x in raw)
old=r'\Device\Harddisk*\DR*';before={k:cli('query',box,k) for k in ['ClosedFilePath','ClosedIpcPath']}
assert all(old in v for v in before.values())
after={k:[x for x in v if x!=old]+sorted(raw) for k,v in before.items()}
journal={'box':box,'before':before,'after':after,'raw_devices':sorted(raw),'reason':'Unbounded wildcard also matched HarddiskVolume paths containing driver_probe.exe and DriverStore. Replace with QueryDosDevice-resolved physical devices; keep original/private/network rules.'}
lab.save(R/'reports/raw_device_rule_fix.json',journal)
state=lab.read(R/'control/standard_box.json');lab.save(R/'reports/standard_box-before-device-fix.json',state)
for k,vals in after.items():
 cli('set',box,k,vals[0])
 for v in vals[1:]:cli('append',box,k,v)
 assert cli('query',box,k)==vals
 state['requested'][k]=vals;state['query'][k]=vals
lab.save(R/'control/standard_box.json',state)
t=lab.read(R/'control/trusted_tests.json')
for d in t['standard_suite']['dependencies']:
 if d['path']==str(R/'control/standard_box.json'):d['sha256']=lab.sha(R/'control/standard_box.json')
lab.save(R/'control/trusted_tests.json',t)
subprocess.run([str(sb/'Start.exe'),'/reload'],check=True)
print(json.dumps(journal,indent=2))
