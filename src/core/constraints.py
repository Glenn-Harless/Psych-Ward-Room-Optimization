"""
Constraint definitions for the ward optimization problem.

This module provides classes and functions to build constraints
for the linear programming optimization model.
"""

import pulp
from typing import List, Tuple

from ..utils.constants import TOTAL_BEDS, DOUBLE_ROOM_CAPACITY
from ..utils.logger import get_logger


logger = get_logger(__name__)


class ConstraintBuilder:
    """
    Builds constraints for the ward optimization problem.
    
    This class encapsulates the logic for creating various constraints
    needed in the linear programming model.
    """
    
    def __init__(self, problem: pulp.LpProblem):
        """
        Initialize the constraint builder.
        
        Args:
            problem: The PuLP problem instance to add constraints to
        """
        self.problem = problem
        self.constraint_count = 0
        
    def add_bed_capacity_constraint(self, D: pulp.LpVariable, S: pulp.LpVariable):
        """
        Add the total bed capacity constraint.
        
        The constraint ensures that the total number of beds
        (2 * double_rooms + single_rooms) equals the ward capacity.
        
        Args:
            D: Double rooms variable
            S: Single rooms variable
        """
        constraint_name = "TotalBeds"
        self.problem += (
            DOUBLE_ROOM_CAPACITY * D + S == TOTAL_BEDS,
            constraint_name
        )
        self.constraint_count += 1
        logger.debug(f"Added constraint: {constraint_name}")
        
    def add_daily_constraints(
        self,
        day_index: int,
        S: pulp.LpVariable,
        D: pulp.LpVariable,
        single_rooms_needed: int,
        double_rooms_needed: int
    ) -> Tuple[pulp.LpVariable, pulp.LpVariable]:
        """
        Add constraints for a specific day's patient allocation.
        
        Creates variables and constraints to track:
        - Singles in doubles (wasted beds)
        - Doubles in singles (wasted potential)
        
        Args:
            day_index: Index of the day in the dataset
            S: Single rooms variable
            D: Double rooms variable
            single_rooms_needed: Number of single room patients on this day
            double_rooms_needed: Number of double room patients on this day
            
        Returns:
            Tuple of (single_in_double_var, double_in_single_var)
        """
        # Create variables for this day's inefficiencies
        single_in_double = pulp.LpVariable(
            f'single_in_double_{day_index}',
            lowBound=0,
            cat='Integer'
        )
        double_in_single = pulp.LpVariable(
            f'double_in_single_{day_index}',
            lowBound=0,
            cat='Integer'
        )
        
        # Constraint: Singles in doubles occurs when single rooms are insufficient
        self.problem += (
            single_in_double >= single_rooms_needed - S,
            f"SingleInDouble_{day_index}"
        )
        self.problem += (
            single_in_double <= single_rooms_needed,
            f"SingleInDoubleCap_{day_index}"
        )
        
        # Constraint: Doubles in singles occurs when double rooms are insufficient
        self.problem += (
            double_in_single >= double_rooms_needed - DOUBLE_ROOM_CAPACITY * D,
            f"DoubleInSingle_{day_index}"
        )
        self.problem += (
            double_in_single <= double_rooms_needed,
            f"DoubleInSingleCap_{day_index}"
        )
        
        self.constraint_count += 4
        
        return single_in_double, double_in_single
    
    def add_accumulation_constraints(
        self,
        total_wasted_beds: pulp.LpVariable,
        total_wasted_potential: pulp.LpVariable,
        single_in_double_vars: List[pulp.LpVariable],
        double_in_single_vars: List[pulp.LpVariable]
    ):
        """
        Add constraints to accumulate total inefficiencies.
        
        Args:
            total_wasted_beds: Variable for total wasted beds
            total_wasted_potential: Variable for total wasted potential
            single_in_double_vars: List of daily single-in-double variables
            double_in_single_vars: List of daily double-in-single variables
        """
        # Total wasted beds is the sum of all singles in doubles
        self.problem += (
            total_wasted_beds == pulp.lpSum(single_in_double_vars),
            "TotalWastedBeds"
        )
        
        # Total wasted potential is the sum of all doubles in singles
        self.problem += (
            total_wasted_potential == pulp.lpSum(double_in_single_vars),
            "TotalWastedPotential"
        )
        
        self.constraint_count += 2
        logger.info(f"Added {self.constraint_count} constraints to the problem")
        
    def add_custom_constraint(
        self,
        constraint_expr: pulp.LpConstraint,
        name: str
    ):
        """
        Add a custom constraint to the problem.
        
        Args:
            constraint_expr: The constraint expression
            name: Name for the constraint
        """
        self.problem += (constraint_expr, name)
        self.constraint_count += 1
        logger.debug(f"Added custom constraint: {name}")
        
    def add_minimum_rooms_constraint(
        self,
        D: pulp.LpVariable,
        S: pulp.LpVariable,
        min_double: int = 0,
        min_single: int = 0
    ):
        """
        Add constraints for minimum number of each room type.
        
        Args:
            D: Double rooms variable
            S: Single rooms variable
            min_double: Minimum number of double rooms
            min_single: Minimum number of single rooms
        """
        if min_double > 0:
            self.problem += (D >= min_double, "MinDoubleRooms")
            self.constraint_count += 1
            
        if min_single > 0:
            self.problem += (S >= min_single, "MinSingleRooms")
            self.constraint_count += 1
            
    def get_constraint_summary(self) -> dict:
        """
        Get a summary of constraints added to the problem.
        
        Returns:
            Dictionary with constraint statistics
        """
        return {
            'total_constraints': self.constraint_count,
            'problem_constraints': len(self.problem.constraints),
            'problem_variables': len(self.problem.variables())
        }