# PV1 reverse-skill 接入预审

日期：2026-10-03（America/Toronto）。结论：仅完成环境预审和项目级接入审查稿；上游获取、完整源码审计、技能加载和真实试点均未完成。当前没有证据支持宣称正式采用通过。

## 已核实的本地事实

- 主工程 D:\Pv1260909\_reverse_work\reconstructed\native 与实验区 D:\PV1Lab 均存在。沿用 lab workspace_id abc0b5b9-f529-47a0-9479-b65924072bf6。lab/control 和父路径未显示 ReparsePoint。新增目录登记见 registration.json。
- 阅读 LAB_README、control/checkpoint、path_policy、workspace 以核对边界。checkpoint 后部记录优先于较早 README；原程序仍禁止运行。本轮未读取卡密、目标配置内容或原始目标静态证据。
- 限定检查 lab/control、staging、tools、downloads/verified，原项目 tools 以及 Codex vendor_imports/现有技能目录，未找到 reverse-skill 副本。未搜索私人目录或重跑 inventory；不能排除其他位置存在副本。
- 已有 Ghidra 12.1.4 PUBLIC，安装位置 D:\Pv1260909\_reverse_work\tools\ghidra_12.1.4_PUBLIC，版本来自 Ghidra/application.properties；分析启动 NOT_RUN。JDK 要求 21，实际 Java 21.0.12.1 可调用。

| 工具 | 实际入口 | 版本核对 |
|---|---|---|
| Python | C:\Users\REDACTED_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe | --version: 3.12.14 |
| JDK | D:\Pv1260909\_reverse_work\tools\jdk-21.0.12.1+1\bin\java.exe | -version: Temurin 21.0.12.1+1 |
| CMake | C:\Users\REDACTED_USER\.cmake-deps\cmake\win\x64\bin\cmake.exe | --version: 4.1.2 |
| MSVC | D:\PV1Lab\tools\VS2022BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64\cl.exe | /Bv: 19.44.35229；无源文件导致 D8003/exit 1，非构建成功 |
| Git | C:\Program Files\Git\cmd\git.exe | --version: 2.55.0.windows.3 |

没有安装工具、修改 PATH、服务、安全配置或客户端配置。版本查询不证明 Ghidra 集成可运行，也不证明 C++ 构建验收通过。

## 来源与权限

用户要求执行提供的 MD；其中审批门随任务保留。第三方上游文本只供审查，不能扩权。公开[提交页面](https://github.com/zhaoxuya520/reverse-skill/commit/cab634bd855fc287f6e420c1f36fd1a6b9245960)可访问；本地 SHA 核对 NOT_RUN，文档所述 2026-09-22 日期尚未独立核对。锁文件明确区分 requested 与 observed。

pause 命令已运行，exit 0 但返回 workspace is not registered，未返回 PAUSE_CONFIRMED。现有登记仅有两个其他项目。没有为了暂停而注册项目或改全局配置；受限目标证据读取暂缓。远端 SHA 验证 NOT_RUN，远端状态 UNKNOWN。实现检测另报 program MODIFIED，本轮不修复或重启同步。

本轮网络操作仅为公开上游提交页及官方技能文档读取，未发送目标或证据。offline、主工程只读和原程序不得访问控制目录都是约定限制，未建立强制隔离；模型仍使用在线服务。

## 拟采用与不采用

拟采用静态方法、Evidence/Finding 组织、交接、case-review 和简报；均待审计/试点证据支持。不启用攻击链/EDR/渗透路由、自动动态执行、全套依赖安装、MCP、hooks、watchdog 或计划任务。详细审查范围见 overlay.md；源码所得结论目前只有公开提交 diff 的有限内容，不能外推完整仓库副作用。

已制作 drafts/pv1-reverse（SKILL.md 与 agents/openai.yaml）及 overlay v0.1。allow_implicit_invocation=false。未写入 .agents/skills，当前会话技能清单无该入口：NOT_LOADED。按照[官方技能文档](https://learn.chatgpt.com/docs/build-skills)核对发现/设置，但文档不代替本机加载验收。

本地 skill-creator quick_validate.py 已实际尝试，exit 1：当前 bundled Python 缺少 PyYAML，校验器在导入 yaml 时退出，未完成格式校验。结果和命令保存在 draft_validation.json；未为此安装依赖。该错误与上游 review_case.py 无关，不能据此判定上游缺少依赖或 schema 不兼容。

## 尚未运行与下一步

1. 按 acquisition_review.md 批准明确的只下载命令，取得对象后核对固定 SHA，逐项审查用户清单及真实依赖。源码审计 NOT_RUN。
2. 解决“工作区未登记”与 AGENTS 所要求 pause 确认之间的条件，才读取目标证据；不改变同步配置作为绕过。
3. 从权威既有报告选择真实静态问题，核验原输入和导出哈希，编制精确复制/脚本副作用清单再批准离线试点。目前没有假设被关闭/降级，没有新 case 或目标复制。
4. schema、strict/hash review、两个可丢弃反例、独立复核：全部 NOT_RUN。原程序行为对照 NOT_TESTED；未来最小实验取决于真实选题，不以 mock 代替。

原树未作写入操作，但没有执行全树哈希比较，不宣称全树一致性证明。首次目录导航搜索输出过宽；随后已限定目录，未重跑全量 inventory 或旧分析。未自动 commit、push、公开上传或进入主工程写回。
