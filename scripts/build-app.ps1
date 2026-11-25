param([string]$Destination)
$ErrorActionPreference='Stop'
$projectRoot=(Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $Destination) { $Destination=Join-Path $projectRoot 'dist' }
elseif (-not [IO.Path]::IsPathRooted($Destination)) { $Destination=Join-Path $projectRoot $Destination }
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
foreach ($name in @('dead_ahead_vertical_nine_v4.json','dead_ahead_vertical_ten_v031_v2202_trial.json','camera_0.png','camera_1.png','scene.png',
                    'dead_ahead_v031_2202.scene.png','dead_ahead_v031_2202.camera0.png','dead_ahead_v031_2202.camera1.png',
                    'wretched_front_hardcore_v2.json','wretched_front_hardcore_v2.scene.png',
                    'wretched_front_hardcore_v031_single_route.route.png')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('calibrations\'+$name)) -Destination (Join-Path $appPath 'calibrations') -Force
}
foreach ($name in @('GOLDIE SCOUTO.vertical-nine-slot1.strat','GOLDIE SCOUTO.vertical-ten-slot1-v031-2202.strat','hardcore_wretched_front_boomerang_crook_farm_v2.json')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('strategies\'+$name)) -Destination (Join-Path $appPath 'strategies') -Force
}
Copy-Item -LiteralPath (Join-Path $projectRoot 'app\README.txt') -Destination $appPath
foreach ($name in @('LICENSE','NOTICE.md')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot $name) -Destination $appPath
}
[void](New-Item -ItemType Directory -Path (Join-Path $appPath 'docs') -Force)
foreach ($name in @('setup.md','APP.md','diagnostic-data.md','troubleshooting.md','strategies.md','verification.md')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('docs\'+$name)) -Destination (Join-Path $appPath 'docs')
}
# Keep the actual strategy prerequisites available offline in the release.
$requirements=Join-Path $appPath 'docs\requirements\strategies'
[void](New-Item -ItemType Directory -Path $requirements -Force)
foreach ($name in @('README.md','_TEMPLATE.md','golden-scout-10.md','golden-scout-9.md','hardcore-gems-3.md','hardcore-gems-xp-4.md')) {
    Copy-Item -LiteralPath (Join-Path $projectRoot ('docs\requirements\strategies\'+$name)) -Destination $requirements
}
# Development-only references belong in the repository, not the runtime ZIP.
# Keep existing local links when their targets are included in the package.
foreach ($doc in (Get-ChildItem -LiteralPath (Join-Path $appPath 'docs') -Filter '*.md' -Recurse -File)) {
    $source=Join-Path $projectRoot $doc.FullName.Substring($appPath.Length+1)
    $body=[IO.File]::ReadAllText($doc.FullName)
    $body=[regex]::Replace($body,'\]\(([^)\r\n]+)\)',{
        param($match)
        $link=$match.Groups[1].Value
        if ($link -match '^(https?://|mailto:|#)') { return $match.Value }
        $parts=$link -split '#',2
        if (Test-Path -LiteralPath (Join-Path $doc.DirectoryName $parts[0])) { return $match.Value }
        $target=[IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $source) $parts[0]))
        if (-not $target.StartsWith($projectRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or -not (Test-Path -LiteralPath $target -PathType Leaf)) {
            throw "Unresolved documentation reference in $($doc.Name): $link"
        }
        $relative=$target.Substring($projectRoot.Length+1).Replace('\','/')
        $anchor=if ($parts.Length -eq 2) { '#'+$parts[1] } else { '' }
        return '](https://github.com/PracticalSwan/TDSMacro/blob/main/'+$relative+$anchor+')'
    })
    [IO.File]::WriteAllText($doc.FullName,$body,[Text.UTF8Encoding]::new($false))
}
& $pythonPath (Join-Path $projectRoot 'scripts\collect-licenses.py') $appPath
if ($LASTEXITCODE -ne 0) { throw 'Dependency notice collection failed.' }
# Screenshot-only matching does not call OpenCV video capture/write APIs.
# Remove just the optional FFmpeg video I/O helper from the new build; the
# otherwise-identical frozen candidate was self-checked without this DLL.
$cv2Dir=Join-Path $appPath '_internal\cv2'
if (Test-Path -LiteralPath $cv2Dir) {
    Get-ChildItem -LiteralPath $cv2Dir -File -Filter 'opencv_videoio_ffmpeg*_64.dll' |
        ForEach-Object {
            Remove-Item -LiteralPath $_.FullName
            Write-Output ('Excluded unused video I/O library: '+$_.Name)
        }
}
Write-Output (Join-Path $appPath 'TDSMacro.exe')
