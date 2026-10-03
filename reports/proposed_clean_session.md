# Proposed system action: clean local Windows test session
Status: PROPOSAL_ONLY; no account/profile/security change made.

Concrete proposed scope: one local standard user named PV1LabTest, ordinary Users group only, no Administrator membership, no Microsoft/cloud account, no auto-logon, no saved credentials. User enters any password/security answers directly in Windows UI; agent never reads, records or requests them. Windows creates its normal profile (normally C:\Users\PV1LabTest), user SID and registry state. These OS-owned files are an explicit exception to lab-output-only scope and require user confirmation. No original project ACL/config changes, no firewall/antivirus/driver changes, no software purchase/reinstallation. All authored scripts/reports/tool output remain D:\PV1Lab.

Purpose: a different logon session has its own interactive window station, clipboard and desktop. This is a proposed additional boundary for personal screen/input isolation, not proof that all remaining acceptance checks pass. Do NOT use Windows Task View's virtual desktop as equivalent. Keep Sandboxie file/registry/network restrictions; account separation alone is not the application sandbox.

Manual account creation, only if user chooses this scope: Windows Settings > Accounts > Other users > Add account > I don't have this person's sign-in information > Add a user without a Microsoft account. Name PV1LabTest, choose password privately. Verify Standard User. No immediate switch is required to approve/prepare this plan. Switching sessions later can interrupt desktop tools; save task checkpoint first. Do not launch original PV1 in the new session.

Before first owned test there: prepare a dedicated new box under D:\PV1Lab\boxes, minimal independently copied authored payload under staging, existing global settings untouched, explicit per-user/session paths and ACL review. Do not reuse another user's live registry hive or silently share the present snapshot root. Probe config, personal/original/lab path denials, process inheritance, network, clipboard and capture boundaries, GPU, stop and native rollback in the new session. Fail closed on unexpected session/account/disk topology.

PV1 device identity may incorporate account/session data; no spoofing, unbinding or license transfer. Report any identity difference before an authorized first original session. No key requested.

Rollback: registered lab outputs can use lab cleanup only; account/profile removal is a separate Windows operation requiring explicit scope and user authorization. It will not undo system installations or server activation records. No server call occurred.

Evidence: reports/capture_capability_results.json showed DuplicateOutput HRESULT0 with all sandbox restrictions enabled. No frame acquisition attempted. Official BlockScreenCapture docs explicitly cover selected USER32/GDI paths only. Buying a supporter certificate is not established as solving this observed gap.

Sources:
https://sandboxie-plus.github.io/sandboxie-docs/Content/BlockScreenCapture/
https://learn.microsoft.com/en-us/windows/win32/winstation/window-stations
https://support.microsoft.com/en-us/windows/security/identity-signin/manage-user-accounts-in-windows
