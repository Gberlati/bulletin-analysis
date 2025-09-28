import os
from dotenv import load_dotenv
from datetime import date

today = date.today()
formatted_date = today.strftime("%Y-%m-%d")

# Cargar variables desde el archivo .env
load_dotenv()

# Configuración de la Base de Datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE')
}

# Configuración del Scraper
BASE_URL = "https://www.boletinoficial.gob.ar/detalleAviso/segunda/{aviso_id}/" + today.strftime("%Y%m%d")
START_AVISO_ID = 1
SLEEP_INTERVAL_SECONDS = 1 # Tiempo de espera entre peticiones
RETRY_ON_EMPTY_SECONDS = 3600 # Tiempo de espera si no hay nuevos avisos (1 hora)
NUM_THREADS = 50
BATCH_SIZE = 50 # Number of notices to process in each batch
