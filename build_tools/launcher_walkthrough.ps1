#Requires -Version 5.1
<#
.SYNOPSIS
  Print a manual God Mode launcher walkthrough checklist (does not launch tools).

.DESCRIPTION
  Reads wintuner/app/data/god_mode_tools.json and outputs a numbered checklist
  for human verification. This script never starts Windows tools automatically.

.PARAMETER ExportMarkdown
  Optional path to write a markdown checklist (e.g. docs/launcher_qa_session.md).

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File build_tools/launcher_walkthrough.ps1

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File build_tools/launcher_walkthrough.ps1 `
    -ExportMarkdown docs/launcher_qa_session.md
#>
param(
    [string]$ExportMarkdown = ""
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ToolsFile = Join-Path $ProjectRoot "wintuner\app\data\god_mode_tools.json"

if (-not (Test-Path $ToolsFile)) {
    Write-Error "Tools file not found: $ToolsFile"
    exit 1
}

$json = Get-Content $ToolsFile -Raw -Encoding UTF8 | ConvertFrom-Json
$tools = @($json.tools | Sort-Object category, name)

Write-Host ""
Write-Host "WinTuner God Mode Launcher Walkthrough"
Write-Host "======================================"
Write-Host "Tools to verify manually: $($tools.Count)"
Write-Host ""
Write-Host "Instructions:"
Write-Host "  1. Open WinTuner (source or dist\WinTuner\WinTuner.exe)."
Write-Host "  2. Go to God Mode OR use Search to find each tool."
Write-Host "  3. Click Launch yourself - this script does NOT open system tools."
Write-Host "  4. Mark Pass/Fail/Skip and note any friendly errors."
Write-Host ""

$lines = @()
$lines += "# God Mode Launcher Walkthrough Session"
$lines += ""
$lines += "Date: _______________"
$lines += "Tester: _______________"
$lines += "Build: source / packaged (circle one)"
$lines += "Elevated: yes / no"
$lines += ""
$lines += '| # | Tool | Category | Admin | Pass | Fail | Skip | Notes |'
$lines += '|---|------|----------|-------|------|------|------|-------|'

$i = 1
foreach ($tool in $tools) {
    $admin = if ($tool.requires_admin) { "Yes" } else { "No" }
    $line = "{0,2}. [{1}] {2}  (Category: {3}, Admin: {4})" -f $i, $tool.id, $tool.name, $tool.category, $admin
    Write-Host $line
    $lines += "| $i | $($tool.name) | $($tool.category) | $admin | | | | |"
    $i++
}

Write-Host ""
Write-Host "Total: $($tools.Count) launcher items."
Write-Host "Record results in docs/QA_V0.1.3.md"
Write-Host ""

if ($ExportMarkdown) {
    $outPath = if ([System.IO.Path]::IsPathRooted($ExportMarkdown)) {
        $ExportMarkdown
    } else {
        Join-Path $ProjectRoot $ExportMarkdown
    }
    $dir = Split-Path -Parent $outPath
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -Path $outPath -Value ($lines -join "`n") -Encoding UTF8
    Write-Host "Exported markdown checklist: $outPath"
}
