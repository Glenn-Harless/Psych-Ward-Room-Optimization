"""
Logging configuration for the Psych Ward Room Optimization system.

Provides centralized logging setup with configurable levels and formats.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import yaml


def load_logging_config():
    """Load logging configuration from config file."""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'model_configs.yaml'
    
    # Default configuration
    default_config = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'date_format': '%Y-%m-%d %H:%M:%S'
    }
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config.get('logging', default_config)
    except Exception:
        return default_config


def setup_logger(name, log_file=None, level=None):
    """
    Set up a logger with the given name and optional log file.
    
    Args:
        name: Name of the logger (typically __name__)
        log_file: Optional path to log file
        level: Optional logging level (overrides config)
        
    Returns:
        Configured logger instance
    """
    config = load_logging_config()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level or getattr(logging, config['level']))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        config['format'],
        datefmt=config['date_format']
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name):
    """
    Get or create a logger with the given name.
    
    This is a convenience function for modules that just need
    basic logging without file output.
    
    Args:
        name: Name of the logger (typically __name__)
        
    Returns:
        Logger instance
    """
    return setup_logger(name)


class LoggerContext:
    """Context manager for temporary logging configuration changes."""
    
    def __init__(self, logger, level=None, handlers=None):
        self.logger = logger
        self.original_level = logger.level
        self.original_handlers = logger.handlers[:]
        self.temp_level = level
        self.temp_handlers = handlers or []
        
    def __enter__(self):
        if self.temp_level:
            self.logger.setLevel(self.temp_level)
        for handler in self.temp_handlers:
            self.logger.addHandler(handler)
        return self.logger
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)
        self.logger.handlers = self.original_handlers


def log_execution_time(func):
    """Decorator to log function execution time."""
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()
        logger.info(f"Starting {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Completed {func.__name__} in {elapsed:.2f} seconds")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed {func.__name__} after {elapsed:.2f} seconds: {str(e)}")
            raise
            
    return wrapper


def create_rotating_log_handler(log_file, max_bytes=10485760, backup_count=5):
    """
    Create a rotating file handler for large log files.
    
    Args:
        log_file: Path to log file
        max_bytes: Maximum size before rotation (default 10MB)
        backup_count: Number of backup files to keep
        
    Returns:
        RotatingFileHandler instance
    """
    from logging.handlers import RotatingFileHandler
    
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    config = load_logging_config()
    formatter = logging.Formatter(
        config['format'],
        datefmt=config['date_format']
    )
    handler.setFormatter(formatter)
    
    return handler