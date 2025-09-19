# Azure Web App Configuration
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'votre_cle_secrete_super_complexe_123456789'
    
    # Azure optimizations
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    # Database files - pour Azure App Service
    CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    
    # Azure App Service port
    PORT = int(os.environ.get('PORT', 8000))
    
    # Pandas optimizations for Azure
    PANDAS_COMPUTE_DTYPE = 'float64'
    PANDAS_MEMORY_USAGE = 'deep'