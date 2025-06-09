# Inpatient Psych Ward Space Optimization

## Project Overview

This project implements a sophisticated optimization system for an inpatient psychiatric ward with a 26-bed capacity. Using linear programming and data-driven analysis, it determines the optimal configuration of single and double rooms to minimize bed waste while accommodating patient needs. The system compares the current configuration (all double rooms) with an optimized configuration to demonstrate significant efficiency improvements.

## Key Features

- **Linear Programming Optimization**: Determines optimal room configuration using PuLP solver
- **Comprehensive Data Pipeline**: Processes monthly census data from Excel files
- **Model Comparison**: Evaluates current vs. optimized configurations
- **Rich Visualizations**: Generates publication-quality charts and analysis reports
- **Modular Architecture**: Clean, maintainable code following software engineering best practices
- **Configuration-Driven**: YAML-based configuration for easy customization

## Project Structure

```
psych-ward-optimization/
├── src/                        # Source code
│   ├── core/                   # Optimization engine
│   ├── models/                 # Configuration models
│   ├── analysis/               # Analysis modules
│   ├── preprocessing/          # Data pipeline
│   └── visualization/          # Chart generation
├── config/                     # Configuration files
├── data/                       # Data files (raw/processed)
├── outputs/                    # Generated outputs
├── scripts/                    # Executable scripts
├── docs/                       # Documentation
└── tests/                      # Test suite
```

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/psych-ward-optimization.git
cd psych-ward-optimization
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Quick Start

Run the complete analysis pipeline:

```bash
python scripts/run_full_analysis.py
```

This will:
1. Process census data
2. Run optimization
3. Evaluate models
4. Generate all visualizations
5. Create analysis reports

### Individual Components

#### 1. Data Preprocessing

Process raw census Excel files:

```bash
python scripts/preprocess_data.py --input data/raw --output data/processed
```

#### 2. Run Optimization

Find optimal room configuration:

```bash
python scripts/run_optimization.py --data data/processed/training/final_census_data.csv
```

#### 3. Evaluate Models

Compare current and optimized configurations:

```bash
python scripts/evaluate_models.py --current --optimized
```

#### 4. Generate Visualizations

Create comparison charts:

```bash
python scripts/generate_reports.py --type comparison --output outputs/visualizations
```

### Using the Python API

```python
# Import modules
from src.core.optimizer import WardOptimizer
from src.models.current_model import CurrentModel
from src.models.optimized_model import OptimizedModel
from src.visualization.comparison_charts import ComparisonCharts

# Run optimization
optimizer = WardOptimizer()
results = optimizer.optimize_space()
print(f"Optimal configuration: {results[1]} single rooms, {results[0]} double rooms")

# Evaluate models
current = CurrentModel()
current_results = current.evaluate('data/processed/training/final_census_data.csv')

optimized = OptimizedModel()
optimized_results = optimized.evaluate('data/processed/training/final_census_data.csv')

# Generate visualizations
charts = ComparisonCharts(current_results, optimized_results)
charts.plot_all_comparisons('outputs/visualizations/comparisons')
```

## Configuration

The system uses YAML configuration files in the `config/` directory:

- `optimization_params.yaml`: Ward capacity, room limits, solver settings
- `model_configs.yaml`: Model configurations and file paths
- `visualization_settings.yaml`: Chart styling and export settings
- `data_pipeline.yaml`: Data processing parameters

Example configuration change:
```yaml
# config/optimization_params.yaml
ward:
  total_beds: 26  # Change to your ward capacity
  max_double_rooms: 13
  max_single_rooms: 26
```

## Results

### Optimization Results
- **Current Model**: 0 single rooms, 13 double rooms
- **Optimized Model**: 10 single rooms, 8 double rooms
- **Efficiency Improvement**: ~99.99% efficiency on test data
- **Waste Reduction**: Minimal waste (2 beds over 4-month test period)

### Key Metrics
- **Wasted Beds**: Single-room patients occupying double rooms
- **Wasted Potential**: Double-room patients forced into single rooms
- **Efficiency**: (Available Beds - Waste) / Available Beds

## Docker Support

Run the entire system in a container:

```bash
# Build the image
docker-compose build

# Run the analysis
docker-compose up

# Run with custom data
docker run -v $(pwd)/data:/app/data psych-ward-optimizer
```

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Models
1. Create a new class inheriting from `BaseModel`
2. Implement the `evaluate_day()` method
3. Register in configuration

### Adding New Visualizations
1. Create a new class inheriting from `BaseChart`
2. Implement chart methods
3. Use `ChartConfig` for consistent styling

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Optimization Algorithm](docs/optimization_algorithm.md)
- [API Reference](docs/api_reference.md)
- [Results Analysis](optimizer_results.md)

## Citation

If you use this work in your research, please cite:
```
@software{psych_ward_optimization,
  title = {Psych Ward Room Optimization System},
  author = {Your Name},
  year = {2024},
  url = {https://github.com/yourusername/psych-ward-optimization}
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hospital staff for providing domain expertise
- PuLP developers for the optimization solver
- Contributors and reviewers