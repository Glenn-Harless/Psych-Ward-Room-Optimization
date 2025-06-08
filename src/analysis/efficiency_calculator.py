"""
Efficiency metrics calculation module.

Provides comprehensive efficiency calculations for ward configurations
including daily, cumulative, and various efficiency metrics.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

from ..utils.logger import get_logger


logger = get_logger(__name__)


class EfficiencyCalculator:
    """
    Calculates various efficiency metrics for ward configurations.
    
    Efficiency is measured as the percentage of available resources
    that are effectively utilized without waste.
    """
    
    @staticmethod
    def calculate_daily_efficiency(
        available_beds: int,
        wasted_beds: int,
        wasted_potential: int
    ) -> float:
        """
        Calculate efficiency for a single day.
        
        Efficiency = (Available - Wasted_Beds - Wasted_Potential) / Available * 100
        
        Args:
            available_beds: Total available beds for the day
            wasted_beds: Beds wasted (singles in doubles)
            wasted_potential: Potential wasted (doubles in singles)
            
        Returns:
            Efficiency percentage (0-100)
        """
        if available_beds <= 0:
            return 0.0
            
        effective_beds = available_beds - wasted_beds - wasted_potential
        efficiency = (effective_beds / available_beds) * 100
        
        return max(0.0, min(100.0, efficiency))
    
    @staticmethod
    def calculate_cumulative_efficiency(
        results_df: pd.DataFrame
    ) -> pd.Series:
        """
        Calculate cumulative efficiency over time.
        
        Args:
            results_df: DataFrame with columns 'Available_Beds', 
                       'Wasted_Beds', 'Wasted_Potential'
            
        Returns:
            Series with cumulative efficiency values
        """
        cumulative_available = results_df['Available_Beds'].cumsum()
        cumulative_wasted_beds = results_df['Wasted_Beds'].cumsum()
        cumulative_wasted_potential = results_df['Wasted_Potential'].cumsum()
        
        cumulative_efficiency = (
            (cumulative_available - cumulative_wasted_beds - cumulative_wasted_potential) /
            cumulative_available * 100
        )
        
        return cumulative_efficiency
    
    @staticmethod
    def calculate_weighted_efficiency(
        results_df: pd.DataFrame,
        bed_weight: float = 1.0,
        potential_weight: float = 1.0
    ) -> pd.Series:
        """
        Calculate efficiency with weighted waste components.
        
        Args:
            results_df: DataFrame with efficiency data
            bed_weight: Weight for wasted beds
            potential_weight: Weight for wasted potential
            
        Returns:
            Series with weighted efficiency values
        """
        weighted_waste = (
            results_df['Wasted_Beds'] * bed_weight +
            results_df['Wasted_Potential'] * potential_weight
        )
        
        weighted_efficiency = (
            (results_df['Available_Beds'] - weighted_waste) /
            results_df['Available_Beds'] * 100
        )
        
        return weighted_efficiency.clip(lower=0, upper=100)
    
    @staticmethod
    def calculate_rolling_efficiency(
        results_df: pd.DataFrame,
        window: int = 7
    ) -> pd.Series:
        """
        Calculate rolling average efficiency.
        
        Args:
            results_df: DataFrame with efficiency data
            window: Rolling window size in days
            
        Returns:
            Series with rolling efficiency values
        """
        # Calculate daily efficiency if not present
        if 'Efficiency' not in results_df.columns:
            results_df['Efficiency'] = results_df.apply(
                lambda row: EfficiencyCalculator.calculate_daily_efficiency(
                    row['Available_Beds'],
                    row['Wasted_Beds'],
                    row['Wasted_Potential']
                ),
                axis=1
            )
        
        return results_df['Efficiency'].rolling(window=window, min_periods=1).mean()
    
    @staticmethod
    def calculate_efficiency_metrics(
        results_df: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate comprehensive efficiency metrics.
        
        Args:
            results_df: DataFrame with model evaluation results
            
        Returns:
            Dictionary with various efficiency metrics
        """
        # Ensure efficiency column exists
        if 'Efficiency' not in results_df.columns:
            results_df['Efficiency'] = results_df.apply(
                lambda row: EfficiencyCalculator.calculate_daily_efficiency(
                    row['Available_Beds'],
                    row['Wasted_Beds'],
                    row['Wasted_Potential']
                ),
                axis=1
            )
        
        # Calculate cumulative metrics
        total_available = results_df['Available_Beds'].sum()
        total_wasted_beds = results_df['Wasted_Beds'].sum()
        total_wasted_potential = results_df['Wasted_Potential'].sum()
        
        overall_efficiency = EfficiencyCalculator.calculate_daily_efficiency(
            total_available, total_wasted_beds, total_wasted_potential
        )
        
        # Calculate distribution metrics
        efficiency_std = results_df['Efficiency'].std()
        efficiency_variance = results_df['Efficiency'].var()
        
        # Calculate percentiles
        percentiles = results_df['Efficiency'].quantile([0.25, 0.5, 0.75])
        
        # Calculate perfect efficiency days
        perfect_days = (results_df['Efficiency'] == 100).sum()
        zero_efficiency_days = (results_df['Efficiency'] == 0).sum()
        
        metrics = {
            'overall_efficiency': overall_efficiency,
            'average_daily_efficiency': results_df['Efficiency'].mean(),
            'median_efficiency': results_df['Efficiency'].median(),
            'min_efficiency': results_df['Efficiency'].min(),
            'max_efficiency': results_df['Efficiency'].max(),
            'efficiency_std': efficiency_std,
            'efficiency_variance': efficiency_variance,
            'efficiency_25th_percentile': percentiles[0.25],
            'efficiency_50th_percentile': percentiles[0.5],
            'efficiency_75th_percentile': percentiles[0.75],
            'perfect_efficiency_days': perfect_days,
            'perfect_efficiency_percent': (perfect_days / len(results_df) * 100),
            'zero_efficiency_days': zero_efficiency_days,
            'days_below_90_percent': (results_df['Efficiency'] < 90).sum(),
            'days_below_95_percent': (results_df['Efficiency'] < 95).sum()
        }
        
        return metrics
    
    @staticmethod
    def calculate_efficiency_trend(
        results_df: pd.DataFrame,
        period: str = 'month'
    ) -> pd.DataFrame:
        """
        Calculate efficiency trends over specified periods.
        
        Args:
            results_df: DataFrame with efficiency data
            period: Grouping period ('week', 'month', 'quarter', 'year')
            
        Returns:
            DataFrame with period-wise efficiency metrics
        """
        # Ensure date column is datetime
        results_df['Date'] = pd.to_datetime(results_df['Date'])
        
        # Set appropriate grouper
        if period == 'week':
            grouper = pd.Grouper(key='Date', freq='W')
        elif period == 'month':
            grouper = pd.Grouper(key='Date', freq='M')
        elif period == 'quarter':
            grouper = pd.Grouper(key='Date', freq='Q')
        elif period == 'year':
            grouper = pd.Grouper(key='Date', freq='Y')
        else:
            raise ValueError(f"Invalid period: {period}")
        
        # Calculate period metrics
        trend_df = results_df.groupby(grouper).agg({
            'Available_Beds': 'sum',
            'Wasted_Beds': 'sum',
            'Wasted_Potential': 'sum',
            'Efficiency': ['mean', 'std', 'min', 'max']
        }).round(2)
        
        # Calculate period efficiency
        trend_df['Period_Efficiency'] = (
            (trend_df['Available_Beds']['sum'] - 
             trend_df['Wasted_Beds']['sum'] - 
             trend_df['Wasted_Potential']['sum']) /
            trend_df['Available_Beds']['sum'] * 100
        )
        
        # Flatten column names
        trend_df.columns = ['_'.join(col).strip() if col[1] else col[0] 
                            for col in trend_df.columns.values]
        
        return trend_df
    
    @staticmethod
    def compare_efficiency(
        model1_results: pd.DataFrame,
        model2_results: pd.DataFrame,
        model1_name: str = "Model 1",
        model2_name: str = "Model 2"
    ) -> Dict[str, any]:
        """
        Compare efficiency between two models.
        
        Args:
            model1_results: Results from first model
            model2_results: Results from second model
            model1_name: Name of first model
            model2_name: Name of second model
            
        Returns:
            Dictionary with comparison metrics
        """
        metrics1 = EfficiencyCalculator.calculate_efficiency_metrics(model1_results)
        metrics2 = EfficiencyCalculator.calculate_efficiency_metrics(model2_results)
        
        comparison = {
            'model1_name': model1_name,
            'model2_name': model2_name,
            'overall_efficiency_diff': metrics1['overall_efficiency'] - metrics2['overall_efficiency'],
            'average_efficiency_diff': metrics1['average_daily_efficiency'] - metrics2['average_daily_efficiency'],
            'efficiency_stability_diff': metrics2['efficiency_std'] - metrics1['efficiency_std'],
            'perfect_days_diff': metrics1['perfect_efficiency_days'] - metrics2['perfect_efficiency_days'],
            'model1_metrics': metrics1,
            'model2_metrics': metrics2
        }
        
        # Determine which model is better
        if comparison['overall_efficiency_diff'] > 0:
            comparison['better_model'] = model1_name
            comparison['efficiency_improvement'] = comparison['overall_efficiency_diff']
        else:
            comparison['better_model'] = model2_name
            comparison['efficiency_improvement'] = -comparison['overall_efficiency_diff']
        
        return comparison