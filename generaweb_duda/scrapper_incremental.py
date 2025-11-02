#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para GeneraWeb Duda - Versión Incremental
Este scrapper guarda cada empresa inmediatamente al CSV conforme la procesa
URL: http://generawebduda.nlocal.com/index.php
"""

import csv
import time
import logging
import os
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneraWebDudaScraperIncremental:
    def __init__(self, base_url="http://generawebduda.nlocal.com", headless=True):
        self.base_url = base_url
        self.login_url = urljoin(base_url, "/index.php")
        self.base_empresas_url = urljoin(base_url, "/index.php")
        self.count = 1000
        self.profile_base_url = "http://generawebduda.nlocal.com"
        self.driver = None
        self.headless = headless
        self.csv_filename = 'generaweb_duda_empresas.csv'
        self.file_exists = os.path.exists(self.csv_filename)
        
    def init_driver(self):
        """Inicializa el driver de Selenium"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✓ Driver de Chrome inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar el driver de Chrome: {e}")
            return False
    
    def close_driver(self):
        """Cierra el driver de Selenium"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver cerrado")
    
    def login(self, username, password):
        """Realiza el login en el sistema"""
        try:
            logger.info(f"Iniciando sesión en: {self.login_url}")
            self.driver.get(self.login_url)
            time.sleep(5)
            
            # Buscar campos de login
            username_field = None
            password_field = None
            
            try:
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "usuario"))
                )
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("✓ Campos encontrados por name")
            except TimeoutException:
                # Buscar por tipo de input
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for input_elem in inputs:
                    input_type = input_elem.get_attribute("type")
                    if input_type == "text":
                        username_field = input_elem
                    elif input_type == "password":
                        password_field = input_elem
            
            if not username_field or not password_field:
                logger.error("No se pudieron encontrar los campos de login")
                return False
            
            # Llenar campos
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            # Buscar botón de login
            login_button = None
            button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='Entrar']",
                "button"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            break
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                login_button.click()
            else:
                password_field.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Verificar login exitoso
            current_url = self.driver.current_url
            if "empresas" in current_url or "dashboard" in current_url:
                logger.info("✓ Login exitoso")
                return True
            else:
                logger.warning("⚠ Posible fallo en el login")
                return False
                
        except Exception as e:
            logger.error(f"Error durante el login: {e}")
            return False
    
    def save_empresa_incremental(self, empresa):
        """Guarda una empresa inmediatamente al CSV"""
        try:
            with open(self.csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'empresa', 'entrada', 'estado',
                    'nombre', 'apellidos', 'razon_social', 'login', 'password', 'cif_nif',
                    'direccion', 'provincia', 'ciudad', 'codigo_postal', 'pais',
                    'telefono', 'fax', 'telefono_movil', 'url', 'email',
                    'num_dominios', 'wordpress_url', 'gestor_proyecto',
                    'url_perfil', 'url_web', 'url_panel'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                # Solo escribir header si el archivo no existe
                if not self.file_exists:
                    writer.writeheader()
                    self.file_exists = True
                    logger.info("✓ Header escrito en nuevo archivo CSV")
                
                writer.writerow(empresa)
                logger.info(f"✓ Empresa guardada: {empresa.get('empresa', 'Sin nombre')} (ID: {empresa.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")
    
    def scrape_page_incremental(self, page_number):
        """Extrae empresas de una página específica y las guarda inmediatamente"""
        try:
            # Construir URL para la página específica
            params = {
                'ids': '',
                'searchCondition': 'CO',
                'name': '',
                'count': str(self.count),
                'dateNewFrom': '',
                'dateNewTo': '',
                'search': 'Buscar',
                's': 'home',
                'page': str(page_number)
            }
            url = f"{self.base_empresas_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"Navegando a página {page_number}: {url}")
            self.driver.get(url)
            time.sleep(8)
            
            # Esperar tabla de resultados
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")),
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                )
                logger.info(f"✓ Página {page_number} cargada correctamente")
            except TimeoutException:
                logger.warning(f"No se encontró tabla en página {page_number}")
                return 0
            
            # Extraer y procesar empresas una por una
            empresas_procesadas = self.extract_and_save_empresas_incremental()
            logger.info(f"✓ Página {page_number} completada: {empresas_procesadas} empresas procesadas y guardadas")
            
            return empresas_procesadas
            
        except Exception as e:
            logger.error(f"Error procesando página {page_number}: {e}")
            return 0
    
    def extract_and_save_empresas_incremental(self):
        """Extrae empresas de la tabla y las guarda una por una"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            empresas_procesadas = 0
            
            table = soup.find('table', class_='table')
            if not table:
                logger.error("No se encontró la tabla de empresas")
                return 0
            
            rows = table.find_all('tr', class_='new_platform')
            logger.info(f"Encontradas {len(rows)} empresas en la tabla")
            
            for i, row in enumerate(rows, 1):
                logger.info(f"Procesando empresa {i}/{len(rows)}")
                
                empresa_data = self.extract_empresa_data(row)
                if empresa_data:
                    # Guardar inmediatamente
                    self.save_empresa_incremental(empresa_data)
                    empresas_procesadas += 1
                    
                    # Pausa entre empresas
                    time.sleep(1)
            
            return empresas_procesadas
            
        except Exception as e:
            logger.error(f"Error extrayendo empresas: {e}")
            return 0
    
    def extract_empresa_data(self, row):
        """Extrae datos de una fila de empresa"""
        try:
            empresa = {
                'id': '',
                'entrada': '',
                'empresa': '',
                'estado': '',
                'url_perfil': '',
                'url_web': '',
                'url_panel': ''
            }
            
            # Extraer ID
            id_cell = row.find('td', class_='first_td')
            if id_cell:
                empresa['id'] = id_cell.get_text(strip=True)
            
            # Extraer datos de las celdas
            cells = row.find_all('td', class_='line')
            
            if len(cells) >= 4:
                if len(cells) > 1:
                    empresa['entrada'] = cells[1].get_text(strip=True)
                if len(cells) > 2:
                    empresa['empresa'] = cells[2].get_text(strip=True)
                if len(cells) > 3:
                    empresa['estado'] = cells[3].get_text(strip=True)
            
            # Extraer URLs
            links = row.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href:
                    if 'user_profile' in href:
                        empresa['url_perfil'] = urljoin(self.base_url, href)
                    elif 'http://www.' in href or 'https://www.' in href:
                        empresa['url_web'] = href
                    elif 'panelcontrol' in href:
                        empresa['url_panel'] = urljoin(self.base_url, href)
            
            return empresa
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de empresa: {e}")
            return None

def main():
    """Función principal - Procesa páginas con guardado incremental"""
    import sys
    
    if len(sys.argv) > 1:
        start_page = int(sys.argv[1])
        end_page = int(sys.argv[2]) if len(sys.argv) > 2 else start_page
    else:
        start_page = 1
        end_page = 1
    
    logger.info("=" * 60)
    logger.info(f"Scraper de GeneraWeb Duda - INCREMENTAL")
    logger.info(f"Páginas: {start_page} a {end_page}")
    logger.info("=" * 60)
    
    scraper = GeneraWebDudaScraperIncremental(headless=True)
    
    if not scraper.init_driver():
        logger.error("No se pudo inicializar el driver")
        return
    
    try:
        # Login
        if not scraper.login("almudena.roman@nlocal.es", "aroman246"):
            logger.error("No se pudo realizar el login")
            return
        
        total_empresas = 0
        
        # Procesar cada página
        for page_num in range(start_page, end_page + 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"PROCESANDO PÁGINA {page_num}")
            logger.info(f"{'='*50}")
            
            empresas_pagina = scraper.scrape_page_incremental(page_num)
            total_empresas += empresas_pagina
            
            # Pausa entre páginas
            if page_num < end_page:
                logger.info("Esperando antes de procesar la siguiente página...")
                time.sleep(3)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPING COMPLETADO")
        logger.info(f"{'='*60}")
        logger.info(f"Total de empresas procesadas: {total_empresas}")
        logger.info(f"Archivo CSV: {scraper.csv_filename}")
    
    except Exception as e:
        logger.error(f"Error durante el scraping: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
