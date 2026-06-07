#Requires -Version 5.1
<#
.SYNOPSIS
  Automated packaged EXE QA checks (normal user context).
#>
param(
    [string]$ExePath = "",
    [int]$WaitSeconds = 6
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ExpectedVersion = (python -c "from wintuner.app.core.version import APP_VERSION; print(APP_VERSION)" 2>$null)
if (-not $ExpectedVersion) { $ExpectedVersion = "0.1.2-alpha" }

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $ExePath = Join-Path $ProjectRoot "dist\WinTuner\WinTuner.exe"
}

$ExePath = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
$DistDir = Split-Path -Parent $ExePath
$LogFile = Join-Path $env:USERPROFILE ".wintuner\logs\wintuner.log"

Write-Host "==> Packaged QA (normal user): $ExePath"
Write-Host "    Expected version: $ExpectedVersion"

$failures = @()

function Add-Failure([string]$msg) {
    $script:failures += $msg
    Write-Host "    FAIL: $msg" -ForegroundColor Red
}

function Add-Pass([string]$msg) {
    Write-Host "    PASS: $msg" -ForegroundColor Green
}

# Bundled data
$dataGod = Join-Path $DistDir "_internal\data\god_mode_tools.json"
$dataProfiles = Join-Path $DistDir "_internal\data\profiles.json"
if (Test-Path $dataGod) { Add-Pass "god_mode_tools.json bundled" } else { Add-Failure "Missing $dataGod" }
if (Test-Path $dataProfiles) { Add-Pass "profiles.json bundled" } else { Add-Failure "Missing $dataProfiles" }

$buildInfo = Join-Path $DistDir "BUILD_INFO.txt"
if (Test-Path $buildInfo) { Add-Pass "BUILD_INFO.txt present" } else { Add-Failure "Missing BUILD_INFO.txt" }

# Log snapshot before launch
$logBefore = ""
if (Test-Path $LogFile) {
    $logBefore = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
}

$proc = $null
try {
    $proc = Start-Process -FilePath $ExePath -PassThru
    Write-Host "    Started PID $($proc.Id), waiting ${WaitSeconds}s..."
    Start-Sleep -Seconds $WaitSeconds

    $running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($running) {
        Add-Pass "EXE still running after ${WaitSeconds}s"
    } else {
        Add-Failure "EXE exited early (possible crash)"
    }

    if (Test-Path $LogFile) {
        $logAfter = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
        $logTail = if ($logAfter.Length -gt 2000) { $logAfter.Substring($logAfter.Length - 2000) } else { $logAfter }
        if ($logAfter -ne $logBefore) {
            Add-Pass "Log file updated at $LogFile"
        } else {
            Add-Failure "Log file did not show new startup entries"
        }
        $versionPattern = [regex]::Escape($ExpectedVersion)
        if ($logTail -match $versionPattern) {
            Add-Pass "Log contains version $ExpectedVersion"
        } else {
            Add-Failure "Log missing version $ExpectedVersion in recent entries"
        }
        if ($logTail -match "standard user") {
            Add-Pass "Log reports standard user (expected for normal launch)"
        } elseif ($logAfter -match "elevated") {
            Add-Failure "Expected standard user but log shows elevated"
        } else {
            Add-Failure "Log missing admin status line"
        }
        if ($logAfter -match "Loaded 13 tweaks") {
            Add-Pass "Tweaks loaded (13)"
        } else {
            Add-Failure "Log missing tweak load confirmation"
        }
    } else {
        Add-Failure "Log file not found: $LogFile"
    }
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        Add-Pass "Process terminated cleanly"
    }
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "==> Packaged normal-user QA PASSED"
    exit 0
} else {
    Write-Host "==> Packaged normal-user QA FAILED ($($failures.Count) issues)"
    exit 1
}
