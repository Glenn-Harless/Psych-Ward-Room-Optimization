from optimizer import WardOptimizer
from tracker import EfficiencyTracker

if __name__ == "__main__":
    data_path = 'data/CleanOptSheet.csv'
    results_csv_path = 'output/ward_optimization_results.csv'
    plot_path = 'output/ward_optimization_chart.png'

    # Optimize ward space
    optimizer = WardOptimizer(data_path)
    double_rooms, single_rooms = optimizer.optimize_space()
    print(f"Optimal number of double rooms: {double_rooms}")
    print(f"Optimal number of single rooms: {single_rooms}")

    # Track efficiency of different room combinations
    tracker = EfficiencyTracker(data_path)
    tracker.evaluate_combinations(results_csv_path, plot_path)
