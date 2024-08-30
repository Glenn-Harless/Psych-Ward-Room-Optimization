import pandas as pd

class OptimizedModelEvaluator:
    def __init__(self, data_path, single_rooms=6, double_rooms=10):
        self.data = pd.read_csv(data_path)
        self.single_rooms = single_rooms
        self.double_rooms = double_rooms

    def calculate_wasted_beds(self):
        records = []

        # Consider only the most recent year(s) of data (2023 and 2024)
        self.data["Date"] = pd.to_datetime(self.data["Date"])
        self.data.dropna(subset=['Single Room E'], inplace=True)
        recent_year_data = self.data[self.data['Date'].dt.year.isin([2023, 2024])]

        running_sum_available_beds = 0
        running_sum_wasted_beds = 0

        for _, row in recent_year_data.iterrows():
            date = pd.to_datetime(row['Date'])

            available_beds = 26 - row['Closed Rooms']
            single_room_patients = row['Total Single Room Patients']

            # Calculate wasted beds
            if single_room_patients > self.single_rooms:
                wasted_single_in_double = single_room_patients - self.single_rooms
            else:
                wasted_single_in_double = 0

            wasted_beds = wasted_single_in_double
            running_sum_available_beds += available_beds
            running_sum_wasted_beds += wasted_beds

            daily_efficiency = (available_beds - wasted_beds) / available_beds if available_beds > 0 else 0
            cumulative_efficiency = (running_sum_available_beds - running_sum_wasted_beds) / running_sum_available_beds if running_sum_available_beds > 0 else 0

            records.append({
                "Date": date.date(),
                "Available Beds": available_beds,
                "Wasted Beds": wasted_beds,
                "Daily Efficiency": daily_efficiency,
                "Cumulative Available Beds": running_sum_available_beds,
                "Cumulative Wasted Beds": running_sum_wasted_beds,
                "Cumulative Efficiency": cumulative_efficiency
            })

        return pd.DataFrame(records)

# Usage
if __name__ == "__main__":
    data_path = 'data/final_census_data.csv'
    evaluator = OptimizedModelEvaluator(data_path)
    df = evaluator.calculate_wasted_beds()
    df.to_csv('output/optimized_model_data.csv', index=False)

    print(df)
