"""
Capacity utilization analysis module.

Analyzes when the ward reaches maximum capacity under different
room configurations and provides detailed capacity metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

from ..utils.logger import get_logger
from ..utils.constants import TOTAL_BEDS, DOUBLE_ROOM_CAPACITY
from ..utils.file_handler import FileHandler
from ..models.base_model import BaseModel


logger = get_logger(__name__)


class CapacityAnalyzer:
    """
    Analyzes capacity utilization for different ward configurations.
    
    Provides detailed analysis of when wards reach maximum capacity,
    turn-away events, and capacity distribution over time.
    """
    
    def __init__(self, model: BaseModel):
        """
        Initialize capacity analyzer with a specific model.
        
        Args:
            model: Ward configuration model to analyze
        """
        self.model = model
        self.capacity_events = []
        self.analysis_results = None
        
    def analyze_capacity(self, census_data: pd.DataFrame) -> Dict[str, any]:
        """
        Analyze capacity utilization for the model configuration.
        
        Args:
            census_data: DataFrame with daily census data
            
        Returns:
            Dictionary with capacity analysis results
        """
        max_capacity_days = []
        turned_away_events = []
        capacity_details = []
        daily_utilization = []
        
        single_rooms = self.model.single_rooms
        double_rooms = self.model.double_rooms
        total_rooms = single_rooms + double_rooms
        
        for index, row in census_data.iterrows():
            single_patients = row['Total Single Room Patients']
            double_patients = row['Double Room Patients']
            total_patients = row['Total Patients for Day']
            closed_rooms = row.get('Closed Rooms', 0)
            
            # Calculate room usage
            room_usage = self._calculate_room_usage(
                single_patients, double_patients, 
                single_rooms, double_rooms
            )
            
            # Calculate capacity metrics
            available_beds = TOTAL_BEDS - closed_rooms
            used_beds = room_usage['beds_used']
            utilization_rate = (used_beds / available_beds * 100) if available_beds > 0 else 0
            
            # Check if at max capacity
            is_max_capacity = (
                used_beds >= available_beds or
                room_usage['rooms_used'] >= total_rooms or
                room_usage['overflow_patients'] > 0
            )
            
            # Check for turn-away events
            would_turn_away = room_usage['overflow_patients'] > 0
            
            # Store daily utilization
            daily_utilization.append({
                'Date': row['Date'],
                'Utilization_Rate': utilization_rate,
                'Used_Beds': used_beds,
                'Available_Beds': available_beds,
                'Is_Max_Capacity': is_max_capacity
            })
            
            # Store capacity events
            if is_max_capacity or would_turn_away:
                capacity_details.append({
                    'Date': row['Date'],
                    'Total_Patients': total_patients,
                    'Single_Patients': single_patients,
                    'Double_Patients': double_patients,
                    'Used_Beds': used_beds,
                    'Available_Beds': available_beds,
                    'Overflow_Patients': room_usage['overflow_patients'],
                    'Is_Max_Capacity': is_max_capacity,
                    'Would_Turn_Away': would_turn_away
                })
                
                if is_max_capacity:
                    max_capacity_days.append(row['Date'])
                if would_turn_away:
                    turned_away_events.append(row['Date'])
        
        # Calculate summary statistics
        total_days = len(census_data)
        utilization_df = pd.DataFrame(daily_utilization)
        
        self.analysis_results = {
            'model_name': self.model.name,
            'total_days': total_days,
            'max_capacity_days': len(max_capacity_days),
            'max_capacity_percent': (len(max_capacity_days) / total_days * 100),
            'turn_away_events': len(turned_away_events),
            'turn_away_percent': (len(turned_away_events) / total_days * 100),
            'avg_utilization': utilization_df['Utilization_Rate'].mean(),
            'std_utilization': utilization_df['Utilization_Rate'].std(),
            'min_utilization': utilization_df['Utilization_Rate'].min(),
            'max_utilization': utilization_df['Utilization_Rate'].max(),
            'capacity_events': pd.DataFrame(capacity_details),
            'daily_utilization': utilization_df,
            'max_capacity_dates': max_capacity_days,
            'turn_away_dates': turned_away_events
        }
        
        logger.info(f"Capacity analysis complete for {self.model.name}:")
        logger.info(f"  Days at max capacity: {self.analysis_results['max_capacity_days']} "
                   f"({self.analysis_results['max_capacity_percent']:.1f}%)")
        logger.info(f"  Average utilization: {self.analysis_results['avg_utilization']:.1f}%")
        
        return self.analysis_results
    
    def _calculate_room_usage(self, single_patients: int, double_patients: int,
                             single_rooms: int, double_rooms: int) -> Dict[str, int]:
        """
        Calculate detailed room usage for given patient counts.
        
        Returns:
            Dictionary with room usage details
        """
        # Place single patients
        singles_in_single = min(single_patients, single_rooms)
        remaining_singles = max(0, single_patients - single_rooms)
        
        # Singles overflow to double rooms
        doubles_for_singles = remaining_singles
        available_doubles = max(0, double_rooms - doubles_for_singles)
        
        # Place double patients in remaining double rooms
        double_capacity = available_doubles * DOUBLE_ROOM_CAPACITY
        doubles_accommodated = min(double_patients, double_capacity)
        
        # Calculate overflow
        overflow_doubles = max(0, double_patients - double_capacity)
        
        # If we have overflow and available single rooms, use them
        singles_for_doubles = 0
        if overflow_doubles > 0 and singles_in_single < single_rooms:
            available_singles = single_rooms - singles_in_single
            singles_for_doubles = min(overflow_doubles, available_singles)
            overflow_doubles -= singles_for_doubles
        
        # Calculate totals
        rooms_used = (
            singles_in_single + 
            doubles_for_singles + 
            (doubles_accommodated // DOUBLE_ROOM_CAPACITY) +
            (1 if doubles_accommodated % DOUBLE_ROOM_CAPACITY > 0 else 0) +
            singles_for_doubles
        )
        
        beds_used = (
            singles_in_single +
            remaining_singles +
            doubles_accommodated +
            singles_for_doubles
        )
        
        return {
            'rooms_used': rooms_used,
            'beds_used': beds_used,
            'singles_in_single': singles_in_single,
            'singles_in_double': remaining_singles,
            'doubles_in_double': doubles_accommodated,
            'doubles_in_single': singles_for_doubles,
            'overflow_patients': overflow_doubles
        }
    
    def compare_capacity(self, other_analyzer: 'CapacityAnalyzer') -> Dict[str, float]:
        """
        Compare capacity metrics with another configuration.
        
        Args:
            other_analyzer: Another capacity analyzer to compare with
            
        Returns:
            Dictionary with comparison metrics
        """
        if self.analysis_results is None or other_analyzer.analysis_results is None:
            raise ValueError("Both analyzers must have results before comparison")
        
        comparison = {
            'max_capacity_reduction': (
                other_analyzer.analysis_results['max_capacity_percent'] -
                self.analysis_results['max_capacity_percent']
            ),
            'turn_away_reduction': (
                other_analyzer.analysis_results['turn_away_percent'] -
                self.analysis_results['turn_away_percent']
            ),
            'utilization_improvement': (
                self.analysis_results['avg_utilization'] -
                other_analyzer.analysis_results['avg_utilization']
            ),
            'utilization_stability': (
                other_analyzer.analysis_results['std_utilization'] -
                self.analysis_results['std_utilization']
            )
        }
        
        return comparison
    
    def save_capacity_events(self, output_path: str):
        """
        Save detailed capacity events to CSV.
        
        Args:
            output_path: Path for output CSV file
        """
        if self.analysis_results is None:
            raise ValueError("No results to save. Run analyze_capacity() first.")
        
        capacity_events = self.analysis_results['capacity_events']
        if not capacity_events.empty:
            FileHandler.write_csv(capacity_events, output_path)
            logger.info(f"Saved {len(capacity_events)} capacity events to {output_path}")
        else:
            logger.info("No capacity events to save")
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get a summary of capacity analysis results.
        
        Returns:
            Dictionary with summary metrics
        """
        if self.analysis_results is None:
            raise ValueError("No results available. Run analyze_capacity() first.")
        
        return {
            'model': self.model.name,
            'configuration': f"{self.model.single_rooms}S/{self.model.double_rooms}D",
            'days_at_max_capacity': self.analysis_results['max_capacity_days'],
            'percent_at_max_capacity': f"{self.analysis_results['max_capacity_percent']:.1f}%",
            'turn_away_events': self.analysis_results['turn_away_events'],
            'average_utilization': f"{self.analysis_results['avg_utilization']:.1f}%",
            'utilization_std_dev': f"{self.analysis_results['std_utilization']:.1f}%"
        }