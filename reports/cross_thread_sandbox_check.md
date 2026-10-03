# Cross-task sandbox check

Read-only review requested by user after another task configured "sandbox".

- Reviewed task: 检查 Sandbox 配置状态, ID 01a0e38f-0dfd-7121-b7b0-c40427468187. It changed Codex config.toml defaults, not the Sandboxie PV1 box. Its final answer explicitly did not confirm the 5-minute warning could be ignored.
- Current config.toml selected values: sandbox_mode=workspace-write, approval_policy=on-request, windows.sandbox=elevated.
- Actual current task runtime still declares danger-full-access, approval_policy=never, network enabled. Disk defaults do not establish this running task's enforcement.
- Sandboxie SbieSvc and SbieDrv are Running. PV1Lab_NoLicense Enabled=n, FileRootPath=D:\PV1Lab\boxes\PV1Lab_NoLicense, RestrictDevices=y. DefaultBox Enabled=y; official /listpids returned 0. No owned isolation_probe or vendor_runner process was found. No original or GPU program launched for this review.
- No supporter certificate contents were read. No current valid entitlement or completed unrestricted runtime qualification was established. RestrictDevices remains a certificate-gated setting, so the 5-minute condition cannot be declared resolved.
- Global templates now include 7zipShellEx, Edge_Fix, OfficeLicensing, OnScreenKeyboard, WindowsLive and WindowsRasMan. The installed OfficeLicensing template opens two Windows/Office licensing RPC endpoint patterns. This is NOT proof of PV1 license mapping, but changes the effective IPC policy and requires re-review. Earlier canary results apply only to their tested configuration.

Conclusion: the 5-minute issue may be deferred while the PV1 box stays disabled and work is limited to trusted host-side development/build/static checks. It must not be ignored for running the original client, activation, or GPU workloads in the box. NOT_READY remains unchanged. No purchase, certificate entry, config changes, or sandbox launch was performed.

For this lab, simply choosing workspace-write with D:\Pv1260909 as the writable project would not express the requested original-read-only/lab-writable split. Any future Codex permission change needs writable scope D:\PV1Lab and separately reviewed read-only original inputs. This review did not change permissions.
