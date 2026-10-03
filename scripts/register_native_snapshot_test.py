import lab
R=lab.ROOT;t=lab.read(R/'control/trusted_tests.json')
for phase in ['before','mutate','verify']:
 p=R/'scripts'/('native_snapshot_'+phase+'.py');p.write_text('from native_snapshot_test import main\nmain('+repr(phase)+')\n')
 deps=[R/'scripts/native_snapshot_test.py',R/'control/standard_box.json',R/'staging/owned-standard-payload/standard_probe.exe',R/'reports/raw_device_rule_fix.json']
 t['native_snapshot_'+phase]={'script':p.name,'sha256':lab.sha(p),'timeout':90,'dependencies':[{'path':str(d),'sha256':lab.sha(d)} for d in deps]}
lab.save(R/'control/trusted_tests.json',t)
print(lab.new_run())
