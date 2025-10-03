# Quick Start Guide

## Get Running in 5 Minutes

### 1. Install Python Packages
```bash
pip install pandas openpyxl anthropic
```

### 2. Get Your API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Go to API Keys section
4. Create a new key
5. Copy it

### 3. Set Your API Key

**Windows (Command Prompt):**
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**Mac/Linux (Terminal):**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 4. Test the Setup
```bash
python test_setup.py
```

If everything is green ✓, you're ready!

### 5. Launch the Application
```bash
python takeoff_converter.py
```

## First Time Use

### Try the Sample File
1. Launch the application
2. Click "Load CSV/Excel"
3. Select `sample_databuild_export.csv`
4. Click through each AI generation button:
   - Generate Cost Types
   - Generate Takeoff Types  
   - Generate Formulas
5. Click "Export to zzTakeoff"
6. Import the result into zzTakeoff

### Use Your Own File
1. Export from your estimating software (Databuild, PlanSwift, etc.)
2. Save as CSV or Excel
3. Load it in the converter
4. Follow the same steps as above

## Workflow

```
Your Export File
     ↓
Load into Converter
     ↓
AI Generates Cost Types (Material/Labor/etc.)
     ↓
AI Generates Takeoff Types (Area/Linear/Count)
     ↓
AI Generates Formulas
     ↓
Export to zzTakeoff Format
     ↓
Import into zzTakeoff
```

## Common Issues

**"API Error"**
- Check your API key is set correctly
- Make sure you have credits in your Anthropic account

**"Module not found"**
- Run: `pip install -r requirements.txt`

**Can't see the GUI**
- Make sure tkinter is installed:
  - Windows: Included with Python
  - Mac: Included with Python
  - Linux: `sudo apt-get install python3-tk`

## What the AI Does

### Cost Type Classification
Analyzes item names, suppliers, and descriptions to determine:
- **Material**: "Supply Face Bricks", "Cement"
- **Labor**: "Fix tiles", "Install batts", "Rough-In"
- **Subcontract**: Items with supplier names (RAVPLUMB, MINHQUAN)
- **Equipment**: Rental items
- **Other**: Everything else

### Takeoff Type Classification
Based on units:
- **Area**: SM, m2, SQ M → Area
- **Linear**: M, Lm, LM → Linear
- **Count**: EA, THOUS, bag → Count

### Formula Generation
Creates formulas based on takeoff type:
- Area → "Area" or "Length * Width"
- Linear → "Length"
- Count → "Count"

## Tips

1. **Better descriptions = better AI results**
2. **Process one file at a time**
3. **Review the first few items** to check accuracy
4. **The AI learns** - it gets better with more data
5. **You can edit** the exported CSV before importing

## Need Help?

Check the full README.md for detailed documentation.

---

**You're all set!** Start with the sample file, then try your own data.
