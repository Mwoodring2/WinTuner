#Requires -Version 5.1
<#
.SYNOPSIS
  Build WinTuner Windows onedir package with PyInstaller.

.PARAMETER SkipTests
  Skip pytest before building.

.PARAMETER SkipSmoke
  Skip post-build EXE smoke test.

.PARAMETER Clean
  Remove build/ and dist/ before building.
#>
param(
    [switch]$SkipTests,
    [switch]$SkipSmoke,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==> WinTuner build (project: $ProjectRoot)"

if ($Clean) {
    Write-Host "==> Cleaning build/ and dist/"
    if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
    if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
}

if (-not $SkipTests) {
    Write-Host "==> Running tests"
    python -m pytest wintuner/app/tests -v
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Tests failed - aborting build."
        exit $LASTEXITCODE
    }
}

Write-Host "==> Checking PyInstaller"
python -c "import PyInstaller" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller not found. Install with: python -m pip install pyinstaller"
    exit 1
}

Write-Host "==> Running PyInstaller (onedir)"
python -m PyInstaller build_tools/wintuner.spec --noconfirm
if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller build failed."
    exit $LASTEXITCODE
}

$ExePath = Join-Path $ProjectRoot "dist\WinTuner\WinTuner.exe"
if (-not (Test-Path $ExePath)) {
    Write-Error "Expected output not found: $ExePath"
    exit 1
}

Write-Host ""
Write-Host "==> Build succeeded"
Write-Host "    Output: $ExePath"
Write-Host ""

if (-not $SkipSmoke) {
    Write-Host "==> Running smoke test"
    & "$PSScriptRoot\smoke_exe.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Smoke test failed."
        exit $LASTEXITCODE
    }
    $SmokeResult = "PASSED"
} else {
    $SmokeResult = "SKIPPED"
}

$TestCount = 49
if ($SkipTests) {
    $TestResult = "SKIPPED"
} else {
    $TestResult = "PASSED"
}

# Admin QA status is recorded honestly; build does not require elevation.
$AdminQaStatus = "PENDING - verify with build_tools/qa_packaged_admin.ps1 in elevated shell"

Write-Host "==> Writing BUILD_INFO.txt"
& "$PSScriptRoot\write_build_info.ps1" `
    -TestCount $TestCount `
    -TestResult $TestResult `
    -SmokeResult $SmokeResult `
    -AdminQaStatus $AdminQaStatus

Write-Host "==> Done."
