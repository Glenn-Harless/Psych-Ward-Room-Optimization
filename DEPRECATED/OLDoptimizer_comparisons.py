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

    def create_visualization(self, plot_path):
        double_rooms = np.arange(0, 14)
        single_rooms = np.arange(0, 27)
        D, S = np.meshgrid(double_rooms, single_rooms)
        wasted_beds = np.zeros_like(D, dtype=float)

        for i in range(D.shape[0]):
            for j in range(D.shape[1]):
                if 2 * D[i, j] + S[i, j] <= 26:
                    wasted_beds[i, j] = self.calculate_wasted_beds(D[i, j], S[i, j])
                else:
                    wasted_beds[i, j] = np.nan

        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(D, S, wasted_beds, cmap='viridis')

        ax.set_xlabel('Number of Double Rooms')
        ax.set_ylabel('Number of Single Rooms')
        ax.set_zlabel('Total Wasted Beds')
        ax.set_title('Wasted Beds as a Function of Double and Single Rooms')
        
        plt.savefig(plot_path)
        plt.show()

    def plot_wasted_beds_vs_double_rooms(self, plot_path):
        double_rooms = np.arange(0, 14)
        wasted_beds = []

        for D in double_rooms:
            S = 26 - 2 * D
            if S >= 0:
                wasted_beds.append(self.calculate_wasted_beds(D, S))
            else:
                wasted_beds.append(np.nan)

        plt.figure(figsize=(10, 6))
        plt.plot(double_rooms, wasted_beds, marker='o', linestyle='-')
        plt.xlabel('Number of Double Rooms')
        plt.ylabel('Total Wasted Beds')
        plt.title('Wasted Beds as a Function of Double Rooms')
        plt.grid(True)
        plt.savefig(plot_path)
        plt.show()

# Usage
if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    surface_plot_path = 'output/wasted_beds_visualization.png'
    line_plot_path = 'output/wasted_beds_vs_double_rooms.png'

    visualizer = Visualizer(data_path)
    visualizer.create_visualization(surface_plot_path)
    visualizer.plot_wasted_beds_vs_double_rooms(line_plot_path)
