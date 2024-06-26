import pandas as pd

def process_sheet(df):
    df = df.reset_index(drop=True)


    # Cut the dataframe to only keep rows above 'Monthly Totals'
    if 'Monthly Totals' in df.iloc[:, 0].values:
        cut_off_index = df[df.iloc[:, 0] == 'Monthly Totals'].index[0]
        df = df.iloc[:cut_off_index]

    # Define the expected column names
    expected_columns = {
        'Unnamed: 1': 'Day',
        'Census': 'Total Census Rooms',
        'Held Beds': 'Single Room E',
        'Held Due To Covid Swab/Quarantine': 'Single Room F',
        'Closed Beds': 'Closed Rooms'
    }

    # Apply column mapping
    df = df.rename(columns=expected_columns)

    # Ensure all required columns are present
    required_columns = ['Day', 'Double Room', 'Single Room E', 'Single Room F', 'Closed Rooms']
    for col in required_columns:
        if col not in df.columns:
            df[col] = 0  # Assign default value if column is missing

    # Calculate total single room patients and double room patients
    df['Single Room E'] = df['Single Room E'].astype(float)
    df['Single Room F'] = df['Single Room F'].astype(float)
    df['Total Single Room Patients'] = df['Single Room E'] + df['Single Room F']
    df['Double Room Patients'] = df['Total Census Rooms'].astype(float) - df['Total Single Room Patients']
    df['Total Patients for Day'] = df['Total Single Room Patients'] + df['Double Room Patients']

    # Select final columns
    df = df[['Day', 'Single Room E', 'Single Room F', 'Total Single Room Patients', 'Double Room Patients', 'Total Patients for Day', 'Closed Rooms']]
    return df

def process_workbooks(file_paths):
    all_data_frames = []

    for file_path in file_paths:
        xls = pd.ExcelFile(file_path)
        for sheet_name in xls.sheet_names:
            if len(sheet_name) == 3:
                df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=4)
                processed_df = process_sheet(df)
                all_data_frames.append(processed_df)

    # Concatenate all dataframes
    final_df = pd.concat(all_data_frames, ignore_index=True)

    # Save the final dataframe to a CSV file
    output_csv_path = 'data/final_census_data.csv'
    final_df.to_csv(output_csv_path, index=False)
    print(f"Data has been successfully written to {output_csv_path}")

# List of file paths to process
file_paths = [
    'data/Monthly Census 2022.xlsx',
    'data/Monthly Census 2023.xlsx',
    'data/Monthly Census 2024.xlsx'
]

# Process the workbooks and generate the CSV
process_workbooks(file_paths)
