param([string]$Destination)
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $Destination) { $Destination=Join-Path $projectRoot 'dist' }
$Destination=[System.IO.Path]::GetFullPath($Destination)
$appPath=Join-Path $Destination 'TDSMacro'
if (Test-Path -LiteralPath $appPath) { throw 'Choose a fresh -Destination; existing app folders are preserved.' }
$pythonPath=Join-Path $projectRoot '.venv\Scripts\python.exe'
$buildPath=Join-Path $projectRoot 'build\app'
& $pythonPath -m PyInstaller --noconfirm --windowed --onedir --name TDSMacro --paths (Join-Path $projectRoot 'src') --collect-all winrt --distpath $Destination --workpath $buildPath --specpath $buildPath (Join-Path $projectRoot 'tds_launcher.py')
if ($LASTEXITCODE -ne 0) { throw 'Application packaging failed.' }
foreach ($folder in @('assets','calibrations','strategies')) {
    [void](New-Item -ItemType Directory -Path (Join-Path $appPath $folder) -Force)
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'assets\ui_2191') -Destination (Join-Path $appPath 'assets') -Recurse -Force
foreach ($name in @('dead_ahead_vertical_nine_v4.json','camera_0.png','camera_1.png','scene.png')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('calibrations\'+$name)) -Destination (Join-Path $appPath 'calibrations') -Force
}
foreach ($name in @('GOLDIE SCOUTO.vertical-nine-slot1.strat')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('strategies\'+$name)) -Destination (Join-Path $appPath 'strategies') -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'app\README.txt') -Destination $appPath
foreach ($name in @('LICENSE','NOTICE.md')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $name) -Destination $appPath
}
[void](New-Item -ItemType Directory -Path (Join-Path $appPath 'docs') -Force)
foreach ($name in @('setup.md','troubleshooting.md','strategies.md')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('docs\'+$name)) -Destination (Join-Path $appPath 'docs')
}
& $pythonPath (Join-Path $projectRoot 'scripts\collect-licenses.py') $appPath
if ($LASTEXITCODE -ne 0) { throw 'Dependency notice collection failed.' }
Write-Output (Join-Path $appPath 'TDSMacro.exe')
