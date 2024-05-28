import pandas as pd
import pulp

class WardOptimizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        
    def optimize_space(self, log_path=None):
        # Define the problem
        problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)

        # Define decision variables
        D = pulp.LpVariable('D', lowBound=0, upBound=13, cat='Integer')  # number of double rooms
        S = pulp.LpVariable('S', lowBound=0, upBound=26, cat='Integer')  # number of single rooms
        total_wasted_beds = pulp.LpVariable('total_wasted_beds', lowBound=0, cat='Integer')
        total_free_beds = pulp.LpVariable('total_free_beds', lowBound=0, cat='Integer')
        
        # Constraint: Total number of beds (2D + S) must equal 26
        problem += 2 * D + S == 26, "TotalBeds"
        
        single_in_double = []
        unused_double_beds = []
        unused_single_beds = []

        # Iterate through each day's data
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            
            # Variables to calculate room allocation
            single_in_double.append(pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer'))
            unused_double_beds.append(pulp.LpVariable(f'unused_double_beds_{i}', lowBound=0, cat='Integer'))
            unused_single_beds.append(pulp.LpVariable(f'unused_single_beds_{i}', lowBound=0, cat='Integer'))

            # Ensure there are enough single rooms or double rooms accommodating single room patients
            problem += S + single_in_double[i] >= single_rooms_needed, f"SingleInDouble_{i}"

            # Ensure there are enough double rooms for double room patients
            problem += double_rooms_needed <= 2 * D, f"DoubleRoomCapacity_{i}"

            # Calculate unused double beds
            problem += unused_double_beds[i] == 2 * D - double_rooms_needed - single_in_double[i], f"UnusedDoubleBeds_{i}"

            # Calculate unused single beds
            problem += unused_single_beds[i] == S - single_rooms_needed, f"UnusedSingleBeds_{i}"

            # Add to total wasted beds and free beds
            problem += total_wasted_beds >= single_in_double[i] + unused_double_beds[i], f"TotalWastedBeds_{i}"
            problem += total_free_beds >= unused_double_beds[i] + unused_single_beds[i], f"TotalFreeBeds_{i}"

        # Objective function to minimize both wasted beds and free beds
        problem += total_wasted_beds + total_free_beds, "MinimizeWastedAndFreeBeds"

        # Debugging: Print problem formulation
        print("Problem formulation:")
        print(problem)

        # Solve the problem with optional logging
        solver = pulp.PULP_CBC_CMD(logPath=log_path)
        problem.solve(solver)

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)
        total_wasted_beds_value = pulp.value(total_wasted_beds)
        total_free_beds_value = pulp.value(total_free_beds)

        # Debugging: Print decision variable values
        print(f"Double Rooms (D): {double_rooms}")
        print(f"Single Rooms (S): {single_rooms}")

        # Additional information
        solver_status = pulp.LpStatus[problem.status]
        objective_value = pulp.value(problem.objective)

        return (double_rooms, single_rooms, total_wasted_beds_value, 
                total_free_beds_value, solver_status, objective_value)

# Usage
optimizer = WardOptimizer('data/final_census_data.csv')
results = optimizer.optimize_space(log_path='output/solver_log.txt')

# Print the results
print(f"Optimal number of double rooms: {results[0]}")
print(f"Optimal number of single rooms: {results[1]}")
print(f"Total wasted beds: {results[2]}")
print(f"Total free beds: {results[3]}")
print(f"Solver status: {results[4]}")
print(f"Objective function value: {results[5]}")
