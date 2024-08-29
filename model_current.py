import pandas as pd

class CurrentModelEvaluator:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)

    def calculate_wasted_beds(self):
        records = []

        # Consider only the most recent year(s) of data (2023 and 2024)
        recent_year_data = self.data[self.data['Month'].apply(lambda x: x.split('-')[-1]).isin(['2023', '2024'])]

        running_sum_available_beds = 0
        running_sum_wasted_beds = 0

        for i, row in recent_year_data.iterrows():
            date_str = f"{row['Month'][:3]}-01-{row['Month'][-4:]}"  # Assumes format like "Jan-2022"
            date = pd.to_datetime(date_str) + pd.to_timedelta(i, unit='D')

            available_beds = 26 - row['Closed Rooms']
            wasted_beds = row['Total Single Room Patients'] + row['Closed Rooms']

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
    evaluator = CurrentModelEvaluator(data_path)
    df = evaluator.calculate_wasted_beds()
    df.to_csv('output/current_model_data.csv', index=False)

    print(df)
