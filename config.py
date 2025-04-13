# config.py
import os
from datetime import timedelta

# Configuración global de conexión
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'sistema_citas',
    'port': 3306
}

class Config:
    SECRET_KEY = os.urandom(24)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
