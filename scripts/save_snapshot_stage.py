import datetime
from pathlib import Path
import lab
R=lab.ROOT;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
base=lab.read(R/'reports/source_protection_continuation.json');checks=[]
for f in base['files']:
 p=Path(f['path']);h=lab.sha(p);checks.append({'path':str(p),'before_sha256':f['before_sha256'],'after_sha256':h,'unchanged':h==f['before_sha256']})
lab.save(R/'reports/source_protection_snapshot_stage.json',{'checked_utc':now,'scope':'explicit previously registered inputs only; not entire tree','files':checks,'all_unchanged':all(f['unchanged'] for f in checks)})
assert all(f['unchanged'] for f in checks),'original inputs drifted; preserve and report'
ready=lab.read(R/'control/readiness.json');ready.update(updated_utc=now,L01='REGISTERED_INPUT_REHASH_UNCHANGED',L04='NATIVE_SNAPSHOT_AND_CLIPBOARD_HANDLE_DISK_TESTS_PASS; DXGI_CAPTURE_CAPABILITY_NOT_BLOCKED',L05='NOT_READY',sandbox_native_snapshot='PASS_FILE_AND_HKCU_ALPHA_BETA_RESTORE_ALPHA',stop_reason='CURRENT_PERSONAL_DESKTOP_ISOLATION_NOT_QUALIFIED',evidence='reports/snapshot_stage_report.md')
lab.save(R/'control/readiness.json',ready)
gate=lab.read(R/'control/standard_gate.json');gate.update(updated_utc=now,native_snapshot_restore_verified=True,clipboard_handle_denial_verified=True,both_physical_disk_handles_denied=True,desktop_capture_boundary='DXGI_DUPLICATEOUTPUT_SUCCEEDED; NO_FRAME_ACQUIRED',allow_original_launch=False,allow_real_activation=False,pending=['Separate clean interactive Windows session or another actually qualified desktop boundary','Original startup/dependency/license-state audit remains partial','Retest actual input/capture boundaries and GPU in selected environment','First real execution/network user confirmation'])
lab.save(R/'control/standard_gate.json',gate)
plan='''# Proposed system action: clean local Windows test session
Status: PROPOSAL_ONLY; no account/profile/security change made.

Concrete proposed scope: one local standard user named PV1LabTest, ordinary Users group only, no Administrator membership, no Microsoft/cloud account, no auto-logon, no saved credentials. User enters any password/security answers directly in Windows UI; agent never reads, records or requests them. Windows creates its normal profile (normally C:\\Users\\PV1LabTest), user SID and registry state. These OS-owned files are an explicit exception to lab-output-only scope and require user confirmation. No original project ACL/config changes, no firewall/antivirus/driver changes, no software purchase/reinstallation. All authored scripts/reports/tool output remain D:\\PV1Lab.

Purpose: a different logon session has its own interactive window station, clipboard and desktop. This is a proposed additional boundary for personal screen/input isolation, not proof that all remaining acceptance checks pass. Do NOT use Windows Task View's virtual desktop as equivalent. Keep Sandboxie file/registry/network restrictions; account separation alone is not the application sandbox.

Manual account creation, only if user chooses this scope: Windows Settings > Accounts > Other users > Add account > I don't have this person's sign-in information > Add a user without a Microsoft account. Name PV1LabTest, choose password privately. Verify Standard User. No immediate switch is required to approve/prepare this plan. Switching sessions later can interrupt desktop tools; save task checkpoint first. Do not launch original PV1 in the new session.

Before first owned test there: prepare a dedicated new box under D:\\PV1Lab\\boxes, minimal independently copied authored payload under staging, existing global settings untouched, explicit per-user/session paths and ACL review. Do not reuse another user's live registry hive or silently share the present snapshot root. Probe config, personal/original/lab path denials, process inheritance, network, clipboard and capture boundaries, GPU, stop and native rollback in the new session. Fail closed on unexpected session/account/disk topology.

PV1 device identity may incorporate account/session data; no spoofing, unbinding or license transfer. Report any identity difference before an authorized first original session. No key requested.

Rollback: registered lab outputs can use lab cleanup only; account/profile removal is a separate Windows operation requiring explicit scope and user authorization. It will not undo system installations or server activation records. No server call occurred.

Evidence: reports/capture_capability_results.json showed DuplicateOutput HRESULT0 with all sandbox restrictions enabled. No frame acquisition attempted. Official BlockScreenCapture docs explicitly cover selected USER32/GDI paths only. Buying a supporter certificate is not established as solving this observed gap.

Sources:
https://sandboxie-plus.github.io/sandboxie-docs/Content/BlockScreenCapture/
https://learn.microsoft.com/en-us/windows/win32/winstation/window-stations
https://support.microsoft.com/en-us/windows/security/identity-signin/manage-user-accounts-in-windows
'''
(R/'reports/proposed_clean_session.md').write_text(plan,encoding='utf-8')
report='''# Snapshot and remaining boundary qualification
Updated UTC: '''+now+'''

Native formal snapshot: PASS. User created CLEAN_NO_LICENSE_STD_01 and used official Go to Snapshot after computer-use clicks failed with coordinate geometry/out-of-bounds errors. Owned file AND HKCU value observed snap-alpha -> snap-beta-3a481290e37744d0908c41c49427a1ee -> snap-alpha. Host marker unchanged, host temporary registry key absent, sandbox/Job active0. Reports native_snapshot_before.json, native_snapshot_mutate.json, native_snapshot_verify.json. No direct copy/delete of sandbox internals or hives.

Clipboard handle test: PASS within Win32 GetClipboardData(CF_UNICODETEXT) scope. Unicode format present before and after, clipboard sequence unchanged, sandbox OpenClipboard succeeds but GetClipboardData returnsNULL. No GlobalLock/dereference, no clipboard text read/printed/copied/cleared. PhysicalDrive0 and PhysicalDrive1 GENERIC_READ handles both denied error5; no disk bytes read. reports/peripheral_results.json.

Desktop capture: NOT QUALIFIED. Sandbox DXGI DuplicateOutput returnedHRESULT0 and interface present. Probe did not call AcquireNextFrame, Map or read/copy/save screen pixels. All interfaces released and process count0. This exposes a capture-capability gap despite passing own-window PrintWindow/message/process access tests. Official BlockScreenCapture covers selected USER32/GDI paths, not every capture API. Do not mark READY or execute original based on the existing box. reports/capture_capability_results.json.

Original startup audit remains PARTIAL: existing startup_flow.md records CRT/TLS initialization, Direct3D UI, reading config.txt and model scanning during initialization; relative-path/cwd and full DLL/TLS startup behavior unresolved. Static imports include TRT, TRT plugin, ORT, OpenCV, gmssl, cpr and registry/input APIs. EXE alone is staged as static input; original runtime DLLs/config/models/licenses are excluded. Thus even pre-inference startup cannot be presumed inert. Host license inheritance not fully qualified, especially unspecified machine-wide registry locations. No business services or activation.

System-action proposal: reports/proposed_clean_session.md. One standard local Windows test account/session can be evaluated without a new Windows install, GPU VM or paid certificate. It remains a proposal requiring user confirmation; no new account or ACL was created/changed. Successful session separation and identity need real retesting.

Original project: read-only throughout; same16registered input hashes rechecked unchanged in source_protection_snapshot_stage.json, not whole-tree proof. Lab control is an operating convention for Codex; sandbox denials above are separate measured enforcement. Prior actual MSVC/TensorRT own GPU pass remains valid. Local snapshots rollback only boxed file/registry state, not tools/services/driver installation, host actions or server records.
'''
(R/'reports/snapshot_stage_report.md').write_text(report,encoding='utf-8')
(R/'reports/license_readiness.md').write_text('# NOT_READY\n\nLatest evidence: snapshot_stage_report.md and control/readiness.json. Native file/HKCU restore and owned GPU passed; desktop capture remains unqualified (DXGI DuplicateOutput succeeded; no frames acquired). Original startup/license-state inheritance audit remains partial. No original/real license/service executed. Do not request keys or activate/unbind. Same-device license rule remains USER_CONFIRMED; no server validation claim.\n',encoding='utf-8')
(R/'reports/remaining_actions.md').write_text('# Current remaining work\n\n1. User decision on proposed_clean_session.md: a new standard local account/session is a system change; nothing created yet.\n2. Qualify capture/input/file/registry/network/GPU and native rollback in the selected clean session.\n3. Complete minimal original startup/dependency and license inheritance review; no original execution without first-session authorization.\n4. Only then assess readiness and request real-run/network scope; keys entered only by user in the normal PV1 UI.\n\nAlready passed: installed toolchain, true MSVC vendor, own engine host+sandbox GPU, path/registry/network/child canaries, native file+HKCU rollback, clipboard data-handle denial, both physical drive handles denied. See snapshot_stage_report.md.\n',encoding='utf-8')
with (R/'control/checkpoint.md').open('a',encoding='utf-8') as f:f.write('\n\n## Latest qualification '+now+'\nRead reports/snapshot_stage_report.md and control/readiness.json first. Native snapshot restoration PASSED file AND HKCU after user official Go to Snapshot. Clipboard handle and both disk handle denials PASSED; no clipboard text/disk bytes read. DXGI DuplicateOutput SUCCEEDED inside standard box: desktop capture NOT QUALIFIED; no frames acquired. Original remains forbidden, not READY. All last probes drained0; GPU interfaces released, no forced kill. Same16original input hashes unchanged. Current action: user must choose/authorize system scope in reports/proposed_clean_session.md (one standard local test account/session, no account created). No blanket permissions relaxed, no certificates or license requested.\n')
print('Saved reports, readiness and checkpoint. Original registered inputs unchanged:',len(checks))
