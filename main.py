import os
from optimizer import WardOptimizer
from tracker import EfficiencyTracker
from visualizer import Visualizer
import matplotlib.pyplot as plt

def generate_report(report_path, optimizer, double_rooms, single_rooms, total_wasted_beds, total_free_beds, efficiency, solver_status, objective_value, data_path):
    # Create a new figure for the report
    fig, axs = plt.subplots(2, 1, figsize=(12, 16))

    # Visualize combined constraints
    visualizer = Visualizer(data_path)
    visualizer.plot_combined_with_constraints((double_rooms, single_rooms, total_wasted_beds), ax=axs[0])

    # Plot wasted beds vs double rooms
    visualizer.plot_wasted_beds_vs_double_rooms('output/wasted_beds_vs_double_rooms.png', ax=axs[1])

    # Save the figure
    plt.tight_layout()
    fig.savefig('output/ward_optimization_report.png')

    # Write the report
    with open(report_path, 'w') as file:
        file.write("Ward Optimization Report\n")
        file.write("========================\n\n")
        file.write(f"Optimal number of double rooms: {double_rooms}\n")
        file.write(f"Optimal number of single rooms: {single_rooms}\n")
        file.write(f"Total wasted beds: {total_wasted_beds}\n")
        file.write(f"Total free beds: {total_free_beds}\n")
        file.write(f"Efficiency: {efficiency:.2f}\n")
        file.write(f"Solver status: {solver_status}\n")
        file.write(f"Objective function value: {objective_value}\n\n")

        # Check the objective value for (0, 26)
        D, S = 0, 26
        wasted_beds_0_26 = visualizer.calculate_wasted_beds(D, S)
        file.write(f"Objective value for (D=0, S=26): {wasted_beds_0_26} wasted beds\n")

        # Check the objective value for the optimal solution from the LP model
        wasted_beds_opt = visualizer.calculate_wasted_beds(double_rooms, single_rooms)
        file.write(f"Objective value for optimal solution (D={double_rooms}, S={single_rooms}): {wasted_beds_opt} wasted beds\n")

        file.write("\n\nGenerated Visualizations:\n")
        file.write("1. Combined Constraints with Optimal Solution and Feasible Region\n")
        file.write("2. Wasted Beds vs Double Rooms\n")

    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    results_csv_path = 'output/ward_optimization_results.csv'
    plot_path = 'output/ward_optimization_chart.png'
    report_path = 'output/ward_optimization_report.txt'
    log_path = 'output/solver_log.txt'
    line_plot_path = 'output/wasted_beds_vs_double_rooms.png'

    # Optimize ward space
    optimizer = WardOptimizer(data_path)
    double_rooms, single_rooms, total_wasted_beds, total_free_beds, efficiency, solver_status, objective_value = optimizer.optimize_space(log_path)

    print("Running Ward Optimization...")
    print("====================================")
    print(f"Optimal number of double rooms: {double_rooms}")
    print(f"Optimal number of single rooms: {single_rooms}")
    print(f"Total wasted beds: {total_wasted_beds}")
    print(f"Total free beds: {total_free_beds}")
    print(f"Efficiency: {efficiency:.2f}")
    print(f"Solver Status: {solver_status}")
    print(f"Objective Function Value: {objective_value}")
    print("====================================")

    # Generate report
    generate_report(report_path, optimizer, double_rooms, single_rooms, total_wasted_beds, total_free_beds, efficiency, solver_status, objective_value, data_path)
    print(f"Report generated: {report_path}")
    print(f"Solver log generated: {log_path}")

    # Track efficiency of different room combinations
    print("Running Efficiency Tracker...")
    tracker = EfficiencyTracker(data_path)
    tracker.evaluate_combinations(results_csv_path, plot_path)
    print(f"Results saved to: {results_csv_path}")
    print(f"Chart saved to: {plot_path}")

    # Visualize the results
    visualizer = Visualizer(data_path)
    visualizer.plot_combined_with_constraints((double_rooms, single_rooms, total_wasted_beds))
    visualizer.plot_wasted_beds_vs_double_rooms(line_plot_path)
    print(f"Visualizations saved to: {line_plot_path}")
