import os
import pandas as pd
from model_optimizer import OptimizedModelEvaluator
from model_current import CurrentModelEvaluator
from visualizer import Visualizer

def main():
    data_path = 'data/final_census_data.csv'
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the current model evaluation
    current_evaluator = CurrentModelEvaluator(data_path)
    current_df = current_evaluator.calculate_wasted_beds()
    current_output_path = os.path.join(output_dir, 'current_model_data.csv')
    current_df.to_csv(current_output_path, index=False)
    
    # Run the optimized model evaluation
    optimized_evaluator = OptimizedModelEvaluator(data_path)
    optimized_df = optimized_evaluator.calculate_wasted_beds()
    optimized_output_path = os.path.join(output_dir, 'optimized_model_data.csv')
    optimized_df.to_csv(optimized_output_path, index=False)
    
    # Visualize the results
    current_df = pd.read_csv('output/current_model_data.csv')
    optimized_df = pd.read_csv('output/optimized_model_data.csv')
    visualizer = Visualizer(current_df, optimized_df)
    
    visualizer.plot_wasted_beds_comparison(os.path.join(output_dir, 'wasted_beds_comparison.png'))
    visualizer.plot_daily_efficiency_comparison(os.path.join(output_dir, 'daily_efficiency_comparison.png'))
    visualizer.plot_cumulative_efficiency_comparison(os.path.join(output_dir, 'cumulative_efficiency_comparison.png'))
    
    print("All operations completed successfully. Check the 'output' directory for results.")

if __name__ == "__main__":
    main()
