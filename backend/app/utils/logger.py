import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# Get the absolute path to the backend directory
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    
    # Use absolute path for log file
    log_file_path = os.path.join(BACKEND_DIR, 'logs', log_file)
    
    # Ensure the logs directory exists
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    # File handler
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10000000, backupCount=5)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    print(f"Logger {name} set up with log file: {log_file_path}")
    
    return logger

# Create loggers
api_logger = setup_logger('api_logger', 'api.log')
db_logger = setup_logger('db_logger', 'db.log')