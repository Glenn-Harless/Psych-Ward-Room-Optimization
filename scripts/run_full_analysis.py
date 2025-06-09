#!/usr/bin/env python3
"""
Run complete analysis pipeline.

This script orchestrates the entire ward optimization analysis,
from data processing through visualization generation.
"""

import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.preprocessing.census_processor import CensusProcessor
from src.core.optimizer import WardOptimizer
from src.models.current_model import CurrentModel
from src.models.optimized_model import OptimizedModel
from src.visualization.comparison_charts import ComparisonCharts
from src.visualization.optimization_charts import OptimizationCharts
from src.analysis.capacity_analyzer import CapacityAnalyzer
from src.visualization.capacity_charts import CapacityCharts
from src.utils.logger import get_logger
from src.utils.constants import config


logger = get_logger(__name__)


def main():
    """Run the complete analysis pipeline."""
    logger.info("Starting Psych Ward Optimization Analysis")
    
    # Step 1: Process data (if needed)
    logger.info("Step 1: Checking data...")
    training_data_path = config.get_data_path('processed/training/final_census_data.csv')
    
    if not training_data_path.exists():
        logger.info("Processing raw census data...")
        processor = CensusProcessor()
        
        # Get raw data files
        raw_files = [
            config.get_data_path('raw/2022/Monthly Census 2022.xlsx'),
            config.get_data_path('raw/2023/Monthly Census 2023.xlsx'),
            config.get_data_path('raw/2024/Monthly Census 2024.xlsx')
        ]
        
        # Process files
        processor.process_files(raw_files, training_data_path)
    else:
        logger.info("Training data already exists, skipping preprocessing")
    
    # Step 2: Run optimization
    logger.info("\nStep 2: Running optimization...")
    optimizer = WardOptimizer()
    optimization_results = optimizer.optimize_space()
    
    logger.info(f"Optimization Results:")
    logger.info(f"  Optimal configuration: {optimization_results[1]} single, {optimization_results[0]} double rooms")
    logger.info(f"  Total waste: {optimization_results[2] + optimization_results[3]}")
    logger.info(f"  Efficiency: {optimization_results[5]:.2%}")
    
    # Step 3: Evaluate models
    logger.info("\nStep 3: Evaluating models...")
    
    # Current model
    current_model = CurrentModel()
    current_results = current_model.evaluate(str(training_data_path))
    current_metrics = current_model.get_metrics()
    logger.info(f"Current model efficiency: {current_metrics['avg_efficiency']:.2f}%")
    
    # Optimized model
    optimized_model = OptimizedModel()
    optimized_results = optimized_model.evaluate(str(training_data_path))
    optimized_metrics = optimized_model.get_metrics()
    logger.info(f"Optimized model efficiency: {optimized_metrics['avg_efficiency']:.2f}%")
    
    # Save model results
    current_output = config.get_output_path('current_model_data.csv', 'exports/model_outputs')
    optimized_output = config.get_output_path('optimized_model_data.csv', 'exports/model_outputs')
    
    current_model.save_results(str(current_output))
    optimized_model.save_results(str(optimized_output))
    
    # Step 4: Run capacity analysis
    logger.info("\nStep 4: Running capacity analysis...")
    
    # Load census data for capacity analysis
    census_data = processor.processed_data if 'processor' in locals() else None
    if census_data is None:
        import pandas as pd
        census_data = pd.read_csv(training_data_path)
    
    # Analyze current model capacity
    current_capacity_analyzer = CapacityAnalyzer(current_model)
    current_capacity_results = current_capacity_analyzer.analyze_capacity(census_data)
    
    # Analyze optimized model capacity
    optimized_capacity_analyzer = CapacityAnalyzer(optimized_model)
    optimized_capacity_results = optimized_capacity_analyzer.analyze_capacity(census_data)
    
    # Step 5: Generate visualizations
    logger.info("\nStep 5: Generating visualizations...")
    
    # Comparison charts
    logger.info("Creating comparison charts...")
    comparison_charts = ComparisonCharts(current_results, optimized_results)
    comparison_output = config.get_output_path('comparisons', 'visualizations')
    comparison_charts.plot_all_comparisons(comparison_output)
    
    # Optimization charts
    logger.info("Creating optimization analysis charts...")
    optimization_charts = OptimizationCharts(census_data)
    optimization_output = config.get_output_path('optimizations', 'visualizations')
    optimization_charts.generate_optimization_report(optimization_output)
    
    # Capacity charts
    logger.info("Creating capacity analysis charts...")
    capacity_charts = CapacityCharts()
    capacity_output = config.get_output_path('capacity', 'visualizations')
    
    # Generate capacity reports for both models
    capacity_charts.generate_capacity_report(
        current_capacity_results,
        comparison_results=[
            ('Current Model', current_capacity_results),
            ('Optimized Model', optimized_capacity_results)
        ],
        output_dir=capacity_output
    )
    
    # Step 6: Generate summary report
    logger.info("\nStep 6: Generating summary report...")
    
    summary = {
        'optimization': {
            'optimal_single_rooms': optimization_results[1],
            'optimal_double_rooms': optimization_results[0],
            'total_waste': optimization_results[2] + optimization_results[3],
            'efficiency': optimization_results[5]
        },
        'current_model': current_metrics,
        'optimized_model': optimized_metrics,
        'improvement': {
            'efficiency_gain': optimized_metrics['avg_efficiency'] - current_metrics['avg_efficiency'],
            'waste_reduction': current_metrics['total_wasted_beds'] - optimized_metrics['total_wasted_beds'],
            'days_with_waste_reduction': current_metrics['days_with_waste'] - optimized_metrics['days_with_waste']
        }
    }
    
    # Save summary
    import json
    import numpy as np
    
    # Convert numpy types to native Python types
    def convert_numpy_types(obj):
        """Recursively convert numpy types to native Python types."""
        if isinstance(obj, dict):
            return {k: convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_types(v) for v in obj]
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif hasattr(obj, 'item'):  # Handle numpy scalars
            return obj.item()
        return obj
    
    summary_converted = convert_numpy_types(summary)
    
    summary_path = config.get_output_path('analysis_summary.json', 'reports/optimization_results')
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(summary_path, 'w') as f:
        json.dump(summary_converted, f, indent=2)
    
    logger.info(f"\nAnalysis complete! Summary saved to {summary_path}")
    logger.info(f"Key findings:")
    logger.info(f"  - Optimal configuration: {summary['optimization']['optimal_single_rooms']}S/{summary['optimization']['optimal_double_rooms']}D")
    logger.info(f"  - Efficiency improvement: {summary['improvement']['efficiency_gain']:.2f}%")
    logger.info(f"  - Waste reduction: {summary['improvement']['waste_reduction']} beds")
    
    return summary


if __name__ == "__main__":
    main()