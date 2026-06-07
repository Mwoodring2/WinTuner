# Screenshots Needed — WinTuner Alpha

Save captured PNGs under **`docs/screenshots/v0.1.2-alpha/`** (create folder when capturing).  
Do **not** mark **Captured** until the file exists in the repo or release assets.

**Status:** Needed · Captured · Optional

---

## Required for GitHub Pre-Release (v0.1.2-alpha)

| # | Screen | Exact filename | Status | Notes |
|---|--------|----------------|--------|-------|
| 1 | Dashboard, standard user | `docs/screenshots/v0.1.2-alpha/01-dashboard-standard-user.png` | Needed | Admin warning visible |
| 2 | Dashboard, administrator | `docs/screenshots/v0.1.2-alpha/02-dashboard-admin.png` | Needed | No admin warning; status Yes |
| 3 | Unified search results | `docs/screenshots/v0.1.2-alpha/03-unified-search-results.png` | Needed | Query e.g. "task"; Tool + Tweak badges |
| 4 | God Mode grid | `docs/screenshots/v0.1.2-alpha/04-god-mode-grid.png` | Needed | Full tool grid or search filtered |
| 5 | Tweaks library list | `docs/screenshots/v0.1.2-alpha/05-tweaks-list.png` | Needed | Risk / admin / reversible labels |
| 6 | Tweak confirm dialog | `docs/screenshots/v0.1.2-alpha/06-tweak-confirm-dialog.png` | Needed | Scroll area; Apply/Cancel pinned |
| 7 | Search tweak detail | `docs/screenshots/v0.1.2-alpha/07-search-tweak-detail.png` | Needed | From Search → View Details |
| 8 | Optimizer profile | `docs/screenshots/v0.1.2-alpha/08-optimizer-profile.png` | Needed | Checklist visible |
| 9 | Temp cleanup preview | `docs/screenshots/v0.1.2-alpha/09-temp-cleanup-preview.png` | Needed | Counts/MB in dialog |
| 10 | Undo Center | `docs/screenshots/v0.1.2-alpha/10-undo-center.png` | Optional | After at least one undoable tweak |
| 11 | Settings page | `docs/screenshots/v0.1.2-alpha/11-settings-page.png` | Needed | Version + log paths |
| 12 | About page | `docs/screenshots/v0.1.2-alpha/12-about-page.png` | Needed | Safety text + version |

---

## Optional (marketing / README hero)

| # | Screen | Exact filename | Status |
|---|--------|----------------|--------|
| 13 | Main window overview | `docs/screenshots/v0.1.2-alpha/13-main-window-overview.png` | Optional |
| 14 | Launcher walkthrough note | `docs/screenshots/v0.1.2-alpha/14-god-mode-services-admin-error.png` | Optional | Services blocked as standard user |

---

## Capture Settings

- **Theme:** Default dark (WinTuner default)
- **Resolution:** 1100×720 or native window size (consistent across set)
- **Format:** PNG
- **Redact:** Machine name / username if publishing publicly
- **Version in UI:** Should match tag (0.1.2-alpha for feature release; 0.1.3-alpha after QA bump)

---

## Verification

After adding files:

```powershell
Get-ChildItem "docs/screenshots/v0.1.2-alpha/*.png" | Select-Object Name, Length
```

Update this table **Captured** only for files that exist.

---

## Current Status

**Captured count:** 0 / 12 required  
**Folder exists:** create on first capture — no PNGs in repo yet
