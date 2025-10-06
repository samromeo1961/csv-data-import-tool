================================================================================
zzTakeoff Items Import Converter
================================================================================

VERSION: 1.0
CREATED: 2025

DESCRIPTION:
Convert CSV/Excel files from various estimating software formats into
zzTakeoff-compatible import files using AI-powered data classification.

================================================================================
INSTALLATION & SETUP
================================================================================

1. LOCATE THE EXECUTABLE:
   - Find "zzTakeoff Items Import Converter.exe" in the dist\ folder
   - You can move this .exe file anywhere you like

2. FIRST-TIME SETUP - API KEY:
   - Double-click the .exe to launch the application
   - Click the "▼ Settings" section to expand it
   - Select your preferred AI Provider (Claude, ChatGPT, Gemini, or DeepSeek)
   - Click "Configure API Key" and paste your API key
   - The Settings section will automatically collapse after saving

3. GET API KEYS (if you don't have one):

   Claude (Anthropic):
   - Visit: https://console.anthropic.com/
   - Sign up and get API key from Account Settings

   ChatGPT (OpenAI):
   - Visit: https://platform.openai.com/
   - Sign up and get API key from API Keys section

   Gemini (Google):
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with Google account and create API key

   DeepSeek:
   - Visit: https://platform.deepseek.com/
   - Sign up and get API key from API Keys section

================================================================================
QUICK START GUIDE
================================================================================

BASIC WORKFLOW:

1. Settings (One-time setup)
   - Select Unit System (Imperial/Metric)
   - Choose AI Provider
   - Configure API Key
   - Select Model

2. File Operations
   - Click "Load CSV/Excel" to load your data file
   - (Optional) Save/Load Progress to resume work later

3. Data Mapping & Templates
   - Click "Import Templates" to save/load column mappings
   - Click "Custom Properties" to map additional columns
   - (Optional) Use Formula Templates and Markup settings

4. AI Processing Workflow (Follow the 3 steps)
   Step 1 → Generate Cost Types
   Step 2 → Generate Takeoff Types
   Step 3 → Generate Formulas

5. Export
   - Click "📤 Export to zzTakeoff" to save your converted file

================================================================================
KEY FEATURES
================================================================================

✓ IMPORT TEMPLATES
  - Save column mappings for different software formats
  - Auto-detect previously used formats
  - Update templates when SQL query formats change
  - Clone templates to create variations

✓ CUSTOM PROPERTIES
  - Map additional CSV columns to zzTakeoff custom properties
  - Rename column headings as needed
  - Preserves leading zeros (001, 007, etc.)
  - Select which columns to include/exclude

✓ INTELLIGENT BATCH PROCESSING
  - Automatically handles large datasets
  - Calculates optimal batch sizes per AI model
  - Processes data in chunks to fit context windows
  - Shows progress: "Batch X/Y (rows start-end of total)"

✓ SAVE/LOAD PROGRESS
  - Save work-in-progress at any stage
  - Resume later without re-running expensive AI calls
  - Files saved as .zztakeoff_progress

✓ MULTIPLE AI PROVIDERS
  - Claude (Sonnet 4, Opus, Haiku)
  - ChatGPT (GPT-4o, GPT-4 Turbo, GPT-3.5)
  - Gemini (2.0 Flash, 1.5 Pro, 1.5 Flash)
  - DeepSeek (Chat, Coder)

================================================================================
TIPS & BEST PRACTICES
================================================================================

1. USE IMPORT TEMPLATES
   - Save your column mappings the first time you process a file
   - Reuse templates for future imports from the same software
   - Update templates when export formats change

2. LARGE DATASETS
   - The app automatically batches large files
   - Models with larger context windows (Gemini 1.5 Pro) process faster
   - Watch the progress indicator: "Batch 2/5 (201-400 of 1000)"

3. CUSTOM PROPERTIES
   - Load your file first, then configure Custom Properties
   - Use dropdown to select columns from your actual data
   - Leading zeros are preserved (001 stays as 001, not 1)

4. SAVE PROGRESS
   - Save after completing Cost Types or Takeoff Types
   - Resume work later without re-running expensive AI calls
   - Great for testing formulas with different settings

5. FORMULA TEMPLATES
   - Save frequently-used formulas for reuse
   - Clone templates to create variations
   - Formulas are applied during Step 3

================================================================================
SUPPORTED FILE FORMATS
================================================================================

INPUT:
- CSV files (.csv)
- Excel files (.xlsx, .xls)

OUTPUT:
- Excel file (.xlsx) formatted for zzTakeoff import
- Includes all standard columns + custom properties
- Leading zeros preserved with text formatting

================================================================================
TROUBLESHOOTING
================================================================================

ISSUE: "API Key Error"
SOLUTION: Verify your API key is correct and has available credits

ISSUE: "Batch processing seems slow"
SOLUTION: Try models with larger context windows (Gemini 1.5 Pro)
         Check your internet connection

ISSUE: "Custom properties don't appear in export"
SOLUTION: Ensure you clicked "Save Mappings" in Custom Properties dialog
         Verify checkboxes are enabled for desired columns

ISSUE: "Leading zeros removed (001 becomes 1)"
SOLUTION: Custom Properties automatically preserve leading zeros
         Make sure you're mapping the column via Custom Properties

ISSUE: "Template columns don't match my file"
SOLUTION: Update the template using "Import Templates" → Select template →
         Load your file → Update mappings → Check "Update existing template"

================================================================================
SYSTEM REQUIREMENTS
================================================================================

- Operating System: Windows 10/11
- Memory: 4GB RAM minimum (8GB recommended for large files)
- Internet: Required for AI API calls
- Disk Space: 200MB for application + space for your data files

================================================================================
DATA PRIVACY
================================================================================

- Your data is sent to the selected AI provider for processing
- No data is stored on external servers beyond API processing
- API keys are stored locally in config.py file
- Progress files (.zztakeoff_progress) are saved locally only

================================================================================
SUPPORT & FEEDBACK
================================================================================

For questions, issues, or feature requests, please contact the developer.

================================================================================
LICENSE
================================================================================

This software is provided for use with zzTakeoff estimating software.
All rights reserved.

================================================================================
