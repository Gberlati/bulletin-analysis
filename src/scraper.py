import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import database
from config import (
    BASE_URL, 
    START_AVISO_ID, 
    SLEEP_INTERVAL_SECONDS, 
    RETRY_ON_EMPTY_SECONDS,
    NUM_THREADS,
    BATCH_SIZE
)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

def parse_date(date_str):
    """Parses a date in 'dd/mm/yyyy' format to 'yyyy-mm-dd'."""
    try:
        date_part = date_str.split(' ')[-1]
        return datetime.strptime(date_part, '%d/%m/%Y').strftime('%Y-%m-%d')
    except (ValueError, IndexError):
        logging.warning(f"Could not parse date: {date_str}")
        return None

def scrape_aviso(aviso_id_str):
    """Scrapes an individual notice and extracts its information."""
    url = BASE_URL.format(aviso_id=aviso_id_str)
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'lxml')

    if soup.find('iframe', id='iframeContingencia'):
        logging.warning(f"Notice {aviso_id_str} contains a contingency PDF. Skipping.")
        return {'status': 'skipped_pdf'}
    
    # Check for "aviso no encontrado" message
    if "aviso no encontrado" in response.text:
        logging.warning(f"Notice {aviso_id_str} not found.")
        return {'status': 'not_found'}

    try:
        seccion = soup.select_one('h2.title-busqueda small').get_text(strip=True)
        
        breadcrumb_links = soup.select('ol.breadcrumb li a')
        rubro_link = breadcrumb_links[1]
        rubro = rubro_link.get_text(strip=True)

        raw_sociedad_text = soup.find(id='tituloDetalleAviso').select_one('h1').get_text()
        sociedad = ' '.join(raw_sociedad_text.split())
        
        parsed_url = urlparse(rubro_link['href'])
        id_rubro = parse_qs(parsed_url.query).get('rubro', [None])[0]

        cuerpo_div = soup.find(id='cuerpoDetalleAviso')
        detalle_aviso_texto = ""

        if cuerpo_div:
            for style_tag in cuerpo_div.find_all('style'):
                style_tag.decompose()
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
        logging.error(f"Error parsing notice {aviso_id_str}: {e}")
        return None

def scrape_and_save_worker(aviso_id_str, conn, db_lock):
    """Worker function for threads: scrapes a notice and saves it."""
    data = scrape_aviso(aviso_id_str)
    
    if data and data['status'] == 'success':
        with db_lock:
            database.save_aviso(conn, data)
    elif data and data['status'] in ['skipped_pdf', 'not_found']:
        pass # Logging is handled in scrape_aviso
    else:
        # Error during request or parsing
        pass

def main():
    """Main function to orchestrate the scraping process with multithreading."""
    conn = database.get_db_connection()
    if not conn:
        return

    database.setup_database(conn)
    db_lock = threading.Lock()

    last_id = database.get_last_aviso_id(conn)
    current_id = last_id + 1 if last_id > 0 else START_AVISO_ID
    logging.info(f"Starting scraper from notice ID: {current_id} with {NUM_THREADS} threads.")

    with ThreadPoolExecutor(max_workers=NUM_THREADS, thread_name_prefix='Scraper') as executor:
        while True:
            # Generate a list of aviso IDs for the current batch
            aviso_ids_to_process = [f"A{i}" for i in range(current_id, current_id + BATCH_SIZE)]
            
            # Submit tasks to the thread pool
            future_to_aviso = {executor.submit(scrape_and_save_worker, aviso_id, conn, db_lock): aviso_id for aviso_id in aviso_ids_to_process}

            # Process futures as they complete
            for future in as_completed(future_to_aviso):
                aviso_id = future_to_aviso[future]
                try:
                    future.result()  # retrieve result or raise exception if one occurred
                except Exception as exc:
                    logging.error(f'{aviso_id} generated an exception: {exc}')

            logging.info(f"Batch starting from {current_id} processed.")
            current_id += BATCH_SIZE
            time.sleep(SLEEP_INTERVAL_SECONDS)

    conn.close()

if __name__ == '__main__':
    main()
