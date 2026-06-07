# WinTuner v0.1.1-alpha — Alpha Handoff

This document is for testers and early adopters receiving the packaged alpha build.

## What This Build Is

**WinTuner 0.1.1-alpha** is a local-first Windows utility that:

- Launches 23+ built-in Windows tools (God Mode)
- Applies **documented, reversible** tweaks with risk labels
- Offers safe optimizer **checklists** (nothing runs until you confirm)
- Logs all changes locally with an Undo Center
- Cleans **user TEMP only** with preview + confirmation

It is **not** a registry cleaner, debloater, or fake speed booster.

## How to Run

1. Receive the full folder: `dist\WinTuner\` (zip it for sharing)
2. Extract anywhere (e.g. `C:\Tools\WinTuner\`)
3. Double-click **`WinTuner.exe`**

### Run as Administrator

Some tools (e.g. **Services**) need elevation:

1. Right-click `WinTuner.exe`
2. Choose **Run as administrator**
3. Dashboard should show admin status **Yes** and hide the elevation warning

## Ship the Whole Folder

**Do not ship only `WinTuner.exe`.** The app requires the `_internal\` folder beside it:

```
WinTuner/
  WinTuner.exe
  BUILD_INFO.txt
  _internal/
    data/
      god_mode_tools.json
      profiles.json
    ... (runtime libraries)
```

## What Is Intentionally Excluded

- Registry cleaners / “boost” snake oil
- Disabling Defender, Firewall, UAC, or Windows Update
- Service killing, prefetch deletion, bulk Store app removal
- Cloud sync, telemetry, ads, background monitoring
- Automatic restore point creation (opens Settings only)

## Safety Principles

Every change shows **what**, **why**, **risk**, **how to undo**, and **admin requirement**.

- Registry tweaks: read → backup → apply → log → undo
- Temp cleanup: user TEMP only, preview first, confirm, skip locked files
- Irreversible actions: explicit warning before apply

## Logs and Change Log

| Data | Location |
|------|----------|
| Application log | `%USERPROFILE%\.wintuner\logs\wintuner.log` |
| Change log | `%USERPROFILE%\.wintuner\change_log.json` |

Logs record events and counts — **not** file contents or personal data.

## Manual Rollback / Undo

1. Open **Undo Center** in the app for reversible tweaks applied by WinTuner
2. Use **System Restore** (Windows) for broader rollback — WinTuner opens the wizard but does not create restore points automatically
3. Temp cleanup and Recycle Bin empty are **not reversible** through WinTuner

## Known Limitations (v0.1.1-alpha)

- **Unsigned** — SmartScreen may warn (“Unknown publisher”)
- **No installer** — copy folder manually
- **Onedir only** — not a single portable EXE
- **Global search** — Tweaks page only (unified search in v0.1.2)
- **Restore points** — manual creation via System Protection
- **Classic context menu tweak** — requires sign-out

## Tester Checklist (Quick)

- [ ] Normal launch — Dashboard loads, standard user warning visible
- [ ] Admin launch — admin status correct, Services opens
- [ ] God Mode — search + launch Task Manager, Storage Settings
- [ ] Tweaks — list loads quickly, apply + undo one safe tweak
- [ ] Optimizer — preview temp cleanup (no delete until confirm)
- [ ] Settings/About — version `0.1.1-alpha`, log paths shown
- [ ] Dialogs — Apply/Cancel visible without maximizing window

## Build Verification

See `BUILD_INFO.txt` in this folder for build date, test results, and QA status.

## Support / Feedback

File issues with: Windows version, normal vs admin launch, steps to reproduce, and relevant log excerpts (redact paths if needed).

## Next Release

**v0.1.2-alpha** — unified search across God Mode + Tweaks
