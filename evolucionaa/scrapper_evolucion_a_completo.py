#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para extraer información completa del catálogo de Evolución-A
Específicamente diseñado para la estructura del "Listado de destacados"
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

class EvolucionScraper:
    def __init__(self, base_url="https://www.evolucion-a.com/es/"):
        self.base_url = base_url
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
            response = self.session.get(url, timeout=10)
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
            # A veces devuelven el HTML como texto codificado (inicia con letras y acaba con ==)
            try:
                if all(c.isalnum() or c in '+/=\n\r' for c in raw_data.decode('ascii', errors='ignore')[:200]):
                    decoded = base64.b64decode(raw_data)
                    print("Contenido decodificado de base64")
                    # Si la decodificación tiene sentido (contiene <html>), usamos eso
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
    
    def extract_catalog_items(self, html_content):
        """Extrae los elementos del catálogo desde el HTML - específico para Evolución-A"""
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
            logger.warning("No se encontró la sección 'Listado de destacados'")
            # Fallback: buscar cualquier lista de productos
            fallback_items = soup.select('.item_list ul li, ul li[id*="iid_"]')
            if fallback_items:
                logger.info(f"Usando fallback: encontrados {len(fallback_items)} elementos")
                for item_element in fallback_items:
                    item_data = self.extract_item_data(item_element)
                    if item_data:
                        items.append(item_data)
        
        return items
    
    def extract_item_data(self, element):
        """Extrae título, imagen, código y enlace de un elemento del catálogo"""
        item = {
            'titulo': '',
            'codigo': '',
            'imagen_principal': '',
            'url_imagen_principal': '',
            'precio': '',
            'enlace_detalle': '',
            'descripcion_corta': ''
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
                    item['descripcion_corta'] = desc_p.get_text(strip=True)[:200]  # Limitar a 200 chars
            
            logger.info(f"Extraído producto: {item['titulo']} - Código: {item['codigo']}")
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
            'archivo_descarga': '',
            'url_archivo_descarga': ''
        }
        
        try:
            logger.info(f"Obteniendo detalles de: {product_url}")
            html_content = self.get_page_content(product_url)
            if not html_content:
                return detailed_info
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extraer imágenes adicionales de la galería
            image_list = soup.find('ul', class_='image_list')
            if image_list:
                image_items = image_list.find_all('li')
                for img_li in image_items:
                    # Buscar el enlace de la imagen grande
                    large_link = img_li.find('div', class_='large_image_link')
                    if large_link:
                        link_elem = large_link.find('a')
                        if link_elem:
                            img_url = link_elem.get('href')
                            if img_url:
                                detailed_info['urls_imagenes_adicionales'].append(img_url)
                                detailed_info['imagenes_adicionales'].append(img_url.split('/')[-1])
                    
                    # También extraer de small_image como fallback
                    if not detailed_info['urls_imagenes_adicionales']:
                        small_img_div = img_li.find('div', class_='small_image')
                        if small_img_div:
                            small_link = small_img_div.find('a')
                            if small_link:
                                img_url = small_link.get('href')
                                if img_url:
                                    detailed_info['urls_imagenes_adicionales'].append(img_url)
                                    detailed_info['imagenes_adicionales'].append(img_url.split('/')[-1].split('?')[0])
            
            # Extraer descripción completa
            desc_div = soup.find('div', class_='text')
            if desc_div:
                # Buscar el párrafo dentro del div
                desc_p = desc_div.find('p')
                if desc_p:
                    detailed_info['descripcion_completa'] = desc_p.get_text(strip=True)
            
            # Extraer enlace de descarga
            download_links = soup.find_all('a', href=True)
            for link in download_links:
                href = link.get('href', '')
                if any(ext in href.lower() for ext in ['.zip', '.pdf', '.doc', '.docx']):
                    detailed_info['url_archivo_descarga'] = href
                    detailed_info['archivo_descarga'] = href.split('/')[-1]
                    break
            
            logger.info(f"Detalles extraídos: {len(detailed_info['imagenes_adicionales'])} imágenes adicionales, "
                       f"descripción: {'Sí' if detailed_info['descripcion_completa'] else 'No'}")
            
        except Exception as e:
            logger.error(f"Error extrayendo detalles de {product_url}: {e}")
        
        return detailed_info
    
    def scrape_catalog(self, max_pages=5):
        """Función principal para hacer scraping del catálogo con información detallada"""
        all_items = []
        
        # Páginas comunes a revisar
        pages_to_check = [
            '',  # Página principal
            'catalogo',
            'productos',
            'productos.html',
            'catalog.html'
        ]
        
        for page in pages_to_check[:max_pages]:
            url = urljoin(self.base_url, page)
            logger.info(f"Escaneando: {url}")
            
            html_content = self.get_page_content(url)
            items = self.extract_catalog_items(html_content)
            
            if items:
                logger.info(f"Encontrados {len(items)} productos en {url}")
                
                # Para cada producto, obtener información detallada
                for item in items:
                    if item.get('enlace_detalle'):
                        detailed_info = self.extract_detailed_product_info(item['enlace_detalle'])
                        # Combinar información básica con detalles
                        item.update(detailed_info)
                        all_items.append(item)
                        
                        # Pausa entre solicitudes para ser respetuoso
                        time.sleep(2)
                    else:
                        # Si no hay enlace de detalle, agregar solo info básica
                        all_items.append(item)
                
                break  # Si encontramos productos en una página, no seguir buscando
            
            # Pausa educada entre solicitudes de páginas
            time.sleep(1)
        
        # Eliminar duplicados basándose en el código del producto
        unique_items = []
        seen_codes = set()
        for item in all_items:
            code = item.get('codigo', '')
            if code and code not in seen_codes:
                unique_items.append(item)
                seen_codes.add(code)
            elif not code:  # Si no tiene código, mantenerlo
                unique_items.append(item)
        
        return unique_items
    
    def save_to_csv(self, items, filename='catalogo_evolucion_a_completo.csv'):
        """Guarda los elementos extraídos en un archivo CSV con toda la información"""
        if not items:
            logger.warning("No hay elementos para guardar")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'titulo',
                'codigo', 
                'precio',
                'imagen_principal',
                'url_imagen_principal',
                'descripcion_corta',
                'descripcion_completa',
                'imagenes_adicionales',
                'urls_imagenes_adicionales',
                'archivo_descarga',
                'url_archivo_descarga',
                'enlace_detalle'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for item in items:
                # Convertir listas a strings separadas por punto y coma para CSV
                item_to_write = item.copy()
                if isinstance(item_to_write.get('imagenes_adicionales'), list):
                    item_to_write['imagenes_adicionales'] = '; '.join(item_to_write['imagenes_adicionales'])
                if isinstance(item_to_write.get('urls_imagenes_adicionales'), list):
                    item_to_write['urls_imagenes_adicionales'] = '; '.join(item_to_write['urls_imagenes_adicionales'])
                
                writer.writerow(item_to_write)
        
        logger.info(f"Guardados {len(items)} productos completos en {filename}")
        
        # Crear también un CSV simplificado solo con título e imagen principal
        simple_filename = filename.replace('_completo.csv', '_simple.csv')
        with open(simple_filename, 'w', newline='', encoding='utf-8') as csvfile:
            simple_fieldnames = ['titulo', 'imagen_principal', 'url_imagen_principal']
            writer = csv.DictWriter(csvfile, fieldnames=simple_fieldnames)
            
            writer.writeheader()
            for item in items:
                simple_item = {
                    'titulo': item.get('titulo', ''),
                    'imagen_principal': item.get('imagen_principal', ''),
                    'url_imagen_principal': item.get('url_imagen_principal', '')
                }
                writer.writerow(simple_item)
        
        logger.info(f"También creado archivo simplificado: {simple_filename}")

def main():
    """Función principal"""
    logger.info("Iniciando scraper específico de Evolución-A...")
    
    scraper = EvolucionScraper()
    
    # Realizar scraping
    items = scraper.scrape_catalog()
    
    if items:
        # Mostrar muestra de resultados
        logger.info(f"Total de productos encontrados: {len(items)}")
        for i, item in enumerate(items[:3]):  # Mostrar primeros 3
            logger.info(f"Producto {i+1}: {item.get('titulo', 'Sin título')} - Código: {item.get('codigo', 'Sin código')}")
        
        # Guardar en CSV
        scraper.save_to_csv(items)
        
        # Estadísticas detalladas
        with_images = sum(1 for item in items if item.get('imagen_principal'))
        with_titles = sum(1 for item in items if item.get('titulo'))
        with_codes = sum(1 for item in items if item.get('codigo'))
        with_prices = sum(1 for item in items if item.get('precio'))
        with_additional_images = sum(1 for item in items if item.get('imagenes_adicionales'))
        with_downloads = sum(1 for item in items if item.get('archivo_descarga'))
        
        logger.info("=== ESTADÍSTICAS DEL SCRAPING ===")
        logger.info(f"Total productos procesados: {len(items)}")
        logger.info(f"Productos con imagen principal: {with_images}")
        logger.info(f"Productos con título: {with_titles}")
        logger.info(f"Productos con código: {with_codes}")
        logger.info(f"Productos con precio: {with_prices}")
        logger.info(f"Productos con imágenes adicionales: {with_additional_images}")
        logger.info(f"Productos con archivos de descarga: {with_downloads}")
        
    else:
        logger.warning("No se encontraron productos en el catálogo")
        logger.info("Posibles razones:")
        logger.info("1. La página usa JavaScript para cargar contenido (usar Selenium)")
        logger.info("2. Los selectores CSS necesitan ajuste")
        logger.info("3. La página tiene protección anti-scraping")
        logger.info("4. La estructura del HTML ha cambiado")

if __name__ == "__main__":
    main()