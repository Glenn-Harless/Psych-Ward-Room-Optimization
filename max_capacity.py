import pandas as pd
import numpy as np
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt

def calculate_max_capacity_events(raw_data_path, current_model_path, optimized_model_path):
    """
    Calculate when the ward reaches max capacity under both configurations.
    
    Parameters:
    raw_data_path: Path to raw census data CSV
    current_model_path: Path to current model results CSV
    optimized_model_path: Path to optimized model results CSV
    
    Returns:
    dict: Statistics about max capacity events for both configurations
    """
    # Load all datasets
    raw_data = pd.read_csv(raw_data_path)
    current_model = pd.read_csv(current_model_path)
    optimized_model = pd.read_csv(optimized_model_path)
    
    # Merge datasets
    analysis_df = pd.merge(raw_data, current_model, on='Date', suffixes=('', '_current'))
    analysis_df = pd.merge(analysis_df, optimized_model, on='Date', suffixes=('', '_optimized'))
    
    def analyze_configuration(df, is_current_model=True):
        max_capacity_days = []
        turned_away_events = []
        capacity_data = []
        
        if is_current_model:
            # Current model: 13 double rooms (26 beds)
            total_rooms = 13
            double_rooms = 13
            single_rooms = 0
        else:
            # Optimized model: 8 double rooms (16 beds) + 10 single rooms (10 beds)
            total_rooms = 18  # 8 + 10
            double_rooms = 8
            single_rooms = 10
            
        for index, row in df.iterrows():
            single_room_patients = row['Total Single Room Patients']
            double_room_patients = row['Double Room Patients']
            total_patients = row['Total Patients for Day']
            
            # Calculate available beds
            if is_current_model:
                # In current model:
                # 1. Single room patients each need their own double room
                rooms_for_single_patients = single_room_patients
                
                # 2. Double room patients can pair up (ceiling division for odd numbers)
                rooms_for_double_patients = -(-double_room_patients // 2)  # ceiling division
                
                # Total occupied double rooms
                occupied_double_rooms = rooms_for_single_patients + rooms_for_double_patients
                
                # Max capacity is reached if:
                # - All rooms are occupied
                # - Or total patients hits the bed limit
                is_max_capacity = (occupied_double_rooms >= double_rooms or 
                                 total_patients >= 26)
                
                # Turn away occurs if we need more rooms than available
                would_turn_away = occupied_double_rooms > double_rooms
                                
            else:
                # Optimized model: 8 double rooms (16 beds) + 10 single rooms (10 beds)
                # First put isolation patients in single rooms
                single_rooms_used = min(single_room_patients, single_rooms)  # how many single rooms are used
                remaining_single_patients = max(0, single_room_patients - single_rooms)  # isolation patients that need double rooms
                
                # These isolation patients each need their own double room
                double_rooms_for_isolation = remaining_single_patients
                
                # Calculate remaining double rooms for double room patients
                available_double_rooms = double_rooms - double_rooms_for_isolation
                beds_in_double_rooms = available_double_rooms * 2
                                
                # Calculate total available beds for double room patients:
                # - Unused single rooms (single_rooms - single_rooms_used)
                # - Available beds in double rooms (available_double_rooms * 2)
                available_beds_for_doubles = (single_rooms - single_rooms_used) + (available_double_rooms * 2)

                # Would turn away if we don't have enough beds for double room patients
                would_turn_away = double_room_patients > available_beds_for_doubles
                
                # Max capacity is hit if total patients equals or exceeds 26
                is_max_capacity = total_patients >= 26

            # Store detailed information for capacity events
            if is_max_capacity or would_turn_away:
                capacity_data.append({
                    'Date': row['Date'],
                    'Total_Patients': total_patients,
                    'Single_Room_Patients': single_room_patients,
                    'Double_Room_Patients': double_room_patients,
                    'Is_Max_Capacity': is_max_capacity,
                    # 'Would_Turn_Away': would_turn_away
                })
            
            if is_max_capacity:
                max_capacity_days.append(row['Date'])
                
            if would_turn_away:
                turned_away_events.append(row['Date'])
        
        return {
            'max_capacity_days': max_capacity_days,
            'turned_away_events': turned_away_events,
            'total_max_capacity_days': len(max_capacity_days),
            'total_turned_away_events': len(turned_away_events),
            'capacity_data': capacity_data
        }
    
    # Analyze both configurations
    current_model_stats = analyze_configuration(analysis_df, is_current_model=True)
    optimized_model_stats = analyze_configuration(analysis_df, is_current_model=False)
    
    # Create and save detailed capacity event CSVs
    current_capacity_df = pd.DataFrame(current_model_stats['capacity_data'])
    if not current_capacity_df.empty:
        current_capacity_df.sort_values('Date').to_csv('output/current_model_max_capacity.csv', index=False)
    
    new_capacity_df = pd.DataFrame(optimized_model_stats['capacity_data'])
    if not new_capacity_df.empty:
        new_capacity_df.sort_values('Date').to_csv('output/new_model_capacity.csv', index=False)
    
    # Calculate additional statistics
    total_days = len(analysis_df)
    
    results = {
        'current_model': {
            **current_model_stats,
            'percent_max_capacity': (current_model_stats['total_max_capacity_days'] / total_days) * 100
        },
        'optimized_model': {
            **optimized_model_stats,
            'percent_max_capacity': (optimized_model_stats['total_max_capacity_days'] / total_days) * 100
        },
        'total_days_analyzed': total_days
    }
    
    # Generate summary report
    summary_df = pd.DataFrame({
        'Metric': ['Total Days at Max Capacity', 'Percent Days at Max Capacity'],
        'Current Model': [
            results['current_model']['total_max_capacity_days'],
            f"{results['current_model']['percent_max_capacity']:.2f}%"
        ],
        'Optimized Model': [
            results['optimized_model']['total_max_capacity_days'],
            f"{results['optimized_model']['percent_max_capacity']:.2f}%"
        ]
    })
    
    # Save results
    summary_df.to_csv('output/max_capacity_summary.csv', index=False)
    
    return results

def create_visualizations(results):
    # Set the style for all plots
    sns.set()

    # Create DataFrame for easier plotting
    data = pd.DataFrame({
        'Model': ['Current Model', 'Optimized Model'],
        'Days at Max Capacity': [
            results['current_model']['total_max_capacity_days'],
            results['optimized_model']['total_max_capacity_days']
        ],
        'Percent at Max Capacity': [
            results['current_model']['percent_max_capacity'],
            results['optimized_model']['percent_max_capacity']
        ]
    })

    # 1. Bar Plot Comparison
    plt.figure(figsize=(10, 6))
    sns.barplot(data=data, x='Model', y='Days at Max Capacity', palette='muted')
    plt.title('Days at Max Capacity by Model')
    plt.ylabel('Number of Days')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('output/capacity_events_comparison.png')
    plt.close()

    # 2. Percentage Comparison
    plt.figure(figsize=(8, 6))
    sns.barplot(data=data, x='Model', y='Percent at Max Capacity', 
                palette=['#ff7f0e', '#2ca02c'])
    plt.title('Percent of Days at Max Capacity')
    plt.ylabel('Percentage')
    plt.xticks(rotation=0)
    for i, v in enumerate(data['Percent at Max Capacity']):
        plt.text(i, v + 1, f'{v:.1f}%', ha='center')
    plt.tight_layout()
    plt.savefig('output/capacity_percentages.png')
    plt.close()

    # 3. Capacity Distribution (Pie Charts)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Current Model
    current_below = 100 - data.loc[0, 'Percent at Max Capacity']
    current_at = data.loc[0, 'Percent at Max Capacity']
    current_data = [current_below, current_at]
    ax1.pie(current_data, labels=['Below Capacity', 'At Max Capacity'], 
            autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    ax1.set_title('Current Model')

    # Optimized Model
    optimized_below = 100 - data.loc[1, 'Percent at Max Capacity']
    optimized_at = data.loc[1, 'Percent at Max Capacity']
    optimized_data = [optimized_below, optimized_at]
    ax2.pie(optimized_data, labels=['Below Capacity', 'At Max Capacity'], 
            autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    ax2.set_title('Optimized Model')

    plt.suptitle('Capacity Distribution')
    plt.tight_layout()
    plt.savefig('output/capacity_distribution.png')
    plt.close()

    # 4. Heatmap of Metrics
    plt.figure(figsize=(10, 4))
    metrics_data = data.set_index('Model').T
    sns.heatmap(metrics_data, annot=True, fmt='.1f', cmap='YlOrRd', 
                cbar_kws={'label': 'Value'})
    plt.title('Summary of Metrics')
    plt.tight_layout()
    plt.savefig('output/metrics_heatmap.png')
    plt.close()

if __name__ == "__main__":
    # Adjust these paths as needed
    results = calculate_max_capacity_events(
        'data/final_census_data.csv',
        'output/current_model_data.csv',
        'output/optimized_model_data.csv'
    )
    
    print("\nAnalysis Complete!")
    print(f"Total days analyzed: {results['total_days_analyzed']}")
    print("\nCurrent Model (13 Double Rooms):")
    print(f"Days at max capacity: {results['current_model']['total_max_capacity_days']}")
    print(f"Percent at max capacity: {results['current_model']['percent_max_capacity']:.2f}%")
    
    print("\nOptimized Model (8 Double + 10 Single Rooms):")
    print(f"Days at max capacity: {results['optimized_model']['total_max_capacity_days']}")
    print(f"Percent at max capacity: {results['optimized_model']['percent_max_capacity']:.2f}%")

    # Create visualizations
    create_visualizations(results)



def calculate_max_capacity_events(raw_data_path, current_model_path, optimized_model_path):
    """
    Calculate when the ward reaches max capacity under both configurations.
    
    Parameters:
    raw_data_path: Path to raw census data CSV
    current_model_path: Path to current model results CSV
    optimized_model_path: Path to optimized model results CSV
    
    Returns:
    dict: Statistics about max capacity events for both configurations
    """
    # Load all datasets
    raw_data = pd.read_csv(raw_data_path)
    current_model = pd.read_csv(current_model_path)
    optimized_model = pd.read_csv(optimized_model_path)
    
    # Merge datasets
    analysis_df = pd.merge(raw_data, current_model, on='Date', suffixes=('', '_current'))
    analysis_df = pd.merge(analysis_df, optimized_model, on='Date', suffixes=('', '_optimized'))
    
