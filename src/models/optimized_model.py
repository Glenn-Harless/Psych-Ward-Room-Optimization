"""
Optimized model implementation.

This model represents the optimized ward configuration determined
by linear programming analysis.
"""

import pandas as pd
from typing import Dict, Optional

from .base_model import BaseModel
from ..utils.logger import get_logger
from ..utils.constants import (
    TOTAL_SINGLE_PATIENTS_COLUMN, DOUBLE_ROOM_PATIENTS_COLUMN,
    DEFAULT_SINGLE_ROOMS, DEFAULT_DOUBLE_ROOMS, DOUBLE_ROOM_CAPACITY
)


logger = get_logger(__name__)


class OptimizedModel(BaseModel):
    """
    Evaluates the optimized ward configuration.
    
    The default configuration (10 single, 8 double) was determined
    by linear programming to minimize total waste across historical data.
    """
    
    def __init__(self, single_rooms: Optional[int] = None, 
                 double_rooms: Optional[int] = None):
        """
        Initialize the optimized model.
        
        Args:
            single_rooms: Number of single rooms (default from config)
            double_rooms: Number of double rooms (default from config)
        """
        # Use provided values or defaults from config
        single_rooms = single_rooms or DEFAULT_SINGLE_ROOMS
        double_rooms = double_rooms or DEFAULT_DOUBLE_ROOMS
        
        super().__init__(
            single_rooms=single_rooms,
            double_rooms=double_rooms,
            name=f"Optimized Model ({single_rooms}S/{double_rooms}D)"
        )
        
    def evaluate_day(self, row: pd.Series) -> Dict[str, float]:
        """
        Evaluate room allocation for a single day in the optimized model.
        
        Calculates:
        - Wasted beds: When single-room patients exceed single room capacity
        - Wasted potential: When double-room patients exceed double room capacity
        
        Args:
            row: DataFrame row containing daily census data
            
        Returns:
            Dictionary with:
                - Wasted_Beds: Singles in doubles beyond single room capacity
                - Wasted_Potential: Doubles in singles beyond double room capacity
        """
        single_room_patients = int(row[TOTAL_SINGLE_PATIENTS_COLUMN])
        double_room_patients = int(row[DOUBLE_ROOM_PATIENTS_COLUMN])
        
        # Calculate wasted beds (single room patients in double rooms)
        # This happens when single patients exceed single room capacity
        wasted_beds = max(0, single_room_patients - self.single_rooms)
        
        # Calculate wasted potential (double room patients in single rooms)
        # This happens when double patients exceed double room capacity
        double_room_capacity = self.double_rooms * DOUBLE_ROOM_CAPACITY
        wasted_potential = max(0, double_room_patients - double_room_capacity)
        
        if wasted_beds > 0 or wasted_potential > 0:
            logger.debug(
                f"Date {row['Date']}: "
                f"Singles={single_room_patients} (capacity={self.single_rooms}), "
                f"Doubles={double_room_patients} (capacity={double_room_capacity}), "
                f"Wasted beds={wasted_beds}, Wasted potential={wasted_potential}"
            )
        
        return {
            'Wasted_Beds': wasted_beds,
            'Wasted_Potential': wasted_potential
        }


class CustomModel(OptimizedModel):
    """
    A custom configuration model for testing different room allocations.
    
    Extends OptimizedModel to allow easy testing of various configurations.
    """
    
    def __init__(self, single_rooms: int, double_rooms: int, name: Optional[str] = None):
        """
        Initialize a custom model configuration.
        
        Args:
            single_rooms: Number of single rooms
            double_rooms: Number of double rooms
            name: Optional custom name for the model
        """
        super().__init__(single_rooms, double_rooms)
        if name:
            self.name = name