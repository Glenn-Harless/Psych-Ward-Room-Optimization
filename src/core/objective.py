"""
Objective function implementations for ward optimization.

This module provides different objective functions that can be used
in the optimization problem, allowing for flexible optimization goals.
"""

import pulp
from typing import List, Dict, Any

from ..utils.logger import get_logger


logger = get_logger(__name__)


class ObjectiveBuilder:
    """
    Builds objective functions for the optimization problem.
    
    Supports various optimization goals including minimizing waste,
    maximizing efficiency, or custom weighted objectives.
    """
    
    def __init__(self, problem: pulp.LpProblem):
        """
        Initialize the objective builder.
        
        Args:
            problem: The PuLP problem instance
        """
        self.problem = problem
        self.objective_type = None
        
    def set_minimize_waste_objective(
        self,
        total_wasted_beds: pulp.LpVariable,
        total_wasted_potential: pulp.LpVariable,
        bed_weight: float = 1.0,
        potential_weight: float = 1.0
    ):
        """
        Set objective to minimize total waste (beds + potential).
        
        This is the primary objective function that minimizes both
        wasted beds (singles in doubles) and wasted potential (doubles in singles).
        
        Args:
            total_wasted_beds: Variable for total wasted beds
            total_wasted_potential: Variable for total wasted potential
            bed_weight: Weight for wasted beds (default 1.0)
            potential_weight: Weight for wasted potential (default 1.0)
        """
        objective = (
            bed_weight * total_wasted_beds +
            potential_weight * total_wasted_potential
        )
        
        self.problem += objective, "MinimizeWastedSpace"
        self.objective_type = "minimize_waste"
        
        logger.info(
            f"Set objective: Minimize waste with weights "
            f"(beds={bed_weight}, potential={potential_weight})"
        )
        
    def set_minimize_wasted_beds_only(
        self,
        total_wasted_beds: pulp.LpVariable
    ):
        """
        Set objective to minimize only wasted beds.
        
        This objective focuses solely on minimizing singles in doubles,
        ignoring wasted potential.
        
        Args:
            total_wasted_beds: Variable for total wasted beds
        """
        self.problem += total_wasted_beds, "MinimizeWastedBeds"
        self.objective_type = "minimize_beds_only"
        
        logger.info("Set objective: Minimize wasted beds only")
        
    def set_minimize_wasted_potential_only(
        self,
        total_wasted_potential: pulp.LpVariable
    ):
        """
        Set objective to minimize only wasted potential.
        
        This objective focuses solely on minimizing doubles in singles,
        ignoring wasted beds.
        
        Args:
            total_wasted_potential: Variable for total wasted potential
        """
        self.problem += total_wasted_potential, "MinimizeWastedPotential"
        self.objective_type = "minimize_potential_only"
        
        logger.info("Set objective: Minimize wasted potential only")
        
    def set_weighted_objective(
        self,
        variables: Dict[str, pulp.LpVariable],
        weights: Dict[str, float]
    ):
        """
        Set a custom weighted objective function.
        
        Args:
            variables: Dictionary of variable names to LpVariable objects
            weights: Dictionary of variable names to weights
        """
        if set(variables.keys()) != set(weights.keys()):
            raise ValueError("Variables and weights must have the same keys")
            
        objective = pulp.lpSum([
            weights[name] * var
            for name, var in variables.items()
        ])
        
        self.problem += objective, "CustomWeightedObjective"
        self.objective_type = "custom_weighted"
        
        logger.info(f"Set custom weighted objective with {len(variables)} variables")
        
    def set_multi_period_objective(
        self,
        period_vars: Dict[str, Dict[str, pulp.LpVariable]],
        period_weights: Dict[str, float]
    ):
        """
        Set objective for multi-period optimization.
        
        Allows different weights for different time periods
        (e.g., prioritize recent data).
        
        Args:
            period_vars: Nested dict of period -> variable_name -> LpVariable
            period_weights: Dictionary of period -> weight
        """
        objective_terms = []
        
        for period, weight in period_weights.items():
            if period not in period_vars:
                logger.warning(f"Period '{period}' not found in variables")
                continue
                
            period_sum = pulp.lpSum(period_vars[period].values())
            objective_terms.append(weight * period_sum)
            
        self.problem += pulp.lpSum(objective_terms), "MultiPeriodObjective"
        self.objective_type = "multi_period"
        
        logger.info(f"Set multi-period objective with {len(period_weights)} periods")
        
    def get_objective_info(self) -> Dict[str, Any]:
        """
        Get information about the current objective function.
        
        Returns:
            Dictionary with objective information
        """
        return {
            'type': self.objective_type,
            'expression': str(self.problem.objective) if self.problem.objective else None,
            'sense': 'minimize' if self.problem.sense == pulp.LpMinimize else 'maximize'
        }