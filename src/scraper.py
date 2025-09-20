import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urlparse, parse_qs
from datetime import datetime

import database
from config import BASE_URL, START_AVISO_ID, SLEEP_INTERVAL_SECONDS, RETRY_ON_EMPTY_SECONDS

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_date(date_str):
    """Parsea una fecha en formato 'dd/mm/yyyy' a 'yyyy-mm-dd'."""
    try:
        # Extrae solo la fecha, ignorando el texto
        date_part = date_str.split(' ')[-1]
        return datetime.strptime(date_part, '%d/%m/%Y').strftime('%Y-%m-%d')
    except (ValueError, IndexError):
        logging.warning(f"No se pudo parsear la fecha: {date_str}")
        return None

def scrape_aviso(aviso_id_str):
    """Realiza el scraping de un aviso individual y extrae la información."""
    url = BASE_URL.format(aviso_id=aviso_id_str)
    logging.info(f"Intentando scrapear: {url}")

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error en la petición a {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    if soup.find('iframe', id='iframeContingencia'):
        logging.warning(f"El aviso {aviso_id_str} contiene un PDF de contingencia. Saltando.")
        return {'status': 'skipped_pdf'}

    try:
        # Extracción de datos
        seccion = soup.select_one('h2.title-busqueda small').get_text(strip=True)
        
        breadcrumb_links = soup.select('ol.breadcrumb li a')
        rubro_link = breadcrumb_links[1]
        rubro = rubro_link.get_text(strip=True)
        sociedad = soup.find(id='tituloDetalleAviso').select_one('h1').get_text(strip=True)
        
        # Extraer id_rubro de la URL del rubro
        parsed_url = urlparse(rubro_link['href'])
        id_rubro = parse_qs(parsed_url.query).get('rubro', [None])[0]

        cuerpo_div = soup.find(id='cuerpoDetalleAviso')
        detalle_aviso_texto = "" # Valor por defecto

        if cuerpo_div:
            # 1. Eliminar todas las etiquetas <style> que no aportan texto
            for style_tag in cuerpo_div.find_all('style'):
                style_tag.decompose()
            
            # 2. Extraer el texto, usando un salto de línea como separador y limpiando espacios
            detalle_aviso_texto = cuerpo_div.get_text(separator='\n', strip=True)

        
        fecha_str = soup.select_one('p.text-muted small').get_text(strip=True)
        fecha_publicacion = parse_date(fecha_str)

        return {
            'status': 'success',
            'aviso_id': aviso_id_str,
            'seccion': seccion,
            'sociedad': sociedad,
            'rubro': rubro,
            'id_rubro': id_rubro,
            'fecha_publicacion': fecha_publicacion,
            'detalle_aviso': detalle_aviso_texto,
        }
    except Exception as e:
        logging.error(f"Error al parsear el aviso {aviso_id_str}: {e}")
        return None

def main():
    """Función principal que orquesta el proceso de scraping."""
    conn = database.get_db_connection()
    if not conn:
        return

    database.setup_database(conn)

    last_id = database.get_last_aviso_id(conn)
    current_id = last_id + 1 if last_id > 0 else START_AVISO_ID
    logging.info(f"Iniciando scraper desde el ID de aviso: {current_id}")

    while True:
        aviso_id_str = f"A{current_id}"
        data = scrape_aviso(aviso_id_str)

        if data:
            if data['status'] == 'success':
                database.save_aviso(conn, data)
                current_id += 1
            elif data['status'] == 'skipped_pdf':
                logging.info(f"Aviso {aviso_id_str} saltado (PDF). Pasando al siguiente.")
                current_id += 1 # Avanzamos al siguiente ID
            elif data['status'] == 'not_found':
                logging.info(f"No hay más avisos. Esperando {RETRY_ON_EMPTY_SECONDS} segundos para reintentar.")
                time.sleep(RETRY_ON_EMPTY_SECONDS)
                # No incrementamos el ID, reintentamos el mismo en el próximo ciclo
        else:
            # Hubo un error de red o parseo, esperamos un poco antes de reintentar el mismo ID
            logging.error(f"Fallo al procesar {aviso_id_str}. Reintentando en 60 segundos.")
            time.sleep(60)

    conn.close()

if __name__ == '__main__':
    main()
