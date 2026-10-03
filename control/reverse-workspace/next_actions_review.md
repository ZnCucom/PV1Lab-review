# 下一步精确命令与审批范围

所有命令均NOT_RUN。这里只申请vendor固定版本checkout及synthetic校验器测试，不申请运行原PV1、目标DLL、Ghidra导入、上游安装器、工具索引刷新、router或case-init。

## 1. 固定版本checkout

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c core.hooksPath=NUL -c core.autocrlf=false -c core.eol=lf -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false -C 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill' checkout --detach 'cab634bd855fc287f6e420c1f36fd1a6b9245960'
```

副作用：vendor目录生成完整固定版本工作树，更新该vendor的.git index与HEAD；无网络、hooks、安装、服务、客户端配置变更。固定tree已检查无链接/子模块，attributes没有过滤器。本地现为no-checkout；如实际工作树已出现未登记内容或SHA变化，停止而非覆盖。

## 2. 三个隔离的synthetic fixtures

入口 scripts/review_case.py 实际SHA-256必须先匹配 aace3fad8514ef24aa1f1a99fed83d58eb531f8e876051b36f284e7d3704158d。以下fixture由Lead生成，是普通独立文件，完全不包含PV1输入、结论或合法密钥。

```powershell
& 'C:\Users\REDACTED_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill\skills\case-review\scripts\review_case.py' 'D:\PV1Lab\control\reverse-workspace\audit\fixtures\valid' --verify-hashes --strict --format json
& 'C:\Users\REDACTED_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill\skills\case-review\scripts\review_case.py' 'D:\PV1Lab\control\reverse-workspace\audit\fixtures\missing-reference' --verify-hashes --strict --format json
& 'C:\Users\REDACTED_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -I -B -X utf8 'D:\PV1Lab\control\reverse-workspace\vendor\reverse-skill\skills\case-review\scripts\review_case.py' 'D:\PV1Lab\control\reverse-workspace\audit\fixtures\tampered-artifact' --verify-hashes --strict --format json
```

预期（不是实际结果）：valid返回PASS/0；missing-reference返回FAIL/1并含reference.unknown_evidence；tampered-artifact返回FAIL/1并含artifact.hash_mismatch。若实际不符合则报告，不改变真实case。-I隔离Python搜索环境，-B避免bytecode写入，均不等同OS沙盒。

副作用：标准库Python读取上游脚本与synthetic fixture；脚本无网络/外部程序/安装/服务/配置更改。Lead将每次实际命令、exit_code、stdout、stderr保存到audit/validator-results/<fixture>.json（外层执行记录）；仅这些结果文件新增/更新，不修改夹具或原项目。保存输出由Lead完成，不向网络发送。

## 3. 真实试点的独立边界

PV1工作区未被Review Sync登记，pause已运行但没有PAUSE_CONFIRMED。当前AGENTS原文要求处理禁上传内容前“run and confirm pause”；本次下载批准未明确修改此条件。请明确是否允许以“PV1与实验区未登记、没有该工具的上传路径”为本轮只读证据读取的前提，保持不注册、不上传、不改变全局配置。若不接受，停在此边界，不能伪称暂停成功。

上述确认只解开只读选题；从既有报告选出问题后仍须登记最小输入副本、对应精确脚本/命令及副作用，再批准真实离线试点。不能把synthetic校验器通过作为PV1试点或原程序正向验证。
