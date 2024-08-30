import pandas as pd

class CurrentModelEvaluator:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)

    def calculate_wasted_beds(self):
        records = []

        # Consider only the most recent year(s) of data (2023 and 2024)
        self.data["Date"] = pd.to_datetime(self.data["Date"])
        self.data.dropna(subset=['Single Room E'], inplace=True)
        recent_year_data = self.data[self.data['Date'].dt.year.isin([2023, 2024])]

        running_sum_available_beds = 0
        running_sum_wasted_beds = 0
        running_sum_wasted_potential = 0

        for _, row in recent_year_data.iterrows():
            date = pd.to_datetime(row['Date'])

            available_beds = 26 - row['Closed Rooms']
            wasted_beds = row['Total Single Room Patients'] + row['Closed Rooms']
            wasted_potential = 0  # No wasted potential in current model as all rooms are double

            running_sum_available_beds += available_beds
            running_sum_wasted_beds += wasted_beds
            running_sum_wasted_potential += wasted_potential

            daily_efficiency = (available_beds - wasted_beds - wasted_potential) / available_beds if available_beds > 0 else 0
            cumulative_efficiency = (running_sum_available_beds - running_sum_wasted_beds - running_sum_wasted_potential) / running_sum_available_beds if running_sum_available_beds > 0 else 0

            records.append({
                "Date": date.date(),
                "Available Beds": available_beds,
                "Wasted Beds": wasted_beds,
                "Wasted Potential": wasted_potential,
                "Daily Efficiency": daily_efficiency,
                "Cumulative Available Beds": running_sum_available_beds,
                "Cumulative Wasted Beds": running_sum_wasted_beds,
                "Cumulative Wasted Potential": running_sum_wasted_potential,
                "Cumulative Efficiency": cumulative_efficiency
            })

        return pd.DataFrame(records)

# Usage
if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    evaluator = CurrentModelEvaluator(data_path)
    df = evaluator.calculate_wasted_beds()
    df.to_csv('output/current_model_data.csv', index=False)

    print(df)
