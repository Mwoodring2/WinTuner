# WinTuner v0.1.2-alpha — Unified Search QA

Manual checks for unified search across God Mode tools and tweaks.

**Tester:** _______________  
**Date:** _______________  
**Build:** Python source / packaged EXE (circle one)

---

## Search Discovery

- [ ] Search **"task"** finds Task Manager (Tool)
- [ ] Search **"device"** finds Device Manager (Tool)
- [ ] Search **"file extensions"** finds Show File Extensions (Tweak)
- [ ] Search **"temp"** finds Clear User Temp Files (Tweak)
- [ ] Empty search shows "Start typing…" (no results, no crash)
- [ ] Result cards show **Tool** or **Tweak** badge
- [ ] Tweak results show risk / admin / reversible labels where applicable

## Safe Actions

- [ ] Typing in search bar does **not** launch tools
- [ ] Typing in search bar does **not** apply tweaks
- [ ] **Launch** on a tool opens the tool (e.g. Task Manager)
- [ ] **View Details** on a tweak opens scrollable dialog with Apply/Close
- [ ] Apply from detail dialog uses same confirmation flow as Tweaks page
- [ ] No tweak auto-applies from search results list alone

## Navigation

- [ ] Top search bar (2+ chars) navigates to Search page
- [ ] Enter in top search bar runs search
- [ ] Sidebar **Search** page works
- [ ] Global search no longer routes only to Tweaks page

## Dialog Compliance

- [ ] Tweak detail from search: resizable, scroll area, pinned buttons
- [ ] Dialog centers over parent window

## Safety

- [ ] No new tweaks added
- [ ] No registry cleaner / debloat / security disabling behavior
- [ ] Optimizer profiles unchanged

## Automated (CI)

- [x] `test_search_service.py` — 11 tests
- [x] Full `pytest wintuner/app/tests -v` pass (49 tests)
- [x] `build_windows.ps1 -Clean` pass (packaged build shows 0.1.2-alpha)

---

**Overall:** PASS / FAIL
