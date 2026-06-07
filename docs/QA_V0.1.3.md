# WinTuner v0.1.3-alpha — Manual QA Checklist

Complete this checklist before a **GitHub pre-release** or wider alpha share.  
Focus: verify behavior that automated tests cannot fully cover.

**Tester:** _______________  
**Date:** _______________  
**Build:** `dist\WinTuner\WinTuner.exe` / Python source (circle one)  
**Version shown in app:** _______________ (expect **0.1.3-alpha** after this patch)  
**Elevated session:** yes / no (run admin sections elevated)

Helper script (lists tools only — **does not launch**):

```powershell
powershell -ExecutionPolicy Bypass -File build_tools\launcher_walkthrough.ps1
powershell -ExecutionPolicy Bypass -File build_tools\launcher_walkthrough.ps1 -ExportMarkdown docs\launcher_qa_session.md
```

---

## 1. Normal Launch (Standard User)

- [ ] App launches without crash
- [ ] Window title shows **WinTuner 0.1.3-alpha** (or current alpha version)
- [ ] Dashboard loads — disk, RAM, startup count visible
- [ ] Admin warning banner visible when not elevated
- [ ] Status bar shows **Standard user**
- [ ] Log updates: `%USERPROFILE%\.wintuner\logs\wintuner.log`

## 2. Admin Launch (Elevated)

> Run `WinTuner.exe` → Right-click → **Run as administrator**

- [ ] App launches elevated without crash
- [ ] Dashboard admin warning hidden (or admin status correct)
- [ ] Status bar shows **Administrator**
- [ ] Log contains `Admin status: elevated`

## 3. Unified Search (v0.1.2+ feature)

- [ ] Search **"task"** → Task Manager (Tool)
- [ ] Search **"device"** → Device Manager (Tool)
- [ ] Search **"file extensions"** → Show File Extensions (Tweak)
- [ ] Search **"temp"** → Clear User Temp Files (Tweak)
- [ ] Empty search → "Start typing…" (no crash)
- [ ] Typing does **not** auto-launch or auto-apply
- [ ] **Launch** on tool works (pick one: Task Manager)
- [ ] **View Details** on tweak opens scroll dialog; Apply requires confirmation

## 4. God Mode — All 23 Launcher Items

Use God Mode page or Search. Click **Launch** manually for each.  
Mark **Pass** if tool opens or a friendly error appears (not a crash).

| # | Tool | Admin | Pass | Fail | Notes |
|---|------|-------|------|------|-------|
| 1 | Programs and Features | No | | | |
| 2 | Device Manager | No | | | |
| 3 | Disk Cleanup | No | | | |
| 4 | Services | **Yes** | | | Test elevated |
| 5 | Task Manager | No | | | |
| 6 | Startup Apps | No | | | |
| 7 | Windows Update | No | | | |
| 8 | System Properties | No | | | |
| 9 | Advanced System Settings | No | | | |
| 10 | Power Options | No | | | |
| 11 | Network Connections | No | | | |
| 12 | Sound Settings | No | | | |
| 13 | Mouse Settings | No | | | |
| 14 | Display Settings | No | | | |
| 15 | Storage Settings | No | | | |
| 16 | Optional Features | No | | | |
| 17 | Event Viewer | No | | | |
| 18 | Reliability Monitor | No | | | |
| 19 | Resource Monitor | No | | | |
| 20 | Windows Security | No | | | |
| 21 | System Restore | No | | | |
| 22 | System Protection | No | | | |
| 23 | Environment Variables | No | | | |

**Services (non-admin):** blocked with clear message when not elevated — verify once.

## 5. Packaged Tweak Apply + Undo

On **packaged EXE** (recommended):

- [ ] Apply **Show File Extensions** (low risk) — confirmation shown
- [ ] Change appears in `%USERPROFILE%\.wintuner\change_log.json`
- [ ] **Undo Center** lists the change
- [ ] Undo restores previous state
- [ ] No silent registry write

## 6. Temp Cleanup Preview

- [ ] Optimizer → **Preview Temp Cleanup** shows count + MB
- [ ] Preview does **not** delete files
- [ ] Confirmed cleanup requires explicit Yes (optional — use test TEMP only)

## 7. Visual Dialog Spot-Check

Verify at least these dialogs:

- [ ] Tweak apply confirmation — resizable, scroll area, Apply/Cancel pinned
- [ ] Tweak detail from Search — View Details → scroll + pinned buttons
- [ ] Temp cleanup confirm — message readable without maximizing
- [ ] Warning/error dialog — scrollable if long
- [ ] Dialog centers on parent / stays on screen

## 8. Safety Exclusions (unchanged)

- [ ] No Defender / Firewall / Update / UAC disabling
- [ ] No registry cleaner, driver updater, debloat
- [ ] No new tweaks in this release
- [ ] Optimizer profiles unchanged

---

## Sign-off

| Area | Pass | Fail | Notes |
|------|------|------|-------|
| Normal launch | | | |
| Admin launch | | | |
| Unified search | | | |
| God Mode (23 tools) | | | |
| Tweak apply/undo (packaged) | | | |
| Temp preview | | | |
| Dialog UX | | | |
| Safety | | | |

**Overall:** PASS / FAIL / PASS WITH CAVEATS

**Caveats / blockers:**

```
1.
2.
```

---

## Automated Baseline (run before manual QA)

```bat
python -m pytest wintuner/app/tests -v
powershell -ExecutionPolicy Bypass -File build_tools\build_windows.ps1 -Clean
powershell -ExecutionPolicy Bypass -File build_tools\qa_packaged_normal.ps1
```

Screenshots: see [SCREENSHOTS_NEEDED.md](SCREENSHOTS_NEEDED.md)

Release notes (v0.1.2 feature set): [RELEASE_NOTES_V0.1.2_ALPHA.md](RELEASE_NOTES_V0.1.2_ALPHA.md)
