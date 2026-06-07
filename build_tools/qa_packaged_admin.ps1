#Requires -Version 5.1
<#
.SYNOPSIS
  Packaged EXE QA in elevated context. Must be run from an admin PowerShell session.
#>
param(
    [string]$ExePath = "",
    [int]$WaitSeconds = 6
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogFile = Join-Path $env:USERPROFILE ".wintuner\logs\wintuner.log"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)
if (-not $isAdmin) {
    Write-Host "==> Admin QA skipped: current shell is not elevated."
    Write-Host "    Right-click PowerShell -> Run as administrator, then re-run this script."
    exit 2
}

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $ExePath = Join-Path $ProjectRoot "dist\WinTuner\WinTuner.exe"
}

$ExePath = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
Write-Host "==> Packaged QA (administrator): $ExePath"

$failures = @()

function Add-Failure([string]$msg) {
    $script:failures += $msg
    Write-Host "    FAIL: $msg" -ForegroundColor Red
}

function Add-Pass([string]$msg) {
    Write-Host "    PASS: $msg" -ForegroundColor Green
}

Add-Pass "Running in elevated PowerShell session"

$logMarker = "admin-qa-$(Get-Date -Format 'yyyyMMddHHmmss')"
$proc = $null
try {
    $proc = Start-Process -FilePath $ExePath -PassThru
    Start-Sleep -Seconds $WaitSeconds

    if (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue) {
        Add-Pass "Elevated EXE launch survived ${WaitSeconds}s"
    } else {
        Add-Failure "Elevated EXE exited early"
    }

    if (Test-Path $LogFile) {
        $log = Get-Content $LogFile -Raw -ErrorAction SilentlyContinue
        if ($log -match "elevated") {
            Add-Pass "Log reports elevated admin status"
        } else {
            Add-Failure "Log should report elevated admin status"
        }
    } else {
        Add-Failure "Log file missing"
    }
}
finally {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}

if ($failures.Count -eq 0) {
    Write-Host "==> Packaged admin QA PASSED"
    exit 0
} else {
    Write-Host "==> Packaged admin QA FAILED"
    exit 1
}
