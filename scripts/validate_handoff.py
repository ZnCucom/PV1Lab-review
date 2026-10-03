import ast,hashlib,json,os,zipfile
from pathlib import Path
import lab
R=lab.ROOT;checks=[]
for p in (R/'scripts').glob('*.py'): ast.parse(p.read_text(encoding='utf-8'));checks.append('syntax:'+p.name)
for p in (R/'control').glob('*.json'): lab.read(lab.checked(p))
for p in (R/'reports').glob('*.json'): lab.read(lab.checked(p))
for name in ('control','scripts','tools','downloads','cache','baselines','staging','runs','boxes','reports','exports'): lab.checked(R/name)
for rid,rec in lab.registry().items():
    lab.require(rec['state'] in ('IDLE','DELETED'),'unresolved run '+rid)
    if rec['state']=='IDLE': lab.run_record(rid)
reg=lab.read(R/'control'/'trusted_tests.json')
for name,item in reg.items():
    lab.require(lab.sha(R/'scripts'/item['script'])==item['sha256'],'test hash drift')
    for dep in item.get('dependencies',[]): lab.require(lab.sha(dep['path'])==dep['sha256'],'dependency hash drift')
source=lab.read(R/'reports'/'source_protection.json')
for item in source['files']: lab.require(lab.sha(item['path'])==item['sha256'],'protected drift')
for item in lab.read(R/'control'/'input_manifest.json')['files']:
    lab.require(lab.sha(item['destination'])==item['sha256'],'staging drift')
    a=Path(item['source']).stat();b=Path(item['destination']).stat()
    lab.require(a.st_ino!=b.st_ino and b.st_nlink==1,'nonindependent copy')
install=lab.read(R/'control'/'sandboxie_acquisition.json')
lab.require(lab.sha(R/'downloads'/'verified'/install['name'])==install['digest'].split(':',1)[1],'installer hash mismatch')
for sig in lab.read(R/'reports'/'verified_signatures.json'):
    if Path(sig['path']).name=='cudart64_12.dll':
        # NVIDIA publishes this DLL unsigned; verify the official archive hash and exact member.
        meta=lab.read(R/'downloads'/'verified'/'redistrib_12.9.1.json')['cuda_cudart']['windows-x86_64']
        archive=R/'downloads'/'verified'/'cuda_cudart-12.9.79.zip'
        lab.require(lab.sha(archive)==meta['sha256'] and archive.stat().st_size==int(meta['size']),'cudart official archive integrity')
        with zipfile.ZipFile(archive) as z:
            payload=z.read('cuda_cudart-windows-x86_64-12.9.79-archive/bin/cudart64_12.dll')
            lab.require(hashlib.sha256(payload).hexdigest()==lab.sha(sig['path']),'cudart differs from official member')
        lab.require(sig['signature']=='NotSigned','unexpected cudart signature classification')
    else: lab.require(sig['signature']=='Valid','signature failure '+sig['path'])
# Candidate keys exist in exact downloaded version; content is disabled and not qualified.
settings=(R/'downloads'/'verified'/'SbieSettings-v1.18.5.ini').read_text(encoding='utf-8-sig')
candidate=(R/'control'/'sandboxie-candidate-v1.18.5.ini').read_text()
for line in candidate.splitlines():
    if '=' in line and not line.startswith(';'): lab.require('['+line.split('=',1)[0]+']' in settings,'unsupported configuration key')
lab.require('Enabled=n' in candidate and 'OpenFilePath=' not in candidate,'candidate must remain disabled/minimal')
lab.require(not any((R/'boxes').iterdir()),'unexpected sandbox state')
checks += ['control JSON parsed','required ordinary roots checked','all registered jobs terminal','trusted source/dependency hashes','protected input hashes unchanged','staging independent bytes','installer published digest + valid signatures','unsigned cudart official archive hash and member match','fixed-version candidate keys','boxes empty / target disabled']
lab.save(R/'reports'/'handoff_validation.json',{'result':'PASS_WITHIN_TESTED_SCOPE','checks':checks,'original_execution':False,'main_tree_whole_hash_verified':False})
print(json.dumps({'result':'PASS_WITHIN_TESTED_SCOPE','checks':len(checks)}))
