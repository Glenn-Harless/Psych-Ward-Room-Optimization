"""
Model comparison visualization module.

Creates charts comparing performance metrics between different
ward configurations (current vs optimized models).
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, List, Tuple
from pathlib import Path

from .chart_utils import BaseChart, ChartConfig, ChartManager
from ..utils.logger import get_logger


logger = get_logger(__name__)


class ComparisonCharts(BaseChart):
    """
    Creates comparison charts between current and optimized models.
    
    Visualizes differences in wasted beds, efficiency, and other
    key performance metrics.
    """
    
    def __init__(self, current_data: pd.DataFrame, 
                 optimized_data: pd.DataFrame,
                 config: Optional[ChartConfig] = None):
        """
        Initialize comparison charts.
        
        Args:
            current_data: Current model results DataFrame
            optimized_data: Optimized model results DataFrame
            config: Optional chart configuration
        """
        super().__init__(config)
        self.current_data = current_data
        self.optimized_data = optimized_data
        
        # Ensure date columns are datetime
        self.current_data['Date'] = pd.to_datetime(self.current_data['Date'])
        self.optimized_data['Date'] = pd.to_datetime(self.optimized_data['Date'])
        
    def plot_wasted_beds_comparison(self, output_path: Optional[Path] = None) -> Path:
        """
        Create wasted beds comparison chart.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='default')
        
        # Plot lines
        ax.plot(self.current_data['Date'], 
               self.current_data['Wasted_Beds'],
               label='Current Model',
               marker='o',
               linestyle='-',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('current_model'))
               
        ax.plot(self.optimized_data['Date'],
               self.optimized_data['Wasted_Beds'],
               label='Optimized Model',
               marker='x',
               linestyle='--',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('optimized_model'))
        
        # Apply formatting
        self.config.apply_common_formatting(
            ax,
            title='Wasted Beds Comparison: Current vs Optimized Model',
            xlabel='Date',
            ylabel='Wasted Beds'
        )
        
        # Format dates
        self.format_dates(ax)
        
        # Add legend
        ax.legend(loc=self.config.plot_settings['legend_location'])
        
        # Save figure
        if output_path is None:
            output_path = Path('wasted_beds_comparison.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_wasted_potential_comparison(self, output_path: Optional[Path] = None) -> Path:
        """
        Create wasted potential comparison chart.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='default')
        
        # Plot lines
        ax.plot(self.current_data['Date'],
               self.current_data['Wasted_Potential'],
               label='Current Model',
               marker='o',
               linestyle='-',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('current_model'))
               
        ax.plot(self.optimized_data['Date'],
               self.optimized_data['Wasted_Potential'],
               label='Optimized Model',
               marker='x',
               linestyle='--',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('optimized_model'))
        
        # Apply formatting
        self.config.apply_common_formatting(
            ax,
            title='Wasted Potential Comparison: Current vs Optimized Model',
            xlabel='Date',
            ylabel='Wasted Potential'
        )
        
        # Format dates
        self.format_dates(ax)
        
        # Add legend
        ax.legend(loc=self.config.plot_settings['legend_location'])
        
        # Save figure
        if output_path is None:
            output_path = Path('wasted_potential_comparison.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_efficiency_comparison(self, efficiency_type: str = 'daily',
                                 output_path: Optional[Path] = None) -> Path:
        """
        Create efficiency comparison chart.
        
        Args:
            efficiency_type: 'daily' or 'cumulative'
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='default')
        
        # Determine column names and prepare data
        if efficiency_type == 'daily':
            efficiency_col = 'Efficiency'
            title = 'Daily Efficiency Comparison'
        else:
            # Calculate cumulative efficiency if not present
            if 'Cumulative Efficiency' not in self.current_data.columns:
                self.current_data['Cumulative Efficiency'] = (
                    self.current_data['Efficiency'].expanding().mean()
                )
            if 'Cumulative Efficiency' not in self.optimized_data.columns:
                self.optimized_data['Cumulative Efficiency'] = (
                    self.optimized_data['Efficiency'].expanding().mean()
                )
            efficiency_col = 'Cumulative Efficiency'
            title = 'Cumulative Efficiency Comparison'
            
        # Plot lines
        ax.plot(self.current_data['Date'],
               self.current_data[efficiency_col],
               label='Current Model',
               marker='o',
               linestyle='-',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('current_model'))
               
        ax.plot(self.optimized_data['Date'],
               self.optimized_data[efficiency_col],
               label='Optimized Model',
               marker='x',
               linestyle='--',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('optimized_model'))
        
        # Apply formatting
        self.config.apply_common_formatting(
            ax,
            title=f'{title}: Current vs Optimized Model',
            xlabel='Date',
            ylabel=self.config.labels['efficiency']
        )
        
        # Format dates
        self.format_dates(ax)
        
        # Add legend
        ax.legend(loc=self.config.plot_settings['legend_location'])
        
        # Format y-axis as percentage
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        
        # Save figure
        if output_path is None:
            output_path = Path(f'{efficiency_type}_efficiency_comparison.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_available_beds_comparison(self, output_path: Optional[Path] = None) -> Path:
        """
        Create available beds comparison chart.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='default')
        
        # Plot lines
        ax.plot(self.current_data['Date'],
               self.current_data['Available_Beds'],
               label='Current Model',
               marker='o',
               linestyle='-',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('current_model'))
               
        ax.plot(self.optimized_data['Date'],
               self.optimized_data['Available_Beds'],
               label='Optimized Model',
               marker='x',
               linestyle='--',
               linewidth=self.config.plot_settings['linewidth'],
               markersize=self.config.plot_settings['markersize'],
               color=self.config.get_color('optimized_model'))
        
        # Apply formatting
        self.config.apply_common_formatting(
            ax,
            title='Available Beds Comparison: Current vs Optimized Model',
            xlabel='Date',
            ylabel='Available Beds'
        )
        
        # Format dates
        self.format_dates(ax)
        
        # Add legend
        ax.legend(loc=self.config.plot_settings['legend_location'])
        
        # Save figure
        if output_path is None:
            output_path = Path('available_beds_comparison.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_all_comparisons(self, output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Generate all comparison charts.
        
        Args:
            output_dir: Directory for output charts
            
        Returns:
            Dictionary mapping chart names to output paths
        """
        if output_dir is None:
            output_dir = Path('output/charts/comparisons')
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chart_manager = ChartManager(output_dir)
        generated_charts = {}
        
        # Generate all charts
        charts_to_generate = [
            ('wasted_beds', self.plot_wasted_beds_comparison),
            ('wasted_potential', self.plot_wasted_potential_comparison),
            ('daily_efficiency', lambda p: self.plot_efficiency_comparison('daily', p)),
            ('cumulative_efficiency', lambda p: self.plot_efficiency_comparison('cumulative', p)),
            ('available_beds', self.plot_available_beds_comparison)
        ]
        
        for chart_name, chart_func in charts_to_generate:
            try:
                output_path = chart_manager.get_output_path(f'{chart_name}_comparison.png')
                saved_path = chart_func(output_path)
                generated_charts[chart_name] = saved_path
                
                # Register chart
                chart_manager.register_chart(saved_path, {
                    'type': 'comparison',
                    'metric': chart_name
                })
                
                logger.info(f"Generated {chart_name} comparison chart")
                
            except Exception as e:
                logger.error(f"Error generating {chart_name} chart: {str(e)}")
                
        # Generate chart index
        chart_manager.generate_chart_index()
        
        return generated_charts
        
    def create_summary_comparison(self, output_path: Optional[Path] = None) -> Path:
        """
        Create a summary comparison with multiple subplots.
        
        Args:
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Subplot 1: Wasted Beds
        axes[0].plot(self.current_data['Date'], self.current_data['Wasted_Beds'],
                    label='Current', color=self.config.get_color('current_model'))
        axes[0].plot(self.optimized_data['Date'], self.optimized_data['Wasted_Beds'],
                    label='Optimized', color=self.config.get_color('optimized_model'))
        axes[0].set_title('Wasted Beds')
        axes[0].set_ylabel('Count')
        axes[0].legend()
        
        # Subplot 2: Wasted Potential
        axes[1].plot(self.current_data['Date'], self.current_data['Wasted_Potential'],
                    label='Current', color=self.config.get_color('current_model'))
        axes[1].plot(self.optimized_data['Date'], self.optimized_data['Wasted_Potential'],
                    label='Optimized', color=self.config.get_color('optimized_model'))
        axes[1].set_title('Wasted Potential')
        axes[1].set_ylabel('Count')
        axes[1].legend()
        
        # Subplot 3: Daily Efficiency
        axes[2].plot(self.current_data['Date'], self.current_data['Efficiency'],
                    label='Current', color=self.config.get_color('current_model'))
        axes[2].plot(self.optimized_data['Date'], self.optimized_data['Efficiency'],
                    label='Optimized', color=self.config.get_color('optimized_model'))
        axes[2].set_title('Daily Efficiency')
        axes[2].set_ylabel('Efficiency (%)')
        axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        axes[2].legend()
        
        # Subplot 4: Summary Statistics
        axes[3].axis('off')
        
        # Calculate summary stats
        current_total_waste = self.current_data['Wasted_Beds'].sum() + self.current_data['Wasted_Potential'].sum()
        optimized_total_waste = self.optimized_data['Wasted_Beds'].sum() + self.optimized_data['Wasted_Potential'].sum()
        improvement = ((current_total_waste - optimized_total_waste) / current_total_waste * 100)
        
        summary_text = f"""Summary Statistics:
        
Current Model:
  Total Wasted Beds: {self.current_data['Wasted_Beds'].sum():,.0f}
  Total Wasted Potential: {self.current_data['Wasted_Potential'].sum():,.0f}
  Average Efficiency: {self.current_data['Efficiency'].mean():.1%}
  
Optimized Model:
  Total Wasted Beds: {self.optimized_data['Wasted_Beds'].sum():,.0f}
  Total Wasted Potential: {self.optimized_data['Wasted_Potential'].sum():,.0f}
  Average Efficiency: {self.optimized_data['Efficiency'].mean():.1%}
  
Total Waste Reduction: {improvement:.1f}%"""
        
        axes[3].text(0.1, 0.9, summary_text, transform=axes[3].transAxes,
                    verticalalignment='top', fontfamily='monospace')
        
        # Format dates on all subplots
        for ax in axes[:3]:
            ax.tick_params(axis='x', rotation=45)
            ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=6))
            ax.grid(True, alpha=0.3)
            
        # Overall title
        fig.suptitle('Model Comparison Summary', fontsize=16, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('model_comparison_summary.png')
            
        self.figure = fig
        self.save_figure(output_path)
        
        return output_path