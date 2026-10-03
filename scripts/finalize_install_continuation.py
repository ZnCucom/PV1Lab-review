"""Finalize observed, no-license continuation evidence. Does not launch any sandbox program."""
import datetime,hashlib,json,subprocess
from pathlib import Path
R=Path(r'D:\PV1Lab');sb=R/'tools'/'Sandboxie-Plus';now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def cli(*args):
    p=subprocess.run([str(sb/'SbieIni.exe'),*args],capture_output=True,text=True);assert p.returncode==0;return p.stdout.strip()
assert cli('query','PV1Lab_NoLicense','Enabled')=='n'
# /listpids rejects a disabled box. The box was observed empty BEFORE disabling;
# retain that actual observation, and check owned canary processes separately.
processes=subprocess.run(['powershell','-NoProfile','-Command',"@(Get-Process -Name isolation_probe,vendor_runner -ErrorAction SilentlyContinue).Count"],capture_output=True,text=True)
assert processes.returncode==0 and processes.stdout.strip()=='0'
runs=read(R/'control'/'runs.json');assert all(v['state'] in ('IDLE','DELETED') for v in runs.values()),'unresolved registered run'
original=read(R/'reports'/'source_protection.json');checked=[]
for f in original['files']:
    p=Path(f['path']);after=digest(p);checked.append({'path':str(p),'before_sha256':f['sha256'],'after_sha256':after,'unchanged':after==f['sha256']})
for f in read(R/'control'/'vendor_build.json')['sources']:
    if not any(v['path']==f['source'] for v in checked):
        p=Path(f['source']);after=digest(p);checked.append({'path':str(p),'before_sha256':f['sha256'],'after_sha256':after,'unchanged':after==f['sha256']})
assert all(v['unchanged'] for v in checked),'protected input changed: report separately'
save(R/'reports'/'source_protection_continuation.json',{'checked_utc':now,'scope':'explicit baseline and vendor inputs only, not a whole-tree equivalence proof','files':checked})
base=R/'boxes'/'PV1Lab_NoLicense'/'drive'/'D'/'PV1Lab'/'staging'/'owned-vendor-payload'
parent=read(base/'probe-results.json');child=read(base/'child-results.json')
assert parent['sbie_loaded']==child['sbie_loaded']==1 and parent['child_exit']==0
denied=['project_open_error','reverse_open_error','private_open_error','control_open_error','scripts_open_error','other_runs_open_error','baseline_open_error']
assert all(p[k]==5 for p in [parent,child] for k in denied)
assert all(p['ipv4_socket_error']==p['ipv6_socket_error']==10013 for p in [parent,child])
launch=read(R/'reports'/'sandbox_probe_launch.json')
assert launch['host_file_unchanged'] and launch['host_registry_unchanged'] and not launch['host_registry_contaminated'] and launch['host_registry_canary_removed']
save(R/'reports'/'sandbox_canary_observations.json',{'parent':parent,'child':child,'launcher':launch,'later_box_process_count':0,'box_enabled_at_stop':False,'no_actual_clipboard_data_read':True,'no_raw_disk_bytes_read':True,'qualification':'FAILED_OR_INCOMPLETE'})
vendor=read(R/'runs'/'87482c17836c48b4a4240b3ccd61fc21'/'output'/'vendor_results.json')
assert vendor['status']=='PASS' and not vendor['mock'] and vendor['resources_released']
save(R/'reports'/'msvc_vendor_results.json',vendor)
components=read(R/'reports'/'system_install'/'installed_components.json');assert all(v['signature']=='Valid' for v in components)
vs=read(R/'reports'/'system_install'/'vs_required_components.json');assert len(vs)==1 and vs[0]['isComplete'] and vs[0]['isLaunchable']
for component in ['Sandboxie','BuildTools']:assert read(R/'control'/('install-'+component+'.json'))['exit_code']==0
state={'updated_utc':now,'L01':'PASS_WITHIN_REHASHED_SCOPE','L02':'PREVIOUS_MANAGEMENT_TESTS_PASS_NO_RETEST_NEEDED','L03':'REAL_MSVC_VENDOR_BUILD_AND_OWN_ENGINE_HOST_RUNTIME_PASS','L04':'ISOLATION_NOT_QUALIFIED: supporter timed termination + incomplete device/desktop/clipboard/native-snapshot tests','L05':'NOT_READY','L06':'NOT_EXECUTED','stop_reason':'USER_INSTRUCTED_STOP_IF_GUI_UNCONTROLLABLE','target_execution_enabled':False,'license_used':False,'real_business_service_accessed':False,'sandbox_gpu':'NOT_RUN','sandbox_native_snapshot':'NOT_RUN','sandbox_enabled':False,'sandbox_active_processes_at_disable':0}
save(R/'control'/'readiness.json',state);save(R/'reports'/'final_status.json',state)
summary={'timestamp':now,'installations':'BOTH_EXIT_0_VERIFIED','msvc_vendor_host':vendor,'sandbox':'DISABLED_NOT_QUALIFIED','source_files_rehashed':len(checked),'source_files_unchanged':True,'gui':'Only empty notification target was exposed; activation failed. Visible wizard not targetable.','license_used':False,'real_business_service_accessed':False}
save(R/'reports'/'continuation_results.json',summary)
save(R/'exports'/'installation-continuation-status.json',summary)
(R/'control'/'checkpoint.md').write_text(f'''# PV1Lab current checkpoint
Updated UTC: {now}
Workspace ID: abc0b5b9-f529-47a0-9479-b65924072bf6
State: STOPPED_AT_GUI_AND_SUPPORTER_FEATURE_BOUNDARY; NOT_READY.

Read reports/continuation_results.json, reports/continuation_report.md, control/readiness.json, control/sandbox_gate.json, control/host_changes.json first. Earlier pre-install reports are historical; this checkpoint supersedes them.

User authorized Sandboxie Plus1.18.5 and VS2022 Build Tools system installation. Both exited0, normal installer self-elevation only, Codex caller remained non-admin. No reboot requested/performed. Sandboxie driver5.73.2/service5.73.5 Running. VS17.14.41,MSVC14.44.35207,cl19.44.35229,SDK10.0.26100.0 validated. Installer/signature/version evidence in reports/system_install and control/install-*.json.

Unique main source remains D:\\Pv1260909\\_reverse_work\\reconstructed\\native, USER_CONFIRMED. Entire original tree read-only by operating convention for Codex. {len(checked)} explicit protected files rehashed unchanged. No original executable, original engine/model/plugin execution. No source/git/config modifications or links to lab. Independent source stage and true MSVC vendor build provenance control/vendor_build.json. Run87482c17836c48b4a4240b3ccd61fc21 passed own TensorRT engine24frames,3cycles,6negative cases,mock=false,resources released,Job active0. Previous own CUDA/CPU/DML/TRT Python tests still valid.

PV1Lab_NoLicense canary parent/child passed project/private/control/scripts/runs/baseline access denial, filesystem+HKCU virtualization,IPv4/v6 socket denial. No external request made. Unique host registry canary removed. Rawdisk handle open succeeded (no data read); clipboard Open succeeded but data not read, isolation therefore unproven. RestrictDevices uses supporter-only feature: user screenshot and exact1.18.5 drv/process.c confirm5min scheduled termination; bundled setting metadata omitted requirement. Do not run GPU under timed configuration. Native sandbox snapshots/restores NOT performed. All sandbox processes reached0 before Enabled=n. Probe/config scripts now hard-gated. Do not re-enable this rejected configuration.

User confirmed Sandboxie PERSONAL_NONCOMMERCIAL. Ordinary GUI handling with computer-use explicitly authorized; user instructed stop if GUI cannot be handled. sky exposed only empty Sandboxie notifications window397704; activation failed; user's visible Setup Wizard/supporter dialog not targetable. Do not repeat same failed UI loop without changed state. SandMan may remain open for user; installed service/driver intentionally remain installed. No actual UAC wait pending; no Allow timer or background work claimed.

Next: user dismisses/finishes current first-run UI to expose normal Sandboxie main window, then re-evaluate GUI availability. Separately design/review standard-feature access rules or user-supplied official entitlement WITHOUT requesting/reading its secret or buying anything. Do not remove security restrictions merely to suppress the warning. Run owned canaries first, then GPU only after no timed termination. Native snapshots only formal management UI/API after all processes stop. Keep original launch/real activation disabled until all criteria and later first-run authorization. No keys or services used; no unbind. Local rollback never undoes server records or system installations.
''',encoding='utf-8')
(R/'reports'/'continuation_report.md').write_text(f'''# 本轮续接验收
时间：{now}。结论：已完成两项授权安装和真实 MSVC vendor 运行验证；应用沙盒未资格，按用户“GUI 无法处理则停止”的规则保存并停止。

## 已完成
- Sandboxie Plus1.18.5安装退出0；SbieSvc5.73.5、SbieDrv5.73.2运行中，数字签名有效。三个版本分别记录，不混写。
- VS2022 Build Tools17.14.41安装退出0；官方vswhere要求MSVC与SDK组件查询通过；v143目录14.44.35207，cl19.44.35229，link14.44.35229，Windows SDK10.0.26100.0。只请求VCTools工作负载、MSVC x64/x86和SDK及其必需依赖，未请求推荐组件或其他workload。
- 当前主工程两份明确源码以独立字节复制到staging，用MSVC /MT真实编译vendor DLL；没有mock或syntax宏。自建engine经C ABI执行24帧、3次生命周期、6个负例；resources_released=true，Job active=0。日志和结果分别见msvc_vendor_build.log与msvc_vendor_results.json。
- 原工程{len(checked)}个明确输入本轮复验哈希一致；范围见source_protection_continuation.json。没有声称扫描或证明整棵原目录完全不变。

## 沙盒实际结果
- 父进程及直接创建的子进程均加载SbieDll，并对原工程、整个_reverse_work、C:\\Users\\REDACTED_USER、控制文件、scripts、runs、baselines返回ERROR_ACCESS_DENIED(5)。这些是实际强制拒绝，不只是目录约定。
- 自建文件写入重定向到boxes内，宿主原标记不变。自建HKCU宿主标记在沙盒不可见，沙盒写入不污染宿主；新建宿主测试key已删除。
- IPv4和IPv6 socket创建均WSAEACCES(10013)，没有发出连接或业务请求。结果仅覆盖这些API，不能泛化为全部网络通道审计完成。
- 专用宿主Event不可见；尚非全部IPC/COM/RPC边界证明。
- 原始磁盘句柄可打开，但未读取任何字节：设备边界不合格。OpenClipboard成功可能是沙盒剪贴板，未读任何内容，不能据此判定隔离通过或泄漏。
- 桌面、输入、完整剪贴板、其他IPC、沙盒GPU兼容、原生快照/恢复尚未完成。已存在的普通run文件快照不等于Sandboxie原生快照。

## 当前阻塞与安全停止
用户截图显示RestrictDevices支持者功能提示。官方对应源码Sandboxie/core/drv/process.c说明缺少相应证书时安排5分钟后终止进程，安装附带SbieSettings.ini未标注这项要求。未购买、未请求证书正文、未绕过限制。未在此配置中运行GPU，避免计时终止GPU工作。
https://github.com/sandboxie-plus/Sandboxie/blob/v1.18.5/Sandboxie/core/drv/process.c
沙盒进程曾在启动器刚退出时剩2个Sandboxie辅助进程，稍后自然退出到0；确认0后Enabled=n。没有按进程名终止任何程序，没有强杀GPU。脚本硬门禁阻止重用此失格配置。
用户确认个人非商业用途。computer-use只能识别空通知窗，激活失败，不能定位截图中向导；已依用户要求停止。当前不是WAITING_FOR_UAC，不宣称后台运行或两分钟计时。

## 回滚与保密范围
普通登记run文件快照/恢复此前通过；本轮Sandboxie文件/注册表恢复未验收，盒内自建数据保留作证据。Sandboxie驱动/服务、C:\\Windows\\Sandboxie.ini、VS Installer、Windows SDK、安装注册表/服务/缓存、系统/GPU日志不由普通run快照回滚，也不随删除D:\\PV1Lab撤销。需要正式卸载/管理流程，不能直接删正在使用的工具目录。
主工程本轮无自动回写；Codex文件系统仍为全访问运行环境，所以其只读边界属于操作约定，不能混称为OS强制访问控制。沙盒规则的实测拒绝是另一项独立证据。
真实卡密使用=否；既有宿主许可证复制/映射=否；PV1真实执行=否；真实业务/激活/解绑服务访问=否；文件上传=否。只进行了官方工具资料/下载/签名相关访问。安装及官方资料访问不等于业务服务访问。

## 最小下一动作
使Sandboxie当前提示和首次向导结束、显示正常主窗口后再续接。无需提供PV1卡密，无需购买证书。后续必须另外解决支持者功能依赖并重测等效边界，不能仅关闭提示或把RestrictDevices删掉就称为合格。原程序启动仍保持拒绝。
''',encoding='utf-8')
(R/'reports'/'remaining_actions.md').write_text('''# 当前剩余工作
两项系统安装已经完成，不再等待安装授权。参见continuation_report.md。
1. GUI：首次Setup Wizard和支持者提示对当前computer-use不可定位；按用户规则已停止。用户让正常Sandboxie主窗口出现后可续接。
2. 政策：当前RestrictDevices会触发5分钟终止，沙盒已停用。评估不依赖该权益且达到要求的正式配置；不要买证书、绕过限制或为了兼容全面开放。
3. 重验设备、剪贴板、桌面、输入、IPC、文件/注册表/子进程/离线规则；计时终止消除前不得运行GPU。
4. 自建GPU/CUDA/TensorRT沙盒兼容，以及停止后经正式管理界面做原生快照/恢复。普通文件snapshot不能替代。
5. 全部满足后才能进入首次真实执行/联网范围审批与手动输入阶段。当前NOT_READY，原程序未启动。
''',encoding='utf-8')
(R/'reports'/'license_readiness.md').write_text('''# NOT_READY
真实卡密、授权界面、真实服务均未使用。Sandboxie配置因支持者功能5分钟终止及未完成的边界/快照/GPU测试而不合格。
不索要卡密，也不要把卡密发入对话或文件。后续达到资格并确认第一次真实运行/联网范围后，用户只在原软件正常授权UI手动输入，期间停用可能捕获输入的UI读取、截图、调试日志。
同设备多次激活/解绑/再激活规则保持USER_CONFIRMED；次数、跨设备、服务端验证均未扩展推断。
''',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
