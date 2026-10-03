param([Parameter(Mandatory=$true)][ValidateSet('Sandboxie','BuildTools')][string]$Component)
$ErrorActionPreference='Stop'
$labRoot='D:\PV1Lab'
$records=Get-Content -LiteralPath "$labRoot\reports\verified_signatures.json" -Raw | ConvertFrom-Json
$installer=if($Component -eq 'Sandboxie'){ "$labRoot\downloads\verified\Sandboxie-Plus-x64-v1.18.5.exe" }else{ "$labRoot\downloads\verified\vs_buildtools.exe" }
$expected=$records | Where-Object path -EQ $installer
if((Get-FileHash -LiteralPath $installer -Algorithm SHA256).Hash.ToLower() -ne $expected.sha256){throw 'Installer hash mismatch'}
if((Get-AuthenticodeSignature -FilePath $installer).Status -ne 'Valid'){throw 'Installer signature invalid'}
$logRoot="$labRoot\reports\system_install"
New-Item -ItemType Directory -Path $logRoot -Force | Out-Null
$tempRoot="$labRoot\cache\installer-temp-$Component"
New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null
$env:TEMP=$tempRoot; $env:TMP=$tempRoot
$statePath="$labRoot\control\install-$Component.json"
$state=[ordered]@{component=$Component;installer=$installer;authorized='USER_EXPLICIT_SYSTEM_INSTALL';started_utc=[DateTime]::UtcNow.ToString('o');state='LAUNCHING_UAC_MAY_APPEAR';pid=$null;exit_code=$null;caller_elevated=([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)}
$installArgs=if($Component -eq 'Sandboxie'){
 '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /SP- /ALLUSERS /TASKS="" /DIR="D:\PV1Lab\tools\Sandboxie-Plus" /LOG="D:\PV1Lab\reports\system_install\sandboxie-install.log"'
}else{
 '--passive --wait --norestart --installPath "D:\PV1Lab\tools\VS2022BuildTools" --path cache="D:\PV1Lab\cache\vs-packages" --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 --add Microsoft.VisualStudio.Component.Windows11SDK.26100'
}
$state.arguments=$installArgs
$state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding utf8
"User authorized $Component; checkpoint saved before installer launch."
try {
    # Normal ShellExecute launch. Any elevation is the signed installer's own Windows UAC flow.
    $proc=Start-Process -FilePath $installer -ArgumentList $installArgs -WorkingDirectory $labRoot -Verb Open -WindowStyle Hidden -PassThru
    $state.pid=$proc.Id; $state.state='INSTALLER_RUNNING'
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding utf8
    "INSTALLER_RUNNING: $Component PID $($proc.Id)"
    $proc.WaitForExit()
    $state.exit_code=$proc.ExitCode; $state.state='INSTALLER_EXITED';$state.finished_utc=[DateTime]::UtcNow.ToString('o')
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding utf8
    $state | ConvertTo-Json -Depth 5
}catch{
    $state.state='LAUNCH_ERROR';$state.error=$_.Exception.Message
    $state | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $statePath -Encoding utf8
    throw
}
