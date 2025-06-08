"""
Common chart utilities and base classes.

Provides reusable components for consistent chart styling,
formatting, and common operations across all visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any
import numpy as np

from ..utils.logger import get_logger
from ..utils.constants import config


logger = get_logger(__name__)


class ChartConfig:
    """
    Centralized configuration for chart styling and formatting.
    
    Loads settings from visualization_settings.yaml and provides
    consistent styling across all charts.
    """
    
    def __init__(self):
        """Initialize chart configuration from settings."""
        viz_config = config.VISUALIZATION
        
        # Seaborn settings
        self.seaborn_style = viz_config['seaborn']['style']
        self.seaborn_context = viz_config['seaborn']['context']
        self.seaborn_palette = viz_config['seaborn']['palette']
        
        # Figure sizes
        self.figure_sizes = viz_config['figure_sizes']
        
        # Plot settings
        self.plot_settings = viz_config['plot_settings']
        
        # Colors
        self.colors = viz_config['colors']
        
        # Markers
        self.markers = viz_config['markers']
        
        # Labels
        self.labels = viz_config['labels']
        
        # Title settings
        self.title_settings = viz_config['titles']
        
        # Grid settings
        self.grid_settings = viz_config['grid']
        
        # Export settings
        self.export_settings = viz_config['export']
        
        # Apply seaborn style
        self._apply_seaborn_style()
        
    def _apply_seaborn_style(self):
        """Apply Seaborn styling from configuration."""
        sns.set(
            style=self.seaborn_style,
            context=self.seaborn_context,
            palette=self.seaborn_palette
        )
        
    def get_figure_size(self, chart_type: str = 'default') -> Tuple[int, int]:
        """Get figure size for specific chart type."""
        size = self.figure_sizes.get(chart_type, self.figure_sizes['default'])
        return tuple(size)
        
    def get_color(self, color_name: str) -> str:
        """Get color by name from configuration."""
        return self.colors.get(color_name, 'blue')
        
    def apply_common_formatting(self, ax: plt.Axes, 
                               title: str = None,
                               xlabel: str = None,
                               ylabel: str = None,
                               show_grid: bool = True):
        """
        Apply common formatting to an axes object.
        
        Args:
            ax: Matplotlib axes object
            title: Chart title
            xlabel: X-axis label
            ylabel: Y-axis label
            show_grid: Whether to show grid
        """
        if title:
            ax.set_title(
                title,
                fontsize=self.title_settings['font_size'],
                fontweight=self.title_settings['font_weight']
            )
            
        if xlabel:
            ax.set_xlabel(xlabel)
            
        if ylabel:
            ax.set_ylabel(ylabel)
            
        if show_grid and self.grid_settings['enabled']:
            ax.grid(True, alpha=self.grid_settings['alpha'])


class BaseChart:
    """
    Base class for all chart types.
    
    Provides common functionality for chart creation,
    styling, and export.
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        """
        Initialize base chart.
        
        Args:
            config: Chart configuration instance
        """
        self.config = config or ChartConfig()
        self.figure = None
        self.axes = None
        
    def create_figure(self, figsize: Optional[Tuple[int, int]] = None,
                     chart_type: str = 'default') -> Tuple[plt.Figure, plt.Axes]:
        """
        Create a new figure with configured size.
        
        Args:
            figsize: Optional custom figure size
            chart_type: Type of chart for size lookup
            
        Returns:
            Tuple of (figure, axes)
        """
        if figsize is None:
            figsize = self.config.get_figure_size(chart_type)
            
        self.figure, self.axes = plt.subplots(figsize=figsize)
        return self.figure, self.axes
        
    def format_dates(self, ax: plt.Axes, 
                    rotation: Optional[int] = None,
                    date_bins: Optional[int] = None):
        """
        Format date labels on x-axis.
        
        Args:
            ax: Axes object
            rotation: Label rotation angle
            date_bins: Number of date bins to show
        """
        if rotation is None:
            rotation = self.config.plot_settings['x_axis_rotation']
            
        if date_bins is None:
            date_bins = self.config.plot_settings['date_bins']
            
        ax.tick_params(axis='x', rotation=rotation)
        ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=date_bins))
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
    def add_value_labels(self, ax: plt.Axes, 
                        values: List[float],
                        positions: List[float],
                        format_str: str = '{:.1f}',
                        offset: float = 0.02):
        """
        Add value labels to chart elements.
        
        Args:
            ax: Axes object
            values: Values to display
            positions: X positions for labels
            format_str: Format string for values
            offset: Vertical offset for labels
        """
        y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
        offset_value = y_range * offset
        
        for pos, val in zip(positions, values):
            ax.text(pos, val + offset_value, format_str.format(val),
                   ha='center', va='bottom')
                   
    def save_figure(self, output_path: Union[str, Path],
                   add_timestamp: bool = False,
                   **kwargs):
        """
        Save figure with configured settings.
        
        Args:
            output_path: Path to save figure
            add_timestamp: Whether to add timestamp to filename
            **kwargs: Additional arguments for savefig
        """
        if self.figure is None:
            raise ValueError("No figure to save. Create a figure first.")
            
        output_path = Path(output_path)
        
        # Add timestamp if requested
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = output_path.stem
            suffix = output_path.suffix
            output_path = output_path.parent / f"{stem}_{timestamp}{suffix}"
            
        # Set default export parameters
        save_params = {
            'dpi': self.config.export_settings['dpi'],
            'format': self.config.export_settings['format'],
            'transparent': self.config.export_settings['transparent'],
            'bbox_inches': 'tight'
        }
        save_params.update(kwargs)
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save figure
        self.figure.savefig(output_path, **save_params)
        logger.info(f"Saved chart to {output_path}")
        
        # Close figure to free memory
        plt.close(self.figure)
        
    @staticmethod
    def create_color_palette(n_colors: int, 
                           palette_name: str = 'colorblind') -> List[str]:
        """
        Create a color palette with specified number of colors.
        
        Args:
            n_colors: Number of colors needed
            palette_name: Seaborn palette name
            
        Returns:
            List of color codes
        """
        return sns.color_palette(palette_name, n_colors)
        
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format value as percentage string."""
        return f"{value:.{decimals}f}%"
        
    @staticmethod
    def format_number(value: float, decimals: int = 0) -> str:
        """Format number with thousands separator."""
        if decimals == 0:
            return f"{value:,.0f}"
        else:
            return f"{value:,.{decimals}f}"


class ChartManager:
    """
    Manages chart generation workflow and output organization.
    """
    
    def __init__(self, output_base_path: Optional[Path] = None):
        """
        Initialize chart manager.
        
        Args:
            output_base_path: Base path for chart outputs
        """
        self.output_base_path = output_base_path or config.get_output_path('charts')
        self.generated_charts = []
        
    def get_output_path(self, chart_name: str, 
                       category: Optional[str] = None) -> Path:
        """
        Get organized output path for a chart.
        
        Args:
            chart_name: Name of the chart
            category: Optional category subdirectory
            
        Returns:
            Full output path
        """
        if category:
            return self.output_base_path / category / chart_name
        return self.output_base_path / chart_name
        
    def register_chart(self, chart_path: Path, metadata: Dict[str, Any]):
        """
        Register a generated chart with metadata.
        
        Args:
            chart_path: Path where chart was saved
            metadata: Chart metadata (type, timestamp, etc.)
        """
        self.generated_charts.append({
            'path': chart_path,
            'timestamp': datetime.now(),
            **metadata
        })
        
    def generate_chart_index(self, output_path: Optional[Path] = None):
        """
        Generate an index of all created charts.
        
        Args:
            output_path: Path for index file
        """
        if not self.generated_charts:
            logger.warning("No charts to index")
            return
            
        output_path = output_path or self.output_base_path / 'chart_index.csv'
        
        # Create DataFrame from chart records
        index_df = pd.DataFrame(self.generated_charts)
        
        # Save index
        index_df.to_csv(output_path, index=False)
        logger.info(f"Generated chart index with {len(index_df)} entries")


def create_comparison_legend(labels: List[str], 
                           colors: Optional[List[str]] = None,
                           markers: Optional[List[str]] = None,
                           location: str = 'upper left') -> plt.Legend:
    """
    Create a standardized comparison legend.
    
    Args:
        labels: Legend labels
        colors: Line colors
        markers: Line markers
        location: Legend location
        
    Returns:
        Legend object
    """
    if colors is None:
        colors = ChartConfig().create_color_palette(len(labels))
        
    if markers is None:
        markers = ['o', 'x', 's', '^', 'v', 'd'][:len(labels)]
        
    # Create legend elements
    from matplotlib.lines import Line2D
    legend_elements = []
    
    for label, color, marker in zip(labels, colors, markers):
        element = Line2D([0], [0], color=color, marker=marker,
                        label=label, markersize=8)
        legend_elements.append(element)
        
    return plt.legend(handles=legend_elements, loc=location)


def apply_chart_theme(theme_name: str = 'default'):
    """
    Apply a predefined chart theme.
    
    Args:
        theme_name: Name of the theme to apply
    """
    themes = {
        'default': {
            'style': 'darkgrid',
            'context': 'talk',
            'palette': 'colorblind'
        },
        'presentation': {
            'style': 'whitegrid',
            'context': 'talk',
            'palette': 'bright'
        },
        'paper': {
            'style': 'ticks',
            'context': 'paper',
            'palette': 'muted'
        },
        'minimal': {
            'style': 'white',
            'context': 'notebook',
            'palette': 'pastel'
        }
    }
    
    if theme_name not in themes:
        logger.warning(f"Unknown theme '{theme_name}', using default")
        theme_name = 'default'
        
    theme = themes[theme_name]
    sns.set(style=theme['style'], 
           context=theme['context'], 
           palette=theme['palette'])