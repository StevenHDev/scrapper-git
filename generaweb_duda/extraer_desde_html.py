#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer dominios desde HTML copiado de GeneraWeb Duda
Útil cuando no se puede acceder directamente a la página por problemas de login
"""

import sys
import os
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapper_dominios import GeneraWebDudaScraperDominios

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extraer_desde_html_manual():
    """
    Extrae dominios desde HTML copiado manualmente de la página
    """
    logger.info("=" * 80)
    logger.info("EXTRACTOR DE DOMINIOS DESDE HTML MANUAL")
    logger.info("=" * 80)
    
    print("\n" + "="*60)
    print("INSTRUCCIONES:")
    print("="*60)
    print("1. Ve a la página: http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&domain=&count=1000&search=Buscar&s=domain_queue#empresas")
    print("2. Haz login con tus credenciales")
    print("3. Copia toda la tabla HTML (desde <table class='table' hasta </table>)")
    print("4. Pega el HTML en el archivo 'html_dominios.html' en este directorio")
    print("5. Ejecuta este script nuevamente")
    print("="*60)
    
    # Verificar si existe el archivo HTML
    html_file = "html_dominios.html"
    if not os.path.exists(html_file):
        logger.info(f"\nNo se encontró el archivo '{html_file}'")
        logger.info("Por favor, crea el archivo con el HTML de la tabla y vuelve a ejecutar el script")
        return 0
    
    # Leer el HTML del archivo
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        logger.info(f"✓ HTML leído desde {html_file}")
    except Exception as e:
        logger.error(f"Error leyendo el archivo HTML: {e}")
        return 0
    
    # Crear instancia del scraper
    scraper = GeneraWebDudaScraperDominios()
    
    # Extraer dominios del HTML
    dominios = scraper.extract_table_data_from_html(html_content)
    
    if not dominios:
        logger.warning("No se encontraron dominios en el HTML")
        logger.info("Verifica que el HTML contenga la tabla con class='table'")
        return 0
    
    logger.info(f"✓ Dominios extraídos: {len(dominios)}")
    logger.info("-" * 50)
    
    # Mostrar resumen de dominios extraídos
    for i, dominio in enumerate(dominios, 1):
        logger.info(f"Dominio {i}:")
        logger.info(f"  ID: {dominio.get('id', 'N/A')}")
        logger.info(f"  Empresa: {dominio.get('empresa', 'N/A')}")
        logger.info(f"  Dominio: {dominio.get('dominio', 'N/A')}")
        logger.info(f"  Principal: {dominio.get('principal', 'N/A')}")
        logger.info(f"  Plataforma Correo: {dominio.get('plataforma_correo', 'N/A')}")
        logger.info(f"  Cuentas Correo: {dominio.get('cuentas_correo', 'N/A')}")
        logger.info("")
    
    # Guardar en CSV
    scraper.save_table_dominios_incremental(dominios)
    logger.info(f"✓ {len(dominios)} dominios guardados en CSV")
    logger.info("✓ Archivo: generaweb_duda_table_dominios.csv")
    
    return len(dominios)

def main():
    """Función principal"""
    total = extraer_desde_html_manual()
    
    logger.info("=" * 80)
    logger.info("EXTRACCIÓN COMPLETADA")
    logger.info("=" * 80)
    
    if total > 0:
        logger.info(f"✓ Total de dominios extraídos: {total}")
        logger.info("✓ Revisa el archivo CSV generado")
    else:
        logger.info("No se extrajeron dominios")
        logger.info("Asegúrate de tener el archivo 'html_dominios.html' con el HTML de la tabla")
    
    return total

if __name__ == "__main__":
    main()
