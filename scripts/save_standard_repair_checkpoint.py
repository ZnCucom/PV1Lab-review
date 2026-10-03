import datetime
from pathlib import Path
import lab
R=lab.ROOT;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
# Save already obtained evidence; no launches, UI calls, configuration edits or tests.
ready={'updated_utc':now,'L01':'PREVIOUS_16_FILE_REHASH_UNCHANGED; NO_SOURCE_WRITES_THIS_CONTINUATION','L02':'PREVIOUS_MANAGEMENT_TESTS_PASS','L03':'REAL_MSVC_VENDOR_AND_OWN_ENGINE_HOST_PASS','L04':'STANDARD_OWN_GPU_AND_BOUNDARY_PASS; NATIVE_SNAPSHOT_AND_REMAINING_INTERACTION_ACCEPTANCE_PENDING','L05':'NOT_READY','L06':'NOT_EXECUTED','target_execution_enabled':False,'license_used':False,'real_business_service_accessed':False,'sandbox_gpu':'PASS_24_FRAMES_3_CYCLES_6_NEGATIVE_TESTS_REAL_VENDOR','sandbox_native_snapshot':'NOT_RUN','sandbox_enabled':True,'sandbox':'PV1Lab_StandardTest','sandbox_active_processes_last_observed':0,'stop_reason':'COMPUTER_USE_USER_ESCAPE; RESULTS_CHECKPOINTED','evidence':'reports/standard_revalidation.json'}
lab.save(R/'control/readiness.json',ready)
lab.save(R/'control/standard_gate.json',{'updated_utc':now,'box':'PV1Lab_StandardTest','allow_original_launch':False,'allow_real_activation':False,'allow_reviewed_owned_tests':True,'owned_gpu_verified':True,'five_minute_hold_verified_ms':370109,'preconditions':['No other active box processes','Requery effective settings against standard_box.json','Validate reviewed payload hashes','Resolve PhysicalDrive device names again before next run and reject unlisted devices; current names Harddisk0/DR0, Harddisk1/DR1','No hotplugged storage during tests'],'pending':['Native formal snapshot create/mutate/restore file AND HKCU proof','Dynamic synthetic clipboard-content test and remaining input/device boundary review','Original startup payload and license-state inheritance audit','Explicit first original execution/network authorization']})
report='''# Sandboxie standard box repair result

Status: owned GPU testing restored; original PV1 NOT READY. Updated UTC: '''+now+'''

The raw-device deny pattern `\\Device\\Harddisk*\\DR*` also matched filesystem paths under HarddiskVolume containing driver_probe.exe and DriverStore because the wildcard spans directories. Explicit asInvoker manifest alone did not solve it. Replaced the pattern, through official SbieIni with the box drained, with QueryDosDevice-resolved `\\Device\\Harddisk0\\DR0` and `\\Device\\Harddisk1\\DR1` in ClosedFilePath and ClosedIpcPath. All original/private/control/network rules retained. Before/after: reports/raw_device_rule_fix.json. Creator script corrected. New device/hotplug requires re-enumeration before more tests; full device namespace has not been exhaustively qualified.

After the rule fix: driver_probe launched normally; host and sandbox nvcuda loading, cuInit, cuDeviceGetCount succeeded, one GPU. Evidence: reports/driver_comparison.txt; run 8c27e86b4114497cb7a55f0243892758.

Boundary regression and real vendor TensorRT passed: 24 frames, 3 cycles, 6 negative inputs; mock=false, resources released, sandbox process count0 and Job active0. Run c658f2b36aa84e16a0a1d0ced6438f6b; reports/standard_revalidation.json. Parent and child could not open original root/_reverse_work, personal directory, control/scripts/runs/baselines; IPv4/IPv6 sockets denied; host fake registry and event unavailable; writes virtualized; PhysicalDrive0 read-access handle denied. Current PhysicalDrive1 is configured denied but was not separately opened. Earlier own hidden-window/process-access probe is still relevant: reports/standard_ui_results.json. No actual user window pixels/input/clipboard contents read.

The standard box completed a prior 370109ms hold naturally. Its certificate-relevant settings are unchanged, so that evidence is reused. Old PV1Lab_NoLicense remains disabled and is NOT cleared by this test. No purchase or certificate was required for the standard owned tests. No five-minute guarantee is claimed for other configurations.

Native snapshots are still untested; ordinary run snapshots are not native Sandboxie snapshots. Computer Use reported user physical Escape; all UI actions stopped. Next manual step: in Sandboxie main window select PV1Lab_StandardTest and open its official snapshots manager; with all sandbox processes stopped create CLEAN_NO_LICENSE_STD_01. If no snapshot command is visible, report the actual UI. Do not manually copy/delete the internal sandbox directory or registry hive. After baseline creation, the next task can change only owned file/HKCU canaries, then use formal restore and compare both.

Original PV1, original models/engine/plugins, licenses and business services were never executed/accessed by this continuation. No original source/config/git writes, no links, no credentials requested/read. Prior16-file hash verification remains the last original protection check; this repair did not rehash the whole tree. System driver/service/toolchain installations remain host changes; folder deletion does not uninstall them or reverse server events. No server activation occurred.
'''
(R/'reports/standard_repair_report.md').write_text(report,encoding='utf-8')
cp='''# PV1Lab current checkpoint
Updated UTC: '''+now+'''
Workspace ID: abc0b5b9-f529-47a0-9479-b65924072bf6
State: OWNED_STANDARD_GPU_PASS; ORIGINAL_NOT_READY; COMPUTER_USE_STOPPED_BY_USER_ESCAPE.

Read reports/standard_repair_report.md, control/readiness.json, control/standard_gate.json, reports/standard_revalidation.json first. These supersede the old supporter/GUI-only conclusion. Historical reports/continuation* and control/sandbox_gate.json describe the disabled PV1Lab_NoLicense box only.

Current box PV1Lab_StandardTest is enabled for reviewed OWNED tests only; last observed sandbox process count0, job active0. Driver launch and CUDA initialization fixed by replacing overbroad raw-device wildcard with resolved physical device paths. Official config before/after saved. asInvoker manifest was tried first and did not fix the issue by itself. Creator script corrected. Re-enumerate raw physical device names before subsequent tests and refuse changed/unlisted devices; do not attach storage mid-test. Current configured paths Harddisk0/DR0 and Harddisk1/DR1; actual raw-handle negative probe covers PhysicalDrive0 only.

Real sandbox vendor GPU passed24frames,3cycles,6negative tests,mock=false,resources released. Boundary parent/child regression passed. Earlier370109ms lifetime test reused because relevant settings unchanged. UI own-canary probe granted host process access0, title/message/PrintWindow denied. Clipboard format count visible; actual user content never read and synthetic content test still pending. Exact standard config in control/standard_box.json is the preparation/effective-rule manifest; its initial stage booleans are historical, current status is control/standard_gate.json.

Remaining: formal native Sandboxie snapshots create/mutate/restore verify BOTH own file and HKCU; remaining clipboard/input/device qualification; original startup/license-state inheritance audit; later first real run/network user confirmation. No READY_FOR_MANUAL_LICENSE_INPUT. Do not execute original, activate/unbind, copy/read host licenses or ask for keys. No private uploads. Unique main source D:\\Pv1260909\\_reverse_work\\reconstructed\\native remains read-only; all output lab. Prior16 protected-input hashes unchanged; no whole-tree equality claim.

Computer Use returned explicit physical Escape stop. Do not call further Computer Use in this turn. No GPU workers remain and none were force-killed. Earlier failed launch cleanup used official box terminate only after each PID verified installed Sandboxie helper; no name-wide kills. Next user action: open official snapshots manager for PV1Lab_StandardTest and create CLEAN_NO_LICENSE_STD_01 with processes0, or later explicitly resume GUI control. Native contents/hives must never be copied/deleted manually.

Installed Sandboxie Plus1.18.5, driver5.73.2/service5.73.5; VS17.14.41,MSVC14.44.35207,SDK10.0.26100.0; host MSVC vendor tests already passed. No system changes by this repair other than this box config; no originals/services/keys used. Local rollback cannot undo system installations/server events. No timer or background work promised.
'''
(R/'control/checkpoint.md').write_text(cp,encoding='utf-8')
print('Saved readiness, standard gate, repair report and checkpoint. No processes launched.')
