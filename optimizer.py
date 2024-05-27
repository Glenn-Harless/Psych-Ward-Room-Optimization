import pandas as pd
import pulp

class WardOptimizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
    
    def optimize_space(self):
        # Define the problem
        problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)

        # Define decision variables
        D = pulp.LpVariable('D', lowBound=0, cat='Integer')  # number of double rooms
        S = pulp.LpVariable('S', lowBound=0, cat='Integer')  # number of single rooms

        # Add constraints
        problem += 2 * D + S == 26, "TotalBeds"  # Adjusted to count beds instead of rooms

        # Objective function to minimize wasted beds
        total_wasted_beds = 0
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            closed_rooms = row['Closed Rooms']

            # Variables to calculate room allocation
            single_in_double = pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer')
            unused_double_beds = pulp.LpVariable(f'unused_double_beds_{i}', lowBound=0, cat='Integer')

            # Constraints
            problem += single_in_double >= single_rooms_needed - S, f"SingleInDoubleConstraint_{i}"
            problem += single_in_double <= single_rooms_needed, f"SingleInDoubleUpperBound_{i}"
            problem += unused_double_beds == D * 2 - (double_rooms_needed * 2 + single_in_double), f"UnusedDoubleBeds_{i}"

            # Calculate wasted beds
            wasted_single_in_double = single_in_double
            total_wasted_beds_day = wasted_single_in_double + unused_double_beds + closed_rooms

            total_wasted_beds += total_wasted_beds_day

        problem += total_wasted_beds, "MinimizeWastedBeds"

        # Solve the problem
        problem.solve()

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)

        return double_rooms, single_rooms
