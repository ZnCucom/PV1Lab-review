# 固定版本兼容性与副作用审计

审计对象：cab634bd855fc287f6e420c1f36fd1a6b9245960；Git tree 83fb489b20c3ea002e482ac8c39f52316633d49a。获取时默认 HEAD 恰好同 SHA；没有跟随 main 更新。源码来自 git show SHA:path，原始字节 SHA-256 见 source_manifest.json。未执行上游脚本。范围仅限用户指定 Windows 路径、其实际依赖与候选校验器；不声称审计整个工具套件。

## 文档声明与源码检查分离

上游 RULES/AGENTS/README_AI 声明：脚本先取得精确命令批准、全局配置 opt-in、scope gate 不可由 Force 绕过。这些可以采用。router adapter 没有携带第二套实现，需要完整 vendor 树。

上游也声明通用路由 hot path、field-journal/checklist 必做；reverse-engineering 假设默认授权沙盒，re-agent-workflow Static 时间盒约15分钟后转 Dynamic，通用 RE 提到 dogbolt.org。PV1 overlay 覆盖这些要求：只允许白名单静态方法、lab 内记录和报告，不启动样本、不公共上传、不写 vendor/journal、不默认安装 MCP。读取上游 ACTION REQUIRED 并不执行它。

## 脚本实际效果

| 入口 | 实际读取 | 实际写入 | 子进程/网络/配置 | 本轮决定 |
|---|---|---|---|---|
| master-route.ps1 | routing.json、PRIMARY 文件存在性、WorkRoot.ps1 | ProjectRoot/OutDir 目录、route-scope.md；省略 ProjectRoot 则默认当前目录 | 无网络，无外部程序 | 不调用；overlay 固定白名单，避免原 cwd 写入与攻击路由 |
| case-init.ps1 | Sample 存在性；WorkRoot、HostRuntime；Hint 非空时调用 master-route、RouteScope | scope/timeline/workitems/README 全部 WriteAllText，会覆盖同名已有案件；evidence/notes/report 目录 | 非空 Hint 启动当前 PowerShell 子进程；TEMP 下路由临时目录，finally 递归删除；不会强制隔离 | 不调用；手工写真实 case，避免覆盖历史、默认 cwd 和 TEMP 副作用 |
| case-guard.ps1 | case scope.md | 无 | 无子进程/网络，Force不绕过 | 可选，但本轮暂不调用；离线 cue 只是正则，不验证样本哈希或真实权限 |
| append-evidence.ps1 | 可选 repro/excerpt/notes 文件、ArtifactPath；hash 文件 | evidence/E-id.md（CreateNew 拒绝覆盖）、INDEX.md 追加 | 无网络，ReproCommand 只是文本，不执行 | 可参考 schema；本轮先手工整理，拒绝链接及外部文件 |
| refresh-tool-index.ps1 | ToolDiscovery、bootstrap-manifest、各 skill 存在性，PATH 和已知用户/安装位置，Codex/Claude MCP 配置 | 默认 vendor/skills/tool-index.md,json；可指定输出；输出覆写 | version 子进程、localhost TCP及HTTP tools/list；只变当前进程 PATH，不改全局 PATH；不自动启动服务/安装 | 本轮不运行；使用已实际核验的最小工具表 |
| review_case.py | case 的 scope/workitems/timeline、evidence/E-*.md、report/**/*.md，--verify-hashes 时读 artifact | 脚本本身无写；stdout 保存由调用方负责 | 标准库，无网络、子进程、安装、服务或配置写入 | 完成源码审查，待精确命令批准后测试 |

依赖：master-route → WorkRoot + routing.json；case-init → WorkRoot + HostRuntime，Hint非空再到master-route + RouteScope；refresh → ToolDiscovery + bootstrap-manifest（只读数据）；review_case.py 无包内 import。未准备调用 bootstrap，因此不对其安装实现作通过判断。

ToolDiscovery 源码的本地端口：23816、13337、8765、9876；先 TCP，再 HTTP POST /mcp tools/list，网络请求没有目标证据载荷，但依旧是副作用。读取 .claude/mcp.json、.codex/config.toml 的服务器名，不修改客户端配置。catalog 使用 Get-Command 和明确回退路径，没有全盘递归搜索；不能覆盖 PV1 自有 Ghidra/JDK 路径，漏报不得据此安装。某些 FixedVersion='v0.5.0' 是静态声明，不是实际运行版本；应使用已核验的实际入口与版本。

## 校验器实际 schema 与边界

- Evidence 文件只能在 evidence 顶层匹配 E-*.md，heading 必须为 ### E-id 且对应文件名。severity 必须为 critical/high/medium/low/info/n/a/n/a_re；status 为 observed/candidate/validated/false_positive/accepted_risk/superseded。repro_command 不能为空；n/a 需 notes 含 offline/离线/not applicable。content_hash 为 n/a 或64位 SHA-256（可带sha256:）；verify-hashes 有hash时核对 artifact。
- Finding 必需 severity、evidence_ids、confidence、location、status；status不接受 static_observed 或 preliminary。源码未验证 Finding severity/ confidence 全部枚举，只检查 validated不能low；overlay另外保持规范。
- workitems 表至少8列，status 在第6列，Evidence 第7列。timeline 事件为含竖线的 ## heading，引用从 evidence_ids 读。P-id 至少允许 path_type（attack/callflow/solve）且有 Evidence 引用。
- strict 将 warning 同样判FAIL，返回1；PASS/WARN返回0。因此两项负例要验证特定错误码，不能只看“非零”。
- scope检查 offline 案件不要求实际资产路径；auth/signoff未ready在offline中记warning，strict会失败。它不能证明授权真实性、样本存在、模块哈希匹配或出站隔离。
- artifact解析越出case只记warning，strict会失败；n/a hash不核对。Markdown或report目录若通过链接指向外部，可能在artifact检查前读取外部；调用前由Lead拒绝reparse/链接，不把脚本当隔离机制。
- 它不检查证据语义、静态/动态独立性、RVA正确性、原始导出与模块对应、验证等级，也不证明源码恢复或程序行为等价。

## checkout 审查

固定 tree 没有 symlink（120000）或 submodule（160000）。只有根 .gitattributes，内容为行尾与binary属性，无filter。系统Git有LFS过滤器，下一步checkout命令仍显式禁用LFS、hooks，并统一LF便于与blob哈希比较；这只作用于vendor。没有checkout审批前，不写入工作树。

## 本机验证

下载exit0；rev-parse固定SHA、提交时间与tree已核对。实际版本核对沿用adoption_report；本次未复跑成功版本命令。上游case-guard、router、case-init、append、refresh、review：NOT_RUN。Ghidra分析：NOT_RUN。准备的synthetic fixtures与真实PV1试点严格分开。
