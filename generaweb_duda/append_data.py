#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para hacer append de datos al CSV existente
"""

import csv
import os
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def append_sample_data():
    """Añade datos de muestra al CSV existente"""
    
    # Datos de muestra para añadir
    sample_empresas = [
        {
            'id': '12345',
            'empresa': 'EMPRESA DE PRUEBA 1',
            'entrada': '22/10/2025',
            'estado': 'Activo',
            'nombre': 'Juan',
            'apellidos': 'Pérez García',
            'razon_social': 'EMPRESA DE PRUEBA 1 SL',
            'login': 'jperez',
            'password': 'password123',
            'cif_nif': '12345678A',
            'direccion': 'Calle Principal 123',
            'provincia': 'Madrid',
            'ciudad': 'Madrid',
            'codigo_postal': '28001',
            'pais': 'Spain',
            'telefono': '911234567',
            'fax': '',
            'telefono_movil': '612345678',
            'url': 'https://www.empresa1.com',
            'email': 'info@empresa1.com',
            'num_dominios': '1',
            'wordpress_url': '',
            'gestor_proyecto': 'Gestor 1',
            'url_perfil': 'http://generawebduda.nlocal.com/index.php?s=user_profile&id=12345',
            'url_web': 'https://www.empresa1.com',
            'url_panel': 'http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id=12345'
        },
        {
            'id': '12346',
            'empresa': 'EMPRESA DE PRUEBA 2',
            'entrada': '22/10/2025',
            'estado': 'Diseño',
            'nombre': 'María',
            'apellidos': 'López Martínez',
            'razon_social': 'EMPRESA DE PRUEBA 2 SL',
            'login': 'mlopez',
            'password': 'password456',
            'cif_nif': '87654321B',
            'direccion': 'Avenida Secundaria 456',
            'provincia': 'Barcelona',
            'ciudad': 'Barcelona',
            'codigo_postal': '08001',
            'pais': 'Spain',
            'telefono': '937654321',
            'fax': '',
            'telefono_movil': '676543210',
            'url': 'https://www.empresa2.com',
            'email': 'info@empresa2.com',
            'num_dominios': '2',
            'wordpress_url': '',
            'gestor_proyecto': 'Gestor 2',
            'url_perfil': 'http://generawebduda.nlocal.com/index.php?s=user_profile&id=12346',
            'url_web': 'https://www.empresa2.com',
            'url_panel': 'http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id=12346'
        }
    ]
    
    filename = 'generaweb_duda_empresas.csv'
    file_exists = os.path.exists(filename)
    
    logger.info(f"Archivo existe: {file_exists}")
    
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
        
        if not file_exists:
            writer.writeheader()
            logger.info("✓ Header escrito en nuevo archivo CSV")
        else:
            logger.info("✓ Añadiendo datos al archivo CSV existente")
        
        for empresa in sample_empresas:
            writer.writerow(empresa)
            logger.info(f"✓ Añadida empresa: {empresa['empresa']} (ID: {empresa['id']})")
    
    logger.info(f"✓ {len(sample_empresas)} empresas añadidas a {filename}")

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Script de Append de Datos")
    logger.info("=" * 60)
    
    append_sample_data()
    
    logger.info("=" * 60)
    logger.info("Proceso completado")
    logger.info("=" * 60)
