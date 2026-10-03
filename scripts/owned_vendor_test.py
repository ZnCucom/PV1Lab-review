import json,os,subprocess,sys
from pathlib import Path
run=Path(sys.argv[1]);payload=Path(r'D:\PV1Lab\staging\owned-vendor-payload')
report=run/'output'/'vendor_results.json'
env=dict(os.environ,PATH=str(payload)+os.pathsep+r'C:\Windows\System32')
with (run/'output'/'vendor_stdout.log').open('w') as log:
    p=subprocess.Popen([str(payload/'vendor_runner.exe'),str(payload/'pv_trt_vendor.dll'),str(payload/'owned_affine.engine'),str(report)],cwd=run/'build',env=env,stdout=log,stderr=subprocess.STDOUT)
    # The outer Job Object manager owns timeout/preservation; never force-kill GPU work.
    code=p.wait()
data=json.loads(report.read_text())
assert code==0 and data['status']=='PASS' and not data['mock'] and data['resources_released'],data
