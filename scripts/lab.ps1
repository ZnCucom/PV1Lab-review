# Normal user entry point; no elevation and no system configuration changes.
$ErrorActionPreference = 'Stop'
& 'C:\Users\REDACTED_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'D:\PV1Lab\scripts\lab.py' @args
exit $LASTEXITCODE
