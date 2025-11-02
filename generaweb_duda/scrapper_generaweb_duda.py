#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para GeneraWeb Duda
Este scrapper maneja autenticación y extrae información de empresas
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

class GeneraWebDudaScraper:
    def __init__(self, base_url="http://generawebduda.nlocal.com", headless=True):
        self.base_url = base_url
        self.login_url = urljoin(base_url, "/index.php")
        # URL base para empresas (se construirá dinámicamente por página)
        self.base_empresas_url = urljoin(base_url, "/index.php")
        self.count = 1000
        # URL base para perfiles de empresas
        self.profile_base_url = "http://generawebduda.nlocal.com"
        self.driver = None
        self.headless = headless
        
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
            
            # Intentar inicializar el driver
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✓ Driver de Chrome inicializado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al inicializar el driver de Chrome: {e}")
            logger.info("Asegúrate de tener Chrome y chromedriver instalados")
            logger.info("Instalar chromedriver: brew install chromedriver (Mac) o descarga desde https://chromedriver.chromium.org/")
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
                "input[value*='Iniciar']",
                "button",
                "input[type='button']"
            ]
            
            for selector in button_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            login_button = button
                            logger.info(f"✓ Botón encontrado con selector: {selector}")
                            break
                    if login_button:
                        break
                except NoSuchElementException:
                    continue
            
            if login_button:
                login_button.click()
                logger.info("✓ Formulario de login enviado")
            else:
                # Si no encuentra botón, intentar con Enter
                password_field.send_keys(Keys.RETURN)
                logger.info("✓ Login enviado con Enter")
            
            # Esperar a que cargue la página después del login
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            # Verificar indicadores de login exitoso
            login_success_indicators = [
                "empresas" in current_url,
                "dashboard" in current_url,
                "panel" in current_url,
                "logout" in page_source,
                "salir" in page_source,
                "cerrar sesión" in page_source
            ]
            
            if any(login_success_indicators):
                logger.info("✓ Login exitoso")
                return True
            else:
                logger.warning("⚠ Posible fallo en el login")
                logger.info(f"URL actual: {current_url}")
                return False
                
        except TimeoutException:
            logger.error("Timeout esperando elementos de login")
            return False
        except Exception as e:
            logger.error(f"Error durante el login: {e}")
            return False
    
    def navigate_to_empresas(self):
        """Navega a la página de empresas y ejecuta la búsqueda"""
        try:
            logger.info(f"Navegando a: {self.empresas_url}")
            self.driver.get(self.empresas_url)
            time.sleep(3)
            
            # Buscar y hacer clic en el botón de búsqueda si existe
            try:
                search_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit'][value*='Buscar']"))
                )
                search_button.click()
                logger.info("✓ Botón de búsqueda presionado")
                time.sleep(3)
            except TimeoutException:
                logger.info("No se encontró botón de búsqueda, continuando...")
            
            # Esperar a que cargue la tabla de resultados
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table.table"))
                )
                logger.info("✓ Tabla de resultados cargada")
            except TimeoutException:
                logger.warning("No se encontró tabla de resultados, continuando...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error navegando a empresas: {e}")
            return False
    
    def get_pagination_info(self):
        """Obtiene información sobre la paginación"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Buscar información de paginación en la tabla de navegación
            pagination_table = soup.find('table', class_='tablebackg')
            if pagination_table:
                # Buscar texto que contenga "Total:" y números de página
                pagination_text = pagination_table.get_text()
                logger.info(f"Texto de paginación encontrado: {pagination_text[:200]}...")
                
                # Extraer total de empresas
                import re
                total_match = re.search(r'Total:\s*(\d+)\s*Empresas', pagination_text)
                total_empresas = int(total_match.group(1)) if total_match else 0
                
                # Extraer página actual y total de páginas
                page_match = re.search(r'Página\s*(\d+)\s*de\s*(\d+)', pagination_text)
                current_page = int(page_match.group(1)) if page_match else 1
                total_pages = int(page_match.group(2)) if page_match else 1
                
                logger.info(f"Paginación detectada: {total_empresas} empresas en {total_pages} páginas")
                return {
                    'total_empresas': total_empresas,
                    'current_page': current_page,
                    'total_pages': total_pages
                }
            else:
                logger.warning("No se encontró la tabla de paginación con class 'tablebackg'")
                # Buscar en toda la página
                page_text = soup.get_text()
                logger.info(f"Buscando en toda la página: {page_text[:500]}...")
                
                # Buscar patrones alternativos
                import re
                total_match = re.search(r'Total:\s*(\d+)\s*Empresas', page_text)
                total_empresas = int(total_match.group(1)) if total_match else 0
                
                page_match = re.search(r'Página\s*(\d+)\s*de\s*(\d+)', page_text)
                current_page = int(page_match.group(1)) if page_match else 1
                total_pages = int(page_match.group(2)) if page_match else 1
                
                if total_empresas > 0:
                    logger.info(f"Paginación detectada (método alternativo): {total_empresas} empresas en {total_pages} páginas")
                    return {
                        'total_empresas': total_empresas,
                        'current_page': current_page,
                        'total_pages': total_pages
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo información de paginación: {e}")
            return None
    
    def navigate_to_page(self, page_number):
        """Navega a una página específica"""
        try:
            # Construir URL con parámetros optimizados
            base_url = "http://generawebduda.nlocal.com/index.php"
            params = {
                'ids': '',
                'searchCondition': 'CO',
                'name': '',
                'count': '1000',  # 1000 empresas por página
                'dateNewFrom': '',
                'dateNewTo': '',
                'search': 'Buscar',
                's': 'home',
                'page': str(page_number)
            }
            url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
            
            logger.info(f"Navegando a página {page_number}: {url}")
            self.driver.get(url)
            time.sleep(8)  # Tiempo para cargar 1000 empresas
            
            # Esperar a que cargue la tabla de resultados
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.table")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "table.tablebackg")),
                        EC.presence_of_element_located((By.TAG_NAME, "table"))
                    )
                )
                logger.info(f"✓ Página {page_number} cargada correctamente")
            except TimeoutException:
                logger.warning(f"No se encontró tabla en página {page_number}, continuando...")
            
            return True
            
        except TimeoutException:
            logger.error(f"Timeout esperando página {page_number}")
            return False
        except Exception as e:
            logger.error(f"Error navegando a página {page_number}: {e}")
            return False
    
    def extract_empresas_table(self):
        """Extrae los datos de la tabla de empresas"""
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            empresas = []
            
            # Buscar la tabla
            table = soup.find('table', class_='table')
            if not table:
                logger.error("No se encontró la tabla de empresas")
                return empresas
            
            # Buscar filas de datos (excluyendo el header)
            rows = table.find_all('tr', class_='new_platform')
            
            logger.info(f"Encontradas {len(rows)} empresas en la tabla")
            
            for row in rows:
                empresa_data = self.extract_empresa_data(row)
                if empresa_data:
                    empresas.append(empresa_data)
            
            return empresas
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de la tabla: {e}")
            return []
    
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
                # Entrada (segunda celda)
                if len(cells) > 1:
                    empresa['entrada'] = cells[1].get_text(strip=True)
                
                # Empresa (tercera celda)
                if len(cells) > 2:
                    empresa['empresa'] = cells[2].get_text(strip=True)
                
                # Estado (cuarta celda)
                if len(cells) > 3:
                    empresa['estado'] = cells[3].get_text(strip=True)
            
            # Extraer URLs de los enlaces
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
            
            logger.info(f"Extraída empresa: {empresa['empresa']} (ID: {empresa['id']})")
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
            
            # Extraer todos los campos del perfil usando los nombres exactos del HTML
            # Buscar todos los inputs y selects en el formulario
            form_elements = soup.find_all(['input', 'select', 'textarea'])
            
            logger.info(f"Total de elementos encontrados: {len(form_elements)}")
            
            # Log de depuración: mostrar todos los elementos encontrados
            for i, element in enumerate(form_elements[:10]):  # Solo los primeros 10
                name = element.get('name', '')
                value = element.get('value', '') or element.get_text(strip=True)
                logger.info(f"Elemento {i+1}: name='{name}', value='{value[:50]}...'")
            
            for element in form_elements:
                name = element.get('name', '')
                value = element.get('value', '') or element.get_text(strip=True)
                
                # Mapear nombres exactos de campos según el HTML proporcionado
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
                    # Gestor de proyecto
                    if element.name == 'select':
                        selected = element.find('option', selected=True)
                        if selected:
                            profile_data['gestor_proyecto'] = selected.get_text(strip=True)
            
            # Log de depuración para ver qué se extrajo
            logger.info(f"Datos extraídos del perfil: {profile_data}")
            
            logger.info(f"Perfil extraído para {profile_data.get('razon_social', 'Empresa sin nombre')}")
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
    
    def scrape_empresas_incremental(self, max_empresas=None, max_pages=None):
        """Función principal para hacer scraping de empresas con guardado incremental"""
        if not self.init_driver():
            return []
        
        try:
            # Login
            if not self.login("almudena.roman@nlocal.es", "aroman246"):
                logger.error("No se pudo realizar el login")
                return []
            
            total_empresas = 0
            
            # Procesar todas las páginas (1-4)
            for page_num in range(1, 5):  # Páginas 1, 2, 3, 4
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
                time.sleep(8)  # Tiempo para cargar 1000 empresas
                
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
                
                # Extraer empresas de la página actual
                empresas_pagina = self.extract_empresas_table()
                if not empresas_pagina:
                    logger.warning(f"No se encontraron empresas en la página {page_num}")
                    continue
                
                logger.info(f"✓ Extraídas {len(empresas_pagina)} empresas de la página {page_num}")
                
                # Procesar todos los registros de la página con guardado incremental
                empresas_procesadas = 0
                for i, empresa in enumerate(empresas_pagina, 1):
                    logger.info(f"Procesando empresa {i}/{len(empresas_pagina)} de la página {page_num}: {empresa.get('empresa', 'Sin nombre')}")
                    
                    # Extraer datos del perfil si existe
                    if empresa.get('id'):
                        # Construir URL del perfil con la nueva base URL
                        profile_url = f"{self.profile_base_url}/index.php?s=user_profile&id={empresa['id']}"
                        logger.info(f"Extrayendo perfil desde: {profile_url}")
                        
                        profile_data = self.extract_empresa_profile(empresa['id'], profile_url)
                        if profile_data:
                            empresa.update(profile_data)
                            logger.info("✓ Datos del perfil extraídos correctamente")
                        else:
                            logger.warning("⚠ No se pudieron extraer datos del perfil")
                    
                    # Guardar empresa inmediatamente
                    self.save_empresa_incremental(empresa)
                    empresas_procesadas += 1
                    total_empresas += 1
                    
                    # Pausa entre empresas para no sobrecargar el servidor
                    time.sleep(2)
            
                logger.info(f"✓ Página {page_num} completada: {empresas_procesadas} empresas procesadas y guardadas")
                
                # Pausa entre páginas
                if page_num < 4:  # Solo pausar si no es la última página
                    logger.info("Esperando antes de procesar la siguiente página...")
                    time.sleep(3)
            
            logger.info(f"\n{'='*60}")
            logger.info(f"SCRAPING COMPLETADO")
            logger.info(f"{'='*60}")
            logger.info(f"Total de empresas extraídas: {total_empresas}")
            logger.info(f"Páginas procesadas: 4 (todas las páginas)")
            
            return total_empresas
            
        except Exception as e:
            logger.error(f"Error durante el scraping: {e}")
            return []
        finally:
            self.close_driver()
    
    def save_to_csv(self, empresas, filename='generaweb_duda_empresas.csv'):
        """Guarda las empresas en CSV (append mode)"""
        if not empresas:
            logger.warning("No hay empresas para guardar")
            return
        
        # Verificar si el archivo existe para determinar si escribir header
        file_exists = os.path.exists(filename)
        
        with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                # Campos básicos de la tabla
                'id', 'empresa', 'entrada', 'estado',
                # Campos del perfil completo
                'nombre', 'apellidos', 'razon_social', 'login', 'password', 'cif_nif',
                'direccion', 'provincia', 'ciudad', 'codigo_postal', 'pais',
                'telefono', 'fax', 'telefono_movil', 'url', 'email',
                'num_dominios', 'wordpress_url', 'gestor_proyecto',
                # URLs
                'url_perfil', 'url_web', 'url_panel'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            # Solo escribir header si el archivo no existe
            if not file_exists:
                writer.writeheader()
                logger.info("✓ Header escrito en nuevo archivo CSV")
            else:
                logger.info("✓ Añadiendo datos al archivo CSV existente")
            
            for empresa in empresas:
                writer.writerow(empresa)
        
        logger.info(f"✓ {len(empresas)} empresas guardadas en {filename}")
    
    def save_empresa_incremental(self, empresa, filename='generaweb_duda_empresas.csv'):
        """Guarda una empresa inmediatamente al CSV (append mode)"""
        try:
            file_exists = os.path.exists(filename)
            
            with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
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
                if not file_exists:
                    writer.writeheader()
                    logger.info("✓ Header escrito en nuevo archivo CSV")
                
                writer.writerow(empresa)
                logger.info(f"✓ Empresa guardada: {empresa.get('empresa', 'Sin nombre')} (ID: {empresa.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Scraper de GeneraWeb Duda - CON PAGINACIÓN")
    logger.info("=" * 60)
    
    # Crear scraper (headless=False para ver el navegador, True para ocultarlo)
    scraper = GeneraWebDudaScraper(headless=True)
    
    # Realizar scraping completo con guardado incremental
    # Procesar todas las páginas (1-4) con guardado inmediato
    total_empresas = scraper.scrape_empresas_incremental(max_empresas=None, max_pages=4)  # Todas las empresas de 4 páginas
    
    if total_empresas > 0:
        logger.info("")
        logger.info(f"✓ Total de empresas extraídas: {total_empresas}")
        logger.info("✓ Todas las empresas se guardaron incrementalmente en el CSV")
        logger.info("✓ Archivo CSV: generaweb_duda_empresas.csv")
        
    else:
        logger.warning("")
        logger.warning("⚠ No se encontraron empresas")
        logger.info("")
        logger.info("Posibles causas:")
        logger.info("1. Error en el login")
        logger.info("2. La tabla no se cargó correctamente")
        logger.info("3. Los selectores CSS necesitan ajuste")
        logger.info("4. Problemas de paginación")

if __name__ == "__main__":
    main()
