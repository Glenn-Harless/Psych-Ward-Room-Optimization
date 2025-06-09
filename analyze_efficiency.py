#!/usr/bin/env python3
"""Analyze efficiency calculations to understand discrepancy."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from src.visualization.optimization_charts import OptimizationCharts
from src.core.optimizer import WardOptimizer
from src.utils.constants import TOTAL_BEDS, MAX_DOUBLE_ROOMS

def main():
    # Load data
    data_path = 'data/processed/training/final_census_data.csv'
    data = pd.read_csv(data_path)
    
    print("Analyzing Efficiency Calculations")
    print("=" * 60)
    
    # 1. Run the optimizer to get its result
    print("\n1. Optimizer Result:")
    optimizer = WardOptimizer(data_path)
    opt_results = optimizer.optimize_space()
    print(f"   Configuration: {opt_results[1]}S/{opt_results[0]}D")
    print(f"   Total Waste: {opt_results[2] + opt_results[3]}")
    print(f"   Wasted Beds: {opt_results[2]}")
    print(f"   Wasted Potential: {opt_results[3]}")
    print(f"   Efficiency (from optimizer): {opt_results[5]:.2f}%")
    
    # 2. Calculate optimization landscape
    print("\n2. Optimization Landscape Analysis:")
    charts = OptimizationCharts(data)
    landscape = charts.calculate_optimization_landscape()
    
    # Find valid configurations
    configs = []
    for s in landscape['single_rooms']:
        d = (TOTAL_BEDS - s) / 2
        if 0 <= d <= MAX_DOUBLE_ROOMS and d.is_integer():
            d = int(d)
            s_idx = list(landscape['single_rooms']).index(s)
            d_idx = list(landscape['double_rooms']).index(d)
            
            efficiency = landscape['efficiency'][s_idx, d_idx]
            waste = landscape['objective_values'][s_idx, d_idx]
            
            if not pd.isna(efficiency):
                configs.append({
                    'config': f'{s}S/{d}D',
                    'single': s,
                    'double': d,
                    'efficiency': efficiency,
                    'total_waste': waste,
                    'singles_in_double': landscape['singles_in_double'][s_idx, d_idx],
                    'doubles_in_single': landscape['doubles_in_single'][s_idx, d_idx]
                })
    
    # Sort by efficiency
    configs.sort(key=lambda x: x['efficiency'], reverse=True)
    
    # Show top configurations
    print("\n   Top Configurations by Efficiency:")
    for i, config in enumerate(configs[:5]):
        print(f"   {i+1}. {config['config']}: Efficiency={config['efficiency']:.2f}%, Total Waste={config['total_waste']:.0f}")
        print(f"      Singles in Doubles: {config['singles_in_double']:.0f}, Doubles in Singles: {config['doubles_in_single']:.0f}")
    
    # Sort by total waste
    configs.sort(key=lambda x: x['total_waste'])
    
    print("\n   Top Configurations by Minimum Total Waste:")
    for i, config in enumerate(configs[:5]):
        print(f"   {i+1}. {config['config']}: Total Waste={config['total_waste']:.0f}, Efficiency={config['efficiency']:.2f}%")
        print(f"      Singles in Doubles: {config['singles_in_double']:.0f}, Doubles in Singles: {config['doubles_in_single']:.0f}")
    
    # 3. Compare efficiency calculations
    print("\n3. Efficiency Calculation Comparison:")
    
    # Check 10S/8D configuration
    s_idx = list(landscape['single_rooms']).index(10)
    d_idx = list(landscape['double_rooms']).index(8)
    
    print(f"\n   For 10S/8D configuration:")
    print(f"   - Total Waste: {landscape['objective_values'][s_idx, d_idx]:.0f}")
    print(f"   - Efficiency (visualization): {landscape['efficiency'][s_idx, d_idx]:.2f}%")
    print(f"   - Efficiency (optimizer): {opt_results[5]:.2f}%")
    
    # Calculate total available beds across all days
    total_available = 0
    total_days = len(data)
    for _, row in data.iterrows():
        closed_rooms = row.get('Closed Rooms', 0)
        available = TOTAL_BEDS - closed_rooms
        total_available += available
    
    print(f"\n   Total available bed-days: {total_available}")
    print(f"   Average available beds per day: {total_available / total_days:.1f}")
    
    # Explain the efficiency formula
    print("\n4. Efficiency Formula Explanation:")
    print("   Visualization uses: (total_available - total_waste) / total_available * 100")
    print("   This represents the percentage of available bed capacity that is properly utilized")
    print("\n   Optimizer uses a different formula that doesn't account for actual usage patterns")
    print("   This is why the optimizer's efficiency calculation shows negative values")

if __name__ == "__main__":
    main()