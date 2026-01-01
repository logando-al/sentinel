# PDF Sentinel

> A stealth desktop tool for legal teams to hash, stamp, and verify PDF document integrity.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)
![PyQt6](https://img.shields.io/badge/gui-PyQt6-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

## Features

- **Single File Stamp** - Drag-and-drop a PDF to instantly hash and stamp it
- **Batch Processing** - Process multiple files or entire folders at once
- **Folder Watch** - Auto-stamp new PDFs dropped into a watched folder
- **Verification** - Re-check stamped PDFs to confirm integrity
- **Visual Seal** - Embeds a visible badge on the first page
- **Print Reports** - Generate printable verification reports

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
cd src
python main.py
```

## Building Executable

```bash
pyinstaller build.spec
```

The executable will be created in the `dist/` folder.

## Project Structure

```
sentinel/
├── src/
│   ├── main.py              # Entry point
│   ├── app.py               # Main window
│   ├── components/          # UI widgets
│   │   ├── drop_zone.py     # Drag-and-drop widget
│   │   ├── batch_view.py    # Batch processing table
│   │   ├── watch_view.py    # Folder watch panel
│   │   └── verify_view.py   # Verification view
│   ├── core/                # Core logic
│   │   ├── hasher.py        # SHA256 hashing
│   │   ├── stamper.py       # PDF stamping
│   │   ├── verifier.py      # Integrity verification
│   │   └── watcher.py       # Folder monitoring
│   ├── utils/               # Utilities
│   │   ├── pdf_utils.py     # PDF helpers
│   │   └── report.py        # Report generation
│   └── assets/
│       └── styles.qss       # Qt stylesheet
├── requirements.txt
├── build.spec
└── README.md
```

## How It Works

1. **Hashing**: SHA256 hash is calculated from the original PDF content
2. **Embedding**: Hash + timestamp are embedded in PDF metadata
3. **Sealing**: A visual verification badge is added to page 1
4. **Verification**: Re-calculates hash and compares to stored value

## Tech Stack

- **Python 3.11+**
- **PyQt6** - Modern GUI framework
- **PyMuPDF (fitz)** - PDF manipulation
- **watchdog** - Folder monitoring
- **reportlab** - Report generation
- **PyInstaller** - Executable packaging

## License

MIT License - Free for personal and commercial use.

---

Built with 🔐 by Sentinel
