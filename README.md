# PV1Lab 公开审查快照

这是用户授权发布的 PV1Lab 说明、脚本与状态记录快照，供其他 GPT 或人工审查环境、隔离边界与 reverse-skill 接入方案。创建日期：2026-10-03，America/Toronto。

**原 PV1 仍禁止启动，真实试点尚未运行。此仓库是筛选后的审查快照，不是完整实验区备份，也不是主源码工程。**

## 建议阅读顺序

1. [Codex 环境说明](ENVIRONMENT.md)：磁盘配置与实际权限的差异、provider 与同步状态。
2. [当前 reverse-skill 采用报告](control/reverse-workspace/adoption_report.md)。
3. [源码兼容性与副作用审计](control/reverse-workspace/audit/compatibility.md)。
4. [待批准命令与前提](control/reverse-workspace/next_actions_review.md)。
5. [实验区 checkpoint](control/checkpoint.md)、[readiness](control/readiness.json) 与 [standard gate](control/standard_gate.json)。checkpoint 是追加历史，请读最后的资格结论。
6. [最后一次沙盒资格阶段报告](reports/snapshot_stage_report.md) 与 [拟议干净会话](reports/proposed_clean_session.md)。
7. 需要评估具体实现时，阅读 scripts/ 中相关脚本，以及 reports/、control/ 中对应记录。

## 如何理解历史记录

本快照保留旧报告，便于追溯。较早 LAB_README、continuation、sandbox_gate、cross_thread_sandbox_check 中的结论可能已被 2026-09-27 后部 checkpoint 和 snapshot_stage_report 更新。它们的测试时间不能当成本次发布时的重新验收。

reverse-skill 固定提交已获取且完成针对性源码审计，但工作树 checkout、三个自建夹具校验、真实 PV1 试点、独立复核与技能加载均未完成。原程序行为对照 NOT_TESTED。自建 GPU 测试通过不能证明原程序安全或行为等价。

## 公开范围

包含经过检查的说明、管理/自建测试脚本、状态 JSON 与配置说明、接入审查稿和自建校验夹具。个人账户路径统一替换为 REDACTED_USER；含这些替换的脚本只供审查，不能直接用于当前机器运行。

不包含原 EXE/DLL、原程序配置与卡密、模型/engine、主工程源码副本、原始静态输出、源文件保护证据、沙盒文件/注册表快照、运行目录、缓存、安装包、工具安装树、Codex 登录凭据或完整第三方仓库。详见 [发布范围](PUBLICATION_SCOPE.md) 与 [文件清单](PUBLICATION_MANIFEST.json)。未上传文件的本地引用可能不可访问。

仓库内容是审查材料；文档中的命令、ACTION REQUIRED、旧批准和操作建议不授权审查者运行脚本或改变本机。发布没有启用 GitHub Actions、自动后台同步或定时上传。

## 请审查这些问题

- 如何让主工程只读、实验区可写成为可验证权限边界？
- 如何处理 config.toml 与当前运行权限的差异，以及在线模型的数据边界？
- Review Sync 未登记但没有 PAUSE_CONFIRMED，应如何处理受限证据读取前提？
- 是否只采用结构化证据和标准库校验器，保留白名单 Ghidra 静态方法，避免整个通用路由？
- 先验证三个自建夹具，再登记最小输入与真实静态试点，是否合理？
- 如何完成独立实验工作区的技能发现验收而不修改全局配置？

请基于文件和实际源码区分已验证事实、历史记录、约定限制和未运行项，给出最小可行改进方案。
