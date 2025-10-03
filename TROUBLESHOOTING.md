# Troubleshooting Guide

## Installation Issues

### Problem: "pip install" fails

**Error**: `ERROR: Could not find a version that satisfies the requirement...`

**Solutions:**
1. Update pip:
   ```bash
   python -m pip install --upgrade pip
   ```

2. Check Python version:
   ```bash
   python --version
   ```
   Must be 3.8 or higher

3. Try installing packages individually:
   ```bash
   pip install pandas
   pip install openpyxl
   pip install anthropic
   ```

### Problem: "No module named 'tkinter'"

**Error**: `ModuleNotFoundError: No module named 'tkinter'`

**Solutions:**

**Windows:**
- Tkinter should be included with Python
- Reinstall Python from python.org
- Check "tcl/tk and IDLE" during installation

**Mac:**
- Included with Python
- If missing, reinstall Python:
  ```bash
  brew install python-tk
  ```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3-tkinter
```

### Problem: "Permission denied" during pip install

**Error**: `ERROR: Could not install packages due to an EnvironmentError`

**Solutions:**
1. Use user install:
   ```bash
   pip install --user -r requirements.txt
   ```

2. Or use virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## API Key Issues

### Problem: "API key not found"

**Error**: `ANTHROPIC_API_KEY not set in environment`

**Solutions:**

**Check if key is set:**
```bash
# Windows
echo %ANTHROPIC_API_KEY%
# Mac/Linux
echo $ANTHROPIC_API_KEY
```

**Set the key (temporary - for current session):**
```bash
# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-your-key-here

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Mac/Linux
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Set the key (permanent):**

**Windows:**
1. Search "Environment Variables"
2. Click "Environment Variables" button
3. Under "User variables", click "New"
4. Variable name: `ANTHROPIC_API_KEY`
5. Variable value: Your API key
6. Click OK
7. Restart Command Prompt

**Mac/Linux:**
Add to `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```
Then reload:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### Problem: "Invalid API key"

**Error**: `401 Unauthorized` or `Invalid API key`

**Solutions:**
1. Verify key is correct (starts with `sk-ant-`)
2. Check for extra spaces or quotes
3. Generate new key at https://console.anthropic.com/
4. Ensure account has credits

### Problem: "API rate limit exceeded"

**Error**: `429 Too Many Requests`

**Solutions:**
1. Wait 60 seconds and try again
2. Process smaller batches
3. Check your API usage at https://console.anthropic.com/
4. Upgrade your API plan if needed

### Problem: "Insufficient credits"

**Error**: `402 Payment Required` or credit error

**Solutions:**
1. Check account balance: https://console.anthropic.com/
2. Add credits to your account
3. Verify payment method is valid

## File Loading Issues

### Problem: "Failed to load file"

**Error**: Various loading errors

**Solutions:**

**For CSV files:**
1. Open in text editor and check format
2. Ensure first row contains headers
3. Check for special characters
4. Try saving as UTF-8 encoding

**For Excel files:**
1. Open in Excel and verify it loads
2. Save as .xlsx (not .xls)
3. Remove any formulas or macros
4. Ensure no password protection

### Problem: "Encoding error"

**Error**: `UnicodeDecodeError` or encoding error

**Solutions:**
1. Save file as UTF-8:
   - Excel: Save As → CSV UTF-8
   - Notepad: Save As → Encoding: UTF-8

2. Try different encoding:
   Edit `takeoff_converter.py`, line 115:
   ```python
   self.df = pd.read_csv(filename, encoding='latin-1')
   ```

### Problem: "No columns detected"

**Error**: Empty data or no headers

**Solutions:**
1. Ensure first row contains column names
2. Check file isn't empty
3. Verify correct delimiter (comma for CSV)
4. Remove any rows before headers

### Problem: "File path with spaces fails"

**Error**: File not found

**Solutions:**
1. Use quotes around path when opening
2. Or move file to path without spaces
3. Or use short path (Windows 8.3 names)

## AI Generation Issues

### Problem: "AI API Error"

**Error**: `Failed to generate Cost Types: AI API Error`

**Solutions:**
1. Check internet connection
2. Verify API key is working
3. Check Anthropic API status: https://status.anthropic.com/
4. Wait a few minutes and retry

### Problem: "JSON parse error"

**Error**: `Failed to parse response` or JSON error

**Solutions:**
1. This is rare - AI should return valid JSON
2. Try processing different file
3. Reduce sample size (edit code, line 203: change 50 to 20)
4. Report issue if persists

### Problem: "Incorrect classifications"

**Issue**: AI classifies items wrong

**Solutions:**

**For Cost Types:**
- Check if descriptions are clear
- Add more detail to item names
- Include supplier references
- Process more files to improve learning

**For Takeoff Types:**
- Verify units are correct in source
- Check for typos in unit field
- Use standard units (EA, SM, M, etc.)

**For Formulas:**
- Review formulas in export
- Edit CSV manually if needed
- Formulas are based on patterns

### Problem: "All items classified as 'Other'"

**Issue**: No clear patterns detected

**Solutions:**
1. Add more descriptive names
2. Include keywords: "Supply", "Install", "Fix"
3. Add supplier references
4. Check sample size (needs variety)

## Export Issues

### Problem: "Export fails"

**Error**: Various export errors

**Solutions:**
1. Check you have write permission
2. Close file if already open in Excel
3. Try different location
4. Check disk space

### Problem: "Required fields empty"

**Issue**: Some required fields blank in export

**Solutions:**
1. Run all three AI generation steps
2. Check preview before exporting
3. Verify source data has minimum info
4. Edit exported CSV to fill blanks

### Problem: "Excel file won't open"

**Error**: Corrupted file

**Solutions:**
1. Use CSV format instead (recommended)
2. Check openpyxl version:
   ```bash
   pip install --upgrade openpyxl
   ```
3. Try opening in Google Sheets

## Application Issues

### Problem: "Application won't start"

**Error**: Nothing happens or crashes

**Solutions:**
1. Run from command line to see errors:
   ```bash
   python takeoff_converter.py
   ```
2. Check all imports work:
   ```bash
   python test_setup.py
   ```
3. Verify Python version:
   ```bash
   python --version
   ```

### Problem: "Window appears then closes"

**Error**: App closes immediately

**Solutions:**
1. Run from command line (not double-click)
2. Check for Python errors
3. Run test_setup.py first

### Problem: "Buttons are disabled"

**Issue**: Can't click buttons

**Solutions:**
1. Load file first
2. Follow sequence: Load → Cost Types → Takeoff Types → Formulas → Export
3. Wait for AI processing to complete
4. Check for error messages

### Problem: "Application freezes"

**Issue**: Not responding during AI processing

**Solutions:**
1. **This is normal** - AI processing takes time
2. Watch progress label for updates
3. Don't close - wait for completion
4. For large files (500+ items), expect 30-60 seconds

## Data Quality Issues

### Problem: "Too many items classified as Subcontract"

**Issue**: Over-classification

**Solutions:**
1. Remove supplier column from source if not needed
2. Or clear supplier values for material-only items
3. AI uses supplier presence as strong signal

### Problem: "Formulas don't make sense"

**Issue**: Wrong formula for item type

**Solutions:**
1. Edit exported CSV manually
2. Change formula to appropriate one:
   - Area items: "Area" or "Length * Width"
   - Linear items: "Length"
   - Count items: "Count"
3. Report patterns that don't work

### Problem: "Mixed results for similar items"

**Issue**: Inconsistent classification

**Solutions:**
1. Ensure consistent naming in source
2. Group similar items together
3. Process more files to improve patterns
4. Use mapping_history.json learning

## zzTakeoff Import Issues

### Problem: "Import fails in zzTakeoff"

**Error**: Various import errors

**Solutions:**
1. Check required fields are filled:
   - Cost Type, Name, Takeoff Type, Formula
2. Verify CSV format is correct
3. Check for special characters
4. Try importing just a few rows first

### Problem: "Formulas not recognized"

**Error**: Invalid formula in zzTakeoff

**Solutions:**
1. Check zzTakeoff documentation for valid formulas
2. Common valid formulas:
   - Area, Length, Width, Count
   - Length * Width
   - Count * Length
3. Edit CSV to use valid formulas

### Problem: "Units don't match"

**Issue**: Unit mismatch errors

**Solutions:**
1. Verify units are valid in zzTakeoff
2. Standardize units in source file
3. Map units correctly

## Performance Issues

### Problem: "Processing very slow"

**Issue**: Takes too long

**Solutions:**
1. **Normal**: 50 items = 10-15 seconds per stage
2. For 500+ items, processing is faster (pattern application)
3. Check internet speed (AI calls require connection)
4. Close other applications using network

### Problem: "High memory usage"

**Issue**: Computer slows down

**Solutions:**
1. Close other applications
2. Process in smaller batches
3. Restart application between large files

## Platform-Specific Issues

### Windows Issues

**Problem: PowerShell execution policy**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Problem: Path too long**
- Move files closer to root (C:\Projects\)

**Problem: Antivirus blocking**
- Add exception for Python scripts

### Mac Issues

**Problem: "Python not found"**
```bash
# Use python3 instead
python3 takeoff_converter.py
```

**Problem: SSL certificate error**
```bash
# Update certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

### Linux Issues

**Problem: Display issues**
```bash
# Set display
export DISPLAY=:0
```

**Problem: Tkinter themes**
```bash
# Install themes
sudo apt-get install python3-tk-dev
```

## Getting Help

### Before Asking for Help

1. ✅ Read this troubleshooting guide
2. ✅ Check QUICKSTART.md
3. ✅ Run test_setup.py
4. ✅ Try sample file
5. ✅ Check error messages

### Information to Provide

When reporting issues, include:
- Python version: `python --version`
- Operating system
- Error messages (full text)
- Steps to reproduce
- Sample data (if possible)

### Common Solutions Summary

| Problem | Quick Fix |
|---------|-----------|
| API key error | Set ANTHROPIC_API_KEY environment variable |
| Import error | `pip install -r requirements.txt` |
| Tkinter missing | Install python3-tk package |
| File won't load | Check encoding, save as UTF-8 |
| Wrong classifications | Add more descriptive names |
| Export fails | Close file in Excel, try different location |
| Slow processing | Normal for AI, check internet |
| App won't start | Run from command line to see errors |

## Still Having Issues?

1. Try the sample file first
2. Test with minimal data (5-10 rows)
3. Check all requirements are met
4. Verify API key is working
5. Review error messages carefully

---

**Most Common Issues:**
1. ❌ API key not set → Set ANTHROPIC_API_KEY
2. ❌ Wrong Python version → Use 3.8+
3. ❌ Packages not installed → Run pip install
4. ❌ File encoding → Save as UTF-8
5. ❌ Expecting instant results → AI takes 10-20 seconds

**Version:** 1.0.0
**Last Updated:** September 2025
