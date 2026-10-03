# 本轮续接验收
时间：2026-09-27T15:44:58.084785+00:00。结论：已完成两项授权安装和真实 MSVC vendor 运行验证；应用沙盒未资格，按用户“GUI 无法处理则停止”的规则保存并停止。

## 已完成
- Sandboxie Plus1.18.5安装退出0；SbieSvc5.73.5、SbieDrv5.73.2运行中，数字签名有效。三个版本分别记录，不混写。
- VS2022 Build Tools17.14.41安装退出0；官方vswhere要求MSVC与SDK组件查询通过；v143目录14.44.35207，cl19.44.35229，link14.44.35229，Windows SDK10.0.26100.0。只请求VCTools工作负载、MSVC x64/x86和SDK及其必需依赖，未请求推荐组件或其他workload。
- 当前主工程两份明确源码以独立字节复制到staging，用MSVC /MT真实编译vendor DLL；没有mock或syntax宏。自建engine经C ABI执行24帧、3次生命周期、6个负例；resources_released=true，Job active=0。日志和结果分别见msvc_vendor_build.log与msvc_vendor_results.json。
- 原工程16个明确输入本轮复验哈希一致；范围见source_protection_continuation.json。没有声称扫描或证明整棵原目录完全不变。

## 沙盒实际结果
- 父进程及直接创建的子进程均加载SbieDll，并对原工程、整个_reverse_work、C:\Users\REDACTED_USER、控制文件、scripts、runs、baselines返回ERROR_ACCESS_DENIED(5)。这些是实际强制拒绝，不只是目录约定。
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
普通登记run文件快照/恢复此前通过；本轮Sandboxie文件/注册表恢复未验收，盒内自建数据保留作证据。Sandboxie驱动/服务、C:\Windows\Sandboxie.ini、VS Installer、Windows SDK、安装注册表/服务/缓存、系统/GPU日志不由普通run快照回滚，也不随删除D:\PV1Lab撤销。需要正式卸载/管理流程，不能直接删正在使用的工具目录。
主工程本轮无自动回写；Codex文件系统仍为全访问运行环境，所以其只读边界属于操作约定，不能混称为OS强制访问控制。沙盒规则的实测拒绝是另一项独立证据。
真实卡密使用=否；既有宿主许可证复制/映射=否；PV1真实执行=否；真实业务/激活/解绑服务访问=否；文件上传=否。只进行了官方工具资料/下载/签名相关访问。安装及官方资料访问不等于业务服务访问。

## 最小下一动作
使Sandboxie当前提示和首次向导结束、显示正常主窗口后再续接。无需提供PV1卡密，无需购买证书。后续必须另外解决支持者功能依赖并重测等效边界，不能仅关闭提示或把RestrictDevices删掉就称为合格。原程序启动仍保持拒绝。
