# 发布范围与检查

来源：D:\PV1Lab 的显式文本白名单；输出为独立普通文件，位于exports/github-review。没有直接在实验区根目录创建Git仓库，也没有将本机所有文件纳入版本控制。

包含scripts顶层源文件、reports顶层说明与状态（排除原始目标与源保护证据）、control顶层说明与JSON、已有简要exports JSON、reverse-workspace接入报告/锁/overlay/drafts/兼容性审计/自建fixtures。

完整排除：baselines/、boxes/、cache/、downloads/、runs/、staging/、tools/；reverse-workspace/vendor/与audit/source/；所有.git历史、原始PV1模块与配置、卡密/许可证、模型/engine、主工程副本、内存dump、Codex auth/全局配置。明确单文件排除见PUBLICATION_MANIFEST.json。

检查：输入必须是UTF-8文本、小于2MB、非reparse路径且非hardlink；检测GitHub/API token格式、Bearer字面量和私钥头，命中则拒绝；替换已知个人账户路径/SID/邮箱。格式检测未命中不等于对任意未来文件作敏感性保证，新增文件必须重新审查。

发布清单同时记录本地源字节与公开字节SHA-256；脱敏后的文件不能拿原字节哈希作fixity验收。manifest内上游审计哈希描述未公开的上游blob，不表示这些blob在此仓库中。

这是一次发布快照，没有自动监控或持续同步。脚本仅作为审查材料复制，没有运行。未创建GitHub工作流；未复跑沙盒或GPU历史测试。
