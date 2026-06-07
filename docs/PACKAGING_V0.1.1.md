# WinTuner v0.1.1-alpha — Packaging Guide

This document describes how to build and smoke-test the packaged Windows alpha.

## Prerequisites

- Windows 10/11
- Python 3.11+ with runtime dependencies installed:

```bat
pip install -r requirements.txt
```

- PyInstaller (build-only, not in runtime requirements):

```bat
python -m pip install pyinstaller
```

## Build Command

From the project root:

```powershell
powershell -ExecutionPolicy Bypass -File build_tools\build_windows.ps1 -Clean
```

### Build Script Flags

| Flag | Effect |
|------|--------|
| `-Clean` | Remove `build/` and `dist/` before building |
| `-SkipTests` | Skip pytest (not recommended for release) |
| `-SkipSmoke` | Skip post-build EXE smoke test |

## Smoke Test Only

After a successful build:

```powershell
powershell -ExecutionPolicy Bypass -File build_tools\smoke_exe.ps1
```

Or run the EXE manually:

```bat
dist\WinTuner\WinTuner.exe
```

## Output Layout

```
dist/
  WinTuner/
    WinTuner.exe          ← main executable
    _internal/            ← PyInstaller bundled libs + data
      data/
        god_mode_tools.json
        profiles.json
      ...
```

**Do not distribute `_internal/` separately** — ship the entire `dist/WinTuner/` folder.

## Why Onedir (Not Onefile) for Alpha

- **Faster startup** — no extraction to temp on every launch
- **Easier debugging** — logs, missing DLLs, and data files are visible in `_internal/`
- **Safer iteration** — smoke tests and manual QA fail faster with clearer errors
- Onefile packaging may come later after alpha stabilizes

## Admin Behavior

- v0.1.1 builds run **as invoker** — no UAC prompt on launch
- Admin-only tools (e.g. Services) show a clear message when not elevated
- **Future:** optional `uac_admin` manifest can be added in `wintuner.spec` — not required for alpha

## SmartScreen / Unsigned EXE Note

PyInstaller output is **unsigned**. Windows SmartScreen may show:

> "Windows protected your PC" / "Unknown publisher"

This is expected for alpha builds. Options for later releases:

- Code signing certificate
- Internal distribution with SmartScreen reputation over time
- Continue testing via Python source until signing is available

## Known Packaging Limitations (v0.1.1-alpha)

| Item | Status |
|------|--------|
| No code signing | SmartScreen warning possible |
| No installer (MSI/Inno) | Copy `dist/WinTuner/` folder manually |
| No auto-update | Manual replace |
| Admin manifest | Not included — launch as admin manually when needed |
| Log/change log paths | Still `%USERPROFILE%\.wintuner\` (correct for packaged app) |
| Global search | Tweaks only (unchanged from v0.1.0) |

## Troubleshooting

**Build fails: PyInstaller not found**

```bat
python -m pip install pyinstaller
```

**EXE starts then immediately exits**

- Check `%USERPROFILE%\.wintuner\logs\wintuner.log`
- Run from cmd to see errors: `dist\WinTuner\WinTuner.exe` (if console build needed for debug, temporarily set `console=True` in spec)

**God Mode / Optimizer empty**

- Verify `_internal/data/god_mode_tools.json` exists in output folder
- Rebuild with `-Clean`

## Manual QA After Packaging

Complete [QA_V0.1.0.md](QA_V0.1.0.md) using the **packaged EXE**, including:

- [ ] Normal user launch
- [ ] **Run as administrator** (still pending until tested)
- [ ] God Mode launchers
- [ ] Tweaks apply + undo
- [ ] Temp cleanup preview + confirm
