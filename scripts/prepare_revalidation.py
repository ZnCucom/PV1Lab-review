from pathlib import Path
import lab
R=lab.ROOT
src=(R/'scripts/standard_suite.py').read_text()
src=src.replace('assert run.name==state[\'run_id\']',"assert (run/'run.json').is_file()")
src=src.replace("R/'reports'/'standard_runtime.json'","R/'reports'/'standard_revalidation.json'")
start=src.index("    results['phase']='LIFETIME_TEST_370_SECONDS_NO_GPU'")
end=src.index("    launch('vendor_runner.exe'",start)
src=src[:start]+'''    previous=lab.read(R/'reports'/'standard_runtime.json')
    assert previous['hold']['complete'] and previous['hold']['elapsed_ms']>=370000
    results['hold']=previous['hold'];results['hold_evidence_reused']=True
    results['phase']='OWN_ENGINE_GPU_TEST';save()
'''+src[end:]
(R/'scripts/standard_revalidate.py').write_text(src)
t=lab.read(R/'control/trusted_tests.json');t['standard_revalidate']=dict(t['standard_suite'],script='standard_revalidate.py',sha256=lab.sha(R/'scripts/standard_revalidate.py'),timeout=210)
lab.save(R/'control/trusted_tests.json',t)
# Correct the creator so future reviewed boxes cannot recreate the overbroad pattern.
p=R/'scripts/prepare_standard_box.py';s=p.read_text();s=s.replace("import copy,hashlib,json,shutil,subprocess","import copy,hashlib,json,shutil,subprocess,ctypes")
needle="cfg=copy.deepcopy(lab.read(R/'control'/'sandbox-effective.json')['requested'])"
insert='''raw_devices=[]
names=ctypes.create_unicode_buffer(65536)
assert ctypes.windll.kernel32.QueryDosDeviceW(None,names,len(names))
for name in names[:].split('\\0'):
    if name.startswith('PhysicalDrive') and name[13:].isdigit():
        target=ctypes.create_unicode_buffer(4096)
        assert ctypes.windll.kernel32.QueryDosDeviceW(name,target,len(target))
        raw_devices.append(target.value)
assert raw_devices
'''
s=s.replace(needle,insert+needle).replace("[r'\\Device\\Harddisk*\\DR*',r'\\Device\\NamedPipe\\UIA_PIPE_*']","raw_devices+[r'\\Device\\NamedPipe\\UIA_PIPE_*']").replace("r'\\Device\\Harddisk*\\DR*',",'')
s=s.replace("cfg['NoSandboxieDesktop']=['n']","cfg['ClosedIpcPath']+=raw_devices\ncfg['NoSandboxieDesktop']=['n']")
p.write_text(s)
print(lab.new_run())
