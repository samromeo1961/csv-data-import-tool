# zzTakeoff Items Import Converter - Mac Installation Guide

## Two Options for Mac Users

### Option A: Run Python Script Directly (EASIEST)

No need to build an executable - just run the Python script!

#### Step 1: Install Python

Check if Python 3 is installed:
```bash
python3 --version
```

If not installed, download from: https://www.python.org/downloads/macos/
(Install Python 3.8 or later)

#### Step 2: Get the Project Files

Copy these files to a folder on your Mac:
- `takeoff_converter.py`
- `zztakeoff-logo.png`
- `requirements.txt`
- `config.example.py`

#### Step 3: Open Terminal

Navigate to the project folder:
```bash
cd ~/Downloads/csv-data-import-tool
# (or wherever you saved the files)
```

#### Step 4: Install Required Libraries

```bash
pip3 install -r requirements.txt
```

This installs:
- pandas
- openpyxl
- anthropic
- openai
- google-generativeai
- Pillow

#### Step 5: Run the Application

```bash
python3 takeoff_converter.py
```

The GUI will open! 🎉

#### Create a Shortcut (Optional)

Create a file named `Launch zzTakeoff Converter.command`:

```bash
#!/bin/bash
cd "$(dirname "$0")"
python3 takeoff_converter.py
```

Make it executable:
```bash
chmod +x "Launch zzTakeoff Converter.command"
```

Now you can double-click this file to launch the app!

---

### Option B: Build Mac Application (.app file)

If you want a standalone Mac application, see **BUILD_FOR_MAC.md** for instructions.

This requires:
- Building on a Mac computer
- Installing PyInstaller
- ~10 minutes build time

The result is a `zzTakeoff Items Import Converter.app` that can be dragged to Applications.

---

## First-Time Setup (Both Options)

1. **Get an API Key** from one of these providers:
   - Claude: https://console.anthropic.com/
   - ChatGPT: https://platform.openai.com/
   - Gemini: https://aistudio.google.com/app/apikey
   - DeepSeek: https://platform.deepseek.com/

2. **Launch the app** (using either Option A or B above)

3. **Configure Settings:**
   - Expand "▼ Settings"
   - Select AI Provider
   - Click "Configure API Key"
   - Paste your API key
   - Click "Save API Key"

4. **Start Converting!**
   - Load your CSV/Excel file
   - Follow the 3-step workflow
   - Export to zzTakeoff

---

## Troubleshooting

### "tkinter not found"

If you get a tkinter error, install it:
```bash
# Using Homebrew (recommended)
brew install python-tk@3.11

# Or reinstall Python from python.org (includes tkinter)
```

### "pip3: command not found"

Use this instead:
```bash
python3 -m pip install -r requirements.txt
```

### "Permission denied" when running .command file

Make it executable:
```bash
chmod +x "Launch zzTakeoff Converter.command"
```

### Security Warning: "App from unidentified developer"

Right-click the .command file → Open → Click "Open" in the dialog

---

## Performance Notes

- Mac M1/M2/M3 (Apple Silicon): Excellent performance
- Intel Macs: Works great
- Minimum: macOS 10.13 High Sierra or later

---

## File Locations

Config file and templates will be saved in the same folder as `takeoff_converter.py`:
- `config.py` - Your API keys
- `import_templates.json` - Saved column mappings
- `formula_templates.json` - Saved formulas
- `*.zztakeoff_progress` - Saved progress files

---

## Need Help?

Contact the developer or refer to DISTRIBUTION_README.txt for detailed feature documentation.
