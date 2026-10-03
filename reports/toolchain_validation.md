# 工具链与自建 GPU 测试
Windows 11 Pro 10.0.26200；NVIDIA GeForce RTX 5090，driver610.88，32,607 MiB，实际 CUDA compute12.0。
已有系统 CUDA driver 可用不等于完整 Toolkit 已安装；未安装／升级 GPU 驱动。

- LLVM-MinGW20260922 UCRT：从原工具归档明确复制，匹配既有依赖 pin，实际编译／链接自建 C++17 ORT 测试成功。
- CUDA NVRTC12.9.86：包 SHA-256 与独立获取的 NVIDIA redistrib12.9.1 元数据匹配；DLL 无 Authenticode 签名，可信依据是官方归档哈希。
- ORT DirectML1.23.0／DirectML1.15.4：包匹配现有 pin；实际加载 DLL 的 Microsoft Authenticode 签名 Valid。
- 自建 CUDA kernel `y=2*x+1`：24 帧输入依赖输出通过，非法 launch 参数被拒绝，分配／module／context 已回收。
- 自建 ONNX 同一公式：CPU、DML 各 24 帧；各 3 次 session 周期、3 次错误 shape 拒绝。profiling 确认 DmlExecutionProvider 实际执行。
- 最初 NVRTC 错误为 builtins DLL 搜索路径；进程级 SetDefaultDllDirectories 配合显式目录已解决，无全局 PATH 变化。

详细数值结果：`runs/8407b1260d3b4c1ca81b1a8c6dde84cc/output/gpu_results.json`；编译和 provider profile 留在该 run。
状态：`OWN_MODEL_RUNTIME_VERIFIED`（CUDA/CPU/DML，宿主可信自建测试）；`TOOLCHAIN_VERIFIED` 仅上述子集。
MSVC ABI／Windows SDK 的 vendor bridge 尚未验证，MinGW 成功不替代它；TensorRT 单独见 `tensorrt_validation.md`。
原源码版本头要求 TensorRT10.10.0.31，vendor 源码 `NV_TENSORRT_VERSION==101000` 且要求 MSVC；没有改成新大版本。
原 client/model/engine/DLL 均 `TARGET_RUNTIME_NOT_EXECUTED`；自建成功不是原软件等价证据。

TensorRT追加验收：官方10.10.0.31已在自建网络/engine上通过24帧、3次周期和错误输入测试；详见 reports/tensorrt_validation.md。MSVC vendor bridge仍待安装后编译。

追加来源核验：CUDA cudart64_12.dll 为 NotSigned，不声称 Authenticode Valid；其归档大小与 SHA256 均匹配 NVIDIA 官方 redistrib12.9.1，已验证解压 DLL 与归档成员字节一致。没有改动旧 expected，也没有接纳历史校验失败包。
