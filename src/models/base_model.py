"""
Abstract base class for room configuration models.

Provides a common interface for evaluating different room configurations
and calculating efficiency metrics.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Tuple, Optional, List

from ..utils.logger import get_logger
from ..utils.constants import (
    TOTAL_BEDS, DATE_COLUMN, SINGLE_ROOM_E_COLUMN,
    TOTAL_SINGLE_PATIENTS_COLUMN, DOUBLE_ROOM_PATIENTS_COLUMN,
    CLOSED_ROOMS_COLUMN, YEARS_TO_PROCESS
)
from ..utils.file_handler import FileHandler


logger = get_logger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for ward configuration models.
    
    Defines the interface that all configuration models must implement,
    ensuring consistent evaluation and reporting across different models.
    """
    
    def __init__(self, single_rooms: int, double_rooms: int, name: Optional[str] = None):
        """
        Initialize the model with room configuration.
        
        Args:
            single_rooms: Number of single rooms
            double_rooms: Number of double rooms
            name: Optional name for the model
        """
        self.single_rooms = single_rooms
        self.double_rooms = double_rooms
        self.name = name or self.__class__.__name__
        
        # Validate configuration
        total_beds = single_rooms + (2 * double_rooms)
        if total_beds != TOTAL_BEDS:
            raise ValueError(
                f"Invalid configuration: {total_beds} beds "
                f"(expected {TOTAL_BEDS})"
            )
            
        # Data and results storage
        self.data = None
        self.results_df = None
        self.metrics = None
        
        logger.info(
            f"Initialized {self.name} with {single_rooms} single rooms "
            f"and {double_rooms} double rooms"
        )
        
    @abstractmethod
    def evaluate_day(self, row: pd.Series) -> Dict[str, float]:
        """
        Evaluate room allocation for a single day.
        
        Must be implemented by subclasses to define how the specific
        configuration handles daily patient allocation.
        
        Args:
            row: DataFrame row containing daily census data
            
        Returns:
            Dictionary with evaluation metrics for the day
        """
        pass
        
    def load_data(self, data_path: str):
        """
        Load census data for evaluation.
        
        Args:
            data_path: Path to census data CSV file
        """
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        self.data = FileHandler.read_csv(data_path)
        
        # Process dates
        self.data[DATE_COLUMN] = pd.to_datetime(self.data[DATE_COLUMN])
        
        # Filter for valid data
        self.data.dropna(subset=[SINGLE_ROOM_E_COLUMN], inplace=True)
        
        # Filter for years to process
        self.data = self.data[
            self.data[DATE_COLUMN].dt.year.isin(YEARS_TO_PROCESS)
        ]
        
        logger.info(f"Loaded {len(self.data)} days of data")
        
    def evaluate(self, data_path: Optional[str] = None) -> pd.DataFrame:
        """
        Evaluate the model configuration against census data.
        
        Args:
            data_path: Optional path to data (uses loaded data if None)
            
        Returns:
            DataFrame with daily evaluation results
        """
        if data_path:
            self.load_data(data_path)
        elif self.data is None:
            raise ValueError("No data loaded. Provide data_path or call load_data() first.")
            
        results = []
        
        for _, row in self.data.iterrows():
            # Get base information
            day_result = {
                'Date': row[DATE_COLUMN],
                'Total_Single_Patients': row[TOTAL_SINGLE_PATIENTS_COLUMN],
                'Double_Room_Patients': row[DOUBLE_ROOM_PATIENTS_COLUMN],
                'Closed_Rooms': row.get(CLOSED_ROOMS_COLUMN, 0)
            }
            
            # Evaluate day using subclass implementation
            evaluation = self.evaluate_day(row)
            day_result.update(evaluation)
            
            # Calculate available beds
            closed_beds = day_result.get('Closed_Rooms', 0)
            day_result['Available_Beds'] = TOTAL_BEDS - closed_beds
            
            # Calculate efficiency
            available_beds = day_result['Available_Beds']
            wasted_beds = day_result.get('Wasted_Beds', 0)
            wasted_potential = day_result.get('Wasted_Potential', 0)
            
            if available_beds > 0:
                day_result['Efficiency'] = (
                    (available_beds - wasted_beds - wasted_potential) / available_beds
                ) * 100
            else:
                day_result['Efficiency'] = 0
                
            results.append(day_result)
            
        self.results_df = pd.DataFrame(results)
        self._calculate_metrics()
        
        return self.results_df
        
    def _calculate_metrics(self):
        """Calculate summary metrics from evaluation results."""
        if self.results_df is None:
            return
            
        self.metrics = {
            'model_name': self.name,
            'single_rooms': self.single_rooms,
            'double_rooms': self.double_rooms,
            'total_days': len(self.results_df),
            'total_wasted_beds': self.results_df['Wasted_Beds'].sum(),
            'total_wasted_potential': self.results_df['Wasted_Potential'].sum(),
            'avg_efficiency': self.results_df['Efficiency'].mean(),
            'min_efficiency': self.results_df['Efficiency'].min(),
            'max_efficiency': self.results_df['Efficiency'].max(),
            'days_with_waste': (self.results_df['Wasted_Beds'] > 0).sum(),
            'days_with_wasted_potential': (self.results_df['Wasted_Potential'] > 0).sum()
        }
        
        logger.info(f"Calculated metrics for {self.name}:")
        logger.info(f"  Average efficiency: {self.metrics['avg_efficiency']:.2f}%")
        logger.info(f"  Total wasted beds: {self.metrics['total_wasted_beds']}")
        logger.info(f"  Total wasted potential: {self.metrics['total_wasted_potential']}")
        
    def get_metrics(self) -> Dict[str, float]:
        """
        Get summary metrics for the model evaluation.
        
        Returns:
            Dictionary of metrics
        """
        if self.metrics is None:
            raise ValueError("No metrics available. Run evaluate() first.")
        return self.metrics
        
    def save_results(self, output_path: str):
        """
        Save evaluation results to CSV file.
        
        Args:
            output_path: Path for output CSV file
        """
        if self.results_df is None:
            raise ValueError("No results to save. Run evaluate() first.")
            
        FileHandler.write_csv(self.results_df, output_path)
        logger.info(f"Saved results to {output_path}")
        
    def get_configuration(self) -> Dict[str, int]:
        """
        Get the room configuration of this model.
        
        Returns:
            Dictionary with room configuration
        """
        return {
            'single_rooms': self.single_rooms,
            'double_rooms': self.double_rooms,
            'total_beds': self.single_rooms + (2 * self.double_rooms)
        }
        
    def compare_with(self, other_model: 'BaseModel') -> Dict[str, float]:
        """
        Compare this model's metrics with another model.
        
        Args:
            other_model: Another model instance to compare with
            
        Returns:
            Dictionary with comparison metrics
        """
        if self.metrics is None or other_model.metrics is None:
            raise ValueError("Both models must be evaluated before comparison")
            
        comparison = {
            'efficiency_improvement': (
                self.metrics['avg_efficiency'] - other_model.metrics['avg_efficiency']
            ),
            'wasted_beds_reduction': (
                other_model.metrics['total_wasted_beds'] - self.metrics['total_wasted_beds']
            ),
            'wasted_potential_reduction': (
                other_model.metrics['total_wasted_potential'] - 
                self.metrics['total_wasted_potential']
            ),
            'total_waste_reduction': (
                (other_model.metrics['total_wasted_beds'] + 
                 other_model.metrics['total_wasted_potential']) -
                (self.metrics['total_wasted_beds'] + 
                 self.metrics['total_wasted_potential'])
            )
        }
        
        return comparison