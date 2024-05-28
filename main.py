from optimizer import WardOptimizer
from tracker import EfficiencyTracker

if __name__ == "__main__":
    # data_path = 'data/CleanOptSheet.csv' # old data path
    data_path = 'data/final_census_data.csv'
    results_csv_path = 'output/ward_optimization_results.csv'
    plot_path = 'output/ward_optimization_chart.png'
    report_path = 'output/ward_optimization_report.txt'
    log_path = 'output/solver_log.txt'

    # Optimize ward space
    optimizer = WardOptimizer(data_path)
    (double_rooms, single_rooms, total_wasted_beds, total_free_beds, 
     solver_status, objective_value) = optimizer.optimize_space(log_path)
    efficiency = optimizer.calculate_efficiency(total_free_beds)
    
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
    optimizer.generate_report(report_path, double_rooms, single_rooms, total_wasted_beds, 
                              total_free_beds, efficiency, solver_status, objective_value)
    print(f"Report generated: {report_path}")
    print(f"Solver log generated: {log_path}")

    # Track efficiency of different room combinations
    print("Running Efficiency Tracker...")
    tracker = EfficiencyTracker(data_path)
    tracker.evaluate_combinations(results_csv_path, plot_path)
