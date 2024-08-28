import pandas as pd
import matplotlib.pyplot as plt
import os

# TODO this is just a brute force method that shows given historical data 26 single rooms is best use of beds
class EfficiencyTracker:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)

    def calculate_wasted_beds(self, D, S):
        wasted_beds = 0
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            closed_rooms = row['Closed Rooms']

            # Calculate wasted beds for single room patients occupying double rooms
            single_in_double = max(0, single_rooms_needed - S)

            # Each single patient in a double room wastes one bed
            wasted_single_in_double = single_in_double

            # Calculate wasted double rooms
            used_double_beds = min(D * 2, double_rooms_needed * 2 + single_in_double)
            wasted_double_beds = D * 2 - used_double_beds

            # Calculate total wasted beds including closed rooms
            wasted_beds_day = wasted_single_in_double + wasted_double_beds + closed_rooms
            wasted_beds += wasted_beds_day

        return wasted_beds

    def evaluate_combinations(self, results_csv_path, plot_path):
        results = []
        for D in range(0, 14):  # From 0 to 13 double rooms (26 beds in total, 13 rooms)
            S = 26 - 2 * D  # Remaining beds are for single rooms
            wasted_beds = self.calculate_wasted_beds(D, S)
            results.append((D, S, wasted_beds))

        # Convert results to DataFrame for better visualization
        results_df = pd.DataFrame(results, columns=['Double Rooms', 'Single Rooms', 'Wasted Beds'])

        # Save results to CSV
        os.makedirs(os.path.dirname(results_csv_path), exist_ok=True)
        results_df.to_csv(results_csv_path, index=False)

        # Find the most efficient setup
        most_efficient = results_df.loc[results_df['Wasted Beds'].idxmin()]

        print(results_df)
        print(f"\nMost efficient setup:\n{most_efficient}")

        # Plot the efficiency of different combinations and save the plot
        plt.figure(figsize=(10, 6))
        plt.plot(results_df['Double Rooms'], results_df['Wasted Beds'], marker='o')
        plt.xlabel('Number of Double Rooms')
        plt.ylabel('Total Wasted Beds')
        plt.title('Efficiency of Different Room Combinations')
        plt.grid(True)
        os.makedirs(os.path.dirname(plot_path), exist_ok=True)
        plt.savefig(plot_path)
        plt.show()

if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    results_csv_path = 'output/ward_optimization_results.csv'
    plot_path = 'output/ward_optimization_chart.png'

    tracker = EfficiencyTracker(data_path)
    tracker.evaluate_combinations(results_csv_path, plot_path)
