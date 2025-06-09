"""
Linear programming optimization engine for ward room configuration.

This module implements the core optimization algorithm that determines
the optimal mix of single and double rooms to minimize bed waste.
"""

import pulp
import pandas as pd
from typing import Tuple, Optional, Dict, Any

from ..utils.logger import get_logger, log_execution_time
from ..utils.constants import (
    config, TOTAL_BEDS, MAX_DOUBLE_ROOMS, MAX_SINGLE_ROOMS,
    DATE_COLUMN, SINGLE_ROOM_E_COLUMN, TOTAL_SINGLE_PATIENTS_COLUMN,
    DOUBLE_ROOM_PATIENTS_COLUMN, YEARS_TO_PROCESS
)
from ..utils.file_handler import FileHandler
from .constraints import ConstraintBuilder
from .objective import ObjectiveBuilder


logger = get_logger(__name__)


class WardOptimizer:
    """
    Optimizes ward room configuration using linear programming.
    
    This class implements the core optimization algorithm that determines
    the optimal number of single and double rooms to minimize both
    wasted beds (singles in doubles) and wasted potential (doubles in singles).
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the optimizer with census data.
        
        Args:
            data_path: Path to census data CSV file. If None, uses default from config.
        """
        self.data_path = data_path or config.get_data_path(
            config.PATHS['input']['training_data']
        )
        self.data = None
        self.problem = None
        self.results = None
        
    def load_data(self):
        """Load and prepare census data for optimization."""
        logger.info(f"Loading census data from {self.data_path}")
        
        # Load data using file handler
        self.data = FileHandler.read_csv(self.data_path)
        
        # Convert date column
        self.data[DATE_COLUMN] = pd.to_datetime(self.data[DATE_COLUMN])
        
        # Drop rows with missing essential data
        self.data.dropna(subset=[SINGLE_ROOM_E_COLUMN], inplace=True)
        
        # Filter for years to process
        self.data = self.data[
            self.data[DATE_COLUMN].dt.year.isin(YEARS_TO_PROCESS)
        ]
        
        logger.info(f"Loaded {len(self.data)} days of census data")
        
    @log_execution_time
    def optimize_space(self, log_path: Optional[str] = None) -> Tuple[int, int, int, int, int, float, str, float]:
        """
        Optimize ward space allocation using linear programming.
        
        Args:
            log_path: Optional path for solver log output
            
        Returns:
            Tuple containing:
                - double_rooms: Optimal number of double rooms
                - single_rooms: Optimal number of single rooms
                - total_wasted_beds: Total beds wasted (singles in doubles)
                - total_wasted_potential: Total potential wasted (doubles in singles)
                - total_free_beds: Unused beds (should be 0)
                - efficiency: Overall efficiency percentage
                - solver_status: Status of the solver
                - objective_value: Value of the objective function
        """
        if self.data is None:
            self.load_data()
            
        # Create the optimization problem
        self.problem = pulp.LpProblem("OptimizeWardSpace", pulp.LpMinimize)
        
        # Create decision variables
        D = pulp.LpVariable('D', lowBound=0, upBound=MAX_DOUBLE_ROOMS, cat='Integer')
        S = pulp.LpVariable('S', lowBound=0, upBound=MAX_SINGLE_ROOMS, cat='Integer')
        
        # Create tracking variables
        total_wasted_beds = pulp.LpVariable('total_wasted_beds', lowBound=0, cat='Integer')
        total_wasted_potential = pulp.LpVariable('total_wasted_potential', lowBound=0, cat='Integer')
        
        # Build constraints
        constraint_builder = ConstraintBuilder(self.problem)
        constraint_builder.add_bed_capacity_constraint(D, S)
        
        # Track daily inefficiencies
        single_in_double_vars = []
        double_in_single_vars = []
        
        for i, row in self.data.iterrows():
            single_rooms_needed = row[TOTAL_SINGLE_PATIENTS_COLUMN]
            double_rooms_needed = row[DOUBLE_ROOM_PATIENTS_COLUMN]
            
            # Create daily inefficiency variables
            sid_var, dis_var = constraint_builder.add_daily_constraints(
                i, S, D, single_rooms_needed, double_rooms_needed
            )
            
            single_in_double_vars.append(sid_var)
            double_in_single_vars.append(dis_var)
            
            logger.debug(
                f"Date: {row[DATE_COLUMN]}, "
                f"Singles needed: {single_rooms_needed}, "
                f"Doubles needed: {double_rooms_needed}"
            )
        
        # Add accumulation constraints
        constraint_builder.add_accumulation_constraints(
            total_wasted_beds, total_wasted_potential,
            single_in_double_vars, double_in_single_vars
        )
        
        # Set objective function
        objective_builder = ObjectiveBuilder(self.problem)
        objective_builder.set_minimize_waste_objective(
            total_wasted_beds, total_wasted_potential
        )
        
        # Solve the problem
        self._solve_problem(log_path)
        
        # Extract and return results
        return self._extract_results(D, S, total_wasted_beds, total_wasted_potential)
    
    def _solve_problem(self, log_path: Optional[str] = None):
        """
        Solve the optimization problem.
        
        Args:
            log_path: Optional path for solver log
        """
        solver_log = log_path or config.get_log_path('solver_log')
        solver = pulp.PULP_CBC_CMD(
            msg=config.OPTIMIZATION['solver_msg'],
            logPath=str(solver_log)
        )
        
        logger.info("Solving optimization problem...")
        self.problem.solve(solver)
        
        status = pulp.LpStatus[self.problem.status]
        logger.info(f"Solver status: {status}")
        
        if self.problem.status != pulp.LpStatusOptimal:
            logger.warning(f"Solver did not find optimal solution. Status: {status}")
    
    def _extract_results(self, D, S, total_wasted_beds, total_wasted_potential) -> Tuple[int, int, int, int, int, float, str, float]:
        """
        Extract results from solved problem.
        
        Returns:
            Tuple of optimization results
        """
        # Get variable values
        double_rooms = int(pulp.value(D))
        single_rooms = int(pulp.value(S))
        wasted_beds = int(pulp.value(total_wasted_beds))
        wasted_potential = int(pulp.value(total_wasted_potential))
        
        # Calculate metrics
        total_free_beds = TOTAL_BEDS - (2 * double_rooms + single_rooms)
        efficiency = (TOTAL_BEDS - total_free_beds - wasted_beds - wasted_potential) / TOTAL_BEDS
        
        # Get solver info
        solver_status = pulp.LpStatus[self.problem.status]
        objective_value = pulp.value(self.problem.objective)
        
        # Store results
        self.results = {
            'double_rooms': double_rooms,
            'single_rooms': single_rooms,
            'total_wasted_beds': wasted_beds,
            'total_wasted_potential': wasted_potential,
            'total_free_beds': total_free_beds,
            'efficiency': efficiency,
            'solver_status': solver_status,
            'objective_value': objective_value
        }
        
        # Log results
        logger.info(f"Optimization Results:")
        logger.info(f"  Double rooms: {double_rooms}")
        logger.info(f"  Single rooms: {single_rooms}")
        logger.info(f"  Total wasted beds: {wasted_beds}")
        logger.info(f"  Total wasted potential: {wasted_potential}")
        logger.info(f"  Efficiency: {efficiency:.2%}")
        
        return (double_rooms, single_rooms, wasted_beds, wasted_potential,
                total_free_beds, efficiency, solver_status, objective_value)
    
    def get_results_dict(self) -> Optional[Dict[str, Any]]:
        """
        Get optimization results as a dictionary.
        
        Returns:
            Dictionary of results or None if not yet solved
        """
        return self.results
    
    def save_results(self, output_path: Optional[str] = None):
        """
        Save optimization results to file.
        
        Args:
            output_path: Path to save results (JSON format)
        """
        if self.results is None:
            raise ValueError("No results to save. Run optimize_space() first.")
            
        output_path = output_path or config.get_output_path(
            'optimization_results.json', 'reports/optimization_results'
        )
        
        FileHandler.write_json(self.results, output_path)
        logger.info(f"Saved optimization results to {output_path}")