# WinTuner — Manual QA Checklist

Covers source (Python) and packaged (`dist\WinTuner\WinTuner.exe`) testing.

**Tester:** Cursor automated + manual spot-check (2026-06-06)  
**Date:** 2026-06-06  
**Windows version:** Windows 11 (10.0.26100)  
**Packaged build:** v0.1.1-alpha

---

## v0.1.1-alpha Packaged QA (2026-06-06)

| Check | Result | Notes |
|-------|--------|-------|
| Build (`build_windows.ps1 -Clean`) | **PASS** | PyInstaller onedir |
| Smoke test (`smoke_exe.ps1`) | **PASS** | 5s process survival |
| Normal packaged launch | **PASS** | `qa_packaged_normal.ps1` |
| Admin packaged launch | **PASS** | `qa_packaged_admin.ps1` via UAC; log shows `elevated` |
| BUILD_INFO.txt in dist | **PASS** | Present after build |
| Bundled JSON data | **PASS** | `_internal/data/*.json` |
| Dialog structure (automated) | **PASS** | `qa_dialogs.ps1` — ScrollDialog + pinned buttons |
| Visual dialog spot-check | **PARTIAL** | Structure verified; full visual walkthrough recommended |
| God Mode launcher manual (each tool) | **NOT RUN** | Automated launch QA not exhaustive |
| Tweak apply/undo manual | **NOT RUN** | Recommend before public share |
| Temp cleanup confirm manual | **NOT RUN** | Preview path verified in prior alpha |

**Output path:** `dist\WinTuner\WinTuner.exe`

**Known limitations:** Unsigned, onedir, no installer, admin manifest not embedded, SmartScreen may warn.

**Failures:** None in automated packaged QA.

---

## v0.1.2-alpha Unified Search (see also [QA_V0.1.2.md](QA_V0.1.2.md))

| Check | Result | Notes |
|-------|--------|-------|
| `test_search_service.py` | **PASS** | 11 automated tests |
| Unified search UI | **IMPLEMENTED** | Search page + top bar |
| Manual search walkthrough | **PENDING** | See QA_V0.1.2.md |

---

## Normal User Launch

- [x] App launches via `python -m wintuner.app.main` without crash (prior sessions)
- [x] App launches via `run.bat` without crash (prior sessions)
- [x] `dist\WinTuner\WinTuner.exe` launches without crash (2026-06-06)
- [x] Dashboard loads (packaged — inferred from log + process survival)
- [x] Status bar / log shows "Standard user" (packaged QA log verified)
- [x] No silent crash in `%USERPROFILE%\.wintuner\logs\wintuner.log`
- [ ] Dashboard admin warning visible (manual visual — not screenshot-verified)

## Admin Launch

- [x] App launches when run as administrator (packaged EXE, UAC elevation 2026-06-06)
- [x] Log reports `Admin status: elevated`
- [ ] Dashboard admin warning hidden (manual visual — not screenshot-verified)
- [ ] Status bar shows "Administrator" (manual visual)
- [ ] Services launcher opens normally (manual — not run in this session)
- [ ] Device Manager opens normally (manual — not run in this session)
- [ ] System Restore / System Protection helper opens (manual — not run in this session)
- [ ] Admin-required tweaks work or explain clearly (manual — not run in this session)

## Packaged EXE Launch (v0.1.1+)

- [x] `dist\WinTuner\WinTuner.exe` launches without crash (normal user)
- [x] God Mode tools load (bundled JSON verified)
- [x] Optimizer profiles load (bundled JSON verified)
- [x] Log path under `%USERPROFILE%\.wintuner\`
- [x] Packaged EXE tested elevated (log verified)

## Dashboard

- [ ] Windows edition and build display
- [ ] Disk free/total displays
- [ ] Startup app count displays (number, not crash)
- [ ] Restore point status shows Available, Unknown, or Not detected
- [ ] Recent changes section loads (empty or populated)
- [ ] Refresh button updates values

## God Mode Launchers

- [ ] Search filters tools correctly
- [ ] Launch Task Manager
- [ ] Launch Device Manager
- [ ] Launch Storage Settings (ms-settings)
- [ ] Launch Programs and Features (control)
- [ ] Launch Environment Variables (allowlisted rundll32)
- [ ] Launch Windows Security (shell URI)
- [ ] Admin-only tool blocked with clear message when not elevated
- [ ] Missing/unavailable tool shows friendly error (not crash)

## Tweaks Page

- [ ] All tweaks listed with risk/admin/reversible labels
- [ ] Search filters tweaks
- [ ] View Details opens scrollable dialog with pinned Close button
- [ ] Apply safe tweak (e.g. Show File Extensions) shows confirmation dialog
- [ ] Confirmation shows: what, why, risk, undo, labels
- [ ] Apply succeeds and appears in change log

## Optimizer Page

- [ ] All 5 profiles load with descriptions
- [ ] Actions are checkable/uncheckable
- [ ] Nothing applies until "Apply Selected" + confirmations
- [ ] Profile apply shows per-action results
- [ ] No security-disabling actions present

## Undo Center

- [ ] Applied reversible tweak appears in list
- [ ] Undo restores previous state
- [ ] Undo is logged
- [ ] Non-reversible changes do not offer undo (or show clear failure)

## Temp Cleanup Dry Run

- [ ] Optimizer → Preview Temp Cleanup shows item count and MB
- [ ] Preview reports skipped count
- [ ] Preview does **not** delete any files
- [ ] Log file records preview summary (counts only, no file paths)

## Temp Cleanup Confirmed Cleanup

- [ ] Apply temp cleanup requires explicit confirmation
- [ ] Only user TEMP folder affected
- [ ] Locked files skipped with report
- [ ] Result shows deleted count, freed MB, skipped count
- [ ] Log file records cleanup result

## Restore Point Helper

- [ ] Settings → Open System Protection opens Windows dialog
- [ ] Medium/high risk tweak prompts restore point helper
- [ ] App does **not** claim a restore point was created automatically
- [ ] "Continue Without" and "Cancel" work as expected

## Dialog Sizing Behavior

- [x] ScrollDialog resizable (`qa_dialogs.ps1` automated)
- [x] Button box pinned outside scroll area (automated)
- [ ] Tweak confirmation dialog visual spot-check (manual recommended)
- [ ] Restore point prompt visual spot-check (manual recommended)
- [ ] Info/warning/error scrollable dialogs visual spot-check (manual recommended)
- [ ] Dialog center/clamp visual spot-check (manual recommended)

## Error Handling

- [ ] App survives invalid launcher (if tested manually with bad JSON in dev)
- [ ] Permission errors show user-friendly messages
- [ ] No unhandled exception dialogs on common paths

## Safety Exclusions

Static review + prior alpha audit (no disabling code found):

- [x] No Defender disabling
- [x] No Firewall disabling
- [x] No Windows Update disabling
- [x] No UAC disabling
- [x] No registry cleaner
- [x] No driver updater
- [x] No bulk app removal
- [x] No silent service changes
- [x] No destructive cleanup without preview and confirmation (code + tests)
- [x] No irreversible tweak without clear warning (metadata validation)

---

## Sign-off

| Check | Pass | Fail | Notes |
|-------|------|------|-------|
| Normal user launch (packaged) | x | | qa_packaged_normal.ps1 |
| Admin launch (packaged) | x | | Log: elevated; UAC session |
| God Mode | | | Manual launcher walkthrough pending |
| Tweaks + Undo | | | Manual apply/undo pending |
| Optimizer + cleanup | | | Manual confirm cleanup pending |
| Dialog UX | x | | Structure automated; visual partial |
| Safety exclusions | x | | Static + test review |

**Overall QA result:** **PASS with caveats** — safe to share alpha folder; complete manual God Mode/tweak walkthrough before wide distribution.
