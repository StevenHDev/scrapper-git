#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para Bombas Bloch usando Selenium
Este scrapper maneja contenido dinámico cargado con JavaScript
URL: https://www.bombasbloch.com/productos
"""

import csv
import time
import logging
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BombasBlochSeleniumScraper:
    def __init__(self, base_url="https://www.bombasbloch.com", headless=True):
        self.base_url = base_url
        self.productos_url = urljoin(base_url, "/productos")
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
    
    def get_page_with_wait(self, url, wait_time=10):
        """Obtiene una página y espera a que cargue el contenido"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Espera inicial para que cargue JavaScript
            
            # Esperar a que el contenido principal cargue
            WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            return self.driver.page_source
            
        except TimeoutException:
            logger.warning(f"Timeout esperando contenido en: {url}")
            return self.driver.page_source if self.driver else None
        except Exception as e:
            logger.error(f"Error cargando página {url}: {e}")
            return None
    
    def extract_categories(self, html_content):
        """Extrae las categorías de productos desde la página principal"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []
        seen_urls = set()
        
        # Buscar enlaces de categorías
        category_links = soup.find_all('a', href=lambda x: x and '/productos/Catalog/listing/' in x)
        
        for link in category_links:
            category_name = link.get_text(strip=True)
            category_url = urljoin(self.base_url, link.get('href'))
            
            if category_name and category_url and category_url not in seen_urls:
                categories.append({
                    'nombre': category_name,
                    'url': category_url
                })
                seen_urls.add(category_url)
        
        return categories
    
    def extract_catalog_items(self, html_content):
        """Extrae los elementos del catálogo desde el HTML"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        
        # Verificar si hay mensaje de "no hay productos"
        no_products = soup.find('div', class_='no-products')
        if no_products:
            return []  # Esta categoría está vacía
        
        # Buscar productos/categorías en la estructura de Bombas Bloch
        # Los elementos están en <li> con id que empieza con "cid_" o "iid_"
        product_items = soup.find_all('li', id=lambda x: x and (x.startswith('cid_') or x.startswith('iid_')))
        
        if product_items:
            logger.info(f"Encontrados {len(product_items)} productos en la página")
        else:
            # Fallback: buscar otras estructuras posibles
            product_selectors = [
                '.item_prod',
                '.product-item',
                '.product',
                'li.product',
                '[data-product-id]'
            ]
            
            for selector in product_selectors:
                product_items = soup.select(selector)
                if product_items:
                    logger.info(f"Encontrados {len(product_items)} productos usando selector: {selector}")
                    break
        
        for item_element in product_items:
            item_data = self.extract_item_data(item_element)
            if item_data and (item_data['titulo'] or item_data['imagen_principal']):
                items.append(item_data)
        
        return items
    
    def extract_item_data(self, element):
        """Extrae datos de un elemento de producto"""
        item = {
            'titulo': '',
            'codigo': '',
            'sku': '',
            'imagen_principal': '',
            'url_imagen_principal': '',
            'precio': '',
            'enlace_detalle': '',
            'descripcion_corta': '',
            'categoria': ''
        }
        
        try:
            # Extraer ID del elemento como código
            element_id = element.get('id', '')
            if element_id:
                item['codigo'] = element_id
                item['sku'] = element_id
            
            # Extraer título - buscar en h3 > a (estructura de Bombas Bloch)
            title_elem = element.find('h3')
            if title_elem:
                link = title_elem.find('a')
                if link:
                    item['titulo'] = link.get_text(strip=True)
                    href = link.get('href')
                    if href and not href.startswith('#'):
                        item['enlace_detalle'] = urljoin(self.base_url, href)
                else:
                    item['titulo'] = title_elem.get_text(strip=True)
            
            # Si no hay h3, buscar en h2 o elementos con clase title
            if not item['titulo']:
                title_elem = (
                    element.find('h2') or 
                    element.find(class_=lambda x: x and 'title' in x.lower())
                )
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        item['titulo'] = link.get_text(strip=True)
                    else:
                        item['titulo'] = title_elem.get_text(strip=True)
            
            # Si aún no hay enlace, buscar el primer enlace del elemento
            if not item['enlace_detalle']:
                link_elem = element.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href')
                    if href and not href.startswith('#'):
                        item['enlace_detalle'] = urljoin(self.base_url, link_elem.get('href'))
            
            # Extraer imagen
            img_elem = element.find('img')
            if img_elem:
                img_src = (
                    img_elem.get('src') or 
                    img_elem.get('data-src') or 
                    img_elem.get('data-lazy-src')
                )
                
                if img_src:
                    item['url_imagen_principal'] = urljoin(self.base_url, img_src)
                    item['imagen_principal'] = img_src.split('/')[-1].split('?')[0]
            
            # Extraer precio
            price_elem = element.find(class_=lambda x: x and 'price' in x.lower())
            if price_elem:
                item['precio'] = price_elem.get_text(strip=True)
            
            # Extraer SKU
            sku_elem = element.find(class_=lambda x: x and ('sku' in x.lower() or 'code' in x.lower()))
            if sku_elem:
                item['sku'] = sku_elem.get_text(strip=True)
                item['codigo'] = sku_elem.get_text(strip=True)
            else:
                item['sku'] = element.get('data-product-id', '')
                item['codigo'] = item['sku']
            
            # Extraer descripción
            desc_elem = element.find(class_=lambda x: x and 'description' in x.lower())
            if desc_elem:
                item['descripcion_corta'] = desc_elem.get_text(strip=True)[:200]
            
            if item['titulo'] or item['imagen_principal']:
                logger.info(f"Extraído: {item['titulo'][:50] if item['titulo'] else 'Producto sin nombre'}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del elemento: {e}")
            return None
    
    def scrape_catalog(self, max_categories=None):
        """Función principal para hacer scraping del catálogo"""
        if not self.init_driver():
            return []
        
        try:
            all_items = []
            
            logger.info(f"Cargando página: {self.productos_url}")
            html_content = self.get_page_with_wait(self.productos_url)
            
            if not html_content:
                logger.error("No se pudo cargar la página principal")
                return all_items
            
            # Extraer categorías
            categories = self.extract_categories(html_content)
            
            if not categories:
                logger.warning("No se encontraron categorías")
                return all_items
            
            logger.info(f"✓ Encontradas {len(categories)} categorías")
            
            if max_categories:
                categories = categories[:max_categories]
                logger.info(f"Limitando a {max_categories} categorías")
            
            # Procesar cada categoría
            for i, category in enumerate(categories, 1):
                logger.info("")
                logger.info(f"{'='*60}")
                logger.info(f"[{i}/{len(categories)}] {category['nombre']}")
                logger.info(f"{'='*60}")
                
                category_html = self.get_page_with_wait(category['url'])
                
                if not category_html:
                    logger.warning(f"No se pudo cargar: {category['nombre']}")
                    continue
                
                items = self.extract_catalog_items(category_html)
                
                if not items:
                    logger.info(f"Sin productos en: {category['nombre']}")
                    continue
                
                logger.info(f"✓ {len(items)} productos encontrados")
                
                for item in items:
                    item['categoria'] = category['nombre']
                    all_items.append(item)
                
                time.sleep(1)  # Pausa entre categorías
            
            return all_items
            
        finally:
            self.close_driver()
    
    def save_to_csv(self, items, filename='catalogo_bombas_bloch_selenium.csv'):
        """Guarda los productos en CSV"""
        if not items:
            logger.warning("No hay productos para guardar")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'titulo', 'codigo', 'sku', 'precio',
                'imagen_principal', 'url_imagen_principal',
                'descripcion_corta', 'categoria', 'enlace_detalle'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for item in items:
                writer.writerow(item)
        
        logger.info(f"✓ {len(items)} productos guardados en {filename}")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Scraper de Bombas Bloch con Selenium")
    logger.info("=" * 60)
    
    # Crear scraper (headless=False para ver el navegador, True para ocultarlo)
    scraper = BombasBlochSeleniumScraper(headless=True)
    
    # Realizar scraping (limitar categorías para prueba)
    items = scraper.scrape_catalog(max_categories=10)
    
    if items:
        logger.info("")
        logger.info(f"✓ Total de productos extraídos: {len(items)}")
        
        # Mostrar muestra
        for i, item in enumerate(items[:5], 1):
            logger.info(f"{i}. {item['titulo']}")
        
        # Guardar en CSV
        scraper.save_to_csv(items)
    else:
        logger.warning("")
        logger.warning("⚠ No se encontraron productos")
        logger.info("")
        logger.info("Posibles causas:")
        logger.info("1. El catálogo está vacío o en mantenimiento")
        logger.info("2. Se requiere autenticación para ver productos")
        logger.info("3. Los productos están en otra sección del sitio")

if __name__ == "__main__":
    main()

