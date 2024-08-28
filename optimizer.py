import pulp
import pandas as pd

# TODO: double room patients CAN be in single rooms
# TODO: Single room patients CAN be in double rooms
    # Maybe expand this in the future
# TODO: Only look at most recent year of data
# TODO: 
"""
Held beds are isolated single rooms


As it is right now, if a patient (under this new model) would be placed in a single room

How it works right now:
- all rooms are double rooms (2 beds)
- since they need their own room, that extra bed is wasted
- that extra bed = held beds

Output goal we are looking for:
- available beds for the last year

Under new system:
- its possible we wouldnt be accept all patients

Available beds under old set up compared to available beds on new set up

- goal is to maximize occupancy
- minimize wasted beds


Old metric (all double rooms):
    - wasted beds = total held beds

How does a room become wasted under new model (combination of single rooms + double rooms)
- if single rooms fill up, can they go into open double rooms?
    - that would be a wasted bed
- Sent away patients?


I think the goal is to minimize wasted beds, so single room patients CAN go into double rooms


Old Model:
- Wasted Beds = "Held Beds":
    Held bed is when a psychotic patient has to be in a single room, old model has all double rooms so second bed is wasted

New Models:
- Wasted Beds:
    - Will only be wasted once all single rooms are filled up
    - any new psychotic patients will have to go in a double room
    - if a double room is filled up with a psychotic patient , then the second bed is wasted


# TODO: Train on a year of data
- if "double room patients" is "-" then it is 0
but the total availale beds becomes 26 - (that difference)
 - omit it for now for simplicity then we can come revisit

 - If census is 12, held beds is 14 then single room patients = 12, double room patients = 0

"""

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

        # Constraint: Total number of beds (2D + S) must equal 26
        problem += 2 * D + S == 26, "TotalBeds"

        single_in_double = []
        unused_double_beds = []

        for i, row in self.data.iterrows():
            single_rooms_needed = row['Total Single Room Patients']
            double_rooms_needed = row['Double Room Patients']

            # Variables to calculate room allocation
            single_in_double_var = pulp.LpVariable(f'single_in_double_{i}', lowBound=0, cat='Integer')
            unused_double_beds_var = pulp.LpVariable(f'unused_double_beds_{i}', lowBound=0, cat='Integer')

            single_in_double.append(single_in_double_var)
            unused_double_beds.append(unused_double_beds_var)

            # Ensure there are enough single rooms or double rooms accommodating single room patients
            problem += S + single_in_double_var >= single_rooms_needed, f"SingleInDouble_{i}"

            # Ensure there are enough double rooms for double room patients
            problem += double_rooms_needed <= 2 * D, f"DoubleRoomCapacity_{i}"

            # Calculate unused double beds
            problem += unused_double_beds_var == 2 * D - double_rooms_needed - single_in_double_var, f"UnusedDoubleBeds_{i}"

            # Add to total wasted beds
            problem += total_wasted_beds >= single_in_double_var + unused_double_beds_var, f"TotalWastedBeds_{i}"

        # Objective function to minimize total wasted beds
        problem += total_wasted_beds, "MinimizeWastedBeds"

        # Solve the problem with optional logging
        solver = pulp.PULP_CBC_CMD(logPath=log_path)
        problem.solve(solver)

        # Get the results
        double_rooms = pulp.value(D)
        single_rooms = pulp.value(S)
        total_wasted_beds_value = pulp.value(total_wasted_beds)

        # Additional information
        solver_status = pulp.LpStatus[problem.status]
        objective_value = pulp.value(problem.objective)

        # Calculate total free beds (26 beds total minus used beds)
        total_free_beds_value = 26 - (2 * double_rooms + single_rooms)

        # Calculate efficiency
        efficiency = (26 - total_free_beds_value) / 26

        return (double_rooms, single_rooms, total_wasted_beds_value, total_free_beds_value, efficiency, solver_status, objective_value)

# Usage
data_path = 'data/final_census_data.csv'
log_path = 'output/solver_log.txt'

optimizer = WardOptimizer(data_path)
(double_rooms, single_rooms, total_wasted_beds, total_free_beds, efficiency, solver_status, objective_value) = optimizer.optimize_space(log_path)

# Print the results
print(f"Optimal number of double rooms: {double_rooms}")
print(f"Optimal number of single rooms: {single_rooms}")
print(f"Total wasted beds: {total_wasted_beds}")
print(f"Total free beds: {total_free_beds}")
print(f"Efficiency: {efficiency:.2f}")
print(f"Solver status: {solver_status}")
print(f"Objective function value: {objective_value}")

# Check the objective value for (0, 26)
D, S = 0, 26
wasted_beds_0_26 = 0
for i, row in optimizer.data.iterrows():
    single_rooms_needed = row['Total Single Room Patients']
    double_rooms_needed = row['Double Room Patients']
    single_in_double = max(0, single_rooms_needed - S)
    wasted_single_in_double = single_in_double
    used_double_beds = min(D * 2, double_rooms_needed * 2 + single_in_double)
    wasted_double_beds = D * 2 - used_double_beds
    closed_rooms = row['Closed Rooms']
    wasted_beds_0_26 += wasted_single_in_double + wasted_double_beds + closed_rooms

print(f"Objective value for (D=0, S=26): {wasted_beds_0_26} wasted beds")

# Check the objective value for the optimal solution from the LP model
wasted_beds_opt = 0
D, S = double_rooms, single_rooms
for i, row in optimizer.data.iterrows():
    single_rooms_needed = row['Total Single Room Patients']
    double_rooms_needed = row['Double Room Patients']
    single_in_double = max(0, single_rooms_needed - S)
    wasted_single_in_double = single_in_double
    used_double_beds = min(D * 2, double_rooms_needed * 2 + single_in_double)
    wasted_double_beds = D * 2 - used_double_beds
    closed_rooms = row['Closed Rooms']
    wasted_beds_opt += wasted_single_in_double + wasted_double_beds + closed_rooms

print(f"Objective value for optimal solution (D={D}, S={S}): {wasted_beds_opt} wasted beds")
