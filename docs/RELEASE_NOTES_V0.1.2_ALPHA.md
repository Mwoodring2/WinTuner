# WinTuner v0.1.2-alpha — Release Notes

**Release type:** Pre-release alpha  
**Tag:** `v0.1.2-alpha`  
**Date:** 2026-06-06

---

## Summary

v0.1.2-alpha adds **unified search** across God Mode tools and the tweaks library. No new optimizer behavior, tweaks, or security-related changes.

---

## What's New

### Unified Search

- Top search bar searches **God Mode tools** and **tweaks** together
- New **Search** sidebar page with result cards
- Result type badges: **Tool** or **Tweak**
- **Launch** for tools (same hardened `launcher.py` path as God Mode)
- **View Details** for tweaks (same confirmation/apply flow as Tweaks page)
- Case-insensitive substring search on title, category, description, id, tags
- Empty query shows “Start typing…” — **no auto-launch, no auto-apply**

### Refactoring (safety)

- Shared `tweak_actions.py` — single apply/detail flow for Tweaks + Search
- 11 new unit tests in `test_search_service.py`

---

## What Did Not Change

- No new tweaks
- Optimizer profiles unchanged
- No registry cleaner, debloat, or security disabling
- Local-only — no telemetry, ads, or cloud sync
- Packaging remains PyInstaller **onedir**

---

## Requirements

- Windows 11 (Windows 10 may work for many features)
- Ship entire `dist\WinTuner\` folder (not EXE alone)
- Unsigned — SmartScreen may warn

---

## Upgrade from v0.1.1-alpha

1. Replace `dist\WinTuner\` folder with new build
2. User data preserved: `%USERPROFILE%\.wintuner\` (logs + change log)
3. Run unified search smoke test (see [QA_V0.1.2.md](QA_V0.1.2.md))

---

## Known Limitations

- Manual God Mode walkthrough (all 23 tools) recommended before wide share
- Screenshots not yet in repo (see [SCREENSHOTS_NEEDED.md](SCREENSHOTS_NEEDED.md))
- Admin manifest not embedded — run as administrator when needed
- Restore points opened manually only

---

## Tests

- **49** unit tests passing at release
- Build + smoke scripts: `build_tools/build_windows.ps1`, `smoke_exe.ps1`

---

## Next (v0.1.3-alpha)

Manual QA polish, screenshot checklist, GitHub pre-release packaging guidance.

---

## Full Changelog (git)

```
v0.1.2-alpha — Add unified search for God Mode tools and tweaks
v0.1.1-alpha — PyInstaller onedir packaging, QA docs, BUILD_INFO
v0.1.0-alpha — Initial safe optimizer / God Mode skeleton
```
