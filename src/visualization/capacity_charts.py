"""
Capacity analysis visualization module.

Creates charts showing capacity utilization, maximum capacity events,
and related metrics for ward configurations.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import numpy as np

from .chart_utils import BaseChart, ChartConfig, ChartManager
from ..utils.logger import get_logger
from ..analysis.capacity_analyzer import CapacityAnalyzer


logger = get_logger(__name__)


class CapacityCharts(BaseChart):
    """
    Creates visualizations for capacity analysis.
    
    Shows capacity utilization patterns, max capacity events,
    and comparisons between different configurations.
    """
    
    def __init__(self, capacity_analyzer: Optional[CapacityAnalyzer] = None,
                 config: Optional[ChartConfig] = None):
        """
        Initialize capacity charts.
        
        Args:
            capacity_analyzer: Optional capacity analyzer with results
            config: Optional chart configuration
        """
        super().__init__(config)
        self.analyzer = capacity_analyzer
        
    def plot_capacity_utilization(self, analysis_results: Dict,
                                output_path: Optional[Path] = None) -> Path:
        """
        Create capacity utilization chart over time.
        
        Args:
            analysis_results: Results from capacity analyzer
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='default')
        
        # Get utilization data
        utilization_df = analysis_results['daily_utilization']
        
        # Plot utilization rate
        ax.plot(utilization_df['Date'], 
               utilization_df['Utilization_Rate'],
               color=self.config.get_color('efficiency_line'),
               linewidth=2,
               label='Utilization Rate')
               
        # Mark max capacity days
        max_capacity_days = utilization_df[utilization_df['Is_Max_Capacity']]
        if not max_capacity_days.empty:
            ax.scatter(max_capacity_days['Date'],
                      max_capacity_days['Utilization_Rate'],
                      color='red', s=50, zorder=5,
                      label=f'Max Capacity Days ({len(max_capacity_days)})')
                      
        # Add average line
        avg_utilization = analysis_results['avg_utilization']
        ax.axhline(y=avg_utilization, color='green', linestyle='--',
                  alpha=0.7, label=f'Average ({avg_utilization:.1f}%)')
                  
        # Labels and formatting
        self.config.apply_common_formatting(
            ax,
            title=f"Capacity Utilization - {analysis_results['model_name']}",
            xlabel='Date',
            ylabel='Utilization Rate (%)'
        )
        
        # Format dates
        self.format_dates(ax)
        
        # Legend
        ax.legend(loc='lower left')
        
        # Save figure
        if output_path is None:
            output_path = Path('capacity_utilization.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_capacity_events_comparison(self, 
                                      results_list: List[Tuple[str, Dict]],
                                      output_path: Optional[Path] = None) -> Path:
        """
        Compare capacity events between models.
        
        Args:
            results_list: List of (model_name, analysis_results) tuples
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Prepare data
        model_names = []
        max_capacity_days = []
        max_capacity_percents = []
        turn_away_events = []
        turn_away_percents = []
        
        for name, results in results_list:
            model_names.append(name)
            max_capacity_days.append(results['max_capacity_days'])
            max_capacity_percents.append(results['max_capacity_percent'])
            turn_away_events.append(results['turn_away_events'])
            turn_away_percents.append(results['turn_away_percent'])
            
        # Subplot 1: Days at max capacity
        x = np.arange(len(model_names))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, max_capacity_days, width,
                        label='Days at Max', color=self.config.get_color('bar_chart'))
        bars2 = ax1.bar(x + width/2, turn_away_events, width,
                        label='Turn Away Events', color='red')
                        
        ax1.set_xlabel('Model')
        ax1.set_ylabel('Number of Days')
        ax1.set_title('Capacity Events by Model')
        ax1.set_xticks(x)
        ax1.set_xticklabels(model_names)
        ax1.legend()
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
                        
        # Subplot 2: Percentages
        bars3 = ax2.bar(x - width/2, max_capacity_percents, width,
                       label='% at Max', color=self.config.get_color('bar_chart'))
        bars4 = ax2.bar(x + width/2, turn_away_percents, width,
                       label='% Turn Away', color='red')
                       
        ax2.set_xlabel('Model')
        ax2.set_ylabel('Percentage')
        ax2.set_title('Capacity Events as Percentage of Total Days')
        ax2.set_xticks(x)
        ax2.set_xticklabels(model_names)
        ax2.legend()
        
        # Add percentage labels
        for bars in [bars3, bars4]:
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%', ha='center', va='bottom')
                        
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('capacity_events_comparison.png')
        self.figure = fig
        self.save_figure(output_path)
        
        return output_path
        
    def plot_capacity_distribution(self, analysis_results: Dict,
                                 output_path: Optional[Path] = None) -> Path:
        """
        Create capacity distribution charts.
        
        Args:
            analysis_results: Results from capacity analyzer
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        utilization_df = analysis_results['daily_utilization']
        
        # Subplot 1: Histogram of utilization rates
        ax1.hist(utilization_df['Utilization_Rate'], bins=20,
                color=self.config.get_color('bar_chart'), alpha=0.7,
                edgecolor='black')
        ax1.axvline(x=analysis_results['avg_utilization'],
                   color='red', linestyle='--', linewidth=2,
                   label=f'Mean: {analysis_results["avg_utilization"]:.1f}%')
        ax1.set_xlabel('Utilization Rate (%)')
        ax1.set_ylabel('Number of Days')
        ax1.set_title('Distribution of Daily Utilization Rates')
        ax1.legend()
        
        # Subplot 2: Pie chart of capacity status
        below_90 = (utilization_df['Utilization_Rate'] < 90).sum()
        between_90_95 = ((utilization_df['Utilization_Rate'] >= 90) & 
                        (utilization_df['Utilization_Rate'] < 95)).sum()
        between_95_100 = ((utilization_df['Utilization_Rate'] >= 95) & 
                         (utilization_df['Utilization_Rate'] < 100)).sum()
        at_100 = (utilization_df['Utilization_Rate'] >= 100).sum()
        
        sizes = [below_90, between_90_95, between_95_100, at_100]
        labels = ['< 90%', '90-95%', '95-100%', '≥ 100%']
        colors = ['green', 'yellow', 'orange', 'red']
        
        # Remove zero values
        non_zero = [(s, l, c) for s, l, c in zip(sizes, labels, colors) if s > 0]
        if non_zero:
            sizes, labels, colors = zip(*non_zero)
            
            wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors,
                                              autopct='%1.1f%%', startangle=90)
            ax2.set_title(f'Capacity Utilization Distribution - {analysis_results["model_name"]}')
            
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('capacity_distribution.png')
        self.figure = fig
        self.save_figure(output_path)
        
        return output_path
        
    def plot_capacity_heatmap(self, analysis_results: Dict,
                            output_path: Optional[Path] = None) -> Path:
        """
        Create monthly capacity heatmap.
        
        Args:
            analysis_results: Results from capacity analyzer
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        fig, ax = self.create_figure(chart_type='heatmap')
        
        # Prepare data for heatmap
        utilization_df = analysis_results['daily_utilization'].copy()
        utilization_df['Date'] = pd.to_datetime(utilization_df['Date'])
        utilization_df['Year'] = utilization_df['Date'].dt.year
        utilization_df['Month'] = utilization_df['Date'].dt.month
        utilization_df['Day'] = utilization_df['Date'].dt.day
        
        # Pivot for heatmap
        heatmap_data = utilization_df.pivot_table(
            values='Utilization_Rate',
            index='Day',
            columns=['Year', 'Month'],
            aggfunc='mean'
        )
        
        # Create heatmap
        sns.heatmap(heatmap_data,
                   cmap='RdYlGn_r',
                   center=90,
                   annot=False,
                   fmt='.0f',
                   cbar_kws={'label': 'Utilization Rate (%)'},
                   ax=ax)
                   
        # Labels and title
        ax.set_xlabel('Year-Month')
        ax.set_ylabel('Day of Month')
        ax.set_title(f'Daily Capacity Utilization Heatmap - {analysis_results["model_name"]}')
        
        # Format x-axis labels
        # Get current tick positions and labels
        xticks = ax.get_xticks()
        if len(xticks) > len(heatmap_data.columns):
            # Adjust ticks to match columns
            step = max(1, len(heatmap_data.columns) // 10)  # Show up to 10 labels
            selected_indices = list(range(0, len(heatmap_data.columns), step))
            ax.set_xticks(selected_indices)
            ax.set_xticklabels([f"{heatmap_data.columns[i][0]}-{heatmap_data.columns[i][1]:02d}" 
                               for i in selected_indices])
        else:
            ax.set_xticklabels([f"{col[0]}-{col[1]:02d}" for col in heatmap_data.columns])
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('capacity_heatmap.png')
        self.save_figure(output_path)
        
        return output_path
        
    def plot_capacity_metrics_summary(self, 
                                    results_list: List[Tuple[str, Dict]],
                                    output_path: Optional[Path] = None) -> Path:
        """
        Create summary visualization of capacity metrics.
        
        Args:
            results_list: List of (model_name, analysis_results) tuples
            output_path: Optional output path for chart
            
        Returns:
            Path where chart was saved
        """
        # Prepare data for visualization
        metrics_data = []
        
        for name, results in results_list:
            metrics_data.append({
                'Model': name,
                'Avg Utilization': results['avg_utilization'],
                'Max Capacity %': results['max_capacity_percent'],
                'Turn Away %': results['turn_away_percent'],
                'Utilization Std': results['std_utilization']
            })
            
        df = pd.DataFrame(metrics_data)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create grouped bar chart
        df_plot = df.set_index('Model')
        df_plot.plot(kind='bar', ax=ax)
        
        # Formatting
        ax.set_title('Capacity Metrics Summary by Model', fontsize=16, fontweight='bold')
        ax.set_xlabel('Model')
        ax.set_ylabel('Value')
        ax.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Rotate x labels
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels on bars
        for container in ax.containers:
            ax.bar_label(container, fmt='%.1f', padding=3)
            
        plt.tight_layout()
        
        # Save figure
        if output_path is None:
            output_path = Path('capacity_metrics_summary.png')
        self.figure = fig
        self.save_figure(output_path)
        
        return output_path
        
    def generate_capacity_report(self, 
                               analysis_results: Dict,
                               comparison_results: Optional[List[Tuple[str, Dict]]] = None,
                               output_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Generate comprehensive capacity analysis charts.
        
        Args:
            analysis_results: Primary model analysis results
            comparison_results: Optional list of models to compare
            output_dir: Directory for output charts
            
        Returns:
            Dictionary mapping chart names to output paths
        """
        if output_dir is None:
            output_dir = Path('output/charts/capacity')
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chart_manager = ChartManager(output_dir)
        generated_charts = {}
        
        # Generate individual model charts
        individual_charts = [
            ('utilization_timeline', self.plot_capacity_utilization),
            ('utilization_distribution', self.plot_capacity_distribution),
            ('utilization_heatmap', self.plot_capacity_heatmap)
        ]
        
        for chart_name, chart_func in individual_charts:
            try:
                output_path = chart_manager.get_output_path(f'{chart_name}.png')
                saved_path = chart_func(analysis_results, output_path)
                generated_charts[chart_name] = saved_path
                
                # Register chart
                chart_manager.register_chart(saved_path, {
                    'type': 'capacity',
                    'model': analysis_results['model_name'],
                    'metric': chart_name
                })
                
                logger.info(f"Generated {chart_name} chart")
                
            except Exception as e:
                logger.error(f"Error generating {chart_name} chart: {str(e)}")
                
        # Generate comparison charts if data provided
        if comparison_results:
            comparison_charts = [
                ('events_comparison', self.plot_capacity_events_comparison),
                ('metrics_summary', self.plot_capacity_metrics_summary)
            ]
            
            for chart_name, chart_func in comparison_charts:
                try:
                    output_path = chart_manager.get_output_path(f'{chart_name}.png')
                    saved_path = chart_func(comparison_results, output_path)
                    generated_charts[chart_name] = saved_path
                    
                    # Register chart
                    chart_manager.register_chart(saved_path, {
                        'type': 'capacity_comparison',
                        'models': [name for name, _ in comparison_results]
                    })
                    
                    logger.info(f"Generated {chart_name} chart")
                    
                except Exception as e:
                    logger.error(f"Error generating {chart_name} chart: {str(e)}")
                    
        # Generate chart index
        chart_manager.generate_chart_index()
        
        return generated_charts