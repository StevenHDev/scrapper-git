#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para extraer información completa del catálogo de Bombas Bloch
URL: https://www.bombasbloch.com/productos
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

class BombasBlochScraper:
    def __init__(self, base_url="https://www.bombasbloch.com"):
        self.base_url = base_url
        self.productos_url = urljoin(base_url, "/productos")
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

            # --- 1️⃣ Detectar compresión ---
            content_encoding = response.headers.get('Content-Encoding', '').lower()

            if 'gzip' in content_encoding:
                try:
                    raw_data = gzip.decompress(raw_data)
                except Exception:
                    pass  # algunos servidores ya lo descomprimen automáticamente

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

            # --- 2️⃣ Detectar si el cuerpo parece base64 ---
            try:
                if all(c.isalnum() or c in '+/=\n\r' for c in raw_data.decode('ascii', errors='ignore')[:200]):
                    decoded = base64.b64decode(raw_data)
                    logger.info("Contenido decodificado de base64")
                    if b'<html' in decoded.lower():
                        raw_data = decoded
            except Exception:
                pass

            # --- 3️⃣ Detectar codificación de texto ---
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding') or response.apparent_encoding or 'utf-8'

            html = raw_data.decode(encoding, errors='replace')

            return html

        except requests.RequestException as e:
            logger.error(f"Error al acceder a {url}: {e}")
            return None
    
    def extract_categories(self, html_content):
        """Extrae las categorías de productos desde la página principal"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []
        
        # Buscar enlaces de categorías en la estructura de Bombas Bloch
        # La estructura es: <li id="ecommerce"><a href="/productos/Catalog/listing/...">
        category_links = soup.find_all('a', href=lambda x: x and '/productos/Catalog/listing/' in x)
        
        for link in category_links:
            category_name = link.get_text(strip=True)
            category_url = urljoin(self.base_url, link.get('href'))
            
            if category_name and category_url:
                categories.append({
                    'nombre': category_name,
                    'url': category_url
                })
                logger.info(f"Categoría encontrada: {category_name}")
        
        return categories
    
    def extract_catalog_items(self, html_content):
        """Extrae los elementos del catálogo desde el HTML - específico para Bombas Bloch"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        
        # Buscar productos/categorías en la estructura específica de Bombas Bloch
        # Los elementos están en <li> con id que empieza con "cid_" o "iid_"
        product_items = soup.find_all('li', id=lambda x: x and (x.startswith('cid_') or x.startswith('iid_')))
        
        if product_items:
            logger.info(f"Encontrados {len(product_items)} elementos en la página")
        else:
            # Fallback: buscar otras estructuras posibles
            product_selectors = [
                '.item_prod',
                '.product-item',
                '.product',
                '.product-card',
                '.grid-item',
                '.collection-item'
            ]
            
            for selector in product_selectors:
                product_items = soup.select(selector)
                if product_items:
                    logger.info(f"Encontrados {len(product_items)} productos usando selector: {selector}")
                    break
        
        if not product_items:
            logger.warning("No se encontraron productos con los selectores predefinidos")
        
        for item_element in product_items:
            item_data = self.extract_item_data(item_element)
            if item_data and (item_data['titulo'] or item_data['imagen_principal']):
                items.append(item_data)
        
        return items
    
    def extract_item_data(self, element):
        """Extrae título, imagen, código y enlace de un elemento del catálogo"""
        item = {
            'titulo': '',
            'codigo': '',
            'sku': '',
            'imagen_principal': '',
            'url_imagen_principal': '',
            'precio': '',
            'precio_regular': '',
            'precio_oferta': '',
            'enlace_detalle': '',
            'descripcion_corta': '',
            'categoria': '',
            'stock': ''
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
                    element.find(class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
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
                        item['enlace_detalle'] = urljoin(self.base_url, href)
            
            # Extraer imagen principal
            img_elem = element.find('img')
            if img_elem:
                # Intentar obtener la imagen de varias fuentes posibles
                img_src = (
                    img_elem.get('src') or 
                    img_elem.get('data-src') or 
                    img_elem.get('data-lazy-src') or
                    img_elem.get('data-original')
                )
                
                if img_src:
                    # Asegurar URL completa
                    full_img_url = urljoin(self.base_url, img_src)
                    item['url_imagen_principal'] = full_img_url
                    # Extraer solo el nombre del archivo
                    item['imagen_principal'] = img_src.split('/')[-1].split('?')[0]
            
            # Extraer precio
            price_elem = element.find(class_=lambda x: x and 'price' in x.lower())
            if price_elem:
                # Buscar precio de oferta
                sale_price = price_elem.find(class_=lambda x: x and ('sale' in x.lower() or 'offer' in x.lower()))
                if sale_price:
                    item['precio_oferta'] = sale_price.get_text(strip=True)
                
                # Buscar precio regular
                regular_price = price_elem.find(class_=lambda x: x and 'regular' in x.lower())
                if regular_price:
                    item['precio_regular'] = regular_price.get_text(strip=True)
                
                # Si no hay separación, tomar el precio general
                if not item['precio_oferta'] and not item['precio_regular']:
                    item['precio'] = price_elem.get_text(strip=True)
            
            # Extraer SKU o código de producto
            sku_elem = element.find(class_=lambda x: x and ('sku' in x.lower() or 'code' in x.lower() or 'ref' in x.lower()))
            if sku_elem:
                item['sku'] = sku_elem.get_text(strip=True)
                item['codigo'] = sku_elem.get_text(strip=True)
            else:
                # Intentar extraer del data attribute
                sku_attr = element.get('data-product-id') or element.get('data-id') or element.get('data-sku')
                if sku_attr:
                    item['sku'] = str(sku_attr)
                    item['codigo'] = str(sku_attr)
            
            # Extraer descripción corta
            desc_elem = element.find(class_=lambda x: x and ('description' in x.lower() or 'excerpt' in x.lower()))
            if desc_elem:
                item['descripcion_corta'] = desc_elem.get_text(strip=True)[:200]
            
            # Extraer categoría
            cat_elem = element.find(class_=lambda x: x and ('category' in x.lower() or 'cat' in x.lower()))
            if cat_elem:
                item['categoria'] = cat_elem.get_text(strip=True)
            
            # Extraer estado de stock
            stock_elem = element.find(class_=lambda x: x and ('stock' in x.lower() or 'availability' in x.lower()))
            if stock_elem:
                item['stock'] = stock_elem.get_text(strip=True)
            
            if item['titulo'] or item['imagen_principal']:
                logger.info(f"Extraído producto: {item['titulo'][:50] if item['titulo'] else 'Sin título'} - SKU: {item['sku']}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del elemento: {e}")
            return None
    
    def extract_detailed_product_info(self, product_url):
        """Extrae información detallada de la página individual del producto"""
        detailed_info = {
            'imagenes_adicionales': [],
            'urls_imagenes_adicionales': [],
            'descripcion_completa': '',
            'especificaciones': '',
            'archivo_descarga': '',
            'url_archivo_descarga': '',
            'atributos': ''
        }
        
        try:
            logger.info(f"Obteniendo detalles de: {product_url}")
            html_content = self.get_page_content(product_url)
            if not html_content:
                return detailed_info
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraer imágenes adicionales de galería
            gallery_selectors = [
                '.product-gallery img',
                '.product-images img',
                '.gallery img',
                '.slider img',
                '[class*="gallery"] img',
                '[class*="slider"] img',
                '.product-image-gallery img',
                '.thumbnails img'
            ]
            
            for selector in gallery_selectors:
                images = soup.select(selector)
                if images:
                    for img in images:
                        img_src = (
                            img.get('src') or 
                            img.get('data-src') or 
                            img.get('data-large-image') or
                            img.get('data-lazy-src')
                        )
                        if img_src:
                            full_url = urljoin(self.base_url, img_src)
                            if full_url not in detailed_info['urls_imagenes_adicionales']:
                                detailed_info['urls_imagenes_adicionales'].append(full_url)
                                detailed_info['imagenes_adicionales'].append(img_src.split('/')[-1].split('?')[0])
                    if detailed_info['imagenes_adicionales']:
                        break
            
            # Extraer descripción completa
            desc_selectors = [
                '.product-description',
                '.product-content',
                '[class*="description"]',
                '#description',
                '.description',
                '.entry-content',
                '.product-details'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    detailed_info['descripcion_completa'] = desc_elem.get_text(strip=True)
                    break
            
            # Extraer especificaciones técnicas
            specs_selectors = [
                '.product-specifications',
                '.specifications',
                '.technical-specs',
                '#specifications',
                '[class*="spec"]'
            ]
            
            for selector in specs_selectors:
                specs_elem = soup.select_one(selector)
                if specs_elem:
                    detailed_info['especificaciones'] = specs_elem.get_text(strip=True)
                    break
            
            # Extraer atributos del producto (tablas de especificaciones)
            tables = soup.find_all('table', class_=lambda x: x and ('attribute' in x.lower() or 'spec' in x.lower()))
            if tables:
                attrs = []
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['th', 'td'])
                        if len(cells) >= 2:
                            key = cells[0].get_text(strip=True)
                            value = cells[1].get_text(strip=True)
                            attrs.append(f"{key}: {value}")
                if attrs:
                    detailed_info['atributos'] = '; '.join(attrs)
            
            # Extraer enlaces de descarga (PDF, catálogos, etc.)
            download_links = soup.find_all('a', href=True)
            for link in download_links:
                href = link.get('href', '')
                if any(ext in href.lower() for ext in ['.pdf', '.zip', '.doc', '.docx', '.xlsx']):
                    detailed_info['url_archivo_descarga'] = urljoin(self.base_url, href)
                    detailed_info['archivo_descarga'] = href.split('/')[-1]
                    break
            
            logger.info(f"Detalles extraídos: {len(detailed_info['imagenes_adicionales'])} imágenes adicionales, "
                       f"descripción: {'Sí' if detailed_info['descripcion_completa'] else 'No'}")
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles de {product_url}: {e}")
        
        return detailed_info
    
    def scrape_catalog(self, get_details=True, max_categories=None):
        """Función principal para hacer scraping del catálogo"""
        all_items = []
        
        logger.info(f"Iniciando scraping de: {self.productos_url}")
        
        # Obtener la página principal de productos
        html_content = self.get_page_content(self.productos_url)
        
        if not html_content:
            logger.error("No se pudo obtener el contenido de la página")
            return all_items
        
        # Extraer las categorías de la página principal
        categories = self.extract_categories(html_content)
        
        if not categories:
            logger.warning("No se encontraron categorías en la página principal")
            # Guardar HTML para análisis
            with open('debug_bombas_bloch.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info("HTML guardado en debug_bombas_bloch.html para análisis manual")
            return all_items
        
        logger.info(f"✓ Encontradas {len(categories)} categorías de productos")
        
        # Limitar categorías si se especifica
        if max_categories:
            categories = categories[:max_categories]
            logger.info(f"Limitando a las primeras {max_categories} categorías")
        
        # Recorrer cada categoría y extraer los productos
        for i, category in enumerate(categories, 1):
            logger.info("")
            logger.info(f"{'='*60}")
            logger.info(f"Procesando categoría {i}/{len(categories)}: {category['nombre']}")
            logger.info(f"{'='*60}")
            
            # Obtener HTML de la categoría
            category_html = self.get_page_content(category['url'])
            
            if not category_html:
                logger.warning(f"No se pudo obtener contenido de: {category['nombre']}")
                continue
            
            # Extraer productos de esta categoría
            items = self.extract_catalog_items(category_html)
            
            if not items:
                logger.warning(f"No se encontraron productos en: {category['nombre']}")
                continue
            
            logger.info(f"✓ Encontrados {len(items)} productos en {category['nombre']}")
            
            # Agregar categoría a cada producto
            for item in items:
                item['categoria'] = category['nombre']
            
            # Si se solicita, obtener información detallada de cada producto
            if get_details:
                for j, item in enumerate(items, 1):
                    logger.info(f"  → Procesando producto {j}/{len(items)}: {item.get('titulo', 'Sin título')[:50]}")
                    if item.get('enlace_detalle'):
                        detailed_info = self.extract_detailed_product_info(item['enlace_detalle'])
                        # Combinar información básica con detalles
                        item.update(detailed_info)
                        
                        # Pausa entre solicitudes para ser respetuoso con el servidor
                        time.sleep(1)
                    
                    all_items.append(item)
            else:
                all_items.extend(items)
            
            # Pausa entre categorías
            time.sleep(1)
        
        # Eliminar duplicados basándose en el enlace o SKU
        logger.info("")
        logger.info("Eliminando duplicados...")
        unique_items = []
        seen_keys = set()
        for item in all_items:
            key = item.get('enlace_detalle') or item.get('sku') or item.get('titulo')
            if key and key not in seen_keys:
                unique_items.append(item)
                seen_keys.add(key)
            elif not key:
                unique_items.append(item)
        
        logger.info(f"✓ Total de productos únicos: {len(unique_items)}")
        
        return unique_items
    
    def save_to_csv(self, items, filename='bombas_bloch_productos.csv'):
        """Guarda los elementos extraídos en un archivo CSV con toda la información"""
        if not items:
            logger.warning("No hay elementos para guardar")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'titulo',
                'codigo',
                'sku',
                'precio',
                'precio_regular',
                'precio_oferta',
                'imagen_principal',
                'url_imagen_principal',
                'descripcion_corta',
                'descripcion_completa',
                'especificaciones',
                'atributos',
                'imagenes_adicionales',
                'urls_imagenes_adicionales',
                'categoria',
                'stock',
                'archivo_descarga',
                'url_archivo_descarga',
                'enlace_detalle'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
            
            writer.writeheader()
            for item in items:
                # Convertir listas a strings separadas por punto y coma para CSV
                item_to_write = item.copy()
                if isinstance(item_to_write.get('imagenes_adicionales'), list):
                    item_to_write['imagenes_adicionales'] = '; '.join(item_to_write['imagenes_adicionales'])
                if isinstance(item_to_write.get('urls_imagenes_adicionales'), list):
                    item_to_write['urls_imagenes_adicionales'] = '; '.join(item_to_write['urls_imagenes_adicionales'])
                
                writer.writerow(item_to_write)
        
        logger.info(f"✓ Guardados {len(items)} productos en {filename}")
        logger.info(f"📁 Archivo listo para importar a WooCommerce")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Iniciando scraper de Bombas Bloch")
    logger.info("URL: https://www.bombasbloch.com/productos")
    logger.info("=" * 60)
    
    scraper = BombasBlochScraper()
    
    # Realizar scraping
    # Opciones:
    # - get_details=True: Extrae información detallada de cada producto (más lento pero completo)
    # - get_details=False: Solo extrae información básica (más rápido)
    # - max_categories=N: Limita el número de categorías a procesar (útil para pruebas)
    
    # Para prueba rápida, usar: scraper.scrape_catalog(get_details=False, max_categories=2)
    # Para extracción completa, usar: scraper.scrape_catalog(get_details=True)
    
    # Extraer las 11 categorías principales de Bombas Bloch
    items = scraper.scrape_catalog(get_details=True, max_categories=11)
    
    if items:
        # Mostrar muestra de resultados
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✓ Total de productos encontrados: {len(items)}")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Muestra de productos extraídos:")
        for i, item in enumerate(items[:5], 1):  # Mostrar primeros 5
            logger.info(f"\n{i}. {item.get('titulo', 'Sin título')}")
            logger.info(f"   SKU: {item.get('sku', 'N/A')}")
            logger.info(f"   Precio: {item.get('precio', '') or item.get('precio_oferta', '') or item.get('precio_regular', 'N/A')}")
            logger.info(f"   Imagen: {item.get('imagen_principal', 'N/A')}")
        
        # Guardar en CSV
        logger.info("")
        scraper.save_to_csv(items)
        
        # Estadísticas detalladas
        with_images = sum(1 for item in items if item.get('imagen_principal'))
        with_titles = sum(1 for item in items if item.get('titulo'))
        with_sku = sum(1 for item in items if item.get('sku'))
        with_prices = sum(1 for item in items if (item.get('precio') or item.get('precio_oferta') or item.get('precio_regular')))
        with_additional_images = sum(1 for item in items if item.get('imagenes_adicionales'))
        with_description = sum(1 for item in items if item.get('descripcion_completa'))
        with_downloads = sum(1 for item in items if item.get('archivo_descarga'))
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("ESTADÍSTICAS DEL SCRAPING")
        logger.info("=" * 60)
        logger.info(f"Total productos procesados:          {len(items)}")
        logger.info(f"Productos con título:                {with_titles}")
        logger.info(f"Productos con SKU/código:            {with_sku}")
        logger.info(f"Productos con precio:                {with_prices}")
        logger.info(f"Productos con imagen principal:      {with_images}")
        logger.info(f"Productos con imágenes adicionales:  {with_additional_images}")
        logger.info(f"Productos con descripción completa:  {with_description}")
        logger.info(f"Productos con archivos de descarga:  {with_downloads}")
        logger.info("=" * 60)
        
    else:
        logger.warning("")
        logger.warning("=" * 60)
        logger.warning("⚠ No se encontraron productos en el catálogo")
        logger.warning("=" * 60)
        logger.info("")
        logger.info("Posibles razones:")
        logger.info("1. La página usa JavaScript para cargar contenido dinámico")
        logger.info("   → Solución: Usar Selenium o Playwright en lugar de requests")
        logger.info("")
        logger.info("2. Los selectores CSS necesitan ajuste para este sitio específico")
        logger.info("   → Solución: Revisar el archivo debug_bombas_bloch.html generado")
        logger.info("")
        logger.info("3. La página tiene protección anti-scraping o requiere cookies")
        logger.info("   → Solución: Agregar más headers o usar un navegador real")
        logger.info("")
        logger.info("4. La URL de productos es diferente")
        logger.info("   → Solución: Verificar la URL correcta en el navegador")

if __name__ == "__main__":
    main()

