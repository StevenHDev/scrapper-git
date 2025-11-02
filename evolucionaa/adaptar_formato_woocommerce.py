#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adaptar el archivo CSV generado al formato correcto de WooCommerce
"""

import csv
import re

def adaptar_archivo_woocommerce():
    """
    Adapta el archivo evolucion_a_woocommerce.csv al formato correcto
    """
    
    # Archivo de entrada y salida
    archivo_entrada = '/Users/juliancastaneda/Documents/03. PROYECTOS/scrapper-git/evolucionaa/evolucion_a_woocommerce.csv'
    archivo_salida = '/Users/juliancastaneda/Documents/03. PROYECTOS/scrapper-git/evolucionaa/evolucion_a_woocommerce_corregido.csv'
    
    # Mapeo de columnas del inglés al español (basado en el archivo correcto)
    mapeo_columnas = {
        'ID': 'ID',
        'Type': 'Tipo',
        'SKU': 'SKU',
        'Name': 'Nombre',
        'Published': 'Publicado',
        'Is featured?': '¿Está destacado?',
        'Visibility in catalog': 'Visibilidad en el catálogo',
        'Short description': 'Descripción corta',
        'Description': 'Descripción',
        'Date sale price starts': 'Día en que empieza el precio rebajado',
        'Date sale price ends': 'Día en que termina el precio rebajado',
        'Tax status': 'Estado del impuesto',
        'Tax class': 'Clase de impuesto',
        'In stock?': '¿Existencias?',
        'Stock': 'Inventario',
        'Backorders allowed?': '¿Permitir reservas de productos agotados?',
        'Sold individually?': '¿Vendido individualmente?',
        'Weight (kg)': 'Peso (kg)',
        'Length (cm)': 'Longitud (cm)',
        'Width (cm)': 'Anchura (cm)',
        'Height (cm)': 'Altura (cm)',
        'Allow customer reviews?': '¿Permitir valoraciones de clientes?',
        'Purchase note': 'Nota de compra',
        'Sale price': 'Precio rebajado',
        'Regular price': 'Precio normal',
        'Categories': 'Categorías',
        'Tags': 'Etiquetas',
        'Shipping class': 'Clase de envío',
        'Images': 'Imágenes',
        'Download limit': 'Límite de descargas',
        'Download expiry days': 'Días de caducidad de la descarga',
        'Parent': 'Superior',
        'Grouped products': 'Productos agrupados',
        'Upsells': 'Ventas dirigidas',
        'Cross-sells': 'Ventas cruzadas',
        'External URL': 'URL externa',
        'Button text': 'Texto del botón',
        'Position': 'Posición',
        'Attribute 1 name': 'Nombre del atributo 1',
        'Attribute 1 value(s)': 'Valor(es) del atributo 1',
        'Attribute 1 visible': 'Atributo visible 1',
        'Attribute 1 global': 'Atributo global 1',
        'Meta: _custom_field_1': 'Meta: _custom_field_1',
        'Meta: _custom_field_2': 'Meta: _custom_field_2'
    }
    
    # Orden de las columnas según el archivo correcto
    orden_columnas = [
        'ID', 'Tipo', 'SKU', 'GTIN, UPC, EAN o ISBN', 'Nombre', 'Publicado', 
        '¿Está destacado?', 'Visibilidad en el catálogo', 'Descripción corta', 
        'Descripción', 'Día en que empieza el precio rebajado', 
        'Día en que termina el precio rebajado', 'Estado del impuesto', 
        'Clase de impuesto', '¿Existencias?', 'Inventario', 
        'Cantidad de bajo inventario', '¿Permitir reservas de productos agotados?', 
        '¿Vendido individualmente?', 'Peso (kg)', 'Longitud (cm)', 
        'Anchura (cm)', 'Altura (cm)', '¿Permitir valoraciones de clientes?', 
        'Nota de compra', 'Precio rebajado', 'Precio normal', 'Categorías', 
        'Etiquetas', 'Clase de envío', 'Imágenes', 'Límite de descargas', 
        'Días de caducidad de la descarga', 'Superior', 'Productos agrupados', 
        'Ventas dirigidas', 'Ventas cruzadas', 'URL externa', 'Texto del botón', 
        'Posición', 'Marcas', 'Nombre del atributo 1', 'Valor(es) del atributo 1', 
        'Atributo visible 1', 'Atributo global 1', 'Meta: _custom_field_1', 
        'Meta: _custom_field_2'
    ]
    
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as archivo_in:
            lector = csv.DictReader(archivo_in)
            
            # Leer todas las filas
            filas = []
            for fila in lector:
                filas.append(fila)
        
        # Crear el archivo de salida con el formato correcto
        with open(archivo_salida, 'w', encoding='utf-8', newline='') as archivo_out:
            escritor = csv.DictWriter(archivo_out, fieldnames=orden_columnas)
            escritor.writeheader()
            
            for fila in filas:
                # Crear nueva fila con el formato correcto
                nueva_fila = {}
                
                # Mapear las columnas existentes
                for col_original, col_nueva in mapeo_columnas.items():
                    if col_original in fila:
                        nueva_fila[col_nueva] = fila[col_original]
                
                # Agregar columnas faltantes con valores por defecto
                for columna in orden_columnas:
                    if columna not in nueva_fila:
                        if columna == 'GTIN, UPC, EAN o ISBN':
                            nueva_fila[columna] = ''
                        elif columna == 'Cantidad de bajo inventario':
                            nueva_fila[columna] = ''
                        elif columna == 'Marcas':
                            nueva_fila[columna] = ''
                        else:
                            nueva_fila[columna] = ''
                
                # Corregir formato de precios (quitar comillas y asegurar formato correcto)
                if 'Precio rebajado' in nueva_fila and nueva_fila['Precio rebajado']:
                    precio = nueva_fila['Precio rebajado'].replace('"', '').replace(',', '.')
                    nueva_fila['Precio rebajado'] = precio
                
                if 'Precio normal' in nueva_fila and nueva_fila['Precio normal']:
                    precio = nueva_fila['Precio normal'].replace('"', '').replace(',', '.')
                    nueva_fila['Precio normal'] = precio
                
                # Corregir URLs de imágenes (cambiar dominio si es necesario)
                if 'Imágenes' in nueva_fila and nueva_fila['Imágenes']:
                    imagen_url = nueva_fila['Imágenes']
                    # Cambiar el dominio de las imágenes si es necesario
                    if 'static.plenummedia.com' in imagen_url:
                        imagen_url = imagen_url.replace('static.plenummedia.com', 'test.evolucion-a.com')
                    nueva_fila['Imágenes'] = imagen_url
                
                # Asegurar que el ID esté vacío para productos nuevos
                if 'ID' in nueva_fila:
                    nueva_fila['ID'] = ''
                
                # Escribir la fila
                escritor.writerow(nueva_fila)
        
        print(f"✅ Archivo adaptado exitosamente: {archivo_salida}")
        print(f"📊 Total de productos procesados: {len(filas)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al procesar el archivo: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔄 Iniciando adaptación del archivo CSV...")
    if adaptar_archivo_woocommerce():
        print("✅ Proceso completado exitosamente")
    else:
        print("❌ El proceso falló")

