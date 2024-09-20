import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

# Load the historical data
data_path = 'data/final_census_data.csv'
data = pd.read_csv(data_path)

# Consider only the most recent years (2023 and 2024)
data["Date"] = pd.to_datetime(data["Date"])
data.dropna(subset=['Single Room E'], inplace=True)
recent_year_data = data[data['Date'].dt.year.isin([2023, 2024])]

# Define the range of single and double rooms
single_rooms = np.arange(0, 27)
double_rooms = np.arange(0, 14)

# Initialize matrices to store the objective function values, singles in double, and doubles in single
objective_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
total_singles_in_double_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
total_doubles_in_single_values = np.full((len(single_rooms), len(double_rooms)), np.nan)

# Iterate through each configuration and calculate the objective function and inefficiencies
for i, S in enumerate(single_rooms):
    for j, D in enumerate(double_rooms):
        if 2 * D + S == 26:  # Feasibility condition
            total_waste = 0
            total_singles_in_double = 0
            total_doubles_in_single = 0

            for _, row in recent_year_data.iterrows():
                single_room_patients = row['Total Single Room Patients']
                double_room_patients = row['Double Room Patients']

                # Wasted beds in double rooms by single patients
                wasted_single_in_double = max(0, single_room_patients - S)

                # Wasted potential double room space when double patients are too many
                wasted_double_in_single = max(0, double_room_patients - 2 * D)

                # Total wasted single patients in double rooms
                total_singles_in_double += wasted_single_in_double

                # Total wasted double patients in single rooms
                total_doubles_in_single += wasted_double_in_single

                # Total waste = wasted single in double + wasted double in single
                total_waste += wasted_single_in_double + wasted_double_in_single

            # Store the total wasted beds, singles in double, and doubles in single
            objective_values[i, j] = total_waste
            total_singles_in_double_values[i, j] = total_singles_in_double
            total_doubles_in_single_values[i, j] = total_doubles_in_single

# Create a heatmap for the total wasted beds
plt.figure(figsize=(10, 8))
sns.heatmap(objective_values, annot=True, fmt=".0f", cmap="YlGnBu", xticklabels=double_rooms, yticklabels=single_rooms)
plt.title("Objective Function Heatmap\n(Minimize Total Incorrectly Assigned Patients)")
plt.xlabel("Number of Double Rooms (D)")
plt.ylabel("Number of Single Rooms (S)")
plt.savefig('output/optimizer_heatmap.png')

# Extract configurations for single/double rooms and wasted beds
configurations = [(S, D) for S in single_rooms for D in double_rooms if 2 * D + S == 26]
wasted_beds_space = [objective_values[i, j] for i, S in enumerate(single_rooms) for j, D in enumerate(double_rooms) if 2 * D + S == 26]
total_singles_in_double_space = [total_singles_in_double_values[i, j] for i, S in enumerate(single_rooms) for j, D in enumerate(double_rooms) if 2 * D + S == 26]
total_doubles_in_single_space = [total_doubles_in_single_values[i, j] for i, S in enumerate(single_rooms) for j, D in enumerate(double_rooms) if 2 * D + S == 26]

# Create a bar chart for wasted beds
plt.figure(figsize=(12, 10))
plt.bar([f"S: {S}, D: {D}" for S, D in configurations], wasted_beds_space, color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Room Configurations (Single Rooms, Double Rooms)")
plt.ylabel("Inefficiency (Wasted Beds + Wasted Potential)")
plt.title("Inefficiency vs. Room Configurations")
plt.savefig('output/optimizer_bar_chart.png')

# Calculate efficiency for each configuration
total_available_beds = len(recent_year_data) * 26
efficiency = [(total_available_beds - wb) / total_available_beds for wb in wasted_beds_space]

# Create a line plot for efficiency
plt.figure(figsize=(12, 10))
plt.plot([f"S: {S}, D: {D}" for S, D in configurations], efficiency, marker='o', color='orange')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Room Configurations (Single Rooms, Double Rooms)")
plt.ylabel("Efficiency")
plt.title("Efficiency vs. Room Configurations")
plt.savefig('output/optimizer_efficiency_plot.png')

# Create line plots for total singles in double and total doubles in single as a function of room configurations
plt.figure(figsize=(12, 10))
plt.plot([f"S: {S}, D: {D}" for S, D in configurations], total_singles_in_double_space, marker='o', label='Singles in Double', color='blue')
plt.plot([f"S: {S}, D: {D}" for S, D in configurations], total_doubles_in_single_space, marker='o', label='Doubles in Single', color='red')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Room Configurations (Single Rooms, Double Rooms)")
plt.ylabel("Total Incorrectly Assigned Patients")
plt.title("Wasted Singles in Double Rooms and Doubles in Single Rooms\nvs. Room Configurations")
plt.legend()
plt.savefig('output/wasted_patients_plot.png')

