import os

class Config:
    HOST = '0.0.0.0'
    PORT = 5000
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = False
    DATA_FILE = 'data/SFPD_Incidents_2021_to_Present_Reduced.csv'