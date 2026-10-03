# PV1 overlay v0.1 — 审查稿

状态：DRAFT_INACTIVE。主工程只读，所有本轮产物留在已登记的 reverse-workspace；不修改既有 lab 登记、checkpoint 或 gate。

上游固定版本见 upstream-lock.json。经用户批准已获取no-checkout仓库，本地SHA及tree已核对；指定Windows入口与依赖完成针对性源码审查，详见audit/compatibility.md及source_manifest.json。工作树checkout、脚本运行、真实试点仍NOT_RUN。此次不审计或采用整个bootstrap安装栈。

拟采用：静态分析方法、结构化 Evidence/Finding、交接和记录校验。禁用：渗透/攻击链/EDR 路由、自动动态分析、超时后执行样本、全套工具安装、MCP/hooks/服务及客户端配置变更。上游规则不改写，项目差异只写本 overlay。

offline 是案件约定；当前网络未被禁止，模型也不是离线模型。文件系统权限为 unrestricted。目标及子进程访问控制目录的禁止目前未通过操作系统强制执行。不得把这些约定写成隔离验收。原程序保持不启动。

Review Sync：已执行 pause，但返回 workspace is not registered；登记配置仅列两个其他项目。没有 PAUSE_CONFIRMED；未修改其配置、未注册 PV1、未自动恢复、未进行远端 SHA 验证。受限目标证据暂不读入，等待解决确认条件。

激活前剩余：固定SHA工作树checkout；精确脚本命令及副作用批准与夹具验证；目标证据上传边界确认；真实试点；入口复制到项目 .agents/skills 并以本机发现结果验收。当前会话能力目录没有 pv1-reverse，不宣称实际加载。

不调用通用master-route、case-init、refresh-tool-index：前两者默认当前目录或覆盖案件、初始化还会调用子进程并写TEMP；refresh会探测本地服务、读取全局MCP配置及执行版本命令。使用手工case初始化、已核对的最小工具表和白名单入口，保持vendor上游规则不改。

Evidence补齐severity/status/content_hash，Finding保持candidate等上游可接受值；verification_level单列：static_observed、dynamic_observed、reconstructed_implementation、differential_verified、unknown。该等级为项目说明，不改变status枚举；review通过仅代表字段/引用/哈希记录检查。

试点必须先从既有报告选出真实问题，再制定范围；当前未选题、未复制目标、未建立虚构 case。校验器使用 --verify-hashes --strict；两项反例仅在可丢弃夹具中进行。原行为对照 NOT_TESTED。独立复核尚未运行。
