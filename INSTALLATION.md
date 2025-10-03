# Installation Checklist

## ✅ Complete Setup Guide

Follow these steps in order for a successful installation.

---

## Step 1: System Requirements

### Check Python Version
```bash
python --version
```
✅ **Required:** Python 3.8 or higher

If not installed or version too old:
- **Windows/Mac:** Download from https://www.python.org/downloads/
- **Linux:** `sudo apt-get install python3.8` or higher

---

## Step 2: Download Project Files

### What You Need

Download all files from the outputs folder:

- [ ] `takeoff_converter.py` (Main application)
- [ ] `requirements.txt` (Dependencies)
- [ ] `test_setup.py` (Installation tester)
- [ ] `sample_databuild_export.csv` (Test data)
- [ ] `README.md` (Full documentation)
- [ ] `QUICKSTART.md` (Quick start guide)
- [ ] `USER_GUIDE.md` (Usage instructions)
- [ ] `TROUBLESHOOTING.md` (Problem solving)
- [ ] `PROJECT_SUMMARY.md` (Technical overview)

### Create Project Folder

```bash
# Create and navigate to project folder
mkdir zzTakeoff-Converter
cd zzTakeoff-Converter

# Place all downloaded files here
```

---

## Step 3: Install Python Packages

### Option A: Install All at Once (Recommended)

```bash
pip install -r requirements.txt
```

### Option B: Install Individually

```bash
pip install pandas
pip install openpyxl
pip install anthropic
```

### Verify Installation

Run the test:
```bash
python test_setup.py
```

**Expected output:**
```
✓ pandas installed
✓ openpyxl installed
✓ anthropic installed
✓ tkinter available
```

---

## Step 4: Get Anthropic API Key

### Create Account
1. Go to https://console.anthropic.com/
2. Sign up (free tier available)
3. Verify your email

### Generate API Key
1. Log in to console
2. Navigate to "API Keys" section
3. Click "Create Key"
4. Copy your key (starts with `sk-ant-`)
5. **Important:** Save it securely - you can't view it again

### Add Credits (if needed)
1. Check billing section
2. Add credits if account is new
3. Minimum ~$5 for testing

---

## Step 5: Configure API Key

### Temporary (for testing)

**Windows Command Prompt:**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-actual-key-here"
```

**Mac/Linux Terminal:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### Permanent (recommended for regular use)

**Windows:**
1. Search for "Environment Variables" in Start Menu
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Variable name: `ANTHROPIC_API_KEY`
6. Variable value: `sk-ant-your-actual-key-here`
7. Click OK on all windows
8. **Restart Command Prompt/PowerShell**

**Mac/Linux:**
Add to shell config file:
```bash
# For bash (most common)
echo 'export ANTHROPIC_API_KEY=sk-ant-your-actual-key-here' >> ~/.bashrc
source ~/.bashrc

# For zsh (Mac default)
echo 'export ANTHROPIC_API_KEY=sk-ant-your-actual-key-here' >> ~/.zshrc
source ~/.zshrc
```

### Verify API Key is Set

```bash
# Windows
echo %ANTHROPIC_API_KEY%

# Mac/Linux
echo $ANTHROPIC_API_KEY
```

Should display your key starting with `sk-ant-`

---

## Step 6: Test Complete Setup

Run full test:
```bash
python test_setup.py
```

**Expected output:**
```
============================================================
zzTakeoff Converter - Installation Test
============================================================
Testing imports...
✓ pandas installed
✓ openpyxl installed
✓ anthropic installed
✓ tkinter available

Testing API key...
✓ API key found (starts with: sk-ant-...)

Creating sample test data...
✓ Created sample_export.csv
  Contains 5 sample items

Testing data loading from sample_export.csv...
✓ Loaded 5 rows
✓ Columns: Databuild Code, Quantity, Cost Centre, Name, Unit Price, Units, Supplier Reference

============================================================
✅ All tests passed! You can now run:
   python takeoff_converter.py
============================================================
```

---

## Step 7: First Run

### Launch Application
```bash
python takeoff_converter.py
```

### Test with Sample File

1. ✅ Application window opens
2. ✅ Click "Load CSV/Excel"
3. ✅ Select `sample_databuild_export.csv`
4. ✅ Data displays in preview table
5. ✅ Click "Generate Cost Types (AI)"
6. ✅ Wait ~10 seconds for AI processing
7. ✅ Review results in preview
8. ✅ Click "Generate Takeoff Types (AI)"
9. ✅ Wait ~10 seconds
10. ✅ Click "Generate Formulas (AI)"
11. ✅ Wait ~10 seconds
12. ✅ Click "Export to zzTakeoff"
13. ✅ Save file
14. ✅ Open exported CSV in Excel/Notepad to verify

**If all steps work → You're ready to use with your own files! 🎉**

---

## Troubleshooting Installation

### ❌ Problem: "pip not found"

**Solution:**
```bash
python -m pip install -r requirements.txt
```

### ❌ Problem: "Permission denied"

**Solution:**
```bash
pip install --user -r requirements.txt
```

### ❌ Problem: "Tkinter not found"

**Windows:** Reinstall Python, ensure "tcl/tk" is selected

**Mac:** Included with Python

**Linux:**
```bash
sudo apt-get install python3-tk
```

### ❌ Problem: "API key not found"

**Solution:**
1. Verify key is set: `echo $ANTHROPIC_API_KEY`
2. Re-run setup from Step 5
3. Make sure to restart terminal after setting permanent variable

### ❌ Problem: "Invalid API key"

**Solution:**
1. Check for typos in key
2. Regenerate key at https://console.anthropic.com/
3. Ensure no quotes or spaces around key
4. Verify account has credits

---

## Post-Installation

### Create Desktop Shortcut (Optional)

**Windows:**
1. Right-click `takeoff_converter.py`
2. Send to → Desktop (create shortcut)
3. Edit shortcut properties
4. Target: `C:\Path\To\Python\python.exe "C:\Path\To\takeoff_converter.py"`

**Mac:**
Create script `run_converter.command`:
```bash
#!/bin/bash
cd /path/to/zzTakeoff-Converter
python3 takeoff_converter.py
```
Make executable: `chmod +x run_converter.command`

**Linux:**
Create `.desktop` file or use terminal alias

---

## Quick Reference Card

### Daily Use Commands

**Start Application:**
```bash
cd zzTakeoff-Converter
python takeoff_converter.py
```

**Test Setup:**
```bash
python test_setup.py
```

**Update Packages:**
```bash
pip install --upgrade pandas openpyxl anthropic
```

### File Locations

- **Application:** `takeoff_converter.py`
- **Test Data:** `sample_databuild_export.csv`
- **Learning Data:** `mapping_history.json` (created on first use)
- **Documentation:** All `.md` files

---

## Verification Checklist

Before considering installation complete, verify:

- [ ] Python 3.8+ installed
- [ ] All packages installed (test_setup.py passes)
- [ ] API key configured and working
- [ ] Application launches successfully
- [ ] Sample file loads
- [ ] AI processing works (generates Cost Types)
- [ ] Export creates valid CSV file
- [ ] Can open exported file in Excel

---

## You're Ready! 🚀

### Next Steps:

1. **Read QUICKSTART.md** for usage overview
2. **Try sample file** to understand workflow  
3. **Process your own file** from estimating software
4. **Review USER_GUIDE.md** for detailed instructions
5. **Keep TROUBLESHOOTING.md** handy for issues

### Support Resources:

- **Setup:** This checklist
- **Quick Start:** QUICKSTART.md
- **Full Guide:** USER_GUIDE.md
- **Problems:** TROUBLESHOOTING.md
- **Technical:** PROJECT_SUMMARY.md

---

## Installation Time

**Estimated Time:** 10-15 minutes

- Download files: 1 min
- Install Python packages: 2-3 min
- Get API key: 3-5 min
- Configure and test: 3-5 min
- First run test: 2 min

---

## Need Help?

1. Check TROUBLESHOOTING.md first
2. Verify each step in this checklist
3. Run test_setup.py to identify issues
4. Review error messages carefully

---

**Version:** 1.0.0  
**Installation Guide Last Updated:** September 2025

**Ready to convert your estimating data to zzTakeoff format!** 🎉
