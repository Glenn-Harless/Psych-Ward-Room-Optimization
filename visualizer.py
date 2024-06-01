import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class Visualizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)

    def plot_combined_with_constraints(self, optimization_result, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))

        # Define the feasible region
        x = np.linspace(0, 13, 400)
        y1 = 26 - 2 * x  # Constraint 1: 2D + S = 26

        # Plot the main constraint
        ax.plot(x, y1, label='2D + S = 26', color='blue')

        # Highlight the optimal solution
        opt_D, opt_S, opt_wasted_beds = optimization_result
        ax.scatter([opt_D], [opt_S], color='green', zorder=5, label=f'Optimal Solution\nDouble Rooms: {opt_D}, Single Rooms: {opt_S}')
        ax.text(opt_D, opt_S - 1, f'({opt_D}, {opt_S})\nObjective: {opt_wasted_beds}', fontsize=9, horizontalalignment='left')

        # Add a red point for (D=0, S=26)
        D0, S26 = 0, 26
        ax.scatter([D0], [S26], color='red', zorder=5, label='D=0, S=26')
        objective_value_D0_S26 = self.calculate_wasted_beds(D0, S26)
        ax.text(D0, S26 - 1, f'({D0}, {S26})\nObjective Value: {objective_value_D0_S26}', fontsize=9, horizontalalignment='left')

        # Calculate the maximum constraints
        max_single_rooms_needed = self.data['Total Single Room Patients'].max()
        max_double_rooms_needed = self.data['Double Room Patients'].max() / 2

        # Shade the infeasible regions based on the maximum constraints
        ax.fill_betweenx(np.linspace(0, 26, 400), max_double_rooms_needed, x, where=(x <= max_double_rooms_needed), color='red', alpha=0.3, label='Infeasible: Double Rooms Constraint')
        ax.fill_between(x, max_single_rooms_needed, y1, where=(y1 <= max_single_rooms_needed), color='purple', alpha=0.3, label='Infeasible: Single Rooms Constraint')

        # Ensure all labels are correctly plotted and not overlapping
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), loc='upper right', bbox_to_anchor=(1.15, 1))

        # Set plot limits and labels
        ax.set_xlim(0, 13)
        ax.set_ylim(0, 26)
        ax.set_xlabel('Number of Double Rooms (D)')
        ax.set_ylabel('Number of Single Rooms (S)')
        ax.set_title('Feasible Region, Objective Function Lines, and Optimal Solution with Additional Constraints')
        ax.grid(True)

    def create_visualization(self, plot_path, ax=None):
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

        if ax is None:
            fig, ax = plt.subplots(figsize=(12, 8))

        c = ax.pcolormesh(D, S, wasted_beds, cmap='viridis', shading='auto')
        fig.colorbar(c, ax=ax)

        ax.set_xlabel('Number of Double Rooms')
        ax.set_ylabel('Number of Single Rooms')
        ax.set_title('Wasted Beds as a Function of Double and Single Rooms')

        plt.savefig(plot_path)
        plt.show()

    def plot_wasted_beds_vs_double_rooms(self, plot_path, ax=None):
        double_rooms = np.arange(0, 14)
        wasted_beds = []

        for D in double_rooms:
            S = 26 - 2 * D
            if S >= 0:
                wasted_beds.append(self.calculate_wasted_beds(D, S))
            else:
                wasted_beds.append(np.nan)

        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(double_rooms, wasted_beds, marker='o', linestyle='-')
        ax.set_xlabel('Number of Double Rooms')
        ax.set_ylabel('Total Wasted Beds')
        ax.set_title('Wasted Beds as a Function of Double Rooms')
        ax.grid(True)

        plt.savefig(plot_path)
        plt.show()

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
