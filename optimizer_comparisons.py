import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
    
    def calculate_wasted_beds(self, D, S):
        wasted_beds = 0
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            closed_rooms = row['Closed Rooms']

            single_in_double = max(0, single_rooms_needed - S)
            wasted_single_in_double = single_in_double
            used_double_beds = min(D * 2, double_rooms_needed * 2 + single_in_double)
            wasted_double_beds = D * 2 - used_double_beds
            wasted_beds_day = wasted_single_in_double + wasted_double_beds + closed_rooms
            wasted_beds += wasted_beds_day

        return wasted_beds

    def plot_combined_results(self, optimization_result, plot_path):
        double_rooms = np.arange(0, 14)
        wasted_beds = []

        for D in double_rooms:
            S = 26 - 2 * D
            if S >= 0:
                wasted_beds.append(self.calculate_wasted_beds(D, S))
            else:
                wasted_beds.append(np.nan)

        plt.figure(figsize=(10, 6))
        plt.plot(double_rooms, wasted_beds, marker='o', linestyle='-', label='Exhaustive Combination')
        
        # Highlight the optimal solution found by the optimization
        opt_D, opt_S, opt_wasted_beds = optimization_result
        plt.scatter([opt_D], [opt_wasted_beds], color='red', zorder=5, label='Optimal Solution')

        plt.xlabel('Number of Double Rooms')
        plt.ylabel('Total Wasted Beds')
        plt.title('Wasted Beds: Exhaustive Combination vs Optimal Solution')
        plt.legend()
        plt.grid(True)
        plt.savefig(plot_path)
        plt.show()

# Usage
if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    plot_path = 'output/combined_results_visualization.png'

    visualizer = Visualizer(data_path)
    
    # Assume the optimization result is (10, 6, 40) for (double_rooms, single_rooms, wasted_beds)
    optimization_result = (10, 6, 40)
    
    visualizer.plot_combined_results(optimization_result, plot_path)
