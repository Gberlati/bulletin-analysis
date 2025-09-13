import mysql.connector
from mysql.connector import errorcode
import time
import logging
from config import DB_CONFIG

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    """Intenta conectarse a la base de datos con reintentos."""
    attempts = 0
    while attempts < 10:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            logging.info("Conexión a la base de datos establecida con éxito.")
            return conn
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Error de acceso a la base de datos: usuario o contraseña incorrectos.")
                return None
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error(f"La base de datos '{DB_CONFIG['database']}' no existe.")
                return None
            else:
                logging.warning(f"No se pudo conectar a la base de datos ({err}). Reintentando en 5 segundos...")
                attempts += 1
                time.sleep(5)
    logging.error("No se pudo establecer la conexión a la base de datos después de varios intentos.")
    return None

def setup_database(conn):
    """Crea la tabla de avisos si no existe."""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS avisos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                aviso_id VARCHAR(50) NOT NULL UNIQUE,
                seccion VARCHAR(255),
                rubro VARCHAR(255),
                id_rubro VARCHAR(50),
                fecha_publicacion DATE,
                detalle_aviso TEXT,
                crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)
        logging.info("Tabla 'avisos' verificada/creada con éxito.")
    except mysql.connector.Error as err:
        logging.error(f"Error al crear la tabla: {err}")
    finally:
        cursor.close()

def get_last_aviso_id(conn):
    """Obtiene el ID numérico del último aviso guardado."""
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT aviso_id FROM avisos ORDER BY id DESC LIMIT 1;")
        result = cursor.fetchone()
        if result:
            last_id_str = result[0].replace('A', '')
            return int(last_id_str)
        return 0 # Si la tabla está vacía
    except mysql.connector.Error as err:
        logging.error(f"Error al obtener el último ID de aviso: {err}")
        return 0
    finally:
        cursor.close()

def save_aviso(conn, data):
    """Guarda un nuevo aviso en la base de datos."""
    cursor = conn.cursor()
    sql = """
        INSERT INTO avisos (aviso_id, seccion, rubro, id_rubro, fecha_publicacion, detalle_aviso)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(sql, (
            data.get('aviso_id'),
            data.get('seccion'),
            data.get('rubro'),
            data.get('id_rubro'),
            data.get('fecha_publicacion'),
            data.get('detalle_aviso')
        ))
        conn.commit()
        logging.info(f"Aviso {data.get('aviso_id')} guardado correctamente.")
    except mysql.connector.Error as err:
        logging.error(f"Error al guardar el aviso {data.get('aviso_id')}: {err}")
        conn.rollback()
    finally:
        cursor.close()
