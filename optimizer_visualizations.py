import pandas as pd
import numpy as np

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

# Initialize a matrix to store the objective function values
objective_values = np.full((len(single_rooms), len(double_rooms)), np.nan)


# Iterate through each configuration and calculate the objective function
for i, S in enumerate(single_rooms):
    for j, D in enumerate(double_rooms):
        if 2 * D + S == 26:  # Feasibility condition
            total_wasted_beds = 0

            for _, row in recent_year_data.iterrows():
                single_room_patients = row['Total Single Room Patients']
                double_room_patients = row['Double Room Patients']

                # Calculate number of patients that can be accommodated
                accommodated_single = min(single_room_patients, S)
                accommodated_double = min(double_room_patients, 2 * D)

                # Wasted beds in double rooms by single patients
                wasted_single_in_double = max(0, single_room_patients - S)

                # Wasted potential double room space when double patients are too many
                wasted_double_in_single = max(0, double_room_patients - 2 * D)

                total_wasted_beds += wasted_single_in_double + wasted_double_in_single

            # Objective function is total wasted beds
            objective_values[i, j] = total_wasted_beds

import seaborn as sns
import matplotlib.pyplot as plt

# Create the heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(objective_values, annot=True, fmt=".0f", cmap="YlGnBu", xticklabels=double_rooms, yticklabels=single_rooms)

# Add labels and title
plt.title("Objective Function Heatmap\n(Total Wasted Beds and Potential)")
plt.xlabel("Number of Double Rooms (D)")
plt.ylabel("Number of Single Rooms (S)")

# Save and show the plot
plt.savefig('output/optimizer_heatmap.png')
# plt.show()


# Extract the relevant data from the heatmap
configurations = [(S, D) for S in single_rooms for D in double_rooms if 2 * D + S == 26]
wasted_beds = [objective_values[i, j] for i, S in enumerate(single_rooms) for j, D in enumerate(double_rooms) if 2 * D + S == 26]

# Create a bar chart
plt.figure(figsize=(12, 6))
plt.bar([f"S: {S}, D: {D}" for S, D in configurations], wasted_beds, color='skyblue')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Room Configurations (Single Rooms, Double Rooms)")
plt.ylabel("Total Wasted Beds")
plt.title("Wasted Beds vs. Room Configurations")
# plt.show()
plt.savefig('output/optimizer_bar_chart.png')


# Calculate efficiency for each configuration
efficiency = [(26 - wb) / 26 for wb in wasted_beds]

# Create a line plot
plt.figure(figsize=(12, 6))
plt.plot([f"S: {S}, D: {D}" for S, D in configurations], efficiency, marker='o', color='orange')
plt.xticks(rotation=45, ha='right')
plt.xlabel("Room Configurations (Single Rooms, Double Rooms)")
plt.ylabel("Efficiency")
plt.title("Efficiency vs. Room Configurations")
# plt.show()
plt.savefig('output/optimizer_efficiency_plot.png')


