"""Logging configuration."""

import logging
import sys
from pathlib import Path


def setup_logger(
    name: str = 'chess_vision',
    level: int = logging.INFO,
    log_file: str = None
):
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name
        level: Logging level
        log_file: Path to log file (None = console only)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'chess_vision'):
    """Get existing logger."""
    return logging.getLogger(name)
