#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer dominios desde la URL específica de GeneraWeb Duda
URL: http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&domain=&count=1000&search=Buscar&s=domain_queue#empresas

Este script extrae datos de la tabla HTML con la estructura específica de dominios.
"""

import sys
import os
import logging
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapper_dominios import GeneraWebDudaScraperDominios

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extraer_dominios_desde_url(url):
    """
    Extrae dominios desde una URL específica de GeneraWeb Duda
    
    Args:
        url (str): URL de la página de dominios de GeneraWeb Duda
    
    Returns:
        int: Número de dominios extraídos
    """
    logger.info("=" * 80)
    logger.info("EXTRACTOR DE DOMINIOS - GENERAWEB DUDA")
    logger.info("=" * 80)
    logger.info(f"URL objetivo: {url}")
    
    # Crear instancia del scraper
    scraper = GeneraWebDudaScraperDominios(headless=True)
    
    try:
        # Extraer dominios desde la URL específica
        total_dominios = scraper.scrape_dominios_from_url(url)
        
        if total_dominios > 0:
            logger.info("")
            logger.info(f"✓ Total de dominios extraídos: {total_dominios}")
            logger.info("✓ Todos los dominios se guardaron en el CSV")
            logger.info("✓ Archivo CSV: generaweb_duda_table_dominios.csv")
            logger.info("")
            logger.info("Campos extraídos por dominio:")
            logger.info("  - ID del dominio")
            logger.info("  - Nombre de la empresa")
            logger.info("  - Dominio web")
            logger.info("  - URL del sitio web")
            logger.info("  - Si es principal (SI/NO)")
            logger.info("  - Plataforma de correo (Arsys, Rackspace, etc.)")
            logger.info("  - Número de cuentas de correo")
            logger.info("  - URL del perfil del dominio")
        else:
            logger.info("")
            logger.info("No se encontraron dominios para procesar")
            logger.info("Posibles causas:")
            logger.info("  - Problema de login")
            logger.info("  - La página no contiene datos")
            logger.info("  - Error de conexión")
        
        return total_dominios
        
    except Exception as e:
        logger.error(f"Error durante la extracción: {e}")
        return 0

def extraer_multiples_paginas():
    """
    Extrae dominios de múltiples páginas de GeneraWeb Duda
    """
    logger.info("=" * 80)
    logger.info("EXTRACTOR DE MÚLTIPLES PÁGINAS - GENERAWEB DUDA")
    logger.info("=" * 80)
    
    # URLs de las páginas a procesar
    urls = [
        "http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&domain=&count=1000&search=Buscar&s=domain_queue#empresas",
        "http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&domain=&count=1000&search=Buscar&s=domain_queue&page=2",
        "http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&domain=&count=1000&search=Buscar&s=domain_queue&page=3"
    ]
    
    total_dominios = 0
    
    for i, url in enumerate(urls, 1):
        logger.info(f"\n{'='*50}")
        logger.info(f"PROCESANDO PÁGINA {i}")
        logger.info(f"{'='*50}")
        
        dominios_pagina = extraer_dominios_desde_url(url)
        total_dominios += dominios_pagina
        
        logger.info(f"✓ Página {i} completada: {dominios_pagina} dominios extraídos")
        
        # Pausa entre páginas
        if i < len(urls):
            logger.info("Esperando antes de procesar la siguiente página...")
            time.sleep(3)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"EXTRACCIÓN COMPLETADA - TOTAL: {total_dominios} dominios")
    logger.info(f"{'='*80}")
    
    return total_dominios

def main():
    """Función principal"""
    # Extraer dominios de múltiples páginas
    total = extraer_multiples_paginas()
    
    logger.info("=" * 80)
    logger.info("EXTRACCIÓN COMPLETADA")
    logger.info("=" * 80)
    
    if total > 0:
        logger.info(f"✓ Total de dominios extraídos: {total}")
        logger.info("✓ Revisa el archivo CSV generado")
        logger.info("✓ Los nuevos dominios se agregaron al archivo existente")
    else:
        logger.info("No se extrajeron dominios")
        logger.info("Verifica las credenciales de login y la conectividad")
    
    return total

if __name__ == "__main__":
    main()
