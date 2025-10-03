# zzTakeoff Import Converter

AI-powered tool to convert estimating software exports (Databuild, PlanSwift, Bluebeam, etc.) into zzTakeoff import format.

## Features

- **Multi-source support**: Handles CSV/Excel exports from various estimating software
- **AI-powered mapping**: Uses Claude AI to intelligently classify:
  - Cost Types (Material, Labor, Equipment, Subcontract, Other)
  - Takeoff Types (Area, Linear, Count, Segment)
  - Formulas based on item characteristics
- **Interactive GUI**: Easy-to-use desktop interface
- **Pattern learning**: Improves accuracy by learning from classifications
- **Batch processing**: Process entire estimating exports at once

## Requirements

- Python 3.8 or higher
- Anthropic API key (for Claude AI)

## Installation

### Step 1: Install Python
Make sure Python 3.8+ is installed on your system.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up API Key
You need an Anthropic API key to use the AI features.

**Option A: Environment Variable (Recommended)**
```bash
# Windows
set ANTHROPIC_API_KEY=your_api_key_here

# Mac/Linux
export ANTHROPIC_API_KEY=your_api_key_here
```

**Option B: Edit the code**
In `takeoff_converter.py`, line 40, replace:
```python
self.client = anthropic.Anthropic()
```
with:
```python
self.client = anthropic.Anthropic(api_key="your_api_key_here")
```

## Usage

### Step 1: Launch the Application
```bash
python takeoff_converter.py
```

### Step 2: Load Your Export File
1. Click "Load CSV/Excel"
2. Select your estimating software export (Databuild, PlanSwift, etc.)
3. The data will be loaded and displayed

### Step 3: Generate Cost Types
1. Click "Generate Cost Types (AI)"
2. Wait for AI to analyze and classify items as Material/Labor/Equipment/Subcontract/Other
3. Review the results in the preview

### Step 4: Generate Takeoff Types
1. Click "Generate Takeoff Types (AI)"
2. AI will classify items as Area/Linear/Count/Segment based on units
3. Review the classifications

### Step 5: Generate Formulas
1. Click "Generate Formulas (AI)"
2. AI will generate appropriate formulas based on takeoff types
3. Review the generated formulas

### Step 6: Export
1. Click "Export to zzTakeoff"
2. Choose save location
3. Import the generated file into zzTakeoff

## Understanding the AI Classification

### Cost Types
- **Material**: Items being supplied (bricks, cement, fixtures)
- **Labor**: Installation, fixing, painting work
- **Equipment**: Rental or hire items
- **Subcontract**: Work by subcontractors (often identified by supplier names)
- **Other**: Miscellaneous items

### Takeoff Types
- **Area**: Measured in square units (SM, m2, SQ M)
- **Linear**: Measured in linear units (M, Lm, meters)
- **Count**: Counted items (EA, THOUS, bags)
- **Segment**: Segmented linear items

### Formulas
The AI generates formulas based on takeoff type:
- Area items: `Area` or `Length * Width`
- Linear items: `Length`
- Count items: `Count` or `Quantity`

## Source File Requirements

The tool works best with files containing these columns:
- **Name/Description** (required): Item description
- **Units** (recommended): Unit of measure (EA, M, SM, etc.)
- **Quantity** (optional): Helps with classification
- **Unit Price/Cost** (optional): Mapped to Cost Each
- **Supplier Reference** (optional): Helps identify subcontract work
- **Code/SKU** (optional): Mapped to SKU field

## Supported Export Formats

### Tested With:
- ✅ Databuild exports
- ✅ PlanSwift CSV exports
- ✅ Bluebeam CSV exports
- ✅ BuildExact exports
- ✅ Generic pricing lists

### File Formats:
- CSV (.csv)
- Excel (.xlsx, .xls)

## zzTakeoff Import Format

The tool generates files with these required fields:
- **Cost Type*** (required)
- **Name*** (required)
- **Takeoff Type*** (required)
- **Formula*** (required)
- Usage
- Waste %
- Round Up to Nearest
- SKU
- Description
- Cost Each
- Markup %
- Units

*Fields marked with asterisk are required by zzTakeoff

## Troubleshooting

### "AI API Error"
- Check your Anthropic API key is set correctly
- Ensure you have API credits available
- Check your internet connection

### "Failed to load file"
- Ensure file is a valid CSV or Excel format
- Check for special characters in file path
- Try opening in Excel/Notepad to verify format

### Incorrect Classifications
- The AI learns from patterns in your data
- Process more files to improve accuracy
- You can manually edit the generated CSV before importing

### Missing Columns in Source File
- The tool adapts to available columns
- Minimum required: A description/name column
- More columns = better AI classification

## Tips for Best Results

1. **Clean source data**: Remove empty rows and ensure consistent formatting
2. **Descriptive names**: Better descriptions = better AI classification
3. **Review before export**: Check a few items to verify accuracy
4. **Batch similar items**: Group similar work types together in source file
5. **Use supplier references**: Include supplier names for better subcontract identification

## Advanced Usage

### Mapping History
The tool saves classification patterns in `mapping_history.json`. Delete this file to reset learning.

### Processing Multiple Files
Process one file at a time. The AI learns and improves with each file.

### Custom Modifications
Edit `takeoff_converter.py` to:
- Add custom classification rules
- Modify AI prompts
- Add additional export fields

## Support

For issues or questions:
1. Check this README
2. Review the example Databuild export provided
3. Verify your API key is working
4. Check Python and package versions

## Future Enhancements

Planned features:
- [ ] Manual override capability for individual items
- [ ] Template saving for common source formats
- [ ] Bulk edit functionality
- [ ] Direct zzTakeoff API integration
- [ ] Support for more estimating software

## License

This tool is provided as-is for converting estimating data to zzTakeoff format.

## Version

Current version: 1.0.0
Last updated: 2025

---

**Note**: This tool requires an active Anthropic API account. Visit https://www.anthropic.com to set up an account and get your API key.
