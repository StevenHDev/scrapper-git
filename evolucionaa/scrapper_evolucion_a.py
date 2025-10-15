#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para Evolución-A Competición
URL: https://www.evolucion-a.com/es/productos
Especialistas en productos para automovilismo de competición
"""

import base64
import requests
from bs4 import BeautifulSoup
import csv
import time
import os
from urllib.parse import urljoin, urlparse
import logging
import gzip
import zlib
import chardet
import brotli

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EvolucionAScraperCompeticion:
    def __init__(self, base_url="https://www.evolucion-a.com"):
        self.base_url = base_url
        self.catalogo_url = urljoin(base_url, "/es/catalogo")
        self.session = requests.Session()
        # Headers para parecer un navegador real
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def get_page_content(self, url):
        """Obtiene el contenido HTML real (descomprimido y decodificado correctamente)."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            raw_data = response.content

            # Detectar compresión
            content_encoding = response.headers.get('Content-Encoding', '').lower()

            if 'gzip' in content_encoding:
                try:
                    raw_data = gzip.decompress(raw_data)
                except Exception:
                    pass

            elif 'deflate' in content_encoding:
                try:
                    raw_data = zlib.decompress(raw_data)
                except Exception:
                    pass
            elif 'br' in content_encoding:
                try:
                    raw_data = brotli.decompress(raw_data)
                except Exception:
                    pass

            # Detectar si el cuerpo parece base64
            try:
                if all(c.isalnum() or c in '+/=\n\r' for c in raw_data.decode('ascii', errors='ignore')[:200]):
                    decoded = base64.b64decode(raw_data)
                    logger.info("Contenido decodificado de base64")
                    if b'<html' in decoded.lower():
                        raw_data = decoded
            except Exception:
                pass

            # Detectar codificación de texto
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding') or response.apparent_encoding or 'utf-8'

            html = raw_data.decode(encoding, errors='replace')

            return html

        except requests.RequestException as e:
            logger.error(f"Error al acceder a {url}: {e}")
            return None
    
    def extract_categories(self, html_content, parent_category=''):
        """Extrae las categorías y subcategorías desde una página"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []
        seen_urls = set()
        
        # Buscar la sección de categorías: div class="category_list"
        category_section = soup.find('div', class_='category_list')
        
        if category_section:
            # Buscar todos los <li> con id que empiece con "cid_"
            category_items = category_section.find_all('li', id=lambda x: x and x.startswith('cid_'))
            
            for item in category_items:
                # Extraer título y enlace del h3 > a
                h3 = item.find('h3')
                if h3:
                    link = h3.find('a')
                    if link:
                        category_name = link.get_text(strip=True)
                        category_url = urljoin(self.base_url, link.get('href'))
                        
                        if category_url not in seen_urls:
                            # Agregar nombre de categoría padre si existe
                            full_name = f"{parent_category} > {category_name}" if parent_category else category_name
                            categories.append({
                                'nombre': full_name,
                                'nombre_corto': category_name,
                                'url': category_url,
                                'id': item.get('id', ''),
                                'es_subcategoria': bool(parent_category)
                            })
                            seen_urls.add(category_url)
                            prefix = "  Subcategoría:" if parent_category else "Categoría:"
                            logger.info(f"{prefix} {category_name}")
        
        return categories
    
    def extract_catalog_items(self, html_content):
        """Extrae los productos desde el HTML - específico para Evolución-A"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        
        # Buscar específicamente la sección "Listado de destacados"
        highlighted_section = soup.find('div', id='block_highlighted_products')
        
        if highlighted_section:
            logger.info("Encontrada sección 'Listado de destacados'")
            # Extraer todos los elementos <li> que contienen los productos
            product_items = highlighted_section.find_all('li')
            logger.info(f"Encontrados {len(product_items)} productos destacados")
            
            for item_element in product_items:
                item_data = self.extract_item_data(item_element)
                if item_data:
                    items.append(item_data)
        else:
            # Fallback: buscar productos en <li> con id="iid_XXX"
            fallback_items = soup.find_all('li', id=lambda x: x and x.startswith('iid_'))
            if fallback_items:
                logger.info(f"Usando fallback: encontrados {len(fallback_items)} elementos")
                for item_element in fallback_items:
                    item_data = self.extract_item_data(item_element)
                    if item_data:
                        items.append(item_data)
            else:
                logger.warning("No se encontraron productos")
        
        return items
    
    def extract_item_data(self, element):
        """Extrae título, imagen, código y enlace de un elemento del catálogo - específico para Evolución-A"""
        item = {
            'titulo': '',
            'codigo': '',
            'imagen_principal': '',
            'url_imagen_principal': '',
            'precio': '',
            'enlace_detalle': '',
            'descripcion_corta': '',
            'marca': 'Evolución-A'
        }
        
        try:
            # Extraer título del enlace en h3
            title_link = element.find('h3')
            if title_link:
                link_elem = title_link.find('a')
                if link_elem:
                    item['titulo'] = link_elem.get_text(strip=True)
                    # URL relativa del producto
                    href = link_elem.get('href')
                    if href:
                        item['enlace_detalle'] = urljoin(self.base_url, href)
            
            # Extraer código del producto
            sku_elem = element.find('p', class_='sku')
            if sku_elem:
                strong_elem = sku_elem.find('strong')
                if strong_elem and strong_elem.next_sibling:
                    item['codigo'] = str(strong_elem.next_sibling).strip()
            
            # Extraer imagen principal
            image_p = element.find('p', class_='image')
            if image_p:
                img = image_p.find('img')
                if img:
                    img_src = img.get('src')
                    if img_src:
                        item['url_imagen_principal'] = img_src
                        item['imagen_principal'] = img_src.split('/')[-1].split('?')[0]
            
            # Extraer precio
            price_elem = element.find('p', class_='price')
            if price_elem:
                price_strong = price_elem.find('strong', class_='sales_price')
                if price_strong:
                    item['precio'] = price_strong.get_text(strip=True)
            
            # Extraer descripción corta
            text_div = element.find('div', class_='text')
            if text_div:
                desc_p = text_div.find('p')
                if desc_p:
                    item['descripcion_corta'] = desc_p.get_text(strip=True)[:200]
            
            logger.info(f"Extraído producto: {item['titulo']} - Código: {item['codigo']}")
            return item
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del elemento: {e}")
            return None
    
    def scrape_catalog(self, max_categories=None):
        """Función principal para hacer scraping del catálogo"""
        all_items = []
        
        logger.info(f"Iniciando scraping de: {self.catalogo_url}")
        
        # Obtener la página del catálogo
        html_content = self.get_page_content(self.catalogo_url)
        
        if not html_content:
            logger.error("No se pudo obtener el contenido de la página")
            return all_items
        
        # Extraer las categorías
        categories = self.extract_categories(html_content)
        
        if not categories:
            logger.warning("No se encontraron categorías, intentando extraer productos de la página principal")
            # Intentar extraer productos directamente del catálogo
            items = self.extract_catalog_items(html_content)
            if items:
                for item in items:
                    item['categoria'] = 'Destacados'
                    all_items.append(item)
            return all_items
        
        logger.info(f"✓ Encontradas {len(categories)} categorías")
        
        # Limitar categorías si se especifica
        if max_categories:
            categories = categories[:max_categories]
            logger.info(f"Limitando a las primeras {max_categories} categorías")
        
        # Recorrer cada categoría y sus subcategorías
        for i, category in enumerate(categories, 1):
            logger.info("")
            logger.info(f"{'='*60}")
            logger.info(f"Procesando categoría {i}/{len(categories)}: {category['nombre']}")
            logger.info(f"{'='*60}")
            
            category_html = self.get_page_content(category['url'])
            
            if not category_html:
                logger.warning(f"No se pudo obtener contenido de: {category['nombre']}")
                continue
            
            # Primero buscar si hay subcategorías en esta categoría
            subcategories = self.extract_categories(category_html, parent_category=category['nombre_corto'] if 'nombre_corto' in category else category['nombre'])
            
            if subcategories:
                logger.info(f"Encontradas {len(subcategories)} subcategorías en {category['nombre_corto']}")
                # Procesar las subcategorías
                for j, subcat in enumerate(subcategories, 1):
                    logger.info(f"  [{j}/{len(subcategories)}] {subcat['nombre_corto']}")
                    
                    subcat_html = self.get_page_content(subcat['url'])
                    if subcat_html:
                        items = self.extract_catalog_items(subcat_html)
                        if items:
                            logger.info(f"  ✓ {len(items)} productos encontrados")
                            for item in items:
                                item['categoria'] = subcat['nombre']
                                all_items.append(item)
                        else:
                            logger.info(f"  Sin productos en: {subcat['nombre_corto']}")
                    
                    time.sleep(0.5)  # Pausa entre subcategorías
            else:
                # No hay subcategorías, buscar productos directamente
                items = self.extract_catalog_items(category_html)
                
                if not items:
                    logger.info(f"Sin productos en: {category['nombre']}")
                else:
                    logger.info(f"✓ {len(items)} productos encontrados")
                    for item in items:
                        item['categoria'] = category['nombre']
                        all_items.append(item)
            
            time.sleep(1)  # Pausa entre categorías
        
        # Eliminar duplicados
        logger.info("")
        logger.info("Eliminando duplicados...")
        unique_items = []
        seen_keys = set()
        for item in all_items:
            key = item.get('enlace_detalle') or item.get('codigo') or item.get('titulo')
            if key and key not in seen_keys:
                unique_items.append(item)
                seen_keys.add(key)
            elif not key:
                unique_items.append(item)
        
        logger.info(f"✓ Total de productos únicos: {len(unique_items)}")
        
        return unique_items
    
    def save_to_csv(self, items, filename='evolucion_a_productos.csv'):
        """Guarda los productos en CSV"""
        if not items:
            logger.warning("No hay elementos para guardar")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'titulo',
                'codigo',
                'precio',
                'imagen_principal',
                'url_imagen_principal',
                'descripcion_corta',
                'categoria',
                'marca',
                'enlace_detalle'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            for item in items:
                writer.writerow(item)
        
        logger.info(f"✓ Guardados {len(items)} productos en {filename}")
        logger.info(f"📁 Archivo listo para convertir a WooCommerce/Duda.co")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Iniciando scraper de Evolución-A Competición")
    logger.info("URL: https://www.evolucion-a.com/es/catalogo")
    logger.info("=" * 60)
    
    scraper = EvolucionAScraperCompeticion()
    
    # Realizar scraping
    # Cambiar max_categories=N para limitar, o None para todas las categorías
    items = scraper.scrape_catalog(max_categories=None)
    
    if items:
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✓ Total de productos encontrados: {len(items)}")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Muestra de productos extraídos:")
        for i, item in enumerate(items[:5], 1):
            logger.info(f"\n{i}. {item.get('titulo', 'Sin título')}")
            logger.info(f"   SKU: {item.get('sku', 'N/A')}")
            logger.info(f"   Categoría: {item.get('categoria', 'N/A')}")
            logger.info(f"   Imagen: {item.get('imagen_principal', 'N/A')}")
        
        # Guardar en CSV
        logger.info("")
        scraper.save_to_csv(items)
        
        # Estadísticas
        with_images = sum(1 for item in items if item.get('imagen_principal'))
        with_titles = sum(1 for item in items if item.get('titulo'))
        with_codes = sum(1 for item in items if item.get('codigo'))
        with_prices = sum(1 for item in items if item.get('precio'))
        with_description = sum(1 for item in items if item.get('descripcion_corta'))
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("ESTADÍSTICAS DEL SCRAPING")
        logger.info("=" * 60)
        logger.info(f"Total productos procesados:     {len(items)}")
        logger.info(f"Productos con título:           {with_titles}")
        logger.info(f"Productos con código:           {with_codes}")
        logger.info(f"Productos con precio:           {with_prices}")
        logger.info(f"Productos con imagen:           {with_images}")
        logger.info(f"Productos con descripción:      {with_description}")
        logger.info("=" * 60)
        
    else:
        logger.warning("")
        logger.warning("=" * 60)
        logger.warning("⚠ No se encontraron productos")
        logger.warning("=" * 60)
        logger.info("")
        logger.info("Posibles causas:")
        logger.info("1. La página usa JavaScript para cargar productos")
        logger.info("2. Los selectores CSS necesitan ajuste")
        logger.info("3. Se requiere autenticación")

if __name__ == "__main__":
    main()

