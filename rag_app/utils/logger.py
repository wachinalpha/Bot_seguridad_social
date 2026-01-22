import logging
import sys
from pathlib import Path


def setup_logger(name: str = None, level: int = logging.INFO, log_file: str = None) -> logging.Logger:
    """
    Setup and configure a logger.
    
    Args:
        name: Logger name (None for root logger)
        level: Logging level (default: INFO)
        log_file: Optional file path for file logging
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler with formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Format: timestamp - name - level - message
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the application's configuration.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Configure root logger for the application
def configure_logging(level: int = logging.INFO, log_file: str = None):
    """
    Configure logging for the entire application.
    
    Args:
        level: Logging level
        log_file: Optional log file path
    """
    setup_logger(name='rag_app', level=level, log_file=log_file)
