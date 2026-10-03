"""Generate a bounded local handoff. Never read licenses, dumps, or whole source trees."""
import datetime,json,re,subprocess
from pathlib import Path
import lab
R=lab.ROOT; w=lab.workspace(); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def md(name,text): (R/name).write_text(text.strip()+'\n',encoding='utf-8')
gpu_id=lab.read(R/'control'/'gpu_run.json')['run_id']; gpu=lab.read(R/'runs'/gpu_id/'output'/'gpu_results.json')
tests=lab.read(R/'reports'/'manager_tests.json'); process=lab.read(R/'reports'/'process_export_tests.json')
protected=lab.read(R/'baselines'/'protected_inputs.json'); comparisons=[]
for item in protected:
    current=lab.sha(lab.checked(item['path'])); comparisons.append({**item,'after_sha256':current,'unchanged':current==item['sha256']})
for item in lab.read(R/'control'/'tool_acquisition.json'):
    current=lab.sha(lab.checked(item['source'])); comparisons.append({'path':item['source'],'sha256':item['observed_sha256'],'after_sha256':current,'unchanged':current==item['observed_sha256']})
lab.require(all(x['unchanged'] for x in comparisons),'protected input changed')
lab.save(R/'reports'/'source_protection.json',{'checked_utc':now,'files':comparisons,'whole_tree_verified':False})
exe=next(x for x in protected if x['path'].lower().endswith('\\pv1.exe'))
lab.save(R/'control'/'path_policy.json',{'workspace_id':w['workspace_id'],'lab':str(R),'protected_root':str(lab.PROTECTED),'main_source':w['main_source'],
 'codex_enforcement':'PROCEDURAL_ONLY; runtime grants unrestricted filesystem; no root/ACL/security changes made',
 'target_enforcement':'NOT_INSTALLED_NOT_TESTED; original launch disabled',
 'copies':'explicit manifest, independent bytes, no project/lab links',
 'sensitive':'never read, hash, copy or export existing license/token/raw authorization/dumps',
 'cleanup_guard':'registered run ID plus marker and inode; canonical path components; Windows handles held without write/delete sharing; delete by same handle',
 'unsupported':['UNC','device paths','ADS','8.3 short names','reparse points','hardlinks','unknown ownership','live/unresolved processes']})
lab.save(R/'control'/'cleanup_policy.json',{'workspace_id':w['workspace_id'],'enabled_scopes':['explicit registered ordinary runs only'],
 'cache_cleanup':'disabled until individually registered; no blanket cache removal',
 'never_delete':['lab root','control','scripts','tools','downloads/verified','downloads/quarantine','baselines','staging','reports','exports','boxes','protected project'],
 'flow':['normal cooperative stop','confirm Job Object active count zero','preview','revalidate and lock objects','delete with pinned handles'],
 'timeouts':'preserve; no process-name kill, forced GPU termination or unsafe unload',
 'snapshot':'ordinary no-license files only; Sandboxie snapshot operations through SandMan only after engine installed and processes stopped'})
lab.save(R/'control'/'host_changes.json',{'system_installs_performed':[],'driver_service_changes':[],'global_PATH_changes':False,'ACL_changes':False,'firewall_changes':False,'reboots':0,
 'host_components_used':['existing Python runtime','Windows System32 CUDA driver','existing GPU driver 610.88','Windows DirectX/system libraries','PowerShell/curl/git read-only queries'],
 'outside_lab_effects':'OS/driver caches, prefetch, signature/revocation and official download network metadata may exist; not fully traced and not undone by lab deletion',
 'registry_canary':'compiled only; not executed; no application registry rollback verified',
 'pending_system_actions':['Sandboxie Plus 1.18.5 driver/service installation by user','Visual Studio 2022 Build Tools MSVC v143 14.44 + compatible Windows SDK by user'],
 'license_used':False,'real_activation_or_unbind_service_accessed':False,'uploads':False})
matrix=[{'boundary':x,'status':'NOT_TESTED','reason':'No installed Sandboxie driver/service; candidate is disabled'} for x in [
 'host file writes redirected','staging bytes unchanged under sandbox execution','protected original directory read denied','private files read denied',
 'registry virtualization and license state noninheritance','child-process confinement','default offline enforced','clipboard','desktop/window capture',
 'input injection and global hooks','COM/IPC','GPU/device exceptions','native sandbox file+registry snapshots']]
lab.save(R/'reports'/'sandbox_validation.json',{'verdict':'ISOLATION_NOT_QUALIFIED','system_action':'REQUIRES_USER_ACTION','engine_version_candidate':'Sandboxie Plus 1.18.5','tests':matrix})
md('reports/source_protection.md',f'''
# 原工程保护与复验
原工程 `D:\\Pv1260909` 本轮按只读操作；唯一主源码 `{w['main_source']}`，路径已由用户确认。
未执行源码修改、配置修改、Git reset/clean/stash/checkout/commit/push、ACL 修改或建立工程到实验区的链接。
运行环境实际是 unrestricted filesystem；不能把操作规程说成 Windows 强制只读。

已对 {len(comparisons)} 个明确登记的原输入／恢复入口／源码节选／工具归档比对 SHA-256，全部相同。清单见 `source_protection.json`。
基线是在本轮准备副本时采集，不能证明基线之前或未登记文件完全未变化；未复验整树、.git、旧 expected 或 raw_decompiled。
仅读取少量 checkpoint、构建约束、版本头和启动契约；未重跑 R01–R05 或旧 156 项主工程测试。

恢复入口为 revision271／pause199，记录 source197／delivery198；旧记录 HEAD 为 02e190d99a3ae1670628f07696746a416d7c9097。
本轮只读 Git 得到 HEAD ed2176b7d2b41908ca36d46ff8e68915ffbbdf7e（Add R15-R24 analysis evidence and scripts），存在大量历史差异，不能继续声称旧 HEAD 就是当前源码版本。
本轮真实输入以明确路径和当前字节哈希为准；实验源码仅不完整静态节选，未创建第二套可替代主工程。

原 EXE 静态副本：`staging/original/static-only-01/Pv1.exe`，{exe['size']} bytes，SHA-256 `{exe['sha256']}`。
PE x64，资源未提供 ProductVersion/FileVersion；导入表见 `original_pe_static.txt`。它未被执行。
未复制模型、engine、原业务 DLL、用户配置、许可状态、token、授权报文或转储。
''')
md('reports/rollback_validation.md',f'''
# 回滚与清理验证
`manager_tests.json`：{tests['count']} 项 PASS；`process_export_tests.json`：8 项 PASS。
涵盖普通文件快照恢复、错误 ID、未登记 run、越界／前缀碰撞／..／UNC／设备／ADS／短名／尾点、错误 workspace marker、junction、硬链接、持有写句柄、检查期间重命名拒绝、活动进程拒绝、缺失恢复源、删除后 canary 完整。
真实自建父子进程测试：Job Object 共 {process['job_processes']} 个进程（含 Python 启动辅助进程），请求合作退出，活动数归零后才清理；没有按名称杀进程或强杀 GPU 工作线程。
GPU run `{gpu_id}` 完成后 Job Object 活动数 0。

普通快照位于受保护 baselines，恢复前验证清单，另存当前普通状态，再替换登记 run；至少保留一份 CLEAN_NO_LICENSE。
普通快照仅含登记 run 文件，不含注册表、驱动、系统配置、私人桌面、许可服务状态。
真正沙盒尚未安装，原生快照及注册表恢复为 NOT_TESTED；boxes 永远不由普通清理器递归删除。

边界：管理器是可信、单操作员流程保护，不是抗同用户恶意篡改控制清单的安全边界；异常／并发更改／锁失败保留现场。
文件句柄阻止已检查对象被重命名替换；新增未登记子对象会导致目录删除失败，可能保留部分现场，不承诺崩溃事务原子性。
TIMEOUT_PRESERVED/STARTING 异常状态须人工核实进程与资源，不自动解除清理门禁。
删除实验区不能卸载驱动、回滚 OS/GPU 缓存或撤销服务端激活／解绑记录。
''')
md('reports/toolchain_validation.md',f'''
# 工具链与自建 GPU 测试
Windows 11 Pro 10.0.26200；NVIDIA GeForce RTX 5090，driver610.88，32,607 MiB，实际 CUDA compute12.0。
已有系统 CUDA driver 可用不等于完整 Toolkit 已安装；未安装／升级 GPU 驱动。

- LLVM-MinGW20260922 UCRT：从原工具归档明确复制，匹配既有依赖 pin，实际编译／链接自建 C++17 ORT 测试成功。
- CUDA NVRTC12.9.86：包 SHA-256 与独立获取的 NVIDIA redistrib12.9.1 元数据匹配；DLL 无 Authenticode 签名，可信依据是官方归档哈希。
- ORT DirectML1.23.0／DirectML1.15.4：包匹配现有 pin；实际加载 DLL 的 Microsoft Authenticode 签名 Valid。
- 自建 CUDA kernel `y=2*x+1`：24 帧输入依赖输出通过，非法 launch 参数被拒绝，分配／module／context 已回收。
- 自建 ONNX 同一公式：CPU、DML 各 24 帧；各 3 次 session 周期、3 次错误 shape 拒绝。profiling 确认 DmlExecutionProvider 实际执行。
- 最初 NVRTC 错误为 builtins DLL 搜索路径；进程级 SetDefaultDllDirectories 配合显式目录已解决，无全局 PATH 变化。

详细数值结果：`runs/{gpu_id}/output/gpu_results.json`；编译和 provider profile 留在该 run。
状态：`OWN_MODEL_RUNTIME_VERIFIED`（CUDA/CPU/DML，宿主可信自建测试）；`TOOLCHAIN_VERIFIED` 仅上述子集。
MSVC ABI／Windows SDK 的 vendor bridge 尚未验证，MinGW 成功不替代它；TensorRT 单独见 `tensorrt_validation.md`。
原源码版本头要求 TensorRT10.10.0.31，vendor 源码 `NV_TENSORRT_VERSION==101000` 且要求 MSVC；没有改成新大版本。
原 client/model/engine/DLL 均 `TARGET_RUNTIME_NOT_EXECUTED`；自建成功不是原软件等价证据。
''')
md('reports/sandbox_validation.md','''
# 应用沙盒资格
**ISOLATION_NOT_QUALIFIED / NEEDS_USER_SYSTEM_ACTION**。
本机默认安装位置及服务名中未找到 Sandboxie；已存在 CodexSandboxService 不是 PV1 应用沙盒资格证据。
已从官方稳定链接获取 Sandboxie Plus1.18.5；完整大小／GitHub公布 digest 匹配且 Authenticode Valid。仅下载，未运行安装器、未装驱动／服务。
`control/sandboxie-candidate-v1.18.5.ini` 是禁用的审查候选；字段对照固定版本 SbieSettings.ini，未导入系统配置。
输入只拟暴露独立 staging/probe 的自建测试。原 EXE 副本仍被禁用；没有给整个 D:\\PV1Lab Direct/Open Access。

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
''')
md('reports/license_readiness.md',f'''
# 正版许可就绪情况
**NOT_READY_FOR_MANUAL_LICENSE_INPUT**，原程序与联网入口关闭。
用户持有原 PV1 正版卡密；同一设备多次激活、解绑、再次激活为 USER_CONFIRMED。次数上限／换设备许可／服务端验证未知，不扩写承诺。
不要向模型提供卡密；以后仅由用户在正常 PV1 UI 手动输入。输入期间暂停截图、UI读取及可能捕获字段的调试。现在无需输入。
真实卡密未读取／输入／使用；现有宿主 license.dat 或许可注册表状态未读取、复制或映射；真实激活／解绑服务未访问。

拟用原 EXE：SHA256 `{exe['sha256']}`，未修改静态副本，版本资源无值。
启动静态证据包含 nvinfer_10、nvinfer_plugin_10、ORT 的普通 PE 导入；启动可能先加载它们。旧启动契约还显示配置读取和模型扫描、TLS／静态初始化／动态加载顺序不完整。
因此“没有点击推理”不构成原 engine/plugin 未执行的证明；必须先补齐启动边界及必要依赖清单。
授权域名／重定向／心跳必要端点和精确网络限制尚未核验，未放行任何真实业务端点。
设备身份差异未知；不伪造、不自动解绑换绑。只有沙盒通过必要资格后才说明首次正常登录观察范围，等待一次明确确认和用户手动输入。

CLEAN_NO_LICENSE：本轮所有登记状态；QUALIFIED_NO_LICENSE：尚未达到；ACTIVATED_SENSITIVE：不存在。
未来敏感状态不纳入普通导出、基线或模型读取，.gitignore 不是访问控制。
本地回滚不能撤回服务器请求、激活/解绑记录、有效期流逝或已发送数据；解绑不是清理步骤。
''')
md('reports/remaining_actions.md','''
# 最小后续操作（本轮尚未执行）
1. **应用沙盒系统安装**：由用户运行已下载并验签的 Sandboxie-Plus-x64-v1.18.5.exe，完成管理员 UAC。安装会注册/加载 SbieDrv 内核驱动和 SbieSvc 服务，并产生系统安装／卸载／配置注册表等宿主记录；GUI 程序可选 D:\\PV1Lab\\tools\\Sandboxie-Plus，沙盒内容根后续配置为 D:\\PV1Lab\\boxes。驱动／服务和系统记录不能承诺全在实验区内。若提示重启，由用户决定和执行。先不启动 PV1，不全面放开兼容权限。
2. **MSVC vendor bridge 系统安装**：由用户运行已验签 Microsoft 的 vs_buildtools.exe（Visual Studio2022）。选择 C++ Build Tools、MSVC v143 x64/x86 14.44 系列、Windows SDK（优先10.0.26100）；保留编译器／CRT／SDK实际版本供下一轮验证。VS Installer、ProgramData缓存、Windows Kits、卸载注册表和可能 CRT 系统组件属于宿主变化。无需新增 CUDA 驱动或修改全局 PATH；不要静默重启。
3. 安装后告知“安装完成”，我再只读复验实际版本，继续自建 probe、MSVC ABI 与隔离资格测试。不需要提供 PV1 卡密。

两项可独立完成。未完成时已通过的宿主自建 CUDA/DirectML 测试仍有效，原程序执行继续关闭。
沙盒安装不保证资格自动通过：免费能力、桌面/IPC、私有路径读取和 GPU 例外仍须实测；若无法满足，不以解除限制或宿主裸跑替代。
''')
md('LAB_README.md',f'''
# PV1Lab 独立实验区
工作区 ID：`{w['workspace_id']}`；根 `D:\\PV1Lab`，原来为空的本地 NTFS 普通目录。
唯一主工程 `{w['main_source']}`，本轮只读。实验区不包含原工程／_reverse_work；未建立关联链接、映射或替代主工程。

当前：L01 完成；L02 管理器与无密钥回滚实测通过；L03 自建 CUDA/CPU/DirectML 已通过，MSVC vendor ABI 待系统工具；L04 未资格；L05/L06 未进入。
操作说明、实际边界和待用户安装事项分别见 reports 下对应报告。主入口不会运行 PV1，sandbox-snapshot 分支也保持拒绝，直到实现并验证正式接口。

PowerShell 示例（正常权限）：
```powershell
D:\\PV1Lab\\scripts\\lab.ps1 init
D:\\PV1Lab\\scripts\\lab.ps1 status
D:\\PV1Lab\\scripts\\lab.ps1 new-run
# 将 new-run 输出的 run_id 代入：
D:\\PV1Lab\\scripts\\lab.ps1 run-trusted --run <run-id> --test own_gpu
D:\\PV1Lab\\scripts\\lab.ps1 snapshot --run <run-id>
D:\\PV1Lab\\scripts\\lab.ps1 restore --run <run-id> --snapshot <snapshot-id>
D:\\PV1Lab\\scripts\\lab.ps1 preview-clean --run <run-id>
D:\\PV1Lab\\scripts\\lab.ps1 clean --run <run-id>
D:\\PV1Lab\\scripts\\lab.ps1 stop --run <run-id>
D:\\PV1Lab\\scripts\\lab.ps1 export
```
`prepare --manifest input_manifest.json` 支持明确清单复制，已完成的目的路径拒绝覆盖；新批次先审查清单、源哈希和目标父目录。
`init` 验证已存在的工作区标识，不清空／重建。`stop` 仅写合作退出请求，未知程序不承诺响应；超时保留，不自动杀进程。
清理只接受登记的 run ID；不支持任意路径删除。普通文件快照与 Sandboxie 原生文件+注册表快照严格分开。

可信测试使用现有 Codex Python Runtime（脚本有固定绝对入口），过程级 TEMP/TMP/CUDA_CACHE_PATH 指向 run。
可信准备不是沙盒，Windows/驱动缓存和日志可能在实验区外；所有本轮主动新增脚本／报告／构建／下载／复制输出均在实验区。
不自动 commit/push/上传；exports 使用固定字段白名单，假密钥 canary 已测试，不能据此保证任意未来原始报告均无敏感信息。
''')
lab.save(R/'control'/'readiness.json',{'updated_utc':now,'L01':'PASS_WITHIN_TESTED_SCOPE','L02':'PASS_WITHIN_TESTED_SCOPE','L03':'OWN_MODEL_RUNTIME_VERIFIED; MSVC_ABI_PENDING','L04':'ISOLATION_NOT_QUALIFIED','L05':'NOT_READY','L06':'NOT_EXECUTED','target_execution_enabled':False,'license_used':False})
md('control/checkpoint.md',f'''
# PV1Lab checkpoint {now}
Read LAB_README.md, control/workspace.json, control/readiness.json and reports/remaining_actions.md.
L01/L02 complete within reported scope; L03 host authored CUDA/CPU/DML passed; L04 requires user system action and full canary qualification.
Original executable/model/engine/DLL execution: NONE. True licenses/services: NONE. Main tree is procedural read-only; {len(comparisons)} explicit inputs rehashed unchanged.
Canonical main path user-confirmed: {w['main_source']}. Actual observed HEAD ed2176b7d2b41908ca36d46ff8e68915ffbbdf7e; old checkpoint HEAD differs; use current file hashes.
System installers only downloaded/signature-verified; never elevate or execute them without user completion/confirmation.
Context STATEFUL helper was attempted once and refused because this lab is not a Git repository; no Git repository created. User-required checkpoint is authoritative navigation.
All ordinary canary snapshots CLEAN_NO_LICENSE. No QUALIFIED_NO_LICENSE or ACTIVATED_SENSITIVE state exists.
Next: complete remaining independent TRT preparation if available, then user system install handoff. Revalidate installed version and effective rules before owned probes. Original launch remains hard-disabled.
No background continuation promised. Waiting timer begins only for observable actual user confirmation wait; platform pause timing UNKNOWN.
''')
print(json.dumps({'reports_written':True,'protected_inputs_unchanged':len(comparisons),'gpu_run':gpu_id}))
