#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para GeneraWeb Duda - Continuar desde donde se quedó
Este scrapper continúa el scraping desde el último ID procesado
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

class GeneraWebDudaScraperContinuar:
    def __init__(self, base_url="http://generawebduda.nlocal.com", headless=True):
        self.base_url = base_url
        self.login_url = urljoin(base_url, "/index.php")
        self.base_empresas_url = urljoin(base_url, "/index.php")
        self.count = 1000
        self.profile_base_url = "http://generawebduda.nlocal.com"
        self.driver = None
        self.headless = headless
        self.csv_filename = 'generaweb_duda_empresas.csv'
        
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
    
    def get_last_processed_id(self):
        """Obtiene el último ID procesado del CSV"""
        try:
            if not os.path.exists(self.csv_filename):
                return 0
            
            with open(self.csv_filename, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                last_id = 0
                for row in reader:
                    if row.get('id') and row['id'].isdigit():
                        last_id = max(last_id, int(row['id']))
                return last_id
        except Exception as e:
            logger.error(f"Error leyendo último ID: {e}")
            return 0
    
    def get_processed_ids(self):
        """Obtiene todos los IDs ya procesados"""
        try:
            if not os.path.exists(self.csv_filename):
                return set()
            
            processed_ids = set()
            with open(self.csv_filename, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('id') and row['id'].isdigit():
                        processed_ids.add(int(row['id']))
            return processed_ids
        except Exception as e:
            logger.error(f"Error leyendo IDs procesados: {e}")
            return set()
    
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
            file_exists = os.path.exists(self.csv_filename)
            
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
                
                if not file_exists:
                    writer.writeheader()
                    logger.info("✓ Header escrito en nuevo archivo CSV")
                
                writer.writerow(empresa)
                logger.info(f"✓ Empresa guardada: {empresa.get('empresa', 'Sin nombre')} (ID: {empresa.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")
    
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
    
    def extract_empresa_profile(self, empresa_id, profile_url):
        """Extrae información detallada del perfil de una empresa"""
        try:
            logger.info(f"Extrayendo perfil de empresa ID: {empresa_id}")
            
            # Abrir perfil en nueva ventana
            self.driver.execute_script(f"window.open('{profile_url}', '_blank');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Esperar a que cargue
            time.sleep(3)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            profile_data = {}
            
            # Extraer todos los campos del perfil
            form_elements = soup.find_all(['input', 'select', 'textarea'])
            
            for element in form_elements:
                name = element.get('name', '')
                value = element.get('value', '') or element.get_text(strip=True)
                
                # Mapear nombres exactos de campos
                if name == 'Id':
                    profile_data['id'] = value
                elif name == 'Nombre':
                    profile_data['nombre'] = value
                elif name == 'Apellidos':
                    profile_data['apellidos'] = value
                elif name == 'RazonSocial':
                    profile_data['razon_social'] = value
                elif name == 'Login':
                    profile_data['login'] = value
                elif name == 'Password_No_Encriptado':
                    profile_data['password'] = value
                elif name == 'NifCif':
                    profile_data['cif_nif'] = value
                elif name == 'Direccion':
                    profile_data['direccion'] = value
                elif name == 'Provincia':
                    profile_data['provincia'] = value
                elif name == 'Ciudad':
                    profile_data['ciudad'] = value
                elif name == 'Cp':
                    profile_data['codigo_postal'] = value
                elif name == 'Pais':
                    profile_data['pais'] = value
                elif name == 'Telefono':
                    profile_data['telefono'] = value
                elif name == 'Fax':
                    profile_data['fax'] = value
                elif name == 'Telefono_movil':
                    profile_data['telefono_movil'] = value
                elif name == 'Url':
                    profile_data['url'] = value
                elif name == 'Email':
                    profile_data['email'] = value
                elif name == 'NumDomains':
                    profile_data['num_dominios'] = value
                elif name == 'UrlAdminWordPress':
                    profile_data['wordpress_url'] = value
                elif name == 'id_gp':
                    if element.name == 'select':
                        selected = element.find('option', selected=True)
                        if selected:
                            profile_data['gestor_proyecto'] = selected.get_text(strip=True)
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error extrayendo perfil: {e}")
            return None
        finally:
            # Cerrar ventana del perfil y volver a la principal
            try:
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
    
    def scrape_empresas_continuar(self, start_page=1):
        """Continúa el scraping desde donde se quedó"""
        if not self.init_driver():
            return 0
        
        try:
            # Login
            if not self.login("almudena.roman@nlocal.es", "aroman246"):
                logger.error("No se pudo realizar el login")
                return 0
            
            # Obtener IDs ya procesados
            processed_ids = self.get_processed_ids()
            logger.info(f"IDs ya procesados: {len(processed_ids)}")
            
            total_empresas_nuevas = 0
            
            # Procesar páginas desde donde se quedó
            for page_num in range(start_page, 5):  # Páginas 1-4
                logger.info(f"\n{'='*50}")
                logger.info(f"PROCESANDO PÁGINA {page_num}")
                logger.info(f"{'='*50}")
                
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
                    'page': str(page_num)
                }
                url = f"{self.base_empresas_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
                
                logger.info(f"Navegando a página {page_num}: {url}")
                self.driver.get(url)
                time.sleep(8)
                
                # Esperar a que cargue la tabla de resultados
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "table.tablebackg")),
                            EC.presence_of_element_located((By.TAG_NAME, "table"))
                        )
                    )
                    logger.info(f"✓ Página {page_num} cargada correctamente")
                except TimeoutException:
                    logger.warning(f"No se encontró tabla en página {page_num}, continuando...")
                    continue
                
                # Extraer empresas de la página actual
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                table = soup.find('table', class_='table')
                if not table:
                    logger.warning(f"No se encontró tabla en página {page_num}")
                    continue
                
                rows = table.find_all('tr', class_='new_platform')
                logger.info(f"Encontradas {len(rows)} empresas en la página {page_num}")
                
                empresas_nuevas_pagina = 0
                
                for i, row in enumerate(rows, 1):
                    empresa_data = self.extract_empresa_data(row)
                    if not empresa_data or not empresa_data.get('id'):
                        continue
                    
                    empresa_id = int(empresa_data['id'])
                    
                    # Verificar si ya fue procesada
                    if empresa_id in processed_ids:
                        logger.info(f"Empresa {empresa_id} ya procesada, saltando...")
                        continue
                    
                    logger.info(f"Procesando empresa nueva {i}/{len(rows)}: {empresa_data.get('empresa', 'Sin nombre')} (ID: {empresa_id})")
                    
                    # Extraer datos del perfil
                    if empresa_data.get('id'):
                        profile_url = f"{self.profile_base_url}/index.php?s=user_profile&id={empresa_data['id']}"
                        profile_data = self.extract_empresa_profile(empresa_data['id'], profile_url)
                        if profile_data:
                            empresa_data.update(profile_data)
                            logger.info("✓ Datos del perfil extraídos correctamente")
                    
                    # Guardar empresa inmediatamente
                    self.save_empresa_incremental(empresa_data)
                    empresas_nuevas_pagina += 1
                    total_empresas_nuevas += 1
                    
                    # Pausa entre empresas
                    time.sleep(2)
                
                logger.info(f"✓ Página {page_num} completada: {empresas_nuevas_pagina} empresas nuevas procesadas")
                
                # Si no hay empresas nuevas en esta página, continuar con la siguiente
                if empresas_nuevas_pagina == 0:
                    logger.info("No hay empresas nuevas en esta página, continuando...")
                    continue
                
                # Pausa entre páginas
                if page_num < 4:
                    logger.info("Esperando antes de procesar la siguiente página...")
                    time.sleep(3)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"SCRAPING COMPLETADO")
            logger.info(f"{'='*60}")
            logger.info(f"Total de empresas nuevas extraídas: {total_empresas_nuevas}")
            
            return total_empresas_nuevas
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            return 0
        finally:
            self.close_driver()

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Scraper de GeneraWeb Duda - CONTINUAR")
    logger.info("=" * 60)
    
    scraper = GeneraWebDudaScraperContinuar(headless=False)
    
    # Continuar desde la página 1 (el scrapper detectará automáticamente los IDs ya procesados)
    total_empresas = scraper.scrape_empresas_continuar(start_page=1)
    
    if total_empresas > 0:
        logger.info("")
        logger.info(f"✓ Total de empresas nuevas extraídas: {total_empresas}")
        logger.info("✓ Todas las empresas se guardaron incrementalmente en el CSV")
        logger.info("✓ Archivo CSV: generaweb_duda_empresas.csv")
    else:
        logger.info("")
        logger.info("No se encontraron empresas nuevas para procesar")

if __name__ == "__main__":
    main()
