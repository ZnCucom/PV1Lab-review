# PV1 reverse-skill 受控接入审计

日期：2026-10-03（America/Toronto）。当前结论：可以进入受控校验器验证，尚不能宣布正式采用或真实试点通过。固定版本已获取并核对，项目入口仍为审查稿、NOT_LOADED。

## 已完成

用户批准的只下载命令exit0。vendor/reverse-skill是完整Git对象仓库，工作树尚未checkout。固定提交cab634bd855fc287f6e420c1f36fd1a6b9245960，CommitDate 2026-09-22 05:18:45 UTC；tree为83fb489b20c3ea002e482ac8c39f52316633d49a；下载时默认HEAD与固定SHA相同。未自动跟随main。

针对RULES、README_AI、AGENTS、Codex router、Ghidra、通用RE/re-agent-workflow、四个ops文档、case-review与review_case.py、Windows master-route/case-init/case-guard/append-evidence/工具索引及真实依赖，完成只读源码审查。文件原始字节来自git show SHA:path，哈希见audit/source_manifest.json；详细路径与副作用见audit/compatibility.md。范围不是整个仓库安全审计。

唯一主源码仍为D:\Pv1260909\_reverse_work\reconstructed\native；整个原项目只读，本轮没有写入操作。全部新产物在已登记的D:\PV1Lab\control\reverse-workspace。未全树哈希比较，不宣称全树一致性证明。没有读卡密或原始目标证据，没有运行PV1/目标DLL/engine、安装软件、修改全局配置、commit/push/公开上传。

## 采用判断

| 部分 | 决定与证据 |
|---|---|
| Evidence/Finding/Path、timeline decision_delta、角色交接 | 可作为受控试点记录契约；纯Markdown，需补齐实际schema |
| review_case.py | 最值得先验证：仅Python标准库，源码无网络/子进程/写入；测试仍NOT_RUN |
| Ghidra静态方法 | 按需参考，复用哈希匹配旧导出；不得重导入整个项目；实际分析NOT_RUN |
| 默认授权沙盒、静态超时转动态、在线dogbolt | 禁用；与本轮明确边界冲突 |
| 全局router和自动checklist/journal回写 | 不采用；overlay白名单替代，不修改上游 |
| master-route/case-init/refresh-tool-index | 不调用：默认cwd写入、初始化覆写和TEMP子进程、索引的MCP配置读取/端口探测/版本程序执行均扩大副作用 |
| 自动安装与MCP/服务/攻击链/EDR路线 | 不采用；本轮无必要性，也未获批 |

review_case真实schema：Evidence需要severity、status、repro_command、content_hash及匹配heading；文档Evidence模板遗漏severity/status。Finding不接受自造static_observed状态，使用candidate等原枚举，verification_level另列。校验器不证明RVA/反编译语义、授权真实性、模型离线或程序等价。

## 本机实测与约定边界

沿用上一轮有效版本核对，不重复运行：Python3.12.14、Temurin JDK21.0.12.1+1、CMake4.1.2；MSVC cl /Bv显示19.44.35229，但无源文件exit1/D8003，不是构建成功。入口完整路径见audit/preflight_report.md。Ghidra12.1.4来自本地application.properties，启动NOT_RUN。

项目入口审查稿位于drafts/pv1-reverse/SKILL.md；agents/openai.yaml设allow_implicit_invocation=false。未进入.agents/skills；本机发现验收NOT_RUN，当前NOT_LOADED。skill-creator格式校验上轮失败：bundled Python缺PyYAML，详见draft_validation.json；未安装包，也未把此问题外推到无需PyYAML的review_case.py。

Review Sync：pause已运行但返回workspace is not registered；当前登记仅有两个其他项目。没有PAUSE_CONFIRMED。程序检测MODIFIED，本轮不修复、不注册、不恢复。远端SHA验证NOT_RUN，远端状态UNKNOWN。受限目标证据读取仍等待该条件的明确处理，不以下载批准扩展此权限。

offline、原项目只读、目标不得访问控制目录均为约定限制，未建立OS强制隔离；runtime文件系统unrestricted，模型在线。网络操作只涉及公开上游下载与先前公开文档读取，未发送目标内容。

## 已准备的下一步与未运行项

已构造audit/fixtures/valid、missing-reference、tampered-artifact：都是Lead自建synthetic文本，独立普通文件，完全不含PV1内容。第二个夹具引用不存在的E-999，第三个只篡改其自有artifact；真实证据没有被修改。

next_actions_review.md列出固定SHA checkout及三条review_case --verify-hashes --strict精确命令、副作用与预期错误码，等待批准。当前三个校验全部NOT_RUN；预期结果不等于实际结果。

真实问题选题、输入哈希配对、复制、case、strict校验及独立第二会话复核全部NOT_RUN。尚无PV1假设被关闭或降级；不虚构字段、函数或结论。原程序正向行为对照NOT_TESTED。未来最小实验需求须在真实选题后明确，不能用synthetic、mock或拒绝路径测试冒充。

下一步最小条件：批准checkout和synthetic校验器命令；明确接受未登记的同步状态作为只读选题前提或提供可确认的暂停途径；随后从既有报告选择真实问题并给出最小输入/离线试点命令审查。当前没有进入主工程写回或全量重构。
