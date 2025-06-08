"""
Project-wide constants for the Psych Ward Room Optimization system.

This module provides centralized access to configuration values,
avoiding hardcoded values throughout the codebase.
"""

from pathlib import Path
import yaml


class Config:
    """Configuration singleton that loads values from YAML files."""
    
    _instance = None
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._loaded:
            self._load_configs()
            self._loaded = True
    
    def _load_configs(self):
        """Load all configuration files."""
        config_dir = Path(__file__).parent.parent.parent / 'config'
        
        # Load optimization parameters
        with open(config_dir / 'optimization_params.yaml', 'r') as f:
            opt_config = yaml.safe_load(f)
            
        # Load model configurations
        with open(config_dir / 'model_configs.yaml', 'r') as f:
            model_config = yaml.safe_load(f)
            
        # Load visualization settings
        with open(config_dir / 'visualization_settings.yaml', 'r') as f:
            viz_config = yaml.safe_load(f)
        
        # Set attributes
        self.WARD = opt_config['ward']
        self.OPTIMIZATION = opt_config['optimization']
        self.DATA_COLUMNS = opt_config['data_columns']
        self.EFFICIENCY = opt_config['efficiency']
        self.CONSTRAINTS = opt_config['constraints']
        
        self.MODELS = model_config['models']
        self.PATHS = model_config['paths']
        self.DATA_PROCESSING = model_config['data_processing']
        self.LOGGING = model_config['logging']
        
        self.VISUALIZATION = viz_config
        
    def get_project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent
    
    def get_data_path(self, filename=None):
        """Get path to data directory or specific data file."""
        root = self.get_project_root()
        data_dir = root / 'data'
        
        if filename:
            return data_dir / filename
        return data_dir
    
    def get_output_path(self, filename=None, subdirectory=None):
        """Get path to output directory or specific output file."""
        root = self.get_project_root()
        output_dir = root / self.PATHS['output']['base_directory']
        
        if subdirectory:
            output_dir = output_dir / subdirectory
            
        if filename:
            return output_dir / filename
        return output_dir
    
    def get_log_path(self, log_type='optimizer_debug'):
        """Get path to log file."""
        root = self.get_project_root()
        return root / self.PATHS['logs'][log_type]


# Create singleton instance
config = Config()

# Export commonly used constants for convenience
TOTAL_BEDS = config.WARD['total_beds']
MAX_DOUBLE_ROOMS = config.WARD['max_double_rooms']
MAX_SINGLE_ROOMS = config.WARD['max_single_rooms']
DEFAULT_SINGLE_ROOMS = config.WARD['default_single_rooms']
DEFAULT_DOUBLE_ROOMS = config.WARD['default_double_rooms']
DOUBLE_ROOM_CAPACITY = config.WARD['double_room_capacity']

# Data column names
DATE_COLUMN = config.DATA_COLUMNS['date']
SINGLE_ROOM_E_COLUMN = config.DATA_COLUMNS['single_room_e']
TOTAL_SINGLE_PATIENTS_COLUMN = config.DATA_COLUMNS['total_single_patients']
DOUBLE_ROOM_PATIENTS_COLUMN = config.DATA_COLUMNS['double_room_patients']
CLOSED_ROOMS_COLUMN = config.DATA_COLUMNS['closed_rooms']

# Years to process
YEARS_TO_PROCESS = config.OPTIMIZATION['years_to_process']