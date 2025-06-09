"""
File I/O operations utility module.

Provides centralized file handling with proper error handling
and logging for the Psych Ward Room Optimization system.
"""

import os
import pandas as pd
from pathlib import Path
import json
import yaml
from typing import Union, Optional, Dict, Any

from .logger import get_logger
from .constants import config


logger = get_logger(__name__)


class FileHandler:
    """Handles all file I/O operations with proper error handling."""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path
            
        Returns:
            Path object for the directory
        """
        path = Path(path)
        if path.suffix:  # If it's a file path, get its parent
            path = path.parent
            
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
        return path
    
    @staticmethod
    def read_csv(filepath: Union[str, Path], **kwargs) -> pd.DataFrame:
        """
        Read a CSV file with error handling.
        
        Args:
            filepath: Path to CSV file
            **kwargs: Additional arguments for pd.read_csv
            
        Returns:
            DataFrame with the CSV data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: For other reading errors
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"CSV file not found: {filepath}")
            raise FileNotFoundError(f"CSV file not found: {filepath}")
            
        try:
            logger.info(f"Reading CSV file: {filepath}")
            df = pd.read_csv(filepath, **kwargs)
            logger.info(f"Successfully read {len(df)} rows from {filepath}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def write_csv(df: pd.DataFrame, filepath: Union[str, Path], **kwargs):
        """
        Write a DataFrame to CSV with error handling.
        
        Args:
            df: DataFrame to write
            filepath: Output file path
            **kwargs: Additional arguments for df.to_csv
        """
        filepath = Path(filepath)
        FileHandler.ensure_directory(filepath)
        
        # Set default index=False if not specified
        if 'index' not in kwargs:
            kwargs['index'] = config.DATA_PROCESSING.get('csv_index', False)
            
        try:
            logger.info(f"Writing {len(df)} rows to CSV: {filepath}")
            df.to_csv(filepath, **kwargs)
            logger.info(f"Successfully wrote CSV to {filepath}")
        except Exception as e:
            logger.error(f"Error writing CSV file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def read_excel(filepath: Union[str, Path], **kwargs) -> Union[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Read an Excel file with error handling.
        
        Args:
            filepath: Path to Excel file
            **kwargs: Additional arguments for pd.read_excel
            
        Returns:
            DataFrame or dict of DataFrames (if sheet_name=None)
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"Excel file not found: {filepath}")
            raise FileNotFoundError(f"Excel file not found: {filepath}")
            
        try:
            logger.info(f"Reading Excel file: {filepath}")
            data = pd.read_excel(filepath, **kwargs)
            
            if isinstance(data, dict):
                logger.info(f"Successfully read {len(data)} sheets from {filepath}")
            else:
                logger.info(f"Successfully read {len(data)} rows from {filepath}")
                
            return data
        except Exception as e:
            logger.error(f"Error reading Excel file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def read_json(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Read a JSON file with error handling.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Parsed JSON data
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"JSON file not found: {filepath}")
            raise FileNotFoundError(f"JSON file not found: {filepath}")
            
        try:
            logger.info(f"Reading JSON file: {filepath}")
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Successfully read JSON from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def write_json(data: Dict[str, Any], filepath: Union[str, Path], indent: int = 2):
        """
        Write data to JSON file with error handling.
        
        Args:
            data: Data to write
            filepath: Output file path
            indent: JSON indentation level
        """
        filepath = Path(filepath)
        FileHandler.ensure_directory(filepath)
        
        try:
            logger.info(f"Writing JSON to: {filepath}")
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=indent)
            logger.info(f"Successfully wrote JSON to {filepath}")
        except Exception as e:
            logger.error(f"Error writing JSON file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def read_yaml(filepath: Union[str, Path]) -> Dict[str, Any]:
        """
        Read a YAML file with error handling.
        
        Args:
            filepath: Path to YAML file
            
        Returns:
            Parsed YAML data
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"YAML file not found: {filepath}")
            raise FileNotFoundError(f"YAML file not found: {filepath}")
            
        try:
            logger.info(f"Reading YAML file: {filepath}")
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
            logger.info(f"Successfully read YAML from {filepath}")
            return data
        except Exception as e:
            logger.error(f"Error reading YAML file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def write_yaml(data: Dict[str, Any], filepath: Union[str, Path]):
        """
        Write data to YAML file with error handling.
        
        Args:
            data: Data to write
            filepath: Output file path
        """
        filepath = Path(filepath)
        FileHandler.ensure_directory(filepath)
        
        try:
            logger.info(f"Writing YAML to: {filepath}")
            with open(filepath, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Successfully wrote YAML to {filepath}")
        except Exception as e:
            logger.error(f"Error writing YAML file {filepath}: {str(e)}")
            raise
    
    @staticmethod
    def copy_file(source: Union[str, Path], destination: Union[str, Path]):
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
        """
        import shutil
        
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            raise FileNotFoundError(f"Source file not found: {source}")
            
        FileHandler.ensure_directory(destination)
        
        try:
            logger.info(f"Copying {source} to {destination}")
            shutil.copy2(source, destination)
            logger.info(f"Successfully copied file")
        except Exception as e:
            logger.error(f"Error copying file: {str(e)}")
            raise
    
    @staticmethod
    def move_file(source: Union[str, Path], destination: Union[str, Path]):
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
        """
        import shutil
        
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            raise FileNotFoundError(f"Source file not found: {source}")
            
        FileHandler.ensure_directory(destination)
        
        try:
            logger.info(f"Moving {source} to {destination}")
            shutil.move(str(source), str(destination))
            logger.info(f"Successfully moved file")
        except Exception as e:
            logger.error(f"Error moving file: {str(e)}")
            raise
    
    @staticmethod
    def file_exists(filepath: Union[str, Path]) -> bool:
        """
        Check if a file exists.
        
        Args:
            filepath: File path to check
            
        Returns:
            True if file exists, False otherwise
        """
        return Path(filepath).exists()
    
    @staticmethod
    def get_file_size(filepath: Union[str, Path]) -> int:
        """
        Get file size in bytes.
        
        Args:
            filepath: File path
            
        Returns:
            File size in bytes
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            raise FileNotFoundError(f"File not found: {filepath}")
            
        return filepath.stat().st_size
    
    @staticmethod
    def list_files(directory: Union[str, Path], pattern: str = "*") -> list:
        """
        List files in a directory matching a pattern.
        
        Args:
            directory: Directory path
            pattern: Glob pattern (default: "*")
            
        Returns:
            List of file paths
        """
        directory = Path(directory)
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            raise FileNotFoundError(f"Directory not found: {directory}")
            
        files = list(directory.glob(pattern))
        logger.debug(f"Found {len(files)} files matching '{pattern}' in {directory}")
        return files