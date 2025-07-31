import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'products_db'),
    'username': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password'),
}

# CSV file path
CSV_FILE_PATH = 'products.csv'

# Database URL for SQLAlchemy
def get_database_url():
    config = DATABASE_CONFIG
    return f"postgresql://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}" 