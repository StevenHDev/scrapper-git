#!/usr/bin/env python3
"""
Script para eliminar duplicados del archivo CSV de dominios
"""

import csv
import logging
from collections import OrderedDict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def eliminar_duplicados_csv(archivo_entrada, archivo_salida=None):
    """
    Elimina duplicados del archivo CSV de dominios
    """
    try:
        logger.info(f"Leyendo archivo: {archivo_entrada}")
        
        # Leer el CSV
        registros = []
        with open(archivo_entrada, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                registros.append(row)
        
        logger.info(f"Total de registros antes de eliminar duplicados: {len(registros)}")
        
        # Mostrar las columnas disponibles para debug
        if registros:
            logger.info(f"Columnas disponibles: {list(registros[0].keys())}")
        
        # Contar duplicados por ID
        ids_vistos = set()
        duplicados_id = 0
        for registro in registros:
            id_valor = registro.get('id', '').strip()
            if id_valor in ids_vistos:
                duplicados_id += 1
            else:
                ids_vistos.add(id_valor)
        
        # Contar duplicados por empresa + dominio
        combinaciones_vistas = set()
        duplicados_empresa_dominio = 0
        for registro in registros:
            empresa = registro.get('empresa', '').strip()
            dominio = registro.get('dominio', '').strip()
            combinacion = (empresa, dominio)
            if combinacion in combinaciones_vistas:
                duplicados_empresa_dominio += 1
            else:
                combinaciones_vistas.add(combinacion)
        
        logger.info(f"Duplicados por ID: {duplicados_id}")
        logger.info(f"Duplicados por empresa + dominio: {duplicados_empresa_dominio}")
        
        # Eliminar duplicados basados en empresa + dominio (mantener el primero)
        registros_finales = []
        combinaciones_procesadas = set()
        
        for registro in registros:
            empresa = registro.get('empresa', '').strip()
            dominio = registro.get('dominio', '').strip()
            combinacion = (empresa, dominio)
            if combinacion not in combinaciones_procesadas:
                registros_finales.append(registro)
                combinaciones_procesadas.add(combinacion)
        
        duplicados_eliminados = len(registros) - len(registros_finales)
        logger.info(f"Duplicados eliminados: {duplicados_eliminados}")
        logger.info(f"Registros finales: {len(registros_finales)}")
        
        # Determinar archivo de salida
        if archivo_salida is None:
            archivo_salida = archivo_entrada.replace('.csv', '_sin_duplicados.csv')
        
        # Guardar el archivo sin duplicados
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as file:
            if registros_finales:
                fieldnames = registros_finales[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(registros_finales)
        
        logger.info(f"✓ Archivo guardado: {archivo_salida}")
        logger.info(f"✓ Total de registros únicos: {len(registros_finales)}")
        logger.info(f"✓ Duplicados eliminados: {len(registros) - len(registros_finales)}")
        
        return len(registros_finales)
        
    except Exception as e:
        logger.error(f"Error al procesar el archivo: {e}")
        return 0

def main():
    """
    Función principal
    """
    logger.info("=" * 80)
    logger.info("ELIMINADOR DE DUPLICADOS - GENERAWEB DUDA")
    logger.info("=" * 80)
    
    archivo_entrada = "generaweb_duda_table_dominios.csv"
    archivo_salida = "generaweb_duda_table_dominios_sin_duplicados.csv"
    
    # Eliminar duplicados
    registros_unicos = eliminar_duplicados_csv(archivo_entrada, archivo_salida)
    
    if registros_unicos > 0:
        logger.info(f"\n{'='*80}")
        logger.info("PROCESO COMPLETADO")
        logger.info(f"{'='*80}")
        logger.info(f"✓ Archivo original: {archivo_entrada}")
        logger.info(f"✓ Archivo sin duplicados: {archivo_salida}")
        logger.info(f"✓ Registros únicos: {registros_unicos}")
    else:
        logger.error("❌ Error en el proceso de eliminación de duplicados")

if __name__ == "__main__":
    main()
