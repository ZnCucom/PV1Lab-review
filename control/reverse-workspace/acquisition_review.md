# 上游获取命令审查 — 已批准并执行

来源：https://github.com/zhaoxuya520/reverse-skill.git；首次审计仅针对 cab634bd855fc287f6e420c1f36fd1a6b9245960。用户本会话已批准下列命令，执行exit0；本地提交SHA、tree和提交时间已核对，见audit/acquisition_result.json和upstream-lock.json。批准获取不等于批准执行仓库代码、安装依赖或运行试点。

精确的第一步命令（EXECUTED，exit0）：

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c core.hooksPath=NUL -c init.templateDir= -c credential.helper= clone --no-checkout --no-recurse-submodules 'https://github.com/zhaoxuya520/reverse-skill.git' 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill'
```

副作用：向 GitHub 发起 HTTPS 下载；普通 Git 克隆写入唯一 vendor 目标目录及其中 .git（含整个仓库历史）；不工作树 checkout、不运行仓库 hooks、脚本、过滤器或安装器、不获取子模块。禁用 Git 模板和 credential helper 的参数仅对本命令生效，不更改全局设置。继承现有网络/代理设置，未建立强制出站隔离。命令在目标已存在时拒绝，不能覆盖已有进展。vendor 父目录仅在本登记工作区中创建。

随后只读核对命令（已执行）：

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -C 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill' rev-parse 'cab634bd855fc287f6e420c1f36fd1a6b9245960^{commit}'
& 'C:\Program Files\Git\cmd\git.exe' -C 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill' show -s --format=fuller 'cab634bd855fc287f6e420c1f36fd1a6b9245960'
& 'C:\Program Files\Git\cmd\git.exe' -C 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill' ls-tree -r 'cab634bd855fc287f6e420c1f36fd1a6b9245960'
```

通过 git show SHA:path 读取清单内源码及实际依赖；先审查 .gitattributes、链接、checkout/filter 配置和 consent gate，再列出固定 SHA 的 checkout/脚本精确命令。当前不申请泛化脚本授权。

影响原项目：本流程不在 D:\Pv1260909 运行任何 Git 操作，不创建 worktree，不写原项目。Ghidra 或 case-review 的后续写入、子进程、网络及配置副作用须由实际源码审查确认。
