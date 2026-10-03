import lab
R=lab.ROOT;t=lab.read(R/'control/trusted_tests.json');deps=[R/'scripts/native_snapshot_test.py',R/'control/standard_box.json',R/'staging/owned-standard-payload/capture_capability_probe.exe',R/'reports/raw_device_rule_fix.json']
t['capture_capability']={'script':'capture_capability_test.py','sha256':lab.sha(R/'scripts/capture_capability_test.py'),'timeout':90,'dependencies':[{'path':str(d),'sha256':lab.sha(d)} for d in deps]};lab.save(R/'control/trusted_tests.json',t);print(lab.new_run())
