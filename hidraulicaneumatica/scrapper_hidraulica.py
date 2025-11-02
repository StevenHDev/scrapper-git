#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para Hidráulica Neumática - Estehyne
URL: https://www.hidraulicaneumatica.es/es/productos
Productos industriales de hidráulica y neumática
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

class HidraulicaNeumatiaScraper:
    def __init__(self, base_url="https://www.hidraulicaneumatica.es"):
        self.base_url = base_url
        self.productos_url = urljoin(base_url, "/es/productos")
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
        
        # Buscar enlaces de categorías en la estructura de Hidráulica Neumática
        # Las categorías están en enlaces que apuntan a /es/productos/List/listing/
        category_links = soup.find_all('a', href=lambda x: x and '/es/productos/List/listing/' in x)
        
        for link in category_links:
            category_name = link.get_text(strip=True)
            category_url = urljoin(self.base_url, link.get('href'))
            
            if category_name and category_url and category_url not in seen_urls:
                # Filtrar nombres muy cortos
                if len(category_name) > 2:
                    full_name = f"{parent_category} > {category_name}" if parent_category else category_name
                    categories.append({
                        'nombre': full_name,
                        'nombre_corto': category_name,
                        'url': category_url
                    })
                    seen_urls.add(category_url)
                    prefix = "  Subcategoría:" if parent_category else "Categoría:"
                    logger.info(f"{prefix} {category_name}")
        
        return categories
    
    def extract_catalog_items(self, html_content):
        """Extrae los productos desde el HTML - específico para Hidráulica Neumática"""
        if not html_content:
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        
        # Buscar productos en <li class="list_index_item" id="iid_XXX">
        product_items = soup.find_all('li', class_='list_index_item', id=lambda x: x and x.startswith('iid_'))
        
        if product_items:
            logger.info(f"Encontrados {len(product_items)} productos en la página")
        else:
            # Fallback: buscar solo por id
            product_items = soup.find_all('li', id=lambda x: x and x.startswith('iid_'))
            if product_items:
                logger.info(f"Encontrados {len(product_items)} productos (fallback)")
        
        if not product_items:
            logger.warning("No se encontraron productos")
        
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
            'imagen_principal': '',
            'url_imagen_principal': '',
            'precio': '',
            'enlace_detalle': '',
            'descripcion_corta': '',
            'marca': 'Hidráulica Neumática',
            'categoria': ''
        }
        
        try:
            # Extraer ID del elemento como código
            element_id = element.get('id', '')
            if element_id:
                item['codigo'] = element_id
            
            # Extraer título en h3 > a o h3.list_index_item_h3 > a
            title_elem = element.find('h3', class_='list_index_item_h3')
            if not title_elem:
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
            
            # Si aún no hay enlace, buscar el primer enlace
            if not item['enlace_detalle']:
                link_elem = element.find('a', href=True)
                if link_elem:
                    href = link_elem.get('href')
                    if href and not href.startswith('#'):
                        item['enlace_detalle'] = urljoin(self.base_url, href)
            
            # Extraer imagen principal desde p class="image"
            image_p = element.find('p', class_='image')
            if image_p:
                img = image_p.find('img')
                if img:
                    img_src = img.get('src')
                    if img_src:
                        item['url_imagen_principal'] = urljoin(self.base_url, img_src)
                        item['imagen_principal'] = img_src.split('/')[-1].split('?')[0]
            
            # Extraer precio
            price_elem = element.find('p', class_='price')
            if price_elem:
                price_strong = price_elem.find('strong')
                if price_strong:
                    item['precio'] = price_strong.get_text(strip=True)
            
            # Extraer código del producto
            sku_elem = element.find('p', class_='sku')
            if sku_elem:
                strong_elem = sku_elem.find('strong')
                if strong_elem and strong_elem.next_sibling:
                    codigo_text = str(strong_elem.next_sibling).strip()
                    if codigo_text:
                        item['codigo'] = codigo_text
            
            # Extraer descripción corta
            text_div = element.find('div', class_='text')
            if text_div:
                desc_p = text_div.find('p')
                if desc_p:
                    item['descripcion_corta'] = desc_p.get_text(strip=True)[:200]
            
            if item['titulo']:
                logger.info(f"Extraído: {item['titulo'][:50]} - Código: {item['codigo']}")
            
            return item
            
        except Exception as e:
            logger.error(f"Error extrayendo datos del elemento: {e}")
            return None
    
    def scrape_catalog(self, max_categories=None, max_subcategories_per_category=10, max_depth=2):
        """Función principal para hacer scraping del catálogo"""
        all_items = []
        
        logger.info(f"Iniciando scraping de: {self.productos_url}")
        
        # Obtener la página principal de productos
        html_content = self.get_page_content(self.productos_url)
        
        if not html_content:
            logger.error("No se pudo obtener el contenido de la página")
            return all_items
        
        # Extraer las categorías
        categories = self.extract_categories(html_content)
        
        if not categories:
            logger.warning("No se encontraron categorías, intentando extraer productos de la página principal")
            items = self.extract_catalog_items(html_content)
            if items:
                for item in items:
                    item['categoria'] = 'General'
                    all_items.append(item)
            return all_items
        
        logger.info(f"✓ Encontradas {len(categories)} categorías")
        
        # Limitar categorías si se especifica
        if max_categories:
            categories = categories[:max_categories]
            logger.info(f"Limitando a las primeras {max_categories} categorías")
        
        # Recorrer cada categoría
        for i, category in enumerate(categories, 1):
            logger.info("")
            logger.info(f"{'='*60}")
            logger.info(f"Procesando categoría {i}/{len(categories)}: {category['nombre_corto']}")
            logger.info(f"{'='*60}")
            
            category_html = self.get_page_content(category['url'])
            
            if not category_html:
                logger.warning(f"No se pudo obtener contenido de: {category['nombre']}")
                continue
            
            # Extraer productos de esta categoría
            items = self.extract_catalog_items(category_html)
            
            if items:
                logger.info(f"✓ {len(items)} productos en nivel actual")
                for item in items:
                    item['categoria'] = category['nombre']
                    all_items.append(item)
            
            # Buscar subcategorías (limitar cantidad)
            subcategories = self.extract_categories(category_html, parent_category=category['nombre_corto'])
            if subcategories:
                # Limitar subcategorías por categoría
                if max_subcategories_per_category and len(subcategories) > max_subcategories_per_category:
                    logger.info(f"→ {len(subcategories)} subcategorías encontradas (limitando a {max_subcategories_per_category})")
                    subcategories = subcategories[:max_subcategories_per_category]
                else:
                    logger.info(f"→ {len(subcategories)} subcategorías encontradas")
                
                for j, subcat in enumerate(subcategories, 1):
                    logger.info(f"  [{j}/{len(subcategories)}] {subcat['nombre_corto']}")
                    
                    subcat_html = self.get_page_content(subcat['url'])
                    if subcat_html:
                        sub_items = self.extract_catalog_items(subcat_html)
                        if sub_items:
                            logger.info(f"    ✓ {len(sub_items)} productos")
                            for item in sub_items:
                                item['categoria'] = subcat['nombre']
                                all_items.append(item)
                        
                        # Solo procesar tercer nivel si max_depth > 2
                        if max_depth > 2:
                            sub_subcategories = self.extract_categories(subcat_html, parent_category=subcat['nombre'])
                            if sub_subcategories:
                                # Limitar sub-subcategorías
                                if len(sub_subcategories) > 10:
                                    logger.info(f"    → {len(sub_subcategories)} sub-subcategorías (limitando a 10)")
                                    sub_subcategories = sub_subcategories[:10]
                                else:
                                    logger.info(f"    → {len(sub_subcategories)} sub-subcategorías")
                                
                                for k, sub_subcat in enumerate(sub_subcategories, 1):
                                    logger.info(f"      [{k}/{len(sub_subcategories)}] {sub_subcat['nombre_corto']}")
                                    
                                    sub_subcat_html = self.get_page_content(sub_subcat['url'])
                                    if sub_subcat_html:
                                        sub_sub_items = self.extract_catalog_items(sub_subcat_html)
                                        if sub_sub_items:
                                            logger.info(f"        ✓ {len(sub_sub_items)} productos")
                                            for item in sub_sub_items:
                                                item['categoria'] = sub_subcat['nombre']
                                                all_items.append(item)
                                    
                                    time.sleep(0.3)
                    
                    time.sleep(0.5)
            
            if not items and not subcategories:
                logger.info(f"Sin productos ni subcategorías en: {category['nombre_corto']}")
            
            # GUARDAR CSV POR CATEGORÍA inmediatamente
            if all_items:
                category_items = [item for item in all_items if item.get('categoria', '').startswith(category['nombre'])]
                if category_items:
                    self.save_category_to_csv(category_items, category['nombre_corto'])
            
            time.sleep(1)  # Pausa entre categorías
        
        # Eliminar duplicados del total
        logger.info("")
        logger.info("Eliminando duplicados del total...")
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
    
    def save_to_csv(self, items, filename='hidraulica_neumatica_productos.csv'):
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
    
    def save_category_to_csv(self, items, category_name, output_dir='categorias'):
        """Guarda productos de una categoría en un CSV individual"""
        if not items:
            return
        
        # Crear carpeta si no existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear nombre de archivo seguro
        safe_name = category_name.replace('/', '-').replace('>', '-').replace(' ', '_').replace('__', '_')
        safe_name = safe_name[:50]  # Limitar longitud
        filename = os.path.join(output_dir, f"{safe_name}.csv")
        
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
        
        logger.info(f"  💾 Guardado: {filename} ({len(items)} productos)")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Iniciando scraper de Hidráulica Neumática - Estehyne")
    logger.info("URL: https://www.hidraulicaneumatica.es/es/productos")
    logger.info("=" * 60)
    
    scraper = HidraulicaNeumatiaScraper()
    
    # Realizar scraping
    # Este sitio tiene MUCHAS subcategorías, configurar límites:
    # - max_categories: Número de categorías principales a procesar
    # - max_subcategories_per_category: Subcategorías por categoría (10 por defecto)
    # - max_depth: Profundidad de navegación (2=solo subcategorías, 3=incluir sub-subcategorías)
    
    items = scraper.scrape_catalog(
        max_categories=None,            # Procesar TODAS las categorías
        max_subcategories_per_category=50,  # Hasta 50 subcategorías por categoría
        max_depth=2                     # Solo 2 niveles (categoría > subcategoría)
    )
    
    if items:
        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✓ Total de productos encontrados: {len(items)}")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Muestra de productos extraídos:")
        for i, item in enumerate(items[:5], 1):
            logger.info(f"\n{i}. {item.get('titulo', 'Sin título')}")
            logger.info(f"   Código: {item.get('codigo', 'N/A')}")
            logger.info(f"   Categoría: {item.get('categoria', 'N/A')}")
            logger.info(f"   Precio: {item.get('precio', 'N/A')}")
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

