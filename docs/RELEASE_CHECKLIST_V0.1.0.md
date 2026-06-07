# WinTuner v0.1.1-alpha — Release Checklist

Complete before tagging **`v0.1.1-alpha`** and sharing the packaged folder.

**Release manager:** _______________  
**Target date:** 2026-06-06  
**Build output:** `dist\WinTuner\`

---

## Automated Checks

- [x] `python -m pytest wintuner/app/tests -v` — **38 passed** (2026-06-06)
- [x] Version constant is `0.1.1-alpha` in `wintuner/app/core/version.py`
- [x] `build_windows.ps1 -Clean` — **PASSED**
- [x] `smoke_exe.ps1` — **PASSED**
- [x] `qa_packaged_normal.ps1` — **PASSED**
- [x] `qa_packaged_admin.ps1` — **PASSED** (UAC elevated session; log confirms `elevated`)
- [x] `qa_dialogs.ps1` — **PASSED** (structure)
- [x] `BUILD_INFO.txt` written to `dist\WinTuner\`

## Manual QA

- [x] [QA_V0.1.0.md](QA_V0.1.0.md) updated with v0.1.1 packaged section
- [x] Tested packaged EXE as normal user (automated + process/log verification)
- [x] Tested packaged EXE as administrator (elevated launch verified via log)
- [ ] Full manual God Mode launcher walkthrough (all 23 tools)
- [ ] Manual tweak apply + undo on packaged EXE
- [ ] Manual temp cleanup confirm on packaged EXE
- [ ] Visual dialog spot-check (structure automated only)

### Admin QA detail

- [x] Elevated EXE launch survives startup (automated)
- [x] Log reports `Admin status: elevated`
- [ ] Services / Device Manager / System Restore opened manually when elevated
- [ ] Dashboard UI confirms admin visually (screenshot pending)

## Documentation

- [x] README reviewed and links handoff/packaging docs
- [x] [HANDOFF_V0.1.1_ALPHA.md](HANDOFF_V0.1.1_ALPHA.md) created
- [x] [PACKAGING_V0.1.1.md](PACKAGING_V0.1.1.md) exists
- [x] [SCREENSHOTS_NEEDED.md](SCREENSHOTS_NEEDED.md) status column added (none captured)

## Functional Verification

- [x] App runs as normal user without crash (packaged)
- [x] App runs as admin without crash (packaged, log verified)
- [x] Change log path: `%USERPROFILE%\.wintuner\change_log.json`
- [x] Application log path: `%USERPROFILE%\.wintuner\logs\wintuner.log`
- [ ] Undo verified on packaged EXE (manual pending)
- [x] Temp cleanup dry-run safety (unit tests; preview cache)
- [ ] Temp cleanup confirmed run on packaged EXE (manual pending)
- [x] No dangerous optimizer actions (static review)

## Safety Review

- [x] No Defender / Firewall / Update / UAC disabling code
- [x] No registry cleaner or driver updater
- [x] Launcher allowlisted command types
- [x] rundll32 allowlist only
- [x] Irreversible tweaks warn in metadata

## Known Limitations (documented)

- [x] Unsigned — SmartScreen warning possible
- [x] Onedir — ship full `dist\WinTuner\` folder
- [x] No installer
- [x] Restore points manual only
- [x] Global search → Tweaks only
- [x] No admin manifest in EXE

## Release Decision

- [x] **Approved for v0.1.1-alpha tag** (packaged alpha share)
- [ ] **Approved for wide public distribution** — pending manual launcher/tweak walkthrough + screenshots

### Remaining before wide share

```
1. Manual God Mode launcher walkthrough on packaged EXE
2. One tweak apply + undo on packaged EXE
3. Screenshots per SCREENSHOTS_NEEDED.md
```

---

## Tag Commands

```bat
cd "C:\Users\punke\Documents\Mesh package\WinTuner"
git status
git add .
git commit -m "Prepare WinTuner v0.1.1-alpha packaged QA"
git tag v0.1.1-alpha
```

---

## Post-Release Next Steps

1. **v0.1.2-alpha** — Unified search (God Mode + Tweaks)
2. **v0.2.0-alpha** — Restore point creation + profile improvements
