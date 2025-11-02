#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convertidor de productos scrapeados al formato de importación de WooCommerce
Convierte los CSV generados por los scrapers al formato estándar de WooCommerce
"""

import csv
import os
import logging
from datetime import datetime

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WooCommerceConverter:
    def __init__(self):
        # Columnas estándar de WooCommerce para importación
        self.woocommerce_fields = [
            'ID',
            'Type',
            'SKU',
            'Name',
            'Published',
            'Is featured?',
            'Visibility in catalog',
            'Short description',
            'Description',
            'Date sale price starts',
            'Date sale price ends',
            'Tax status',
            'Tax class',
            'In stock?',
            'Stock',
            'Backorders allowed?',
            'Sold individually?',
            'Weight (kg)',
            'Length (cm)',
            'Width (cm)',
            'Height (cm)',
            'Allow customer reviews?',
            'Purchase note',
            'Sale price',
            'Regular price',
            'Categories',
            'Tags',
            'Shipping class',
            'Images',
            'Download limit',
            'Download expiry days',
            'Parent',
            'Grouped products',
            'Upsells',
            'Cross-sells',
            'External URL',
            'Button text',
            'Position',
            'Attribute 1 name',
            'Attribute 1 value(s)',
            'Attribute 1 visible',
            'Attribute 1 global',
            'Meta: _custom_field_1',
            'Meta: _custom_field_2'
        ]
    
    def convert_csv(self, input_file, output_file=None):
        """Convierte un CSV de scrapper al formato WooCommerce"""
        
        if not os.path.exists(input_file):
            logger.error(f"Archivo no encontrado: {input_file}")
            return False
        
        # Generar nombre de archivo de salida si no se proporciona
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_woocommerce.csv"
        
        try:
            # Leer el CSV original
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            if not products:
                logger.warning(f"No hay productos en: {input_file}")
                return False
            
            logger.info(f"Leyendo {len(products)} productos de {input_file}")
            
            # Convertir a formato WooCommerce
            woo_products = []
            for i, product in enumerate(products, 1):
                woo_product = self.convert_product(product, i)
                woo_products.append(woo_product)
            
            # Guardar en formato WooCommerce
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.woocommerce_fields)
                writer.writeheader()
                writer.writerows(woo_products)
            
            logger.info(f"✓ Archivo WooCommerce creado: {output_file}")
            logger.info(f"✓ {len(woo_products)} productos convertidos")
            return True
            
        except Exception as e:
            logger.error(f"Error convirtiendo archivo: {e}")
            return False
    
    def convert_product(self, product, product_id):
        """Convierte un producto individual al formato WooCommerce"""
        
        # Extraer y limpiar datos
        sku = product.get('sku', '') or product.get('codigo', '') or f"PROD-{product_id}"
        name = product.get('titulo', 'Producto sin nombre').strip()
        short_desc = product.get('descripcion_corta', '').strip()
        full_desc = product.get('descripcion_completa', short_desc).strip()
        category = product.get('categoria', 'Sin categoría').strip()
        
        # Precio
        precio = product.get('precio', '').strip()
        precio_regular = product.get('precio_regular', precio).strip()
        precio_oferta = product.get('precio_oferta', '').strip()
        
        # Limpiar precios (eliminar símbolos de moneda)
        precio_regular = self.clean_price(precio_regular)
        precio_oferta = self.clean_price(precio_oferta)
        
        # Imágenes
        images = []
        if product.get('url_imagen_principal'):
            images.append(product['url_imagen_principal'])
        
        # Imágenes adicionales (separadas por ; en el CSV original)
        if product.get('urls_imagenes_adicionales'):
            additional_images = product['urls_imagenes_adicionales'].split(';')
            images.extend([img.strip() for img in additional_images if img.strip()])
        
        images_str = ', '.join(images)
        
        # Stock
        stock_status = product.get('stock', '').lower()
        in_stock = 1 if 'disponible' in stock_status or 'stock' in stock_status or not stock_status else 0
        
        # Crear producto en formato WooCommerce
        woo_product = {
            'ID': '',  # Vacío para nuevos productos
            'Type': 'simple',  # Tipo de producto (simple, variable, grouped, external)
            'SKU': sku,
            'Name': name,
            'Published': 1,  # 1 = publicado, 0 = borrador
            'Is featured?': 0,
            'Visibility in catalog': 'visible',
            'Short description': short_desc,
            'Description': full_desc,
            'Date sale price starts': '',
            'Date sale price ends': '',
            'Tax status': 'taxable',
            'Tax class': '',
            'In stock?': in_stock,
            'Stock': '',  # Cantidad en stock (vacío = sin gestión de stock)
            'Backorders allowed?': 0,
            'Sold individually?': 0,
            'Weight (kg)': '',
            'Length (cm)': '',
            'Width (cm)': '',
            'Height (cm)': '',
            'Allow customer reviews?': 1,
            'Purchase note': '',
            'Sale price': precio_oferta,
            'Regular price': precio_regular,
            'Categories': category,
            'Tags': '',
            'Shipping class': '',
            'Images': images_str,
            'Download limit': '',
            'Download expiry days': '',
            'Parent': '',
            'Grouped products': '',
            'Upsells': '',
            'Cross-sells': '',
            'External URL': product.get('enlace_detalle', ''),
            'Button text': '',
            'Position': 0,
            'Attribute 1 name': 'Código',
            'Attribute 1 value(s)': sku,
            'Attribute 1 visible': 1,
            'Attribute 1 global': 0,
            'Meta: _custom_field_1': '',
            'Meta: _custom_field_2': ''
        }
        
        return woo_product
    
    def clean_price(self, price_str):
        """Limpia el string de precio eliminando símbolos de moneda"""
        if not price_str:
            return ''
        
        # Eliminar símbolos comunes de moneda y espacios
        price_str = price_str.replace('€', '').replace('$', '').replace('USD', '')
        price_str = price_str.replace('EUR', '').replace(',', '.').strip()
        
        # Intentar convertir a float para validar
        try:
            float(price_str)
            return price_str
        except ValueError:
            return ''
    
    def convert_all_csvs(self, directory='.'):
        """Convierte todos los CSV de productos encontrados en el directorio"""
        logger.info(f"Buscando archivos CSV en: {directory}")
        
        # Patrones de archivos a convertir
        patterns = [
            'catalogo_bombas_bloch',
            'catalogo_evolucion',
            '_completo.csv',
            '_simple.csv',
            '_selenium.csv'
        ]
        
        converted_files = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.csv') and not filename.endswith('_woocommerce.csv'):
                # Verificar si coincide con algún patrón
                if any(pattern in filename for pattern in patterns):
                    input_path = os.path.join(directory, filename)
                    logger.info(f"\n{'='*60}")
                    logger.info(f"Procesando: {filename}")
                    logger.info(f"{'='*60}")
                    
                    if self.convert_csv(input_path):
                        converted_files.append(filename)
        
        if converted_files:
            logger.info(f"\n{'='*60}")
            logger.info(f"✓ Conversión completada")
            logger.info(f"{'='*60}")
            logger.info(f"Archivos convertidos: {len(converted_files)}")
            for f in converted_files:
                logger.info(f"  - {f}")
        else:
            logger.warning("\n⚠ No se encontraron archivos CSV para convertir")
            logger.info("\nArchivos compatibles:")
            logger.info("  - catalogo_bombas_bloch_*.csv")
            logger.info("  - catalogo_evolucion_*.csv")
    
    def convert_to_duda(self, input_file, output_file='bombas_bloch_duda.csv'):
        """Convierte productos al formato de importación de Duda.co"""
        
        if not os.path.exists(input_file):
            logger.error(f"Archivo no encontrado: {input_file}")
            return False
        
        try:
            # Leer el CSV original
            with open(input_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                products = list(reader)
            
            if not products:
                logger.warning(f"No hay productos en: {input_file}")
                return False
            
            logger.info(f"Convirtiendo {len(products)} productos a formato Duda.co")
            
            # Campos requeridos por Duda.co
            duda_fields = [
                'Product Name',
                'SKU',
                'Description',
                'Price',
                'Compare at Price',
                'Category',
                'Subcategory',
                'Image URL',
                'Additional Image URLs',
                'Product URL',
                'Stock',
                'Weight',
                'Brand',
                'Product Options',
                'Option Values',
                'Tax',
                'Shipping',
                'Meta Title',
                'Meta Description',
                'Custom Fields'
            ]
            
            # Convertir productos
            duda_products = []
            for product in products:
                duda_product = {
                    'Product Name': product.get('titulo', ''),
                    'SKU': product.get('sku', '') or product.get('codigo', ''),
                    'Description': product.get('descripcion_completa', '') or product.get('descripcion_corta', ''),
                    'Price': self.clean_price(product.get('precio', '') or product.get('precio_regular', '')),
                    'Compare at Price': self.clean_price(product.get('precio_regular', '')),
                    'Category': product.get('categoria', 'General'),
                    'Subcategory': '',
                    'Image URL': product.get('url_imagen_principal', ''),
                    'Additional Image URLs': product.get('urls_imagenes_adicionales', '').replace(';', ',').strip(),
                    'Product URL': product.get('enlace_detalle', ''),
                    'Stock': '999' if product.get('stock', '').lower() != 'agotado' else '0',
                    'Weight': '',
                    'Brand': 'Bombas Bloch',
                    'Product Options': '',
                    'Option Values': '',
                    'Tax': 'true',
                    'Shipping': 'true',
                    'Meta Title': product.get('titulo', '')[:60],
                    'Meta Description': product.get('descripcion_corta', '')[:160],
                    'Custom Fields': ''
                }
                duda_products.append(duda_product)
            
            # Guardar en formato Duda
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=duda_fields)
                writer.writeheader()
                writer.writerows(duda_products)
            
            logger.info(f"✓ Archivo Duda.co creado: {output_file}")
            logger.info(f"✓ {len(duda_products)} productos convertidos para Duda.co")
            return True
            
        except Exception as e:
            logger.error(f"Error convirtiendo a formato Duda.co: {e}")
            return False

def main():
    """Función principal"""
    logger.info("="*60)
    logger.info("Convertidor a formato WooCommerce")
    logger.info("="*60)
    logger.info("")
    
    converter = WooCommerceConverter()
    
    # Convertir todos los CSV encontrados en el directorio actual
    converter.convert_all_csvs('.')
    
    logger.info("")
    logger.info("="*60)
    logger.info("Cómo importar en WooCommerce:")
    logger.info("="*60)
    logger.info("1. En WordPress, ve a: WooCommerce > Productos")
    logger.info("2. Haz clic en 'Importar' (arriba de la página)")
    logger.info("3. Selecciona el archivo *_woocommerce.csv generado")
    logger.info("4. Mapea las columnas (WooCommerce lo hace automáticamente)")
    logger.info("5. Haz clic en 'Ejecutar importación'")
    logger.info("")
    logger.info("Notas:")
    logger.info("- Las imágenes deben estar accesibles por URL")
    logger.info("- Puedes editar precios antes de importar")
    logger.info("- Las categorías se crearán automáticamente")
    logger.info("="*60)

if __name__ == "__main__":
    main()

