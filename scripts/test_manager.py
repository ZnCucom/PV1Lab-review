"""All destructive negative fixtures are self-created inside PV1Lab."""
import json,os,subprocess,sys,time,uuid
from pathlib import Path
import lab
results=[]
def denied(name,fn):
    try: fn()
    except (RuntimeError,OSError,ValueError,TypeError) as e:
        results.append({'test':name,'result':'PASS','refusal':str(e)}); return
    raise AssertionError('unsafe acceptance: '+name)
def passed(name): results.append({'test':name,'result':'PASS'})
def main():
    rid=lab.new_run(); p,r=lab.run_record(rid)
    f=p/'output'/'canary.txt'; f.write_text('baseline-only',encoding='ascii')
    sid=lab.snapshot(rid)['snapshot_id']; f.write_text('changed',encoding='ascii')
    lab.restore(rid,sid); assert f.read_text()=='baseline-only'; passed('ordinary snapshot restore')
    denied('fake run ID',lambda:lab.clean('fake'))
    denied('unregistered UUID',lambda:lab.clean(uuid.uuid4().hex))
    for name,path in [('outside',r'D:\other\x'),('prefix collision',r'D:\PV1Lab-evil\runs\x'),('parent traversal',r'D:\PV1Lab\runs\..\control'),('UNC',r'\\server\share\x'),('device',r'\\?\D:\PV1Lab\runs\x'),('ADS',r'D:\PV1Lab\runs\x:stream'),('short',r'D:\PV1LAB~1\runs'),('trailing dot',r'D:\PV1Lab\runs\x.')]:
        denied(name,lambda path=path:lab.below(path,lab.ROOT/'runs'))
    denied('root cleanup path',lambda:lab.below(lab.ROOT,lab.ROOT))
    denied('missing restore baseline',lambda:lab.restore(rid,uuid.uuid4().hex))
    reg=lab.registry(); reg[rid]['state']='RUNNING'; lab.save(lab.ROOT/'control'/'runs.json',reg)
    denied('active process record',lambda:lab.clean(rid)); denied('restore active process',lambda:lab.restore(rid,sid))
    reg[rid]['state']='IDLE'; lab.save(lab.ROOT/'control'/'runs.json',reg)
    marker=lab.read(p/'run.json'); wrong=dict(marker,workspace_id=str(uuid.uuid4())); lab.save(p/'run.json',wrong)
    denied('wrong workspace ID marker',lambda:lab.clean(rid)); lab.save(p/'run.json',marker)
    victim=lab.ROOT/'control'/'canaries'/'must-survive.txt'; victim.write_text('canary-safe',encoding='ascii')
    link=p/'output'/'hardlink.txt'; os.link(victim,link)
    denied('hardlink object',lambda:lab.clean(rid)); link.unlink(); assert victim.read_text()=='canary-safe'
    junction=p/'output'/'junction'
    # Native PowerShell creates only this known canary junction; no original paths are linked.
    cmd="New-Item -ItemType Junction -Path '"+str(junction)+"' -Target '"+str(victim.parent)+"' | Out-Null"
    cp=subprocess.run(['powershell.exe','-NoProfile','-NonInteractive','-Command',cmd],capture_output=True,text=True)
    assert cp.returncode==0,cp.stderr
    denied('junction traversal',lambda:lab.clean(rid)); os.rmdir(junction); assert victim.read_text()=='canary-safe'
    # An actual open writer must block cleanup, independently of the registry state.
    with open(f,'ab'):
        denied('open file resource',lambda:lab.clean(rid))
    with lab.locked_tree(p):
        denied('rename while pinned',lambda:os.rename(p,p.with_name(p.name+'-replacement')))
    with open(str(f)+':hidden','w') as h: h.write('fake stream')
    denied('ADS discovered on object',lambda:lab.clean(rid)); os.remove(str(f)+':hidden')
    assert any(x['path']==str(f) for x in lab.preview(rid)); passed('cleanup preview')
    lab.clean(rid); assert not p.exists(); assert victim.read_text()=='canary-safe'; passed('registered deletion and protected canary survival')
    lab.save(lab.ROOT/'reports'/'manager_tests.json',{'results':results,'count':len(results),'scope':'self-authored canaries; no original mutations'})
    print(json.dumps({'passed':len(results),'result':'PASS'},indent=2))
if __name__=='__main__': main()
