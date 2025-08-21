# Meta Ads Parser Validation Suite

A comprehensive set of scripts to validate the performance of our advanced ad name parser against real Meta Ads data and analyst-provided CSV data.

## 📋 Overview

This validation suite tests our ad name parser against:
- **Real Meta API data** from July 28 - August 10, 2025 (matching your analyst's date range)
- **Analyst's CSV data** with manually categorized ad information
- **Sample data** based on the ad name examples you provided

## 🚀 Quick Start

### Option 1: Complete Validation (Recommended)
```bash
# Run full validation suite
python run_parser_validation.py

# Or with your analyst's CSV file
python run_parser_validation.py path/to/analyst_data.csv
```

### Option 2: Quick Test
```bash
# Run basic tests only (faster)
python run_parser_validation.py --quick
```

## 📁 Individual Scripts

### 1. `test_ad_name_parsing.py`
Tests basic parser functionality with known examples.
```bash
python test_ad_name_parsing.py
```

### 2. `fetch_july_august_meta_data.py`
Fetches real Meta API data for the exact date range July 28 - August 10, 2025.
```bash
# Fetch data and test parser
python fetch_july_august_meta_data.py --save-csv --test-parser

# Just fetch data
python fetch_july_august_meta_data.py --save-csv
```

### 3. `test_parser_vs_analyst_data.py`
Compares parser results against analyst's categorized data.
```bash
# Use sample data
python test_parser_vs_analyst_data.py

# Use your CSV file
python test_parser_vs_analyst_data.py analyst_data.csv
```

## 📊 Expected CSV Format

If you have analyst data in CSV format, it should contain these columns:

```csv
Reporting starts,Reporting ends,Launch Date,Days Live,Category,Product,Color,Content Type,Handle,Format,Ad Name,Campaign Optimization,Amount spent (USD)
2025-07-28,2025-08-10,2025-07-09,32,Tumbling Mat,Folklore,Fog,Whitelist,BrookeKnuth,Video,"7/9/2025 - Tumbling Mat - Folklore - Fog - Whitelist - BrookeKnuth - Video - Brooke.knuth Folklore Tumbling Mat Whitelist",Standard,1250.75
```

A sample CSV file (`sample_analyst_data.csv`) is included for testing.

## 📈 What Gets Validated

The validation suite checks parser accuracy for:

- **Launch Date Extraction** - Date parsing from ad names
- **Category Detection** - Tumbling Mat, Bath, Standing Mat, Play Mat, etc.
- **Product Identification** - Folklore, Checks, Multi, Arden, etc.
- **Color Recognition** - Fog, Biscuit, Multi, Wisp, etc.
- **Content Type Parsing** - Whitelist, Brand, UGC, Brand UGC, etc.
- **Handle/Creator Detection** - BrookeKnuth, HoN, Madison, etc.
- **Format Classification** - Video, Collection, Carousel, Image, etc.
- **Campaign Optimization** - Standard vs Incremental

## 📄 Generated Reports

After running validation, you'll get:

1. **Text Report** (`parser_validation_report_TIMESTAMP.txt`)
   - Human-readable summary with accuracy percentages
   - Field-by-field breakdown
   - Specific discrepancies and recommendations

2. **JSON Report** (`parser_validation_report_TIMESTAMP.json`)
   - Machine-readable detailed results
   - Full comparison data for further analysis

3. **Discrepancies CSV** (`parser_validation_report_TIMESTAMP_discrepancies.csv`)
   - Specific cases where parser disagreed with analyst data
   - Useful for targeted improvements

4. **Raw Meta Data** (`validation_run_raw.csv`)
   - Direct Meta API results for the date range

5. **Parsed Comparison** (`validation_run_parsed.csv`)
   - Side-by-side comparison of Meta data vs parser results

## ✅ Success Criteria

The validation considers the parser successful if:
- **Overall accuracy ≥ 90%** (excellent performance)
- **Overall accuracy ≥ 80%** (acceptable with warnings)
- **Overall accuracy < 80%** (needs improvement)

## 🔧 Troubleshooting

### Meta API Connection Issues
If you get Meta API errors:
```bash
# Test Meta connection separately
python test_meta_connection.py

# Check environment variables
echo $META_ACCESS_TOKEN
echo $META_ACCOUNT_ID
```

### Parser Logic Issues
If specific fields show low accuracy:
1. Review discrepancies CSV for patterns
2. Check parser logic in `app/services/ad_name_parser.py`
3. Update recognition patterns/lists
4. Re-run validation

### CSV Format Issues
If your analyst CSV has different column names:
1. Check the `_normalize_column_name()` function in `test_parser_vs_analyst_data.py`
2. Add your column mappings
3. Or rename your CSV columns to match expected format

## 🎯 Example Usage Scenarios

### Scenario 1: You have analyst's CSV data
```bash
# Place your CSV file in the backend directory
python run_parser_validation.py my_analyst_data.csv
```

### Scenario 2: Testing parser improvements
```bash
# After updating parser logic
python run_parser_validation.py --quick
```

### Scenario 3: Just checking Meta API data
```bash
# Fetch and analyze current ad names
python fetch_july_august_meta_data.py --test-parser --save-csv
```

## 💡 Interpreting Results

### High Accuracy (90%+)
- Parser is production-ready
- Minor tweaks might improve edge cases
- Consider monitoring ongoing accuracy

### Medium Accuracy (80-90%)
- Parser is functional but needs refinement
- Review specific field discrepancies
- Focus on most problematic categories

### Low Accuracy (<80%)
- Significant parser improvements needed
- May need more comprehensive ad name patterns
- Consider alternative parsing approaches

## 📞 Support

If you encounter issues:
1. Check the generated text report for specific recommendations
2. Review the discrepancies CSV for patterns
3. Examine the detailed JSON report for full context
4. Update parser rules based on real ad name patterns found

The validation suite is designed to give you complete visibility into how well the parser performs against real House of Noa ad data.