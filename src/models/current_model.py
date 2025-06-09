"""
Current model implementation (all double rooms).

This model represents the current ward configuration where all
13 rooms are configured as double occupancy rooms.
"""

import pandas as pd
from typing import Dict

from .base_model import BaseModel
from ..utils.logger import get_logger
from ..utils.constants import TOTAL_SINGLE_PATIENTS_COLUMN


logger = get_logger(__name__)


class CurrentModel(BaseModel):
    """
    Evaluates the current ward configuration with all double rooms.
    
    In this configuration:
    - 0 single rooms
    - 13 double rooms (26 beds total)
    - All single-room patients must occupy double rooms, wasting one bed each
    - No wasted potential since all rooms can accommodate double occupancy
    """
    
    def __init__(self):
        """Initialize the current model with 13 double rooms."""
        super().__init__(
            single_rooms=0,
            double_rooms=13,
            name="Current Model (All Double Rooms)"
        )
        
    def evaluate_day(self, row: pd.Series) -> Dict[str, float]:
        """
        Evaluate room allocation for a single day in the current model.
        
        In the current configuration:
        - Every single-room patient wastes one bed (occupies double room alone)
        - No wasted potential (all rooms are double, so no undersized rooms)
        
        Args:
            row: DataFrame row containing daily census data
            
        Returns:
            Dictionary with:
                - Wasted_Beds: Number of beds wasted by singles in doubles
                - Wasted_Potential: Always 0 for current model
        """
        # In current model, all single patients waste a bed
        wasted_beds = int(row[TOTAL_SINGLE_PATIENTS_COLUMN])
        
        # No wasted potential in current model (all rooms are double)
        wasted_potential = 0
        
        logger.debug(
            f"Date {row['Date']}: {wasted_beds} single patients "
            f"in double rooms (wasted beds)"
        )
        
        return {
            'Wasted_Beds': wasted_beds,
            'Wasted_Potential': wasted_potential
        }