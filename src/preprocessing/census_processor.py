"""
Main census data preprocessing module.

Orchestrates the preprocessing pipeline for monthly census Excel files,
converting them into standardized CSV format for analysis.
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Union
import re

from ..utils.logger import get_logger, log_execution_time
from ..utils.constants import config
from ..utils.file_handler import FileHandler
from .excel_reader import ExcelReader
from .data_validator import DataValidator


logger = get_logger(__name__)


class CensusProcessor:
    """
    Processes monthly census Excel files into standardized format.
    
    Handles data extraction, transformation, validation, and 
    consolidation of census data across multiple years.
    """
    
    def __init__(self):
        """Initialize the census processor."""
        self.excel_reader = ExcelReader()
        self.validator = DataValidator()
        self.processed_data = []
        
    @log_execution_time
    def process_files(
        self, 
        file_paths: List[Union[str, Path]],
        output_path: Optional[Union[str, Path]] = None
    ) -> pd.DataFrame:
        """
        Process multiple census Excel files and combine into single dataset.
        
        Args:
            file_paths: List of paths to Excel files
            output_path: Optional output path for processed data
            
        Returns:
            Combined DataFrame with all processed data
        """
        logger.info(f"Processing {len(file_paths)} census files")
        
        all_data_frames = []
        
        for file_path in file_paths:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue
                
            try:
                # Extract year from filename
                year = self._extract_year_from_filename(file_path)
                logger.info(f"Processing {file_path.name} for year {year}")
                
                # Read and process Excel file
                sheets_data = self.excel_reader.read_monthly_sheets(file_path)
                
                for sheet_name, df in sheets_data.items():
                    if self._is_valid_month_sheet(sheet_name):
                        processed_df = self._process_sheet(df, sheet_name, year)
                        
                        if processed_df is not None and not processed_df.empty:
                            all_data_frames.append(processed_df)
                            logger.debug(f"Processed {len(processed_df)} rows from {sheet_name} {year}")
                            
            except Exception as e:
                logger.error(f"Error processing {file_path}: {str(e)}")
                continue
        
        if not all_data_frames:
            raise ValueError("No data was successfully processed from input files")
        
        # Combine all dataframes
        final_df = pd.concat(all_data_frames, ignore_index=True)
        
        # Sort by date
        final_df.sort_values('Date', inplace=True)
        
        # Validate combined data
        validation_results = self.validator.validate_dataframe(final_df)
        if not validation_results['is_valid']:
            logger.warning(f"Data validation issues: {validation_results['issues']}")
        
        # Save if output path provided
        if output_path:
            FileHandler.write_csv(final_df, output_path)
            logger.info(f"Saved processed data to {output_path}")
        
        self.processed_data = final_df
        logger.info(f"Successfully processed {len(final_df)} total records")
        
        return final_df
    
    def _process_sheet(self, df: pd.DataFrame, sheet_name: str, year: str) -> Optional[pd.DataFrame]:
        """
        Process a single month's sheet of census data.
        
        Args:
            df: Raw DataFrame from Excel sheet
            sheet_name: Name of the sheet (month abbreviation)
            year: Year of the data
            
        Returns:
            Processed DataFrame or None if processing fails
        """
        try:
            # Reset index to ensure clean processing
            df = df.reset_index(drop=True)
            
            # Remove rows after 'Monthly Totals' if present
            df = self._truncate_at_monthly_totals(df)
            
            # Apply column mapping
            df = self._apply_column_mapping(df)
            
            # Ensure all required columns exist
            df = self._ensure_required_columns(df)
            
            # Calculate patient counts
            df = self._calculate_patient_counts(df)
            
            # Generate dates
            df = self._generate_dates(df, sheet_name, year)
            
            # Select and order final columns
            df = self._select_final_columns(df)
            
            # Validate processed data
            if not self.validator.validate_processed_sheet(df, sheet_name, year):
                logger.warning(f"Validation failed for {sheet_name} {year}")
                return None
                
            return df
            
        except Exception as e:
            logger.error(f"Error processing sheet {sheet_name} {year}: {str(e)}")
            return None
    
    def _truncate_at_monthly_totals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove rows after 'Monthly Totals' marker."""
        if 'Monthly Totals' in df.iloc[:, 0].values:
            cut_off_index = df[df.iloc[:, 0] == 'Monthly Totals'].index[0]
            df = df.iloc[:cut_off_index]
        return df
    
    def _apply_column_mapping(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply standardized column names."""
        column_mapping = {
            'Unnamed: 1': 'Day',
            'Census': 'Total Census Rooms',
            'Held Beds': 'Single Room E',
            'Held Due To Covid Swab/Quarantine': 'Single Room F',
            'Closed Beds': 'Closed Rooms'
        }
        return df.rename(columns=column_mapping)
    
    def _ensure_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required columns exist with default values."""
        required_columns = [
            'Day', 'Double Room', 'Single Room E', 
            'Single Room F', 'Closed Rooms', 'Total Census Rooms'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = 0
                logger.debug(f"Added missing column '{col}' with default value 0")
                
        return df
    
    def _calculate_patient_counts(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate single and double room patient counts."""
        # Convert to float for calculations
        df['Single Room E'] = pd.to_numeric(df['Single Room E'], errors='coerce').fillna(0)
        df['Single Room F'] = pd.to_numeric(df['Single Room F'], errors='coerce').fillna(0)
        df['Total Census Rooms'] = pd.to_numeric(df['Total Census Rooms'], errors='coerce').fillna(0)
        
        # Calculate total single room patients
        df['Total Single Room Patients'] = df['Single Room E'] + df['Single Room F']
        
        # Cap single room patients at total census
        df['Total Single Room Patients'] = df[['Total Single Room Patients', 'Total Census Rooms']].min(axis=1)
        
        # Calculate double room patients
        df['Double Room Patients'] = df['Total Census Rooms'] - df['Total Single Room Patients']
        df['Double Room Patients'] = df['Double Room Patients'].clip(lower=0)
        
        # Calculate total patients
        df['Total Patients for Day'] = df['Total Single Room Patients'] + df['Double Room Patients']
        
        return df
    
    def _generate_dates(self, df: pd.DataFrame, month: str, year: str) -> pd.DataFrame:
        """Generate exact dates for each row."""
        # Use index + 1 as day of month
        df['Day'] = df.index + 1
        
        # Create date string and parse
        date_str = df['Day'].astype(str) + '-' + month + '-' + year
        df['Date'] = pd.to_datetime(date_str, format='%d-%b-%Y', errors='coerce')
        
        # Remove any rows with invalid dates
        df = df.dropna(subset=['Date'])
        
        return df
    
    def _select_final_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Select and order final columns for output."""
        final_columns = [
            'Date', 'Day', 'Single Room E', 'Single Room F',
            'Total Single Room Patients', 'Double Room Patients',
            'Total Patients for Day', 'Closed Rooms', 'Total Census Rooms'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in final_columns if col in df.columns]
        
        return df[available_columns]
    
    def _extract_year_from_filename(self, file_path: Path) -> str:
        """Extract year from filename like 'Monthly Census 2022.xlsx'."""
        # Try to find 4-digit year in filename
        year_match = re.search(r'(\d{4})', file_path.stem)
        
        if year_match:
            return year_match.group(1)
        else:
            raise ValueError(f"Could not extract year from filename: {file_path.name}")
    
    def _is_valid_month_sheet(self, sheet_name: str) -> bool:
        """Check if sheet name is a valid 3-letter month abbreviation."""
        valid_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        return sheet_name in valid_months
    
    def get_summary_statistics(self) -> Dict[str, any]:
        """Get summary statistics of processed data."""
        if self.processed_data is None or self.processed_data.empty:
            return {}
        
        df = self.processed_data
        
        return {
            'total_records': len(df),
            'date_range': f"{df['Date'].min()} to {df['Date'].max()}",
            'years_covered': sorted(df['Date'].dt.year.unique().tolist()),
            'avg_single_patients': df['Total Single Room Patients'].mean(),
            'avg_double_patients': df['Double Room Patients'].mean(),
            'avg_total_patients': df['Total Patients for Day'].mean(),
            'max_single_patients': df['Total Single Room Patients'].max(),
            'max_double_patients': df['Double Room Patients'].max(),
            'max_total_patients': df['Total Patients for Day'].max(),
            'total_closed_room_days': (df['Closed Rooms'] > 0).sum()
        }