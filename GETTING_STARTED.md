# Getting Started Guide

## Quick Start for Users of the Old System

If you're familiar with the old system, here's how to run it with the new structure:

### Option 1: Use Docker (Recommended)

**Run with Docker exactly like before:**
```bash
# Build the image
docker-compose build

# Run the new full analysis (default)
docker-compose up

# Or run the legacy workflow (like old main.py)
docker-compose up ward-optimization-legacy

# Or run the original main.py
docker-compose up ward-optimization-original
```

### Option 2: Use the Legacy Script

This runs exactly like the old `main.py`:

```bash
python scripts/run_legacy_workflow.py
```

This will:
- Run current model evaluation
- Run optimized model evaluation  
- Generate all visualizations
- Save results to the `output/` directory (same as before)

### Option 3: Use the New Full Analysis Script

For the new modular system with more features:

```bash
python scripts/run_full_analysis.py
```

This provides:
- More detailed analysis
- Additional visualizations
- Capacity analysis
- Organized outputs in `outputs/` directory

## What Changed?

### File Locations
- **Old**: Everything was in the root directory
- **New**: Code is organized in `src/` with submodules

### Running Scripts
- **Old**: `python main.py`
- **New**: `python scripts/run_full_analysis.py` or `python scripts/run_legacy_workflow.py`

### Output Location
- **Old**: `output/` directory
- **New**: `outputs/` directory with better organization (unless using legacy script)

### Data Location
- **Old**: `data/` directory mixed everything
- **New**: 
  - Raw data: `data/raw/`
  - Processed data: `data/processed/`
  - External data: `data/external/`

## Step-by-Step Guide

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data

If you have new monthly census Excel files:
1. Place them in `data/raw/YYYY/` (where YYYY is the year)
2. Run preprocessing:
   ```bash
   python util_scripts/preprocess_data.py
   ```

### 3. Run Analysis

Choose one of these options:

**For Legacy Behavior:**
```bash
python scripts/run_legacy_workflow.py
```

**For New Features:**
```bash
python scripts/run_full_analysis.py
```

### 4. View Results

**Legacy Script Results:**
- Charts: `output/charts/`
- Data: `output/data/`

**New Script Results:**
- Charts: `outputs/visualizations/`
- Data: `outputs/exports/`
- Reports: `outputs/reports/`

## Using Individual Components

### Run Only Optimization
```python
from src.core.optimizer import WardOptimizer

optimizer = WardOptimizer()
results = optimizer.optimize_space()
print(f"Optimal: {results[1]} single, {results[0]} double rooms")
```

### Evaluate Models Only
```python
from src.models.current_model import CurrentModel
from src.models.optimized_model import OptimizedModel

# Evaluate current configuration
current = CurrentModel()
current_results = current.evaluate('data/processed/training/final_census_data.csv')

# Evaluate optimized configuration  
optimized = OptimizedModel()
optimized_results = optimized.evaluate('data/processed/training/final_census_data.csv')
```

### Generate Charts Only
```python
from src.visualization.comparison_charts import ComparisonCharts

charts = ComparisonCharts(current_results, optimized_results)
charts.plot_all_comparisons()
```

## Configuration

To customize the analysis, edit the YAML files in `config/`:
- `optimization_params.yaml` - Change ward capacity, constraints
- `model_configs.yaml` - Modify file paths, model settings
- `visualization_settings.yaml` - Adjust chart appearance

## Troubleshooting

### "Module not found" Error
Make sure you're running scripts from the project root directory, not from inside `scripts/`.

### Missing Data Files
If you get file not found errors:
1. Check that census Excel files are in `data/raw/`
2. Run preprocessing: `python util_scripts/preprocess_data.py`

### Old Scripts Not Working
The old scripts (`main.py`, `model_current.py`, etc.) still exist and should work.
If they don't, use the legacy workflow script: `python scripts/run_legacy_workflow.py`

## Need Help?

1. Check the full README: `README_updated.md`
2. Look at the documentation in `docs/`
3. Review the example code in the scripts