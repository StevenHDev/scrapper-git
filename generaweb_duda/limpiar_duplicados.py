#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpiar duplicados del CSV de empresas
"""

import csv
import os
import logging
from collections import defaultdict

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def limpiar_duplicados():
    """Limpia los duplicados del CSV manteniendo la versión más completa"""
    csv_filename = 'generaweb_duda_empresas.csv'
    backup_filename = 'generaweb_duda_empresas_backup.csv'
    
    if not os.path.exists(csv_filename):
        logger.error("❌ El archivo CSV no existe")
        return
    
    # Crear backup
    logger.info("📋 Creando backup del archivo original...")
    with open(csv_filename, 'r', encoding='utf-8-sig') as original:
        with open(backup_filename, 'w', encoding='utf-8-sig') as backup:
            backup.write(original.read())
    logger.info(f"✅ Backup creado: {backup_filename}")
    
    # Leer datos
    logger.info("📖 Leyendo datos del CSV...")
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        empresas = list(reader)
    
    logger.info(f"📊 Total de empresas antes de limpiar: {len(empresas)}")
    
    # Agrupar por ID
    empresas_por_id = defaultdict(list)
    for empresa in empresas:
        if empresa.get('id') and empresa['id'].isdigit():
            empresas_por_id[int(empresa['id'])].append(empresa)
    
    logger.info(f"🔢 IDs únicos encontrados: {len(empresas_por_id)}")
    
    # Limpiar duplicados
    empresas_limpias = []
    duplicados_eliminados = 0
    
    for id_empresa, lista_empresas in empresas_por_id.items():
        if len(lista_empresas) == 1:
            # No hay duplicados
            empresas_limpias.append(lista_empresas[0])
        else:
            # Hay duplicados, elegir la mejor versión
            logger.info(f"🔄 Procesando duplicados para ID {id_empresa} ({len(lista_empresas)} copias)")
            
            # Criterio para elegir la mejor versión:
            # 1. La que tenga más campos completos
            # 2. La que tenga datos de perfil (nombre, apellidos, etc.)
            mejor_empresa = None
            mejor_puntuacion = -1
            
            for empresa in lista_empresas:
                puntuacion = 0
                
                # Puntos por campos básicos
                if empresa.get('empresa'):
                    puntuacion += 1
                if empresa.get('estado'):
                    puntuacion += 1
                
                # Puntos por datos del perfil
                if empresa.get('nombre'):
                    puntuacion += 2
                if empresa.get('apellidos'):
                    puntuacion += 2
                if empresa.get('email'):
                    puntuacion += 2
                if empresa.get('telefono'):
                    puntuacion += 2
                if empresa.get('direccion'):
                    puntuacion += 1
                if empresa.get('cif_nif'):
                    puntuacion += 1
                
                if puntuacion > mejor_puntuacion:
                    mejor_puntuacion = puntuacion
                    mejor_empresa = empresa
            
            empresas_limpias.append(mejor_empresa)
            duplicados_eliminados += len(lista_empresas) - 1
    
    logger.info(f"🧹 Duplicados eliminados: {duplicados_eliminados}")
    logger.info(f"📊 Total de empresas después de limpiar: {len(empresas_limpias)}")
    
    # Escribir archivo limpio
    logger.info("💾 Escribiendo archivo limpio...")
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        if empresas_limpias:
            fieldnames = empresas_limpias[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(empresas_limpias)
    
    logger.info("✅ Archivo limpio guardado")
    
    # Verificar resultado
    logger.info("🔍 Verificando resultado...")
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        empresas_finales = list(reader)
    
    ids_finales = set()
    for empresa in empresas_finales:
        if empresa.get('id') and empresa['id'].isdigit():
            ids_finales.add(int(empresa['id']))
    
    logger.info(f"📊 Total de empresas finales: {len(empresas_finales)}")
    logger.info(f"🔢 IDs únicos finales: {len(ids_finales)}")
    
    if len(empresas_finales) == len(ids_finales):
        logger.info("✅ ¡Limpieza exitosa! No hay duplicados")
    else:
        logger.warning("⚠️  Aún hay duplicados después de la limpieza")
    
    # Estadísticas finales
    estados = {}
    for empresa in empresas_finales:
        estado = empresa.get('estado', 'Desconocido')
        estados[estado] = estados.get(estado, 0) + 1
    
    logger.info("📋 Distribución final por estados:")
    for estado, cantidad in sorted(estados.items()):
        logger.info(f"   {estado}: {cantidad} empresas")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("LIMPIEZA DE DUPLICADOS")
    logger.info("=" * 60)
    
    limpiar_duplicados()
    
    logger.info("\n" + "="*60)
    logger.info("LIMPIEZA COMPLETADA")
    logger.info("="*60)

if __name__ == "__main__":
    main()
