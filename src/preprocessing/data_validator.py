"""
Data validation module for census data.

Provides comprehensive validation rules and checks to ensure
data quality and consistency throughout the preprocessing pipeline.
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

from ..utils.logger import get_logger
from ..utils.constants import TOTAL_BEDS


logger = get_logger(__name__)


class DataValidator:
    """
    Validates census data at various stages of processing.
    
    Implements validation rules for:
    - Data types and formats
    - Value ranges and constraints
    - Logical consistency
    - Temporal consistency
    """
    
    def __init__(self):
        """Initialize the data validator."""
        self.validation_rules = self._define_validation_rules()
        self.validation_history = []
        
    def _define_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Define validation rules for each column."""
        return {
            'Date': {
                'type': 'datetime64[ns]',
                'nullable': False,
                'unique': True
            },
            'Day': {
                'type': 'numeric',
                'min': 1,
                'max': 31,
                'nullable': False
            },
            'Single Room E': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            },
            'Single Room F': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            },
            'Total Single Room Patients': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            },
            'Double Room Patients': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            },
            'Total Patients for Day': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            },
            'Closed Rooms': {
                'type': 'numeric',
                'min': 0,
                'max': 13,  # Maximum number of rooms
                'nullable': False
            },
            'Total Census Rooms': {
                'type': 'numeric',
                'min': 0,
                'max': TOTAL_BEDS,
                'nullable': False
            }
        }
    
    def validate_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive validation on a DataFrame.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check for required columns
        missing_cols = self._check_required_columns(df)
        if missing_cols:
            issues.extend(missing_cols)
        
        # Validate data types
        type_issues = self._validate_data_types(df)
        issues.extend(type_issues)
        
        # Validate value ranges
        range_issues = self._validate_value_ranges(df)
        issues.extend(range_issues)
        
        # Check logical consistency
        logic_issues = self._validate_logical_consistency(df)
        issues.extend(logic_issues)
        
        # Check temporal consistency
        temporal_issues = self._validate_temporal_consistency(df)
        warnings.extend(temporal_issues)
        
        # Check for duplicates
        duplicate_issues = self._check_duplicates(df)
        if duplicate_issues:
            issues.extend(duplicate_issues)
        
        # Summary statistics
        stats = self._calculate_validation_stats(df)
        
        result = {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'stats': stats,
            'timestamp': datetime.now()
        }
        
        self.validation_history.append(result)
        
        return result
    
    def _check_required_columns(self, df: pd.DataFrame) -> List[str]:
        """Check for required columns."""
        issues = []
        required_columns = list(self.validation_rules.keys())
        
        for col in required_columns:
            if col not in df.columns:
                issues.append(f"Missing required column: {col}")
                
        return issues
    
    def _validate_data_types(self, df: pd.DataFrame) -> List[str]:
        """Validate data types for each column."""
        issues = []
        
        for col, rules in self.validation_rules.items():
            if col not in df.columns:
                continue
                
            expected_type = rules.get('type')
            if expected_type == 'numeric':
                if not pd.api.types.is_numeric_dtype(df[col]):
                    issues.append(f"Column '{col}' should be numeric")
            elif expected_type == 'datetime64[ns]':
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    issues.append(f"Column '{col}' should be datetime")
                    
        return issues
    
    def _validate_value_ranges(self, df: pd.DataFrame) -> List[str]:
        """Validate value ranges for numeric columns."""
        issues = []
        
        for col, rules in self.validation_rules.items():
            if col not in df.columns:
                continue
                
            if 'min' in rules or 'max' in rules:
                col_values = df[col]
                
                if 'min' in rules:
                    below_min = col_values < rules['min']
                    if below_min.any():
                        count = below_min.sum()
                        issues.append(f"Column '{col}' has {count} values below minimum {rules['min']}")
                        
                if 'max' in rules:
                    above_max = col_values > rules['max']
                    if above_max.any():
                        count = above_max.sum()
                        issues.append(f"Column '{col}' has {count} values above maximum {rules['max']}")
                        
        return issues
    
    def _validate_logical_consistency(self, df: pd.DataFrame) -> List[str]:
        """Check logical consistency between columns."""
        issues = []
        
        # Check: Total Single Room Patients = Single Room E + Single Room F
        if all(col in df.columns for col in ['Single Room E', 'Single Room F', 'Total Single Room Patients']):
            calculated_total = df['Single Room E'] + df['Single Room F']
            mismatch = (calculated_total != df['Total Single Room Patients'])
            
            if mismatch.any():
                count = mismatch.sum()
                issues.append(f"Total Single Room Patients calculation mismatch in {count} rows")
        
        # Check: Total Patients = Single + Double patients
        if all(col in df.columns for col in ['Total Single Room Patients', 'Double Room Patients', 'Total Patients for Day']):
            calculated_total = df['Total Single Room Patients'] + df['Double Room Patients']
            mismatch = (calculated_total != df['Total Patients for Day'])
            
            if mismatch.any():
                count = mismatch.sum()
                issues.append(f"Total Patients calculation mismatch in {count} rows")
        
        # Check: Total patients <= Total beds - Closed beds
        if all(col in df.columns for col in ['Total Patients for Day', 'Closed Rooms']):
            available_beds = TOTAL_BEDS - (df['Closed Rooms'] * 2)  # Assuming closed rooms are doubles
            over_capacity = df['Total Patients for Day'] > available_beds
            
            if over_capacity.any():
                count = over_capacity.sum()
                issues.append(f"Total patients exceed available capacity in {count} rows")
                
        return issues
    
    def _validate_temporal_consistency(self, df: pd.DataFrame) -> List[str]:
        """Check temporal consistency of dates."""
        warnings = []
        
        if 'Date' not in df.columns:
            return warnings
            
        # Check for gaps in dates
        df_sorted = df.sort_values('Date')
        date_diff = df_sorted['Date'].diff()
        
        # Find gaps larger than 1 day
        gaps = date_diff[date_diff > pd.Timedelta(days=1)]
        if len(gaps) > 0:
            warnings.append(f"Found {len(gaps)} gaps in date sequence")
            
        # Check for dates in the future
        future_dates = df['Date'] > pd.Timestamp.now()
        if future_dates.any():
            count = future_dates.sum()
            warnings.append(f"Found {count} dates in the future")
            
        return warnings
    
    def _check_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Check for duplicate dates."""
        issues = []
        
        if 'Date' in df.columns:
            duplicates = df['Date'].duplicated()
            if duplicates.any():
                count = duplicates.sum()
                issues.append(f"Found {count} duplicate dates")
                
        return issues
    
    def _calculate_validation_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate validation statistics."""
        stats = {
            'total_rows': len(df),
            'date_range': None,
            'missing_values': {},
            'zero_patient_days': 0,
            'max_capacity_days': 0
        }
        
        # Date range
        if 'Date' in df.columns:
            stats['date_range'] = f"{df['Date'].min()} to {df['Date'].max()}"
        
        # Missing values
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                stats['missing_values'][col] = null_count
        
        # Special cases
        if 'Total Patients for Day' in df.columns:
            stats['zero_patient_days'] = (df['Total Patients for Day'] == 0).sum()
            stats['max_capacity_days'] = (df['Total Patients for Day'] >= TOTAL_BEDS).sum()
            
        return stats
    
    def validate_processed_sheet(
        self, 
        df: pd.DataFrame, 
        sheet_name: str, 
        year: str
    ) -> bool:
        """
        Validate a processed monthly sheet.
        
        Args:
            df: Processed DataFrame
            sheet_name: Month name
            year: Year of data
            
        Returns:
            True if valid, False otherwise
        """
        if df.empty:
            logger.error(f"Empty dataframe for {sheet_name} {year}")
            return False
            
        # Check minimum required columns
        required = ['Date', 'Total Single Room Patients', 'Double Room Patients']
        missing = [col for col in required if col not in df.columns]
        
        if missing:
            logger.error(f"Missing columns in {sheet_name} {year}: {missing}")
            return False
            
        # Check date consistency
        if 'Date' in df.columns:
            # All dates should be in the correct month/year
            months = df['Date'].dt.month.unique()
            years = df['Date'].dt.year.unique()
            
            if len(months) > 1 or len(years) > 1:
                logger.warning(f"Multiple months/years in {sheet_name} {year}")
                return False
                
        return True
    
    def generate_validation_report(self) -> pd.DataFrame:
        """
        Generate a report of all validation runs.
        
        Returns:
            DataFrame with validation history
        """
        if not self.validation_history:
            return pd.DataFrame()
            
        report_data = []
        
        for i, result in enumerate(self.validation_history):
            report_data.append({
                'run_number': i + 1,
                'timestamp': result['timestamp'],
                'is_valid': result['is_valid'],
                'issue_count': len(result['issues']),
                'warning_count': len(result['warnings']),
                'total_rows': result['stats']['total_rows'],
                'date_range': result['stats']['date_range']
            })
            
        return pd.DataFrame(report_data)