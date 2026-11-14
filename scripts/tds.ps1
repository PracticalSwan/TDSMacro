param(
    [ValidateSet('start','status','pause','resume','stop')][string]$Action='status',
    [string]$SessionPath,
    [ValidateRange(1,10)][int]$Matches=1,
    [ValidateSet('play-again','lobby')][string]$RepeatRoute='play-again',
    [switch]$ConfirmStart,
    [switch]$Continuous,
    [switch]$PrepareOnly
)
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$pythonPath=Join-Path $projectRoot '.venv\Scripts\python.exe'
$pointerPath=Join-Path $projectRoot 'captures\last_session.txt'
if ($Action -eq 'start') {
    if (-not $ConfirmStart) { throw 'Starting input requires -ConfirmStart. F8 or Escape stops.' }
    if (-not $SessionPath) { $SessionPath=Join-Path $projectRoot ('captures\runs\'+(Get-Date -Format 'yyyyMMdd_HHmmss')) }
    $SessionPath=[System.IO.Path]::GetFullPath($SessionPath)
    if (Test-Path -LiteralPath $SessionPath) { throw 'Choose a new output folder; existing runs are preserved.' }
} elseif (-not $SessionPath) {
    if (-not (Test-Path -LiteralPath $pointerPath)) { throw 'No launcher session yet; specify -SessionPath.' }
    $SessionPath=[System.IO.File]::ReadAllText($pointerPath).Trim()
}
$arguments=@('-X','utf8','-m','tds_auto.session',$Action,'--output',$SessionPath)
if ($Action -eq 'start') {
    $arguments+=@('--confirm-start','--matches',"$Matches",'--repeat-route',$RepeatRoute,'--startup-delay','5')
    if ($PrepareOnly) { $arguments+='--prepare-only' }
    if ($Continuous) { $arguments+='--continuous' }
    Write-Host 'Switch to Roblox within 5 seconds. F8 or Escape stops; focus loss stops.'
    Write-Host "Session: $SessionPath"
}
$previousPythonPath=$env:PYTHONPATH
try {
    $env:PYTHONPATH=Join-Path $projectRoot 'src'
    & $pythonPath @arguments
    $runExitCode=$LASTEXITCODE
} finally {
    $env:PYTHONPATH=$previousPythonPath
}
exit $runExitCode
