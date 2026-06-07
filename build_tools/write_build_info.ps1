#Requires -Version 5.1
<#
.SYNOPSIS
  Write BUILD_INFO.txt into dist/WinTuner after a successful build.
#>
param(
    [string]$DistDir = "",
    [int]$TestCount = 0,
    [string]$TestResult = "unknown",
    [string]$SmokeResult = "unknown",
    [string]$AdminQaStatus = "PENDING - not verified in this build session"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($DistDir)) {
    $DistDir = Join-Path $ProjectRoot "dist\WinTuner"
}

$pythonVersion = (python -c "import sys; print(sys.version.split()[0])" 2>$null)
if (-not $pythonVersion) { $pythonVersion = "unknown" }

try {
    $pyinstallerVersion = (python -c "import PyInstaller; print(PyInstaller.__version__)" 2>$null)
} catch {
    $pyinstallerVersion = "unknown"
}

$version = (python -c "from wintuner.app.core.version import APP_NAME, APP_VERSION, APP_STAGE; print(f'{APP_NAME}|{APP_VERSION}|{APP_STAGE}')" 2>$null)
$parts = $version -split '\|'
$appName = if ($parts.Length -ge 1) { $parts[0] } else { "WinTuner" }
$appVersion = if ($parts.Length -ge 2) { $parts[1] } else { "unknown" }
$appStage = if ($parts.Length -ge 3) { $parts[2] } else { "alpha" }

$buildTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss K"

$content = @"
WinTuner Build Manifest
=======================

App Name:       $appName
Version:        $appVersion
Stage:          $appStage
Build Date:     $buildTime

Python:         $pythonVersion
PyInstaller:    $pyinstallerVersion
Spec File:      build_tools/wintuner.spec
Build Command:  python -m PyInstaller build_tools/wintuner.spec --noconfirm
Full Build:     powershell -ExecutionPolicy Bypass -File build_tools/build_windows.ps1 -Clean

Tests:          $TestResult ($TestCount tests)
Smoke Test:     $SmokeResult
Admin QA:       $AdminQaStatus

Output:         dist/WinTuner/WinTuner.exe
Ship:           Entire dist/WinTuner/ folder (includes _internal/)

Notes:
- Unsigned alpha build; SmartScreen may warn on first run.
- No forced elevation; run EXE as administrator when needed.
- Logs: %USERPROFILE%\.wintuner\logs\wintuner.log
- Change log: %USERPROFILE%\.wintuner\change_log.json
"@

$outFile = Join-Path $DistDir "BUILD_INFO.txt"
if (-not (Test-Path $DistDir)) {
    Write-Error "Dist directory not found: $DistDir"
    exit 1
}

Set-Content -Path $outFile -Value $content -Encoding UTF8
Write-Host "==> Wrote $outFile"
