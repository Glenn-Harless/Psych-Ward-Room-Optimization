"""
Optimization analysis visualization module.

Creates charts showing the optimization landscape, including
heatmaps, efficiency plots, and configuration comparisons.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, List, Tuple, Union
from pathlib import Path

from .chart_utils import BaseChart, ChartConfig, ChartManager
from ..utils.logger import get_logger
from ..utils.constants import TOTAL_BEDS, MAX_DOUBLE_ROOMS, MAX_SINGLE_ROOMS


logger = get_logger(__name__)


class OptimizationCharts(BaseChart):
    """
    Creates visualization for optimization analysis.
    
    Shows the optimization landscape and helps understand
    how different configurations perform.
    """
    
    def __init__(self, data: pd.DataFrame, config: Optional[ChartConfig] = None):
        """
        Initialize optimization charts.
        
        Args:
            data: Census data DataFrame
            config: Optional chart configuration
        """
        super().__init__(config)
        self.data = data
        
        # Ensure date column is datetime
        self.data['Date'] = pd.to_datetime(self.data['Date'])
        
        # Calculate optimization landscape
        self.optimization_results = None
        
    def calculate_optimization_landscape(self) -> Dict[str, np.ndarray]:
        """
        Calculate objective function values for all room configurations.
        
        Returns:
            Dictionary with optimization results
        """
        logger.info("Calculating optimization landscape...")
        
        # Define ranges
        single_rooms = np.arange(0, MAX_SINGLE_ROOMS + 1)
        double_rooms = np.arange(0, MAX_DOUBLE_ROOMS + 1)
        
        # Initialize matrices
        objective_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
        singles_in_double_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
        doubles_in_single_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
        efficiency_values = np.full((len(single_rooms), len(double_rooms)), np.nan)
        
        # Calculate for each configuration
        for i, S in enumerate(single_rooms):
            for j, D in enumerate(double_rooms):
                # Check feasibility
                if 2 * D + S == TOTAL_BEDS:
                    total_waste = 0
                    total_singles_in_double = 0
                    total_doubles_in_single = 0
                    total_available = 0
                    
                    for _, row in self.data.iterrows():
                        single_patients = row['Total Single Room Patients']
                        double_patients = row['Double Room Patients']
                        closed_rooms = row.get('Closed Rooms', 0)
                        
                        # Calculate waste
                        singles_in_double = max(0, single_patients - S)
                        doubles_in_single = max(0, double_patients - 2 * D)
                        
                        total_singles_in_double += singles_in_double
                        total_doubles_in_single += doubles_in_single
                        total_waste += singles_in_double + doubles_in_single
                        
                        # Track available beds
                        available = TOTAL_BEDS - closed_rooms
                        total_available += available
                        
                    # Store results
                    objective_values[i, j] = total_waste
                    singles_in_double_values[i, j] = total_singles_in_double
                    doubles_in_single_values[i, j] = total_doubles_in_single
                    
                    # Calculate efficiency
                    if total_available > 0:
                        efficiency = (total_available - total_waste) / total_available * 100
                        efficiency_values[i, j] = efficiency
                        
        self.optimization_results = {
            'single_rooms': single_rooms,
            'double_rooms': double_rooms,
            'objective_values': objective_values,
            'singles_in_double': singles_in_double_values,
            'doubles_in_single': doubles_in_single_values,
            'efficiency': efficiency_values
        }
        
        return self.optimization_results
        
    def plot_optimization_heatmap(self, metric: str = 'objective',
                                 output_path: Optional[Path] = None) -> Path:
        """
        Create heatmap of optimization landscape.
        
        Args:
            metric: Which metric to plot ('objective', 'efficiency', etc.)
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        if self.optimization_results is None:
            self.calculate_optimization_landscape()
            
        # Select data based on metric
        metric_map = {
            'objective': ('objective_values', 'Total Waste', 'YlOrRd'),
            'efficiency': ('efficiency', 'Efficiency (%)', 'YlGnBu'),
            'singles_waste': ('singles_in_double', 'Singles in Doubles', 'YlOrRd'),
            'doubles_waste': ('doubles_in_single', 'Doubles in Singles', 'YlOrRd')
        }
        
        if metric not in metric_map:
            raise ValueError(f"Unknown metric: {metric}")
            
        data_key, title_suffix, cmap = metric_map[metric]
        data = self.optimization_results[data_key]
        
        # Create figure
        fig, ax = self.create_figure(chart_type='heatmap')
        
        # Create heatmap
        sns.heatmap(data.T,
                   xticklabels=self.optimization_results['single_rooms'],
                   yticklabels=self.optimization_results['double_rooms'],
                   fmt='.0f',
                   cmap=cmap,
                   annot=True,
                   ax=ax)
                   
        # Labels and title
        ax.set_xlabel('Number of Single Rooms')
        ax.set_ylabel('Number of Double Rooms')
        ax.set_title(f'Optimization Heatmap: {title_suffix}')
        
        # Add constraint line (2D + S = 26)
        # This appears as a diagonal line on the heatmap
        single_rooms = self.optimization_results['single_rooms']
        double_rooms = self.optimization_results['double_rooms']
        
        constraint_points = []
        for s in single_rooms:
            d = (TOTAL_BEDS - s) / 2
            if 0 <= d <= MAX_DOUBLE_ROOMS and d.is_integer():
                constraint_points.append((s, int(d)))
                
        if constraint_points:
            x_points = [p[0] for p in constraint_points]
            y_points = [p[1] for p in constraint_points]
            ax.plot(x_points, y_points, 'w-', linewidth=2, alpha=0.8)
            
        # Save figure
        if output_path is None:
            output_path = Path(f'optimization_heatmap_{metric}.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_configuration_comparison(self, configurations: List[Tuple[int, int]],
                                    output_path: Optional[Path] = None) -> Path:
        """
        Create bar chart comparing specific configurations.
        
        Args:
            configurations: List of (single_rooms, double_rooms) tuples
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        if self.optimization_results is None:
            self.calculate_optimization_landscape()
            
        # Extract data for configurations
        config_data = []
        
        for single, double in configurations:
            # Find indices
            s_idx = np.where(self.optimization_results['single_rooms'] == single)[0]
            d_idx = np.where(self.optimization_results['double_rooms'] == double)[0]
            
            if len(s_idx) > 0 and len(d_idx) > 0:
                s_idx = s_idx[0]
                d_idx = d_idx[0]
                
                config_data.append({
                    'Configuration': f'{single}S/{double}D',
                    'Total Waste': self.optimization_results['objective_values'][s_idx, d_idx],
                    'Efficiency': self.optimization_results['efficiency'][s_idx, d_idx],
                    'Singles in Doubles': self.optimization_results['singles_in_double'][s_idx, d_idx],
                    'Doubles in Singles': self.optimization_results['doubles_in_single'][s_idx, d_idx]
                })
                
        df = pd.DataFrame(config_data)
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Subplot 1: Waste comparison
        waste_data = df[['Configuration', 'Singles in Doubles', 'Doubles in Singles']].set_index('Configuration')
        waste_data.plot(kind='bar', stacked=True, ax=ax1,
                       color=[self.config.get_color('singles_line'),
                              self.config.get_color('doubles_line')])
        ax1.set_title('Waste Breakdown by Configuration')
        ax1.set_ylabel('Total Waste')
        ax1.set_xlabel('Configuration')
        ax1.legend(title='Waste Type')
        
        # Subplot 2: Efficiency comparison
        ax2.bar(df['Configuration'], df['Efficiency'],
               color=self.config.get_color('efficiency_line'))
        ax2.set_title('Efficiency by Configuration')
        ax2.set_ylabel('Efficiency (%)')
        ax2.set_xlabel('Configuration')
        
        # Add value labels
        for i, (config, efficiency) in enumerate(zip(df['Configuration'], df['Efficiency'])):
            ax2.text(i, efficiency + 0.5, f'{efficiency:.1f}%', ha='center')
            
        # Rotate x labels
        for ax in [ax1, ax2]:
            ax.tick_params(axis='x', rotation=45)
            
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('configuration_comparison.png')
        self.figure = fig
        self.save_figure(output_path)
        
        return output_path
        
    def plot_efficiency_by_configuration(self, output_path: Optional[Path] = None) -> Path:
        """
        Create line plot showing efficiency for valid configurations.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        if self.optimization_results is None:
            self.calculate_optimization_landscape()
            
        # Extract valid configurations (where 2D + S = 26)
        valid_configs = []
        
        for s in self.optimization_results['single_rooms']:
            d = (TOTAL_BEDS - s) / 2
            if 0 <= d <= MAX_DOUBLE_ROOMS and d.is_integer():
                d = int(d)
                s_idx = np.where(self.optimization_results['single_rooms'] == s)[0][0]
                d_idx = np.where(self.optimization_results['double_rooms'] == d)[0][0]
                
                efficiency = self.optimization_results['efficiency'][s_idx, d_idx]
                if not np.isnan(efficiency):
                    valid_configs.append({
                        'Single Rooms': s,
                        'Double Rooms': d,
                        'Efficiency': efficiency,
                        'Configuration': f'{s}S/{d}D'
                    })
                    
        df = pd.DataFrame(valid_configs)
        
        # Create figure
        fig, ax = self.create_figure(chart_type='line_plot')
        
        # Plot efficiency line
        ax.plot(df['Single Rooms'], df['Efficiency'],
               marker=self.config.markers['efficiency'],
               color=self.config.get_color('efficiency_line'),
               linewidth=2,
               markersize=8)
               
        # Highlight optimal configuration
        optimal_idx = df['Efficiency'].idxmax()
        optimal_config = df.iloc[optimal_idx]
        
        ax.scatter(optimal_config['Single Rooms'], optimal_config['Efficiency'],
                  color='red', s=200, zorder=5, marker='*')
        ax.annotate(f"Optimal: {optimal_config['Configuration']}\n{optimal_config['Efficiency']:.2f}%",
                   xy=(optimal_config['Single Rooms'], optimal_config['Efficiency']),
                   xytext=(10, -20), textcoords='offset points',
                   bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))
                   
        # Labels and title
        ax.set_xlabel('Number of Single Rooms')
        ax.set_ylabel('Efficiency (%)')
        ax.set_title('Efficiency by Room Configuration')
        ax.grid(True, alpha=0.3)
        
        # Add secondary x-axis for double rooms
        ax2 = ax.twiny()
        ax2.set_xlim(ax.get_xlim())
        ax2.set_xticks(df['Single Rooms'])
        ax2.set_xticklabels(df['Double Rooms'])
        ax2.set_xlabel('Number of Double Rooms')
        
        # Save figure
        if output_path is None:
            output_path = Path('efficiency_by_configuration.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_waste_components(self, output_path: Optional[Path] = None) -> Path:
        """
        Create stacked area chart showing waste components over time.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        # Calculate waste for optimal configuration (10S/8D)
        optimal_single = 10
        optimal_double = 8
        
        waste_data = []
        
        for _, row in self.data.iterrows():
            single_patients = row['Total Single Room Patients']
            double_patients = row['Double Room Patients']
            
            singles_in_double = max(0, single_patients - optimal_single)
            doubles_in_single = max(0, double_patients - 2 * optimal_double)
            
            waste_data.append({
                'Date': row['Date'],
                'Singles in Doubles': singles_in_double,
                'Doubles in Singles': doubles_in_single
            })
            
        df = pd.DataFrame(waste_data)
        
        # Create figure
        fig, ax = self.create_figure(chart_type='default')
        
        # Create stacked area chart
        ax.fill_between(df['Date'], 0, df['Singles in Doubles'],
                       label='Singles in Doubles',
                       color=self.config.get_color('singles_line'),
                       alpha=0.7)
                       
        ax.fill_between(df['Date'], df['Singles in Doubles'],
                       df['Singles in Doubles'] + df['Doubles in Singles'],
                       label='Doubles in Singles',
                       color=self.config.get_color('doubles_line'),
                       alpha=0.7)
                       
        # Labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Wasted Beds/Potential')
        ax.set_title('Waste Components Over Time (Optimized Model)')
        ax.legend(loc='upper left')
        
        # Format dates
        self.format_dates(ax)
        
        # Save figure
        if output_path is None:
            output_path = Path('waste_components.png')
        self.save_figure(output_path)
        
        return output_path
        
    def generate_optimization_report(self, output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Generate comprehensive optimization analysis charts.
        
        Args:
            output_dir: Directory for output charts
            
        Returns:
            Dictionary mapping chart names to output paths
        """
        if output_dir is None:
            output_dir = Path('output/charts/optimizations')
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chart_manager = ChartManager(output_dir)
        generated_charts = {}
        
        # Calculate optimization landscape first
        self.calculate_optimization_landscape()
        
        # Generate charts
        charts_to_generate = [
            ('heatmap_objective', lambda p: self.plot_optimization_heatmap('objective', p)),
            ('heatmap_efficiency', lambda p: self.plot_optimization_heatmap('efficiency', p)),
            ('configuration_comparison', lambda p: self.plot_configuration_comparison(
                [(0, 13), (10, 8), (20, 3)], p  # Current, Optimal, Alternative
            )),
            ('efficiency_line', self.plot_efficiency_by_configuration),
            ('waste_components', self.plot_waste_components)
        ]
        
        for chart_name, chart_func in charts_to_generate:
            try:
                output_path = chart_manager.get_output_path(f'{chart_name}.png')
                saved_path = chart_func(output_path)
                
                if saved_path:
                    # Move to proper location
                    final_path = output_path
                    if saved_path != output_path:
                        import shutil
                        shutil.move(str(saved_path), str(output_path))
                        
                    generated_charts[chart_name] = final_path
                    
                    # Register chart
                    chart_manager.register_chart(final_path, {
                        'type': 'optimization',
                        'analysis': chart_name
                    })
                    
                    logger.info(f"Generated {chart_name} chart")
                    
            except Exception as e:
                logger.error(f"Error generating {chart_name} chart: {str(e)}")
                
        # Generate chart index
        chart_manager.generate_chart_index()
        
        return generated_charts