# 应用沙盒资格
**ISOLATION_NOT_QUALIFIED / NEEDS_USER_SYSTEM_ACTION**。
本机默认安装位置及服务名中未找到 Sandboxie；已存在 CodexSandboxService 不是 PV1 应用沙盒资格证据。
已从官方稳定链接获取 Sandboxie Plus1.18.5；完整大小／GitHub公布 digest 匹配且 Authenticode Valid。仅下载，未运行安装器、未装驱动／服务。
`control/sandboxie-candidate-v1.18.5.ini` 是禁用的审查候选；字段对照固定版本 SbieSettings.ini，未导入系统配置。
输入只拟暴露独立 staging/probe 的自建测试。原 EXE 副本仍被禁用；没有给整个 D:\PV1Lab Direct/Open Access。

所有应用级限制和原生快照均 NOT_TESTED，完整矩阵见 sandbox_validation.json。
普通目录、TEMP/TMP、Job Object 管理以及管理器清理测试均不能当作应用隔离验证。

官方注意事项：Privacy Mode 需要 supporter certificate；v1.18.5 的 UsePrivacyMode、UseSecurityMode、UseSandboxDesktop 在设置元数据中有要求，不能假定本机拥有。没有购买或启用证书。
BlockScreenCapture/BlockInterferenceControl 在该版标为实验性；UseSandboxDesktop 也需独立能力核验。能运行 GPU/GUI 不表示私人桌面安全。
NetworkAccess=Block 仅是候选规则；未验证 WFP/网络设备封锁，BlockNetworkFiles 仅针对网络文件，不能据此声称离线。

下一次安装后先核验签名／版本／SbieDrv与SbieSvc／有效规则，再仅运行自建 probe。
自建 probe 已编译，**未运行**。其原工程请求仅为无枚举目录句柄；控制区为自建 canary；注册表用全新 PV1Lab_NoLicense_Probe_20260927 键。
测试必须补齐：文件虚拟化、私人／原工程读拒绝、子进程、宿主许可状态不继承、网络出站/回环受控 canary、GUI/输入/IPC/设备与 GPU 最小例外。
原生快照使用 SandMan 的 Sandbox Tools > Snapshots Manager；进程全部退出后创建／恢复文件和注册表 canary。不捏造 CLI 快照命令，不手动改 boxes 内部状态。

官方资料：
- https://sandboxie-plus.com/downloads/
- https://sandboxie-plus.github.io/sandboxie-docs/PlusContent/privacy-mode/
- https://sandboxie-plus.github.io/sandboxie-docs/PlusContent/BoxSnapshots/
- https://sandboxie-plus.github.io/sandboxie-docs/PlusContent/WFPSupport.html
- https://github.com/sandboxie-plus/Sandboxie/blob/v1.18.5/Sandboxie/install/SbieSettings.ini
