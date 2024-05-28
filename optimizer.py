import pandas as pd
import pulp
import math

class WardOptimizer:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        
    def optimize_space(self):
        # Define the problem
        problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)

        # Define decision variables
        D = pulp.LpVariable('D', lowBound=0, upBound=13, cat='Integer')  # number of double rooms
        S = pulp.LpVariable('S', lowBound=0, upBound=26, cat='Integer')  # number of single rooms

        # Constraint: Total number of beds (2D + S) must equal 26
        problem += 2 * D + S == 26, "TotalBeds"

        # Objective function to minimize wasted beds
        total_wasted_beds = 0
        
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            
            # Variables to calculate room allocation
            single_in_double = pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer')

            # Constraint: Ensure there are enough single rooms or double rooms accommodating single room patients
            problem += S + single_in_double >= single_rooms_needed, f"SingleInDouble_{i}"

            # Calculate wasted beds:
            # Wasted single_in_double: Number of single room patients placed in double rooms (wasting one bed each)
            # Unused double beds: Number of double room beds not occupied by any patients
            wasted_single_in_double = single_in_double
            unused_double_beds = 2 * D - (double_rooms_needed + single_in_double)
            wasted_beds_day = wasted_single_in_double + unused_double_beds
            total_wasted_beds += wasted_beds_day

        # Add the objective function to the problem
        problem += total_wasted_beds, "MinimizeWastedBeds"

        # Solve the problem
        problem.solve()

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)

        # Adjust results if necessary (rounding issues)
        if double_rooms % 1 == 0.5:
            double_rooms = math.floor(double_rooms)
            single_rooms += 1

        # Calculate the final total free beds and total wasted beds based on the results
        total_wasted_beds_value = 0
        total_free_beds_value = 0
        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']
            
            # Calculate single_in_double and wasted_single_in_double
            single_in_double_value = max(0, single_rooms_needed - single_rooms)
            wasted_single_in_double_value = single_in_double_value
            unused_double_beds_value = max(0, 2 * double_rooms - (double_rooms_needed + single_in_double_value))
            wasted_beds_day_value = wasted_single_in_double_value + unused_double_beds_value
            total_wasted_beds_value += wasted_beds_day_value

            # Calculate remaining free beds
            free_beds_day_value = max(0, 2 * double_rooms + single_rooms - (single_rooms_needed + double_rooms_needed))
            total_free_beds_value += free_beds_day_value

        return double_rooms, single_rooms, total_wasted_beds_value, total_free_beds_value

    def calculate_efficiency(self, total_free_beds):
        # Calculate census: Number of beds occupied by patients
        census = 26 - total_free_beds

        # Calculate efficiency: Ratio of occupied beds to total beds (26)
        efficiency = census / 26 if census != 0 else 0
        return efficiency

if __name__ == "__main__":
    data_path = 'data/CleanOptSheet.csv'
    optimizer = WardOptimizer(data_path)
    double_rooms, single_rooms, total_wasted_beds, total_free_beds = optimizer.optimize_space()
    efficiency = optimizer.calculate_efficiency(total_free_beds)
    
    print("Running Ward Optimization...")
    print("====================================")
    print(f"Optimal number of double rooms: {double_rooms}")
    print(f"Optimal number of single rooms: {single_rooms}")
    print(f"Total wasted beds: {total_wasted_beds}")
    print(f"Total free beds: {total_free_beds}")
    print(f"Efficiency: {efficiency:.2f}")
