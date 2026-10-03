# Codex 环境与状态（2026-10-03）

此文件来自本次会话只读核对，不包含登录信息或密钥。它是当时状态，不承诺未来会话相同。

- Windows 10.0.26200.0，PowerShell Core7.6.5，Codex CLI0.153.4；桌面应用版本未核对。
- 当前会话cwd为D:\Pv1260909；唯一主工程D:\Pv1260909\_reverse_work\reconstructed\native；实验区D:\PV1Lab。
- 用户config.toml配置：model_provider=yoda，model=gpt-6.1-sol，reasoning=medium，sandbox_mode=workspace-write，approval_policy=on-request，windows.sandbox=elevated，web_search=live。
- 当前实际运行权限：danger-full-access/unrestricted，approval_policy=never，网络启用。运行权限优先于磁盘默认；配置值不证明ACL、管理员身份或隔离。
- provider实际后端、最终模型身份与数据处理方式尚未核对。
- 配置启用app-tools、browser、Chrome、Computer Use、visualize、documents、pdf、spreadsheets、presentations、template-creator、code-review。MCP名称node_repl/cua_repl；工具出现不证明所有账户连接通过。
- 多代理工具可用，4个并发槽位；本轮没有启动子代理，独立第二会话复核未运行。
- 实际版本核对：Python3.12.14、Git2.55.0.windows.3、JDK21.0.12.1、CMake4.1.2；MSVC/Bv显示19.44.35229，因无源文件exit1，不是编译成功；Ghidra12.1.4来自安装元数据，未启动。
- bundled Python缺PyYAML，本地skill-creator格式校验失败；未安装包。review_case.py仅标准库。
- Review Sync有Stop/Interrupt/SessionEnd hooks和既有后台安装记录。PV1没有登记，pause返回workspace is not registered，未得到PAUSE_CONFIRMED；程序检测MODIFIED，未调查修复，远端SHA状态UNKNOWN。
- 主工程只读、目标禁止访问控制目录、离线分析属于操作约定；未建立本轮OS强制隔离。模型在线，不能写成模型离线。
- reverse-skill固定SHA已下载；未checkout、未执行上游脚本。pv1-reverse只在drafts，NOT_LOADED。三个夹具和真实试点均NOT_RUN，原程序对照NOT_TESTED。

本次用户随后明确授权创建公开GitHub审查仓库，批准的范围是经检查的说明、脚本和状态记录。此授权只允许这个审查快照公开，不允许上传被排除的目标/凭据、运行目标或执行待批准试点命令。历史报告中的“不上传”描述其原任务范围，不代表本次已批准的审查快照未发布。
