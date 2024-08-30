import pulp
import pandas as pd

class WardOptimizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        
    def optimize_space(self, log_path=None):
        # Define the problem
        problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)

        # Decision Variables
        D = pulp.LpVariable('D', lowBound=0, upBound=13, cat='Integer')  # number of double rooms
        S = pulp.LpVariable('S', lowBound=0, upBound=26, cat='Integer')  # number of single rooms
        total_wasted_beds = pulp.LpVariable('total_wasted_beds', lowBound=0, cat='Integer')
        total_wasted_potential = pulp.LpVariable('total_wasted_potential', lowBound=0, cat='Integer')

        # Constraint: Total number of beds (2D + S) must equal 26
        problem += 2 * D + S == 26, "TotalBeds"

        single_in_double = []
        unused_double_beds = []
        double_in_single = []

        self.data["Date"] = pd.to_datetime(self.data["Date"])
        self.data.dropna(subset=['Single Room E'], inplace=True)
        recent_year_data = self.data[self.data['Date'].dt.year.isin([2023, 2024])]
        
        for i, row in recent_year_data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']

            # Variables to calculate room allocation
            single_in_double_var = pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer')
            unused_double_beds_var = pulp.LpVariable(f'unused_double_beds_{i}', lowBound=0, cat='Integer')
            double_in_single_var = pulp.LpVariable(f'double_in_single_{i}', lowBound=0, cat='Integer')

            single_in_double.append(single_in_double_var)
            unused_double_beds.append(unused_double_beds_var)
            double_in_single.append(double_in_single_var)

            # Ensure there are enough single rooms or double rooms accommodating single room patients
            problem += S + single_in_double_var >= single_rooms_needed, f"SingleInDouble_{i}"

            # Ensure there are enough double rooms for double room patients
            problem += double_rooms_needed <= 2 * D + double_in_single_var, f"DoubleRoomCapacity_{i}"

            # Calculate unused double beds
            problem += unused_double_beds_var == 2 * D - double_rooms_needed - single_in_double_var, f"UnusedDoubleBeds_{i}"

            # Calculate wasted potential (double room patients placed in single rooms)
            problem += double_in_single_var >= double_rooms_needed - 2 * D, f"DoubleInSingle_{i}"

            # Add to total wasted beds and wasted potential
            problem += total_wasted_beds >= single_in_double_var + unused_double_beds_var, f"TotalWastedBeds_{i}"
            problem += total_wasted_potential >= double_in_single_var, f"TotalWastedPotential_{i}"

        # Objective function to minimize total wasted beds and wasted potential
        problem += total_wasted_beds + total_wasted_potential, "MinimizeWastedSpace"

        # Solve the problem with optional logging
        solver = pulp.PULP_CBC_CMD(logPath=log_path)
        problem.solve(solver)

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)
        total_wasted_beds_value = pulp.value(total_wasted_beds)
        total_wasted_potential_value = pulp.value(total_wasted_potential)

        # Additional information
        solver_status = pulp.LpStatus[problem.status]
        objective_value = pulp.value(problem.objective)

        # Calculate total free beds (26 beds total minus used beds)
        total_free_beds_value = 26 - (2 * double_rooms + single_rooms)

        # Calculate efficiency considering both wasted beds and potential
        efficiency = (26 - total_free_beds_value - total_wasted_beds_value - total_wasted_potential_value) / 26

        return (double_rooms, single_rooms, total_wasted_beds_value, total_wasted_potential_value, total_free_beds_value, efficiency, solver_status, objective_value)

# Usage
if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    log_path = 'output/solver_log.txt'

    optimizer = WardOptimizer(data_path)
    (double_rooms, single_rooms, total_wasted_beds, total_wasted_potential, total_free_beds, efficiency, solver_status, objective_value) = optimizer.optimize_space(log_path)

    print(f"Optimal number of double rooms: {double_rooms}")
    print(f"Optimal number of single rooms: {single_rooms}")
    print(f"Total wasted beds: {total_wasted_beds}")
    print(f"Total wasted potential: {total_wasted_potential}")
    print(f"Total free beds: {total_free_beds}")
    print(f"Efficiency: {efficiency:.2f}")
    print(f"Solver status: {solver_status}")
    print(f"Objective function value: {objective_value}")
