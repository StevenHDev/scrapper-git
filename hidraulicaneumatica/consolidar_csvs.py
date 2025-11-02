#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para consolidar todos los CSV de categorías en uno solo
Elimina duplicados y combina las categorías de productos repetidos
"""

import csv
import os
from collections import defaultdict
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def consolidar_csvs():
    """
    Consolida todos los CSV de la carpeta categorias/
    """
    categorias_dir = 'categorias'
    
    if not os.path.exists(categorias_dir):
        logger.error(f"No existe la carpeta {categorias_dir}")
        return
    
    # Diccionario para almacenar productos únicos por código
    # Estructura: {codigo: {datos del producto + lista de categorías}}
    productos_unicos = defaultdict(lambda: {
        'titulo': '',
        'codigo': '',
        'precio': '',
        'imagen_principal': '',
        'url_imagen_principal': '',
        'descripcion_corta': '',
        'categorias': set(),  # Usamos set para evitar duplicados de categorías
        'marca': '',
        'enlace_detalle': ''
    })
    
    # Leer todos los CSV
    archivos_csv = [f for f in os.listdir(categorias_dir) if f.endswith('.csv')]
    logger.info(f"Encontrados {len(archivos_csv)} archivos CSV en {categorias_dir}/")
    
    total_productos_leidos = 0
    
    for archivo in archivos_csv:
        ruta_archivo = os.path.join(categorias_dir, archivo)
        
        try:
            with open(ruta_archivo, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    codigo = row.get('codigo', '').strip()
                    titulo = row.get('titulo', '').strip()
                    
                    if not codigo:
                        continue
                    
                    total_productos_leidos += 1
                    
                    # Si es la primera vez que vemos este producto, guardamos todos los datos
                    if not productos_unicos[codigo]['codigo']:
                        productos_unicos[codigo]['codigo'] = codigo
                        productos_unicos[codigo]['titulo'] = titulo
                        productos_unicos[codigo]['precio'] = row.get('precio', '').strip()
                        productos_unicos[codigo]['imagen_principal'] = row.get('imagen_principal', '').strip()
                        productos_unicos[codigo]['url_imagen_principal'] = row.get('url_imagen_principal', '').strip()
                        productos_unicos[codigo]['descripcion_corta'] = row.get('descripcion_corta', '').strip()
                        productos_unicos[codigo]['marca'] = row.get('marca', '').strip()
                        productos_unicos[codigo]['enlace_detalle'] = row.get('enlace_detalle', '').strip()
                    elif titulo and not productos_unicos[codigo]['titulo']:
                        # Si ya existe pero no tiene título, actualizar solo el título
                        productos_unicos[codigo]['titulo'] = titulo
                    
                    # Siempre agregamos la categoría (puede estar en múltiples)
                    categoria = row.get('categoria', '').strip()
                    if categoria:
                        productos_unicos[codigo]['categorias'].add(categoria)
        
        except Exception as e:
            logger.error(f"Error leyendo {archivo}: {e}")
            continue
    
    logger.info(f"Total de productos leídos (con duplicados): {total_productos_leidos}")
    logger.info(f"Total de productos únicos: {len(productos_unicos)}")
    
    # Guardar CSV consolidado
    output_file = 'hidraulica_neumatica_consolidado.csv'
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
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
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        productos_ordenados = sorted(productos_unicos.values(), key=lambda x: x['codigo'])
        
        for producto in productos_ordenados:
            # Convertir set de categorías a string separado por " | "
            categorias_str = ' | '.join(sorted(producto['categorias']))
            
            writer.writerow({
                'titulo': producto['titulo'],
                'codigo': producto['codigo'],
                'precio': producto['precio'],
                'imagen_principal': producto['imagen_principal'],
                'url_imagen_principal': producto['url_imagen_principal'],
                'descripcion_corta': producto['descripcion_corta'],
                'categoria': categorias_str,
                'marca': producto['marca'],
                'enlace_detalle': producto['enlace_detalle']
            })
    
    logger.info(f"✅ CSV consolidado guardado: {output_file}")
    
    # Estadísticas
    productos_con_multiples_categorias = sum(1 for p in productos_unicos.values() if len(p['categorias']) > 1)
    logger.info(f"📊 Productos con múltiples categorías: {productos_con_multiples_categorias}")
    
    # Mostrar algunos ejemplos de productos con múltiples categorías
    logger.info("\n📋 Ejemplos de productos con múltiples categorías:")
    ejemplos = 0
    for producto in productos_ordenados:
        if len(producto['categorias']) > 1 and ejemplos < 5:
            logger.info(f"  • {producto['titulo']} ({producto['codigo']})")
            logger.info(f"    Categorías ({len(producto['categorias'])}): {' | '.join(list(producto['categorias'])[:3])}...")
            ejemplos += 1
    
    return output_file


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("CONSOLIDACIÓN DE CSV - Hidráulica Neumática")
    logger.info("=" * 60)
    
    output = consolidar_csvs()
    
    if output:
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ CONSOLIDACIÓN COMPLETADA")
        logger.info("=" * 60)
        logger.info(f"Archivo generado: {output}")



