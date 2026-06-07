#Requires -Version 5.1
<#
.SYNOPSIS
  Code-level dialog compliance checks (ScrollDialog structure).
#>
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "==> Dialog structure QA (automated)"

python -c @"
import sys
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QScrollArea, QVBoxLayout

app = QApplication(sys.argv)

from wintuner.app.ui.dialogs import ScrollDialog, confirm_dialog, show_info

dlg = ScrollDialog('Test Dialog')
assert dlg.isSizeGripEnabled(), 'Dialog must be resizable'
layout = dlg.layout()
assert isinstance(layout, QVBoxLayout)
scroll = dlg.findChild(QScrollArea)
assert scroll is not None, 'Must contain QScrollArea'
btn_box = dlg.findChild(QDialogButtonBox)
assert btn_box is not None, 'Must contain QDialogButtonBox'
# Button box should be sibling after scroll in layout, not inside scroll
scroll_idx = layout.indexOf(scroll)
btn_idx = layout.indexOf(btn_box)
assert btn_idx > scroll_idx, 'Buttons must be pinned below scroll area'

print('PASS: ScrollDialog resizable with pinned button box')
"@

if ($LASTEXITCODE -ne 0) {
    Write-Error "Dialog structure QA failed"
    exit 1
}

Write-Host "==> Dialog structure QA passed"
exit 0
