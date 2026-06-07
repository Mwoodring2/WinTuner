#Requires -Version 5.1
<#
.SYNOPSIS
  Smoke-test the packaged WinTuner EXE launches and exits cleanly.
#>
param(
    [string]$ExePath = "",
    [int]$WaitSeconds = 5
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($ExePath)) {
    $ExePath = Join-Path $ProjectRoot "dist\WinTuner\WinTuner.exe"
}

$ExePath = (Resolve-Path -LiteralPath $ExePath -ErrorAction Stop).Path
Write-Host "==> Smoke test: $ExePath"

if (-not (Test-Path -LiteralPath $ExePath)) {
    Write-Error "EXE not found: $ExePath"
    exit 1
}

$proc = $null
try {
    $proc = Start-Process -FilePath $ExePath -PassThru
    Write-Host "    Started PID $($proc.Id), waiting ${WaitSeconds}s..."
    Start-Sleep -Seconds $WaitSeconds

    $running = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if (-not $running) {
        Write-Error "Process exited before smoke test completed (likely crash on startup)."
        exit 1
    }

    Write-Host "    Process still running - OK"
    Write-Host "    Closing process..."
    Stop-Process -Id $proc.Id -Force -ErrorAction Stop
    Start-Sleep -Seconds 1

    $still = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
    if ($still) {
        Write-Error "Failed to terminate process cleanly."
        exit 1
    }

    Write-Host "==> Smoke test passed"
    exit 0
}
catch {
    if ($proc -and -not $proc.HasExited) {
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Error $_
    exit 1
}
