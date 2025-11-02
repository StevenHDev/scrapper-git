#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para GeneraWeb Duda - DOMINIOS
Este scrapper extrae información de dominios desde la sección domain_queue
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

class GeneraWebDudaScraperDominios:
    def __init__(self, base_url="http://generawebduda.nlocal.com", headless=True):
        self.base_url = base_url
        self.login_url = urljoin(base_url, "/index.php")
        self.base_dominios_url = urljoin(base_url, "/index.php")
        self.count = 1000
        self.profile_base_url = "http://generawebduda.nlocal.com"
        self.driver = None
        self.headless = headless
        self.csv_filename = 'generaweb_duda_dominios.csv'
        
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
            
            # Debug: imprimir el HTML para ver la estructura
            logger.info("Analizando estructura de la página de login...")
            
            # Buscar campos de login con múltiples estrategias
            username_field = None
            password_field = None
            
            # Estrategia 1: Buscar por name
            try:
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, "usuario"))
                )
                password_field = self.driver.find_element(By.NAME, "password")
                logger.info("✓ Campos encontrados por name")
            except TimeoutException:
                pass
            
            # Estrategia 2: Buscar por input type
            if not username_field or not password_field:
                try:
                    inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.info(f"Encontrados {len(inputs)} campos input")
                    
                    for input_elem in inputs:
                        input_type = input_elem.get_attribute("type")
                        input_name = input_elem.get_attribute("name") or ""
                        input_id = input_elem.get_attribute("id") or ""
                        
                        logger.info(f"Input: type={input_type}, name={input_name}, id={input_id}")
                        
                        if input_type == "text" and ("usuario" in input_name.lower() or "user" in input_name.lower() or "login" in input_name.lower()):
                            username_field = input_elem
                            logger.info("✓ Campo usuario encontrado por tipo text")
                        elif input_type == "password":
                            password_field = input_elem
                            logger.info("✓ Campo password encontrado")
                except Exception as e:
                    logger.warning(f"Error en estrategia 2: {e}")
            
            # Estrategia 3: Buscar por placeholder o label
            if not username_field or not password_field:
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    for input_elem in all_inputs:
                        placeholder = input_elem.get_attribute("placeholder") or ""
                        if "usuario" in placeholder.lower() or "user" in placeholder.lower():
                            username_field = input_elem
                        elif "contraseña" in placeholder.lower() or "password" in placeholder.lower():
                            password_field = input_elem
                except Exception as e:
                    logger.warning(f"Error en estrategia 3: {e}")
            
            if not username_field or not password_field:
                logger.error("No se pudieron encontrar los campos de login")
                logger.info("Estructura HTML de la página:")
                logger.info(self.driver.page_source[:1000])
                return False
            
            # Llenar campos
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            logger.info("✓ Campos llenados correctamente")
            
            # Buscar y hacer clic en el botón de login
            login_button = None
            button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "input[value*='Entrar']",
                "input[value*='Login']",
                "button"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            logger.info(f"✓ Botón de login encontrado: {selector}")
                            break
                    if login_button:
                        break
                except Exception as e:
                    logger.warning(f"Error buscando botón con selector {selector}: {e}")
                    continue
            
            if login_button:
                login_button.click()
                logger.info("✓ Botón de login clickeado")
            else:
                logger.info("No se encontró botón, intentando con Enter")
                password_field.send_keys(Keys.RETURN)
            
            time.sleep(8)
            
            # Verificar login exitoso
            current_url = self.driver.current_url
            logger.info(f"URL después del login: {current_url}")
            
            # Verificar si hay elementos que indiquen login exitoso
            try:
                # Buscar elementos que indiquen que estamos logueados
                if "empresas" in current_url or "dashboard" in current_url or "domain_queue" in current_url:
                    logger.info("✓ Login exitoso - URL indica acceso correcto")
                    return True
                elif "login" not in current_url.lower() and "index.php" in current_url:
                    logger.info("✓ Login exitoso - No hay redirección a login")
                    return True
                else:
                    logger.warning("⚠ Posible fallo en el login - Verificando elementos de la página")
                    # Verificar si hay elementos de la página principal
                    if self.driver.find_elements(By.CSS_SELECTOR, "table.table"):
                        logger.info("✓ Login exitoso - Tabla encontrada en la página")
                        return True
                    else:
                        logger.warning("⚠ No se encontró tabla, posible fallo en login")
                        return False
            except Exception as e:
                logger.error(f"Error verificando login: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error durante el login: {e}")
            return False
    
    def save_dominio_incremental(self, dominio):
        """Guarda un dominio inmediatamente al CSV"""
        try:
            file_exists = os.path.exists(self.csv_filename)
            
            with open(self.csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'entrada', 'empresa', 'dominio', 'estado',
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
                
                writer.writerow(dominio)
                logger.info(f"✓ Dominio guardado: {dominio.get('dominio', 'Sin dominio')} (ID: {dominio.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")
    
    def save_table_dominios_incremental(self, dominios, filename='generaweb_duda_table_dominios.csv'):
        """Guarda dominios extraídos de la tabla HTML en un CSV específico"""
        try:
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'empresa', 'dominio', 'url_web', 'principal', 
                    'plataforma_correo', 'cuentas_correo', 'url_perfil'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                if not file_exists:
                    writer.writeheader()
                    logger.info("✓ Header escrito en nuevo archivo CSV de tabla")
                
                for dominio in dominios:
                    writer.writerow(dominio)
                    logger.info(f"✓ Dominio de tabla guardado: {dominio.get('empresa', 'Sin empresa')} - {dominio.get('dominio', 'Sin dominio')} (ID: {dominio.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando dominios de tabla: {e}")
    
    def extract_dominio_data(self, row):
        """Extrae datos de una fila de dominio"""
        try:
            dominio = {
                'id': '',
                'entrada': '',
                'empresa': '',
                'dominio': '',
                'estado': '',
                'url_perfil': '',
                'url_web': '',
                'url_panel': ''
            }
            
            # Extraer ID
            id_cell = row.find('td', class_='first_td')
            if id_cell:
                dominio['id'] = id_cell.get_text(strip=True)
            
            # Extraer datos de las celdas
            cells = row.find_all('td', class_='line')
            
            if len(cells) >= 4:
                if len(cells) > 1:
                    dominio['entrada'] = cells[1].get_text(strip=True)
                if len(cells) > 2:
                    dominio['empresa'] = cells[2].get_text(strip=True)
                if len(cells) > 3:
                    dominio['dominio'] = cells[3].get_text(strip=True)
                if len(cells) > 4:
                    dominio['estado'] = cells[4].get_text(strip=True)
            
            # Extraer URLs
            links = row.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href:
                    if 'user_profile' in href:
                        dominio['url_perfil'] = urljoin(self.base_url, href)
                    elif 'http://www.' in href or 'https://www.' in href:
                        dominio['url_web'] = href
                    elif 'panelcontrol' in href:
                        dominio['url_panel'] = urljoin(self.base_url, href)
            
            return dominio
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de empresa: {e}")
            return None
    
    def extract_table_data_from_html(self, html_content):
        """Extrae datos de la tabla HTML específica con estructura de dominios"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table', class_='table')
            
            if not table:
                logger.warning("No se encontró tabla con class 'table'")
                return []
            
            dominios = []
            
            # Buscar todas las filas de datos (excluyendo el header)
            rows = table.find_all('tr')
            
            for row in rows:
                # Saltar el header y filas vacías
                if not row.find('td', class_='line'):
                    continue
                
                # Extraer datos de cada fila
                cells = row.find_all('td', class_='line')
                
                if len(cells) >= 6:  # Verificar que tenga todas las columnas necesarias
                    dominio = {
                        'id': cells[0].get_text(strip=True),
                        'empresa': cells[1].get_text(strip=True),
                        'dominio': '',
                        'principal': cells[3].get_text(strip=True),
                        'plataforma_correo': '',
                        'cuentas_correo': '',
                        'url_perfil': ''
                    }
                    
                    # Extraer dominio del enlace
                    dominio_link = cells[2].find('a')
                    if dominio_link:
                        dominio['dominio'] = dominio_link.get_text(strip=True)
                        dominio['url_web'] = dominio_link.get('href', '')
                    
                    # Extraer información de plataforma de correo
                    select_element = cells[4].find('select')
                    if select_element:
                        selected_option = select_element.find('option', selected=True)
                        if selected_option:
                            dominio['plataforma_correo'] = selected_option.get_text(strip=True)
                    
                    # Extraer número de cuentas de correo
                    texto_plataforma = cells[4].get_text(strip=True)
                    if '(' in texto_plataforma and ')' in texto_plataforma:
                        import re
                        match = re.search(r'\((\d+)\s+cuentas?\)', texto_plataforma)
                        if match:
                            dominio['cuentas_correo'] = match.group(1)
                    
                    # Extraer URL del perfil
                    perfil_link = cells[5].find('a')
                    if perfil_link:
                        onclick = perfil_link.get('onclick', '')
                        if 'domain_profile' in onclick:
                            # Extraer ID del dominio del onclick
                            import re
                            match = re.search(r"id=(\d+)", onclick)
                            if match:
                                dominio_id = match.group(1)
                                dominio['url_perfil'] = f"{self.profile_base_url}/index.php?s=domain_profile&id={dominio_id}"
                    
                    dominios.append(dominio)
                    logger.info(f"✓ Dominio extraído: {dominio['empresa']} - {dominio['dominio']} (ID: {dominio['id']})")
            
            return dominios
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de la tabla HTML: {e}")
            return []
    
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
    
    def scrape_dominios(self, start_page=1):
        """Extrae información de dominios desde la sección domain_queue"""
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
                
                # Construir URL para la página específica de dominios
                params = {
                    'ids': '',
                    'searchCondition': 'CO',
                    'name': '',
                    'domain': '',
                    'count': str(self.count),
                    'search': 'Buscar',
                    's': 'domain_queue',
                    'page': str(page_num)
                }
                url = f"{self.base_dominios_url}?" + "&".join([f"{k}={v}" for k, v in params.items()]) + "#empresas"
                
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
                
                # Extraer dominios de la página actual usando la nueva función
                dominios_pagina = self.extract_table_data_from_html(self.driver.page_source)
                logger.info(f"Encontrados {len(dominios_pagina)} dominios en la página {page_num}")
                
                dominios_nuevos_pagina = 0
                
                for i, dominio_data in enumerate(dominios_pagina, 1):
                    if not dominio_data or not dominio_data.get('id'):
                        continue
                    
                    dominio_id = int(dominio_data['id'])
                    
                    # Verificar si ya fue procesado
                    if dominio_id in processed_ids:
                        logger.info(f"Dominio {dominio_id} ya procesado, saltando...")
                        continue
                    
                    logger.info(f"Procesando dominio nuevo {i}/{len(dominios_pagina)}: {dominio_data.get('empresa', 'Sin empresa')} - {dominio_data.get('dominio', 'Sin dominio')} (ID: {dominio_id})")
                    
                    # Guardar dominio inmediatamente usando la función específica para tabla
                    self.save_table_dominios_incremental([dominio_data])
                    dominios_nuevos_pagina += 1
                    total_empresas_nuevas += 1
                    
                    # Pausa entre dominios
                    time.sleep(2)
                
                logger.info(f"✓ Página {page_num} completada: {dominios_nuevos_pagina} dominios nuevos procesados")
                
                # Si no hay dominios nuevos en esta página, continuar con la siguiente
                if dominios_nuevos_pagina == 0:
                    logger.info("No hay dominios nuevos en esta página, continuando...")
                    continue
                
                # Pausa entre páginas
                if page_num < 4:
                    logger.info("Esperando antes de procesar la siguiente página...")
                    time.sleep(3)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"SCRAPING DE DOMINIOS COMPLETADO")
            logger.info(f"{'='*60}")
            logger.info(f"Total de dominios nuevos extraídos: {total_empresas_nuevas}")
            
            return total_empresas_nuevas
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            return 0
        finally:
            self.close_driver()
    
    def scrape_dominios_from_url(self, url):
        """Extrae dominios desde una URL específica usando la nueva función de extracción"""
        if not self.init_driver():
            return 0
        
        try:
            # Login
            if not self.login("almudena.roman@nlocal.es", "aroman246"):
                logger.error("No se pudo realizar el login")
                return 0
            
            logger.info(f"Navegando a URL: {url}")
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
                logger.info("✓ Página cargada correctamente")
            except TimeoutException:
                logger.warning("No se encontró tabla en la página")
                return 0
            
            # Extraer dominios usando la nueva función
            dominios = self.extract_table_data_from_html(self.driver.page_source)
            logger.info(f"Encontrados {len(dominios)} dominios en la página")
            
            if dominios:
                # Guardar todos los dominios
                self.save_table_dominios_incremental(dominios)
                logger.info(f"✓ {len(dominios)} dominios guardados en CSV")
            
            return len(dominios)
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            return 0
        finally:
            self.close_driver()

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Scraper de GeneraWeb Duda - DOMINIOS")
    logger.info("=" * 60)
    
    scraper = GeneraWebDudaScraperDominios(headless=True)
    
    # Extraer dominios desde la página 1
    total_dominios = scraper.scrape_dominios(start_page=1)
    
    if total_dominios > 0:
        logger.info("")
        logger.info(f"✓ Total de dominios extraídos: {total_dominios}")
        logger.info("✓ Todos los dominios se guardaron incrementalmente en el CSV")
        logger.info("✓ Archivo CSV: generaweb_duda_dominios.csv")
    else:
        logger.info("")
        logger.info("No se encontraron dominios nuevos para procesar")

if __name__ == "__main__":
    main()
