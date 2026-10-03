# PV1Lab 独立实验区
工作区 ID：`abc0b5b9-f529-47a0-9479-b65924072bf6`；根 `D:\PV1Lab`，原来为空的本地 NTFS 普通目录。
唯一主工程 `D:\Pv1260909\_reverse_work\reconstructed\native`，本轮只读。实验区不包含原工程／_reverse_work；未建立关联链接、映射或替代主工程。

当前：两项授权系统安装已完成；L03 自建 CUDA/CPU/DirectML/TensorRT 已通过，真实 MSVC vendor 编译及自建 engine 运行也通过。L04 部分无密钥 canary 完成，但 RestrictDevices 触发支持者功能5分钟终止，GUI工具无法定位首次向导；依用户要求停止。沙盒已停用，L05/L06 未进入。
以 control/checkpoint.md、control/readiness.json、reports/continuation_report.md 为当前状态；早期安装前报告保留为历史。主入口不会运行 PV1，sandbox-snapshot 分支也保持拒绝。原生快照与沙盒GPU尚未验证。

PowerShell 示例（正常权限）：
```powershell
D:\PV1Lab\scripts\lab.ps1 init
D:\PV1Lab\scripts\lab.ps1 status
D:\PV1Lab\scripts\lab.ps1 new-run
# 将 new-run 输出的 run_id 代入：
D:\PV1Lab\scripts\lab.ps1 run-trusted --run <run-id> --test own_gpu
D:\PV1Lab\scripts\lab.ps1 snapshot --run <run-id>
D:\PV1Lab\scripts\lab.ps1 restore --run <run-id> --snapshot <snapshot-id>
D:\PV1Lab\scripts\lab.ps1 preview-clean --run <run-id>
D:\PV1Lab\scripts\lab.ps1 clean --run <run-id>
D:\PV1Lab\scripts\lab.ps1 stop --run <run-id>
D:\PV1Lab\scripts\lab.ps1 export
```
`prepare --manifest input_manifest.json` 支持明确清单复制，已完成的目的路径拒绝覆盖；新批次先审查清单、源哈希和目标父目录。
`init` 验证已存在的工作区标识，不清空／重建。`stop` 仅写合作退出请求，未知程序不承诺响应；超时保留，不自动杀进程。
清理只接受登记的 run ID；不支持任意路径删除。普通文件快照与 Sandboxie 原生文件+注册表快照严格分开。

可信测试使用现有 Codex Python Runtime（脚本有固定绝对入口），过程级 TEMP/TMP/CUDA_CACHE_PATH 指向 run。
可信准备不是沙盒，Windows/驱动缓存和日志可能在实验区外；所有本轮主动新增脚本／报告／构建／下载／复制输出均在实验区。
不自动 commit/push/上传；exports 使用固定字段白名单，假密钥 canary 已测试，不能据此保证任意未来原始报告均无敏感信息。

TensorRT10.10.0.31的真实MSVC vendor bridge已在自建engine上通过24帧、3次周期、6个错误输入负例；详见 reports/msvc_vendor_results.json。不要重启已失格的Sandboxie配置，control/sandbox_gate.json当前拒绝所有沙盒测试启动。
