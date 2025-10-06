# Custom Properties & Batch Processing Features

## Overview
The zzTakeoff Converter now supports **Custom Properties** mapping and **Intelligent Batch Processing** for large datasets.

## Features Added

### 1. Custom Property Column Mapping
- **Button Location**: Control panel (appears after loading a file)
- **Functionality**:
  - Maps additional CSV columns to zzTakeoff custom properties
  - Rename column headings as needed
  - Select which columns to include/exclude
  - Shows sample values for each column
  - Custom properties are appended to the export file

**How to Use**:
1. Load your CSV/Excel file
2. Click "Custom Properties" button
3. Check the columns you want to include
4. Rename them if needed (defaults to original column name)
5. Click "Save Mappings"

### 2. Intelligent Batch Processing

#### Context Window Calculation
The application automatically calculates optimal batch sizes based on:
- Selected AI model's context window size
- Estimated token count per row
- Safe margin (80% of available tokens)

**Model Context Windows**:
- Claude models: 200,000 tokens
- GPT-4o/GPT-4 Turbo: 128,000 tokens
- GPT-3.5 Turbo: 16,000 tokens
- Gemini 2.0 Flash: 1,000,000 tokens
- Gemini 1.5 Pro: 2,000,000 tokens
- Gemini 1.5 Flash: 1,000,000 tokens
- DeepSeek: 64,000 tokens

#### Automatic Batching
- Processes datasets larger than batch size automatically
- Shows progress: "Batch X/Y (rows start-end of total)"
- No manual intervention needed
- Results are seamlessly combined

**Functions Updated with Batch Processing**:
1. `generate_cost_types()` - Processes ALL rows in batches
2. `generate_takeoff_types()` - Processes ALL rows in batches
3. `generate_formulas()` - Processes ALL rows in batches

### 3. Token Estimation
- Rough estimate: ~4 characters per token
- Calculates based on actual data sample
- Reserves 5,000 tokens for prompt structure and response
- Batch size range: 10-1000 rows (safety bounds)

## Technical Details

### New Methods
```python
estimate_token_count(text: str) -> int
    # Estimates tokens in text (~4 chars per token)

calculate_batch_size(sample_size: int = 50) -> int
    # Calculates optimal batch size for current model

process_in_batches(data: List[Dict], process_func, description: str) -> List
    # Handles automatic batching with progress updates

show_custom_properties()
    # UI dialog for custom property mapping

apply_custom_properties()
    # Applies custom property mappings to dataframe
```

### Custom Property Storage
- Stored in `self.custom_property_mappings` dictionary
- Format: `{source_column: custom_name}`
- Applied after standard columns
- Included in final export

## Example Workflow

### For Large Dataset (1000+ rows):
1. Load file (1000 rows)
2. Click "Custom Properties" to map additional columns
3. Click "Generate Cost Types"
   - Shows: "Batch 1/5 (1-200 of 1000)"
   - Shows: "Batch 2/5 (201-400 of 1000)"
   - ... continues automatically
4. Click "Generate Takeoff Types"
   - Processes all rows in batches
5. Click "Generate Formulas"
   - Processes all rows in batches
6. Export includes all mapped columns + custom properties

### Custom Properties Example:
**Original CSV Columns**:
- Name
- Unit Price
- Units
- Supplier Reference
- Project Code *(extra)*
- Location *(extra)*
- Notes *(extra)*

**Custom Property Mapping**:
- Project Code → "Project ID"
- Location → "Site Location"
- Notes → "Additional Notes"

**Final Export**: All standard zzTakeoff columns + 3 custom properties

## Benefits

### 1. Scalability
- Handle datasets of any size (within API limits)
- No manual data splitting required
- Automatic optimization per AI model

### 2. Flexibility
- Map any additional columns as custom properties
- Rename columns for zzTakeoff compatibility
- Choose which extra data to include

### 3. Performance
- Optimal batch sizing reduces API costs
- Progress tracking for long operations
- Efficient token usage

### 4. Data Preservation
- No data loss from original CSV
- All custom properties preserved
- Maintains data integrity

## Limitations & Notes

1. **Batch size varies** by model - larger context windows = bigger batches
2. **Progress updates** show batch number and row ranges
3. **Custom properties** appear after standard columns in export
4. **Token estimation** is approximate (~4 chars per token)
5. **API rate limits** may still apply for very large datasets

## Troubleshooting

**If batching seems slow**:
- Consider using models with larger context windows (Gemini 1.5 Pro)
- Check your internet connection
- Verify API key and rate limits

**If custom properties don't appear**:
- Ensure you clicked "Save Mappings"
- Check that checkboxes are enabled
- Verify column names are not empty

**If batch processing fails mid-way**:
- Check API error messages
- Verify API key is valid
- Try smaller model or check rate limits
