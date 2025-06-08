#!/usr/bin/env python3
"""
Legacy workflow script that mimics the old main.py behavior.

This script provides backwards compatibility for users familiar
with the original workflow.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import old modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the old modules
import model_current
import model_optimizer
import visualizer
from src.utils.logger import get_logger


logger = get_logger(__name__)


def main():
    """Run the legacy workflow similar to old main.py."""
    logger.info("Running legacy workflow for backwards compatibility")
    
    # Define paths (matching old structure)
    data_path = 'data/processed/training/final_census_data.csv'
    output_dir = 'output'
    
    # Ensure output directory exists
    Path(output_dir).mkdir(exist_ok=True)
    Path(f"{output_dir}/data").mkdir(exist_ok=True)
    Path(f"{output_dir}/charts").mkdir(exist_ok=True)
    
    # Step 1: Run current model evaluation
    logger.info("Evaluating current model...")
    current_evaluator = model_current.CurrentModelEvaluator(data_path)
    current_df = current_evaluator.calculate_wasted_beds()
    current_df.to_csv(f'{output_dir}/data/current_model_data.csv', index=False)
    logger.info(f"Current model results saved to {output_dir}/data/current_model_data.csv")
    
    # Step 2: Run optimized model evaluation
    logger.info("Evaluating optimized model...")
    optimized_evaluator = model_optimizer.OptimizedModelEvaluator(data_path)
    optimized_df = optimized_evaluator.calculate_wasted_beds()
    optimized_df.to_csv(f'{output_dir}/data/optimized_model_data.csv', index=False)
    logger.info(f"Optimized model results saved to {output_dir}/data/optimized_model_data.csv")
    
    # Step 3: Generate visualizations
    logger.info("Generating visualizations...")
    viz = visualizer.Visualizer(current_df, optimized_df)
    
    # Generate all comparison charts
    viz.plot_wasted_beds_comparison(f'{output_dir}/charts/wasted_beds_comparison.png')
    viz.plot_wasted_potential_comparison(f'{output_dir}/charts/wasted_potential_comparison.png')
    viz.plot_daily_efficiency_comparison(f'{output_dir}/charts/daily_efficiency_comparison.png')
    viz.plot_cumulative_efficiency_comparison(f'{output_dir}/charts/cumulative_efficiency_comparison.png')
    
    logger.info(f"Visualizations saved to {output_dir}/charts/")
    
    # Print summary statistics
    print("\n=== Analysis Summary ===")
    print("\nCurrent Model (All Double Rooms):")
    print(f"  Total Wasted Beds: {current_df['Wasted Beds'].sum()}")
    print(f"  Average Daily Efficiency: {current_df['Daily Efficiency'].mean():.2%}")
    print(f"  Final Cumulative Efficiency: {current_df['Cumulative Efficiency'].iloc[-1]:.2%}")
    
    print("\nOptimized Model (10 Single, 8 Double):")
    print(f"  Total Wasted Beds: {optimized_df['Wasted Beds'].sum()}")
    print(f"  Average Daily Efficiency: {optimized_df['Daily Efficiency'].mean():.2%}")
    print(f"  Final Cumulative Efficiency: {optimized_df['Cumulative Efficiency'].iloc[-1]:.2%}")
    
    print("\nImprovement:")
    waste_reduction = current_df['Wasted Beds'].sum() - optimized_df['Wasted Beds'].sum()
    efficiency_improvement = optimized_df['Daily Efficiency'].mean() - current_df['Daily Efficiency'].mean()
    print(f"  Waste Reduction: {waste_reduction} beds")
    print(f"  Efficiency Improvement: {efficiency_improvement:.2%}")
    
    print("\nAnalysis complete! Check the output/ directory for results.")


if __name__ == "__main__":
    main()