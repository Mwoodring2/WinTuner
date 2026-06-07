# WinTuner



**Version: 0.1.2-alpha** · Local-first · No telemetry · No account



WinTuner is a trustworthy Windows 11 utility that combines a **God Mode-style tool launcher** with a **safe, reversible optimizer**. It helps you find settings, launch hidden Windows tools, clean user temp files, and apply documented tweaks — with full transparency and undo support.



## What WinTuner Is



- A **control-panel launcher** for 23+ built-in Windows tools

- **Unified search** across God Mode tools and tweaks (top bar + Search page)

- A **tweaks library** with risk labels, admin requirements, and undo instructions

- A **safe optimizer** using preset checklists — nothing runs until you confirm each action

- An **undo center** backed by a local JSON change log

- A **temp cleanup helper** with dry-run preview before any deletion



## What WinTuner Is Not



WinTuner is intentionally **not** a sketchy optimizer. It does **not**:



- Run registry cleaners or promise fake speed boosts

- Disable Windows Defender, Firewall, UAC, or Windows Update

- Kill services, delete prefetch/system files, or debloat your PC

- Remove Microsoft Store apps in bulk

- Use cloud accounts, telemetry, ads, or background monitoring



## Safety Principles



Every change shows:



1. **What** it changes  

2. **Why** someone might use it  

3. **Risk level** (low / medium / high)  

4. **How to undo** it  

5. Whether **admin** is required  



Additional rules:



- Registry writes: read → backup → apply → log → provide undo  

- File cleanup: user TEMP only, preview first, confirm, skip locked files  

- Medium/high risk: prompt to create a restore point (opens System Protection manually)  

- Irreversible actions: explicit warning before apply  



## Requirements



- Windows 11 (Windows 10 may work for many features)

- Python 3.11+

- PySide6



## How to Run (Development)



```bat

cd WinTuner

pip install -r requirements.txt

python -m wintuner.app.main

```



Or double-click `run.bat`.



### Run as Administrator



Some tools (e.g. Services) and tweaks require elevation:



1. Close WinTuner if open  

2. Right-click `run.bat`, terminal, or `dist\WinTuner\WinTuner.exe`  

3. Choose **Run as administrator**  



The Dashboard shows a warning when running as a standard user.



## Build Packaged Alpha



Install PyInstaller (build-only):



```bat

python -m pip install pyinstaller

```



Build onedir package (runs tests + smoke test):



```powershell

powershell -ExecutionPolicy Bypass -File build_tools\build_windows.ps1 -Clean

```



Run packaged app:



```bat

dist\WinTuner\WinTuner.exe

```



See [docs/PACKAGING_V0.1.1.md](docs/PACKAGING_V0.1.1.md) for full details, flags, and troubleshooting.

After build, `dist\WinTuner\BUILD_INFO.txt` records test/smoke/QA status.

Packaged QA scripts: `build_tools\qa_packaged_normal.ps1`, `qa_packaged_admin.ps1`, `qa_dialogs.ps1`



### Known Alpha Packaging Limitations



- **Onedir only** — ship the entire `dist/WinTuner/` folder  

- **Unsigned** — Windows SmartScreen may warn on first run  

- **No installer** — copy folder manually  

- **No forced elevation** — admin manifest optional in a future release  

- Logs and change log still live in `%USERPROFILE%\.wintuner\`



## How to Run Tests



```bat

python -m pytest wintuner/app/tests -v

```



## Local Data Paths



| Data | Path |

|------|------|

| Change log | `%USERPROFILE%\.wintuner\change_log.json` |

| Application log | `%USERPROFILE%\.wintuner\logs\wintuner.log` |



Logs record startup, admin status, launcher/tweak/cleanup events — **not** file contents or personal data.



## Project Structure



```

wintuner/

  app/                   # Application source

build_tools/

  build_windows.ps1      # Build script

  smoke_exe.ps1          # EXE smoke test

  wintuner.spec          # PyInstaller spec

docs/

  PACKAGING_V0.1.1.md

  QA_V0.1.0.md

  RELEASE_CHECKLIST_V0.1.0.md

```



## Release Documentation



- [Packaging Guide v0.1.1](docs/PACKAGING_V0.1.1.md)

- [Alpha Handoff v0.1.1](docs/HANDOFF_V0.1.1_ALPHA.md)

- [Manual QA Checklist v0.1.2 (Unified Search)](docs/QA_V0.1.2.md)

- [Manual QA Checklist](docs/QA_V0.1.0.md)

- [Release Checklist](docs/RELEASE_CHECKLIST_V0.1.0.md)

- [Screenshots Needed](docs/SCREENSHOTS_NEEDED.md)



## Known Limitations (v0.1.2-alpha)



- **Admin QA pending** — must verify elevated launch manually  

- **Restore points** — app opens System Protection; you create points manually  

- **Startup count** — estimate from registry Run keys  

- **Classic context menu tweak** — requires sign-out to take effect  

- **Screenshots** — still needed (see docs/SCREENSHOTS_NEEDED.md)



## Roadmap



| Version | Focus |

|---------|--------|

| 0.1.0-alpha | Safety audit, logging, QA docs |

| 0.1.1-alpha | PyInstaller onedir packaging |

| **0.1.2-alpha** | Unified search (God Mode + Tweaks) — current |

| 0.2.0-alpha | Restore point creation + profile improvements |



## License



MIT (suggested — adjust as needed)


