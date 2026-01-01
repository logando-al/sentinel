# Project: PDF Sentinel
> A stealth desktop tool for legal teams to hash, stamp, and verify PDF document integrity.
---
## 1. The Strategy
| Aspect | Detail |
|--------|--------|
| **Pitch** | A drag-and-drop Windows app that SHA256-stamps PDFs with tamper-proof metadata and visual seals for legal verification. |
| **Target User** | Legal teams handling contracts, compliance, and official documentation. |
| **Monetization** | One-time license fee or internal tool for a client retainer. |
| **Stealth Mode** | No history, no logs, no database — pure stateless operation. |
---
## 2. Tech Architecture
### Stack
| Component | Technology |
|-----------|------------|
| **Language** | Python 3.11+ |
| **GUI Framework** | PyQt6 |
| **PDF Manipulation** | pypdf / PyMuPDF (fitz) |
| **Hashing** | `hashlib` (SHA256) |
| **Folder Watching** | `watchdog` |
| **Report Generation** | `reportlab` or HTML → PDF |
| **Packaging** | PyInstaller (→ `.exe`) |
### Core Features
| Feature | Description |
|---------|-------------|
| **Single File Mode** | Select one PDF → Hash → Stamp → Save |
| **Batch Mode** | Select folder or multiple files → Process all at once |
| **Folder Watch** | Auto-process new PDFs dropped into a watched folder |
| **Verification** | Re-check any stamped PDF to confirm integrity |
| **Visual Seal** | Embed a visible badge/stamp on the first page |
| **Print Report** | Generate a printable verification report |
### Data Flow
```
┌─────────────────────────────────────────────────────────────┐
│                        PDF SENTINEL                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │  INPUT   │───▶│   PROCESS    │───▶│     OUTPUT       │  │
│  │          │    │              │    │                  │  │
│  │ • Drag   │    │ • SHA256     │    │ • Stamped PDF    │  │
│  │ • Browse │    │ • Embed Meta │    │ • Visual Seal    │  │
│  │ • Watch  │    │ • Add Seal   │    │ • Verification   │  │
│  │ • Batch  │    │              │    │ • Print Report   │  │
│  └──────────┘    └──────────────┘    └──────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
### Metadata Schema (Embedded in PDF)
```json
{
  "sentinel_hash": "sha256:e3b0c44298fc1c149afbf4c8996fb924...",
  "sentinel_timestamp": "2026-01-01T15:04:51+08:00",
  "sentinel_version": "1.0.0"
}
```
---
## 3. UX Vision
### Vibe
> **Sleek • Modern • Fast**
### Design Tokens
| Element | Style |
|---------|-------|
| **Theme** | Dark mode with accent color (e.g., electric blue or emerald green) |
| **Typography** | Clean sans-serif (Segoe UI / Inter) |
| **Icons** | Minimal line icons (Lucide or Feather) |
| **Animations** | Subtle fade/slide transitions, progress indicators |
### Key Views
| View | Purpose |
|------|---------|
| **Home / Drop Zone** | Large drag-and-drop area for instant file upload |
| **Batch Processor** | Table view of selected files with status indicators |
| **Folder Watch** | Configure watched folder, live activity feed |
| **Verification** | Re-check stamped PDFs, show ✅ or ❌ result |
| **Settings** | Output folder, seal design, metadata options |
### User Story (Happy Path)
```
1. User launches PDF Sentinel
2. Drags a contract PDF onto the drop zone
3. App instantly calculates SHA256 hash
4. Hash is embedded in PDF metadata
5. A visual seal/badge is stamped on page 1
6. Stamped PDF auto-saves to output folder
7. User sees "✅ Stamped Successfully"
--- LATER ---
8. User drags the same PDF to verify
9. App recalculates hash → compares to stored metadata
10. Result: "✅ Original - No tampering detected"
    OR: "❌ TAMPERED - Hash mismatch!"
11. User can print a verification report
```
---
## 4. Feature Breakdown
### Phase 1: MVP
- [ ] Basic PyQt6 window with drag-and-drop
- [ ] SHA256 hash generation
- [ ] Embed hash in PDF metadata
- [ ] Visual seal on first page
- [ ] Single file verify mode
- [ ] Package as `.exe`
### Phase 2: Power Features
- [ ] Batch processing (multi-select)
- [ ] Folder watch with auto-process
- [ ] Printable verification report
- [ ] Custom seal design options
- [ ] Settings persistence (QSettings)
### Phase 3: Polish
- [ ] Dark/Light theme toggle
- [ ] Drag-drop animations
- [ ] Sound feedback (optional)
- [ ] Keyboard shortcuts
- [ ] Installer with desktop shortcut
---
## 5. File Structure (Proposed)
```
pdf-sentinel/
├── src/
│   ├── main.py              # Entry point
│   ├── app.py               # Main window
│   ├── components/
│   │   ├── drop_zone.py     # Drag-and-drop widget
│   │   ├── batch_view.py    # Batch processing table
│   │   ├── watch_view.py    # Folder watch panel
│   │   └── verify_view.py   # Verification result
│   ├── core/
│   │   ├── hasher.py        # SHA256 logic
│   │   ├── stamper.py       # Embed metadata + visual seal
│   │   ├── verifier.py      # Compare hashes
│   │   └── watcher.py       # Folder monitoring
│   ├── utils/
│   │   ├── pdf_utils.py     # PDF manipulation helpers
│   │   └── report.py        # Generate print reports
│   └── assets/
│       ├── seal.png         # Visual seal image
│       └── styles.qss       # Qt stylesheet
├── requirements.txt
├── build.spec               # PyInstaller config
└── README.md
```
---
## 6. Next Steps
1. **Approve this Blueprint** — Let me know if anything needs adjustment
2. **Scaffold the Project** — I'll create the folder structure and boilerplate
3. **Build MVP** — Start with single-file stamp + verify
4. **Iterate** — Add batch, watch, and reports
---
**Ready to start building?** 🚀