import pandas as pd

def process_sheet(df):
    df = df.reset_index(drop=True)

    # Cut the dataframe to only keep rows above 'Monthly Totals'
    if 'Monthly Totals' in df.iloc[:, 0].values:
        cut_off_index = df[df.iloc[:, 0] == 'Monthly Totals'].index[0]
        df = df.iloc[:cut_off_index]

    # Define the expected column names
    expected_columns = {
        'Date': 'Date',
        'Census': 'Total Census Rooms',
        'Held Beds': 'Single Room E',
        'Held Due To Covid Swab/Quarantine': 'Single Room F',
        'Closed Beds': 'Closed Rooms'
    }

    # Apply column mapping
    df = df.rename(columns=expected_columns)


    # Calculate total single room patients and double room patients
    df['Single Room E'] = df['Single Room E'].astype(float)
    df['Single Room F'] = df['Single Room F'].astype(float)
    df['Total Single Room Patients'] = df['Single Room E'] + df['Single Room F']

    # If Total Single Rooms (held beds) > Total Census Rooms, set Total Single Rooms to Total Census Rooms, 
    df['Total Single Room Patients'] = df[['Total Single Room Patients', 'Total Census Rooms']].min(axis=1)

    df['Double Room Patients'] = df['Total Census Rooms'].astype(float) - df['Total Single Room Patients']
    df['Total Patients for Day'] = df['Total Single Room Patients'] + df['Double Room Patients']

    # Generate exact date based on the sheet_name (Month) and year
    df['Date'] = pd.to_datetime(df['Date'])

    # Select final columns
    df = df[
        [
            'Date', 'Single Room E', 'Single Room F', 
            'Total Single Room Patients', 'Double Room Patients', 
            'Total Patients for Day', 'Closed Rooms', 'Total Census Rooms'
        ]
    ]
    return df

def process_workbooks(file_paths):
    all_data_frames = []

    for file_path in file_paths:
        # Get year from file path
        # example file path: Monthly Census 2022.xlsx
        df = pd.read_csv(file_path)
        processed_df = process_sheet(df)
        all_data_frames.append(processed_df)

    # Concatenate all dataframes
    final_df = pd.concat(all_data_frames, ignore_index=True)

    # Save the final dataframe to a CSV file
    output_csv_path = 'data/final_census_data_test_set.csv'
    final_df.to_csv(output_csv_path, index=False)
    print(f"Data has been successfully written to {output_csv_path}")

# List of file paths to process
file_paths = [
    'data/Monthly Census 2024(Aug).csv',
    'data/Monthly Census 2024(Jul).csv',
    'data/Monthly Census 2024(Jun).csv',
    'data/Monthly Census 2024(May).csv',
]

# Process the workbooks and generate the CSV
process_workbooks(file_paths)
