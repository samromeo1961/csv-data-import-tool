# Building zzTakeoff Items Import Converter for Mac

## Prerequisites

1. **Mac computer** with macOS 10.13 or later
2. **Python 3.8+** installed
3. **Terminal** application

## Step-by-Step Build Instructions

### 1. Install Python (if not already installed)

Check if Python is installed:
```bash
python3 --version
```

If not installed, download from: https://www.python.org/downloads/macos/

### 2. Transfer Project Files to Mac

Copy these files to your Mac:
- `takeoff_converter.py`
- `zztakeoff-logo.png`
- `requirements.txt`
- `config.example.py`

### 3. Open Terminal and Navigate to Project Folder

```bash
cd /path/to/csv-data-import-tool
```

### 4. Install Dependencies

```bash
pip3 install -r requirements.txt
pip3 install pyinstaller
```

### 5. Create Mac-Specific Build Spec File

Create a file named `build_mac.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['takeoff_converter.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('zztakeoff-logo.png', '.'),
    ],
    hiddenimports=[
        'anthropic',
        'openai',
        'google.generativeai',
        'PIL',
        'PIL._tkinter_finder',
        'openpyxl',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='zzTakeoff Items Import Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='zzTakeoff Items Import Converter.app',
    icon=None,
    bundle_identifier='com.zztakeoff.converter',
)
```

### 6. Build the Mac Application

```bash
pyinstaller build_mac.spec --clean
```

### 7. Locate the Mac Application

The Mac app will be created in:
```
dist/zzTakeoff Items Import Converter.app
```

### 8. Distribute

Compress the .app file:
```bash
cd dist
zip -r "zzTakeoff Items Import Converter.zip" "zzTakeoff Items Import Converter.app"
```

Share the ZIP file with Mac users. They can:
1. Unzip it
2. Drag the .app to their Applications folder
3. Double-click to run

## Important Mac Notes

### First Run - Security Warning

Mac users will see a security warning on first run. To bypass:

1. **Method 1:**
   - Right-click (or Control+click) the .app
   - Select "Open"
   - Click "Open" in the dialog

2. **Method 2:**
   - Go to System Preferences → Security & Privacy
   - Click "Open Anyway" for the blocked app

### Permissions

If the app needs file access permissions, Mac will prompt the user automatically.

## Troubleshooting Mac Build Issues

**Issue: "tkinter not found"**
```bash
# Install tkinter (may require Homebrew)
brew install python-tk@3.11
```

**Issue: "PIL/Pillow errors"**
```bash
pip3 install --upgrade Pillow
```

**Issue: "Command not found: pyinstaller"**
```bash
# Add to PATH or use full path
python3 -m PyInstaller build_mac.spec --clean
```

**Issue: "App damaged and can't be opened" (Mac Gatekeeper)**
```bash
# Remove quarantine attribute
xattr -cr "dist/zzTakeoff Items Import Converter.app"
```

## Building for Apple Silicon (M1/M2/M3)

If building on Apple Silicon Mac, the app will run natively on M-series chips.

If building on Intel Mac, the app will run on both Intel and Apple Silicon (via Rosetta).

For universal binary (both architectures):
```bash
# Build on Apple Silicon Mac
pyinstaller build_mac.spec --clean --target-arch universal2
```

---

**Note:** The .exe file built on Windows will NOT work on Mac. You must build separately for each platform.
