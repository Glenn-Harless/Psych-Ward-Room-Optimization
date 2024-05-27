import pandas as pd
import pulp

class WardOptimizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        
    def optimize_space(self):
        # Define the problem
        problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)

        # Define decision variables
        D = pulp.LpVariable('D', lowBound=0, upBound=13, cat='Integer')  # number of double rooms
        S = pulp.LpVariable('S', lowBound=0, upBound=26, cat='Integer')  # number of single rooms

        # Add constraints
        problem += 2 * D + S == 26, "TotalCapacity"  # Ensure exactly 26 beds are used

        # Objective function to minimize wasted beds
        total_wasted_beds = 0
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            
            # Variables to calculate room allocation
            single_in_double = pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer')

            # Constraints to ensure enough rooms
            problem += S + single_in_double >= single_rooms_needed, f"SingleRoomNeed_{i}"
            problem += 2 * D >= double_rooms_needed, f"DoubleRoomNeed_{i}"

            # Calculate wasted beds
            unused_double_beds = 2 * D - (double_rooms_needed + single_in_double)
            total_wasted_beds += single_in_double + unused_double_beds  # Only count single in double as wasted if exceeds single rooms needed

        problem += total_wasted_beds, "MinimizeWastedBeds"

        # Solve the problem
        problem.solve()

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)

        return double_rooms, single_rooms

if __name__ == "__main__":
    data_path = 'data/CleanOptSheet.csv'
    optimizer = WardOptimizer(data_path)
    double_rooms, single_rooms = optimizer.optimize_space()
    print(f"Optimal number of double rooms: {double_rooms}")
    print(f"Optimal number of single rooms: {single_rooms}")
