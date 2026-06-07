# GitHub Release — WinTuner v0.1.3-alpha

**Title:** WinTuner v0.1.3-alpha  
**Tag:** `v0.1.3-alpha`  
**Type:** Pre-release (trusted-tester alpha)  
**Asset:** `release/WinTuner-v0.1.3-alpha-win64.zip`

Copy the sections below into the GitHub release editor when publishing.

---

## Release body (paste into GitHub)

### What this is

WinTuner is a **local-first Windows 11 utility** that combines a God Mode-style tool launcher with a safe, reversible optimizer. This is a **trusted-tester alpha** build — documentation and QA polish only; **no new product features** since v0.1.2-alpha.

### What changed since v0.1.2-alpha

- Version bump to **0.1.3-alpha** (QA/docs polish release)
- **Manual QA checklist** — [docs/QA_V0.1.3.md](docs/QA_V0.1.3.md)
- **Launcher walkthrough helper** — `build_tools/launcher_walkthrough.ps1` (checklist only; does not auto-launch tools)
- **Screenshot checklist** — [docs/SCREENSHOTS_NEEDED.md](docs/SCREENSHOTS_NEEDED.md) with exact PNG filenames
- **Release notes for v0.1.2 feature set** — [docs/RELEASE_NOTES_V0.1.2_ALPHA.md](docs/RELEASE_NOTES_V0.1.2_ALPHA.md)
- README roadmap and doc links updated

**Unchanged from v0.1.2-alpha:** unified search, 13 tweaks, 23 God Mode tools, optimizer profiles, undo center, temp cleanup preview.

### Safety notes

This build does **not** include:

- Registry cleaning
- Debloat scripts
- Defender, Firewall, Windows Update, or UAC disabling
- Telemetry, ads, or background services

All tweaks require explicit confirmation. Search does not auto-launch tools or auto-apply tweaks.

### How to run

1. Download **WinTuner-v0.1.3-alpha-win64.zip**
2. **Unzip the whole folder** — you must keep `WinTuner.exe`, `_internal/`, and `BUILD_INFO.txt` together
3. Run `WinTuner.exe` (right-click → **Run as administrator** when a tool or tweak requires elevation)
4. Logs: `%USERPROFILE%\.wintuner\logs\wintuner.log`
5. Change log: `%USERPROFILE%\.wintuner\change_log.json`

**Note:** Unsigned alpha — Windows SmartScreen may warn on first run.

### Known limitations

- Admin manifest not embedded — elevate manually when needed
- Restore points opened via System Protection; creation is manual
- Startup count is an estimate from registry Run keys
- Classic context menu tweak may require sign-out

### QA status

| Area | Status |
|------|--------|
| Unit tests (49) | **PASS** |
| PyInstaller build + smoke | **PASS** |
| Packaged normal-user QA script | **PASS** |
| Manual all-23 God Mode launcher walkthrough | **PENDING** |
| Packaged tweak apply/undo walkthrough | **PENDING** |
| Screenshots (12 required) | **PENDING** |
| Elevated packaged QA | **PENDING** — run `build_tools/qa_packaged_admin.ps1` elevated |

See [docs/QA_V0.1.3.md](docs/QA_V0.1.3.md) for the full checklist.

### Download note

**Unzip the entire folder and run `WinTuner.exe`.** Do not copy the EXE alone — the app requires the `_internal/` directory and bundled data files.

---

## Publishing steps

1. Upload `release/WinTuner-v0.1.3-alpha-win64.zip` as a release asset
2. Check **This is a pre-release**
3. Paste the release body above
4. Publish
