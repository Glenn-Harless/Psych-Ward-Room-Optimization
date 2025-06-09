"""
Waste analysis module.

Analyzes bed waste and potential waste patterns to identify
optimization opportunities and inefficiencies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime

from ..utils.logger import get_logger


logger = get_logger(__name__)


class WasteAnalyzer:
    """
    Analyzes waste patterns in ward configurations.
    
    Two types of waste are analyzed:
    1. Wasted Beds: Single patients occupying double rooms
    2. Wasted Potential: Double patients forced into single rooms
    """
    
    @staticmethod
    def analyze_waste_patterns(
        results_df: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Analyze comprehensive waste patterns from evaluation results.
        
        Args:
            results_df: DataFrame with columns 'Date', 'Wasted_Beds', 
                       'Wasted_Potential', 'Available_Beds'
            
        Returns:
            Dictionary with detailed waste analysis
        """
        # Basic waste statistics
        total_days = len(results_df)
        total_wasted_beds = results_df['Wasted_Beds'].sum()
        total_wasted_potential = results_df['Wasted_Potential'].sum()
        total_waste = total_wasted_beds + total_wasted_potential
        
        # Days with waste
        days_with_bed_waste = (results_df['Wasted_Beds'] > 0).sum()
        days_with_potential_waste = (results_df['Wasted_Potential'] > 0).sum()
        days_with_any_waste = ((results_df['Wasted_Beds'] > 0) | 
                               (results_df['Wasted_Potential'] > 0)).sum()
        
        # Waste intensity
        avg_bed_waste_when_occurs = (
            results_df[results_df['Wasted_Beds'] > 0]['Wasted_Beds'].mean()
            if days_with_bed_waste > 0 else 0
        )
        avg_potential_waste_when_occurs = (
            results_df[results_df['Wasted_Potential'] > 0]['Wasted_Potential'].mean()
            if days_with_potential_waste > 0 else 0
        )
        
        # Waste distribution
        bed_waste_percentiles = results_df['Wasted_Beds'].quantile([0.25, 0.5, 0.75, 0.95])
        potential_waste_percentiles = results_df['Wasted_Potential'].quantile([0.25, 0.5, 0.75, 0.95])
        
        # Consecutive waste analysis
        consecutive_waste = WasteAnalyzer._analyze_consecutive_waste(results_df)
        
        # Peak waste analysis
        peak_bed_waste_date = results_df.loc[results_df['Wasted_Beds'].idxmax(), 'Date']
        peak_bed_waste_value = results_df['Wasted_Beds'].max()
        peak_potential_waste_date = results_df.loc[results_df['Wasted_Potential'].idxmax(), 'Date']
        peak_potential_waste_value = results_df['Wasted_Potential'].max()
        
        analysis = {
            # Totals
            'total_days': total_days,
            'total_wasted_beds': total_wasted_beds,
            'total_wasted_potential': total_wasted_potential,
            'total_waste': total_waste,
            
            # Frequency
            'days_with_bed_waste': days_with_bed_waste,
            'days_with_potential_waste': days_with_potential_waste,
            'days_with_any_waste': days_with_any_waste,
            'percent_days_with_bed_waste': (days_with_bed_waste / total_days * 100),
            'percent_days_with_potential_waste': (days_with_potential_waste / total_days * 100),
            'percent_days_with_any_waste': (days_with_any_waste / total_days * 100),
            
            # Averages
            'avg_daily_bed_waste': results_df['Wasted_Beds'].mean(),
            'avg_daily_potential_waste': results_df['Wasted_Potential'].mean(),
            'avg_bed_waste_when_occurs': avg_bed_waste_when_occurs,
            'avg_potential_waste_when_occurs': avg_potential_waste_when_occurs,
            
            # Distribution
            'bed_waste_std': results_df['Wasted_Beds'].std(),
            'potential_waste_std': results_df['Wasted_Potential'].std(),
            'bed_waste_25th': bed_waste_percentiles[0.25],
            'bed_waste_median': bed_waste_percentiles[0.5],
            'bed_waste_75th': bed_waste_percentiles[0.75],
            'bed_waste_95th': bed_waste_percentiles[0.95],
            'potential_waste_25th': potential_waste_percentiles[0.25],
            'potential_waste_median': potential_waste_percentiles[0.5],
            'potential_waste_75th': potential_waste_percentiles[0.75],
            'potential_waste_95th': potential_waste_percentiles[0.95],
            
            # Peaks
            'peak_bed_waste_date': peak_bed_waste_date,
            'peak_bed_waste_value': peak_bed_waste_value,
            'peak_potential_waste_date': peak_potential_waste_date,
            'peak_potential_waste_value': peak_potential_waste_value,
            
            # Consecutive waste
            'max_consecutive_bed_waste_days': consecutive_waste['max_bed_waste_days'],
            'max_consecutive_potential_waste_days': consecutive_waste['max_potential_waste_days'],
            'avg_consecutive_bed_waste_days': consecutive_waste['avg_bed_waste_days'],
            'avg_consecutive_potential_waste_days': consecutive_waste['avg_potential_waste_days']
        }
        
        return analysis
    
    @staticmethod
    def _analyze_consecutive_waste(results_df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze consecutive days of waste.
        
        Returns:
            Dictionary with consecutive waste statistics
        """
        # Track consecutive bed waste
        bed_waste_streaks = []
        current_streak = 0
        
        for waste in results_df['Wasted_Beds']:
            if waste > 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    bed_waste_streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            bed_waste_streaks.append(current_streak)
        
        # Track consecutive potential waste
        potential_waste_streaks = []
        current_streak = 0
        
        for waste in results_df['Wasted_Potential']:
            if waste > 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    potential_waste_streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            potential_waste_streaks.append(current_streak)
        
        return {
            'max_bed_waste_days': max(bed_waste_streaks) if bed_waste_streaks else 0,
            'max_potential_waste_days': max(potential_waste_streaks) if potential_waste_streaks else 0,
            'avg_bed_waste_days': np.mean(bed_waste_streaks) if bed_waste_streaks else 0,
            'avg_potential_waste_days': np.mean(potential_waste_streaks) if potential_waste_streaks else 0
        }
    
    @staticmethod
    def analyze_waste_by_period(
        results_df: pd.DataFrame,
        period: str = 'month'
    ) -> pd.DataFrame:
        """
        Analyze waste patterns by time period.
        
        Args:
            results_df: DataFrame with waste data
            period: Time period for grouping ('week', 'month', 'quarter', 'year')
            
        Returns:
            DataFrame with period-wise waste analysis
        """
        # Ensure date column is datetime
        results_df['Date'] = pd.to_datetime(results_df['Date'])
        
        # Set appropriate grouper
        freq_map = {
            'week': 'W',
            'month': 'M',
            'quarter': 'Q',
            'year': 'Y'
        }
        
        if period not in freq_map:
            raise ValueError(f"Invalid period: {period}")
        
        grouper = pd.Grouper(key='Date', freq=freq_map[period])
        
        # Aggregate by period
        period_analysis = results_df.groupby(grouper).agg({
            'Wasted_Beds': ['sum', 'mean', 'max', 'std'],
            'Wasted_Potential': ['sum', 'mean', 'max', 'std'],
            'Available_Beds': 'sum'
        }).round(2)
        
        # Calculate waste rates
        period_analysis['Bed_Waste_Rate'] = (
            period_analysis[('Wasted_Beds', 'sum')] / 
            period_analysis[('Available_Beds', 'sum')] * 100
        )
        period_analysis['Potential_Waste_Rate'] = (
            period_analysis[('Wasted_Potential', 'sum')] / 
            period_analysis[('Available_Beds', 'sum')] * 100
        )
        
        # Flatten column names
        period_analysis.columns = ['_'.join(col).strip() if col[1] else col[0] 
                                  for col in period_analysis.columns.values]
        
        return period_analysis
    
    @staticmethod
    def identify_waste_triggers(
        results_df: pd.DataFrame,
        census_df: pd.DataFrame
    ) -> Dict[str, any]:
        """
        Identify patterns that trigger waste events.
        
        Args:
            results_df: DataFrame with waste data
            census_df: DataFrame with census data
            
        Returns:
            Dictionary with waste trigger analysis
        """
        # Merge results with census data
        analysis_df = pd.merge(results_df, census_df, on='Date')
        
        # Analyze correlations
        waste_correlations = {
            'bed_waste_vs_single_patients': analysis_df['Wasted_Beds'].corr(
                analysis_df['Total Single Room Patients']
            ),
            'potential_waste_vs_double_patients': analysis_df['Wasted_Potential'].corr(
                analysis_df['Double Room Patients']
            ),
            'bed_waste_vs_total_patients': analysis_df['Wasted_Beds'].corr(
                analysis_df['Total Patients for Day']
            )
        }
        
        # Identify thresholds
        bed_waste_df = analysis_df[analysis_df['Wasted_Beds'] > 0]
        potential_waste_df = analysis_df[analysis_df['Wasted_Potential'] > 0]
        
        triggers = {
            'correlations': waste_correlations,
            'bed_waste_triggers': {
                'min_single_patients': bed_waste_df['Total Single Room Patients'].min(),
                'avg_single_patients': bed_waste_df['Total Single Room Patients'].mean(),
                'threshold_single_patients': bed_waste_df['Total Single Room Patients'].quantile(0.1)
            },
            'potential_waste_triggers': {
                'min_double_patients': potential_waste_df['Double Room Patients'].min() if len(potential_waste_df) > 0 else 0,
                'avg_double_patients': potential_waste_df['Double Room Patients'].mean() if len(potential_waste_df) > 0 else 0,
                'threshold_double_patients': potential_waste_df['Double Room Patients'].quantile(0.1) if len(potential_waste_df) > 0 else 0
            }
        }
        
        return triggers
    
    @staticmethod
    def calculate_waste_cost(
        results_df: pd.DataFrame,
        bed_cost_per_day: float = 500.0
    ) -> Dict[str, float]:
        """
        Calculate the financial impact of waste.
        
        Args:
            results_df: DataFrame with waste data
            bed_cost_per_day: Cost per bed per day
            
        Returns:
            Dictionary with cost analysis
        """
        total_wasted_beds = results_df['Wasted_Beds'].sum()
        total_wasted_potential = results_df['Wasted_Potential'].sum()
        
        costs = {
            'bed_waste_cost': total_wasted_beds * bed_cost_per_day,
            'potential_waste_cost': total_wasted_potential * bed_cost_per_day,
            'total_waste_cost': (total_wasted_beds + total_wasted_potential) * bed_cost_per_day,
            'daily_avg_waste_cost': results_df['Wasted_Beds'].mean() * bed_cost_per_day,
            'monthly_avg_waste_cost': results_df['Wasted_Beds'].mean() * bed_cost_per_day * 30,
            'annual_projected_waste_cost': results_df['Wasted_Beds'].mean() * bed_cost_per_day * 365
        }
        
        return costs
    
    @staticmethod
    def compare_waste(
        model1_results: pd.DataFrame,
        model2_results: pd.DataFrame,
        model1_name: str = "Model 1",
        model2_name: str = "Model 2"
    ) -> Dict[str, any]:
        """
        Compare waste between two models.
        
        Args:
            model1_results: Results from first model
            model2_results: Results from second model
            model1_name: Name of first model
            model2_name: Name of second model
            
        Returns:
            Dictionary with waste comparison
        """
        waste1 = WasteAnalyzer.analyze_waste_patterns(model1_results)
        waste2 = WasteAnalyzer.analyze_waste_patterns(model2_results)
        
        comparison = {
            'model1_name': model1_name,
            'model2_name': model2_name,
            'bed_waste_reduction': waste2['total_wasted_beds'] - waste1['total_wasted_beds'],
            'potential_waste_reduction': waste2['total_wasted_potential'] - waste1['total_wasted_potential'],
            'total_waste_reduction': waste2['total_waste'] - waste1['total_waste'],
            'bed_waste_reduction_percent': (
                (waste2['total_wasted_beds'] - waste1['total_wasted_beds']) / 
                waste2['total_wasted_beds'] * 100 if waste2['total_wasted_beds'] > 0 else 0
            ),
            'days_with_waste_reduction': waste2['days_with_any_waste'] - waste1['days_with_any_waste'],
            'model1_waste': waste1,
            'model2_waste': waste2
        }
        
        # Determine which model has less waste
        if comparison['total_waste_reduction'] > 0:
            comparison['better_model'] = model1_name
            comparison['waste_improvement'] = comparison['total_waste_reduction']
        else:
            comparison['better_model'] = model2_name
            comparison['waste_improvement'] = -comparison['total_waste_reduction']
        
        return comparison