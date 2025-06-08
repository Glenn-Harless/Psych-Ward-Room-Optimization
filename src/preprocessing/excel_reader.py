"""
Excel file reading and parsing module.

Handles the complexities of reading monthly census Excel files
with various formats and structures.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
import warnings

from ..utils.logger import get_logger


logger = get_logger(__name__)


class ExcelReader:
    """
    Specialized reader for monthly census Excel files.
    
    Handles various Excel formats, sheet structures, and
    common data quality issues in census files.
    """
    
    def __init__(self, skiprows: int = 4):
        """
        Initialize Excel reader.
        
        Args:
            skiprows: Number of header rows to skip (default 4)
        """
        self.skiprows = skiprows
        
    def read_monthly_sheets(
        self, 
        file_path: Union[str, Path],
        sheet_filter: Optional[callable] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Read all monthly sheets from an Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_filter: Optional function to filter sheet names
            
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        file_path = Path(file_path)
        sheets_data = {}
        
        try:
            # Suppress Excel file warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning)
                
                # Read Excel file
                excel_file = pd.ExcelFile(file_path)
                logger.info(f"Reading Excel file: {file_path.name}")
                logger.debug(f"Found sheets: {excel_file.sheet_names}")
                
                for sheet_name in excel_file.sheet_names:
                    # Apply filter if provided
                    if sheet_filter and not sheet_filter(sheet_name):
                        logger.debug(f"Skipping sheet: {sheet_name}")
                        continue
                    
                    try:
                        # Read sheet with configured skip rows
                        df = pd.read_excel(
                            excel_file, 
                            sheet_name=sheet_name,
                            skiprows=self.skiprows
                        )
                        
                        # Basic validation
                        if df.empty:
                            logger.warning(f"Empty sheet: {sheet_name}")
                            continue
                            
                        sheets_data[sheet_name] = df
                        logger.debug(f"Read sheet '{sheet_name}' with {len(df)} rows")
                        
                    except Exception as e:
                        logger.error(f"Error reading sheet '{sheet_name}': {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            raise
            
        return sheets_data
    
    def read_single_sheet(
        self,
        file_path: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        **kwargs
    ) -> pd.DataFrame:
        """
        Read a single sheet from an Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name or index of sheet to read
            **kwargs: Additional arguments for pd.read_excel
            
        Returns:
            DataFrame with sheet data
        """
        file_path = Path(file_path)
        
        try:
            # Set default skiprows if not provided
            if 'skiprows' not in kwargs:
                kwargs['skiprows'] = self.skiprows
                
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            logger.info(f"Read sheet '{sheet_name}' from {file_path.name}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error reading sheet '{sheet_name}' from {file_path}: {str(e)}")
            raise
    
    def read_with_fallback(
        self,
        file_path: Union[str, Path],
        sheet_name: str,
        fallback_skiprows: List[int] = [0, 1, 2, 3, 4, 5]
    ) -> Optional[pd.DataFrame]:
        """
        Try reading with different skiprows values as fallback.
        
        Useful when Excel files have inconsistent header rows.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name to read
            fallback_skiprows: List of skiprows values to try
            
        Returns:
            DataFrame if successful, None otherwise
        """
        file_path = Path(file_path)
        
        for skiprows in fallback_skiprows:
            try:
                df = pd.read_excel(
                    file_path,
                    sheet_name=sheet_name,
                    skiprows=skiprows
                )
                
                # Check if we got valid data
                if not df.empty and len(df.columns) > 1:
                    logger.info(f"Successfully read with skiprows={skiprows}")
                    return df
                    
            except Exception:
                continue
                
        logger.error(f"Failed to read sheet '{sheet_name}' with any skiprows value")
        return None
    
    def detect_header_rows(
        self,
        file_path: Union[str, Path],
        sheet_name: Union[str, int] = 0,
        max_check_rows: int = 10
    ) -> int:
        """
        Auto-detect number of header rows to skip.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet to analyze
            max_check_rows: Maximum rows to check
            
        Returns:
            Detected number of header rows
        """
        try:
            # Read first rows without skipping
            df_test = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                nrows=max_check_rows
            )
            
            # Look for row that starts with numeric day values
            for i in range(len(df_test)):
                first_col = df_test.iloc[i, 0]
                second_col = df_test.iloc[i, 1] if len(df_test.columns) > 1 else None
                
                # Check if this looks like data row (numeric day)
                if pd.notna(second_col) and str(second_col).isdigit():
                    logger.info(f"Detected {i} header rows")
                    return i
                    
        except Exception as e:
            logger.warning(f"Error detecting header rows: {str(e)}")
            
        # Return default if detection fails
        return self.skiprows
    
    def read_census_file(
        self,
        file_path: Union[str, Path],
        year: Optional[int] = None
    ) -> Dict[str, pd.DataFrame]:
        """
        Read census file with year-specific handling.
        
        Args:
            file_path: Path to census Excel file
            year: Optional year for format-specific handling
            
        Returns:
            Dictionary of sheet name to DataFrame
        """
        file_path = Path(file_path)
        
        # Year-specific configurations
        year_configs = {
            2022: {'skiprows': 4},
            2023: {'skiprows': 4},
            2024: {'skiprows': 4}
        }
        
        # Use year-specific config if available
        if year and year in year_configs:
            self.skiprows = year_configs[year]['skiprows']
            logger.debug(f"Using year {year} config: skiprows={self.skiprows}")
        
        # Read monthly sheets (3-letter month names)
        def is_month_sheet(name):
            return len(name) == 3 and name.isalpha()
            
        return self.read_monthly_sheets(file_path, sheet_filter=is_month_sheet)
    
    @staticmethod
    def combine_excel_files(
        file_paths: List[Union[str, Path]],
        sheet_name: Union[str, int] = 0
    ) -> pd.DataFrame:
        """
        Combine data from multiple Excel files.
        
        Args:
            file_paths: List of Excel file paths
            sheet_name: Sheet to read from each file
            
        Returns:
            Combined DataFrame
        """
        all_data = []
        
        for file_path in file_paths:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                all_data.append(df)
                logger.debug(f"Read {len(df)} rows from {Path(file_path).name}")
            except Exception as e:
                logger.error(f"Error reading {file_path}: {str(e)}")
                continue
                
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined {len(all_data)} files into {len(combined)} total rows")
            return combined
        else:
            raise ValueError("No data could be read from provided files")