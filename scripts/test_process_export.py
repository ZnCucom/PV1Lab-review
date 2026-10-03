import json,subprocess,sys,time
from pathlib import Path
import lab
tests=lab.read(lab.ROOT/'control'/'trusted_tests.json')
tests['owned_child']={'script':'owned_child_test.py','sha256':lab.sha(lab.ROOT/'scripts'/'owned_child_test.py'),'timeout':20}
lab.save(lab.ROOT/'control'/'trusted_tests.json',tests)
rid=lab.new_run(); p,r=lab.run_record(rid)
proc=subprocess.Popen([sys.executable,'-B',str(lab.ROOT/'scripts'/'lab.py'),'run-trusted','--run',rid,'--test','owned_child'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
deadline=time.monotonic()+12
while not (p/'output'/'child_started.txt').exists():
    assert time.monotonic()<deadline,'owned child failed to start'
    assert proc.poll() is None,'manager exited early'
    time.sleep(.05)
try: lab.clean(rid)
except RuntimeError: pass
else: raise AssertionError('cleanup accepted a running child')
(p/'temp'/'stop.request').write_text('cooperative test stop')
stdout,stderr=proc.communicate(timeout=20); assert proc.returncode==0,stderr
assert (p/'output'/'child_stopped.txt').exists()
p,r=lab.run_record(rid); assert r['active_processes']==0 and r['job_total_processes']>=2
job_count=r['job_total_processes']  # bundled Python launcher may add helper processes
lab.clean(rid); assert not p.exists()
fake='PV1LAB_FAKE_SECRET_CANARY_7b826725'
data={'cuda':{'status':'PASS','frames':24,'license':fake},'token':fake,'raw_authorization':fake}
assert fake not in json.dumps(lab.sanitized_summary(data))
for bad in ({'cuda':{'status':fake,'frames':1}},{'cuda':{'status':'PASS','frames':fake}}):
    try: lab.sanitized_summary(bad)
    except RuntimeError: pass
    else: raise AssertionError('export accepted secret in typed field')
lab.save(lab.ROOT/'reports'/'process_export_tests.json',{'result':'PASS','cases':['actual descendant retains job','active cleanup refused','cooperative stop','job drains to zero','cleanup after drain','fake secret excluded','invalid enum refused','invalid number refused'],'job_processes':job_count})
print('PASS: 8 process/export cases')
