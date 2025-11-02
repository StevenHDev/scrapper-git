#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado actual del CSV y determinar qué hacer
"""

import csv
import os
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verificar_estado_csv():
    """Verifica el estado actual del CSV"""
    csv_filename = 'generaweb_duda_empresas.csv'
    
    if not os.path.exists(csv_filename):
        logger.info("❌ El archivo CSV no existe")
        return
    
    # Contar líneas totales
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        total_lines = sum(1 for line in csvfile)
    
    logger.info(f"📊 Total de líneas en el CSV: {total_lines}")
    
    # Leer datos y analizar
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        empresas = list(reader)
        total_empresas = len(empresas)
        
        logger.info(f"📈 Total de empresas: {total_empresas}")
        
        if total_empresas == 0:
            logger.info("❌ No hay empresas en el CSV")
            return
        
        # Analizar IDs
        ids = []
        for empresa in empresas:
            if empresa.get('id') and empresa['id'].isdigit():
                ids.append(int(empresa['id']))
        
        if ids:
            min_id = min(ids)
            max_id = max(ids)
            logger.info(f"🔢 Rango de IDs: {min_id} - {max_id}")
            logger.info(f"📊 Total de IDs únicos: {len(set(ids))}")
            
            # Verificar duplicados
            ids_duplicados = len(ids) - len(set(ids))
            if ids_duplicados > 0:
                logger.warning(f"⚠️  IDs duplicados encontrados: {ids_duplicados}")
            else:
                logger.info("✅ No hay IDs duplicados")
        
        # Analizar estados
        estados = {}
        for empresa in empresas:
            estado = empresa.get('estado', 'Desconocido')
            estados[estado] = estados.get(estado, 0) + 1
        
        logger.info("📋 Distribución por estados:")
        for estado, cantidad in sorted(estados.items()):
            logger.info(f"   {estado}: {cantidad} empresas")
        
        # Mostrar últimas 5 empresas
        logger.info("🔍 Últimas 5 empresas procesadas:")
        for i, empresa in enumerate(empresas[-5:], 1):
            logger.info(f"   {i}. ID: {empresa.get('id', 'N/A')} - {empresa.get('empresa', 'Sin nombre')} - {empresa.get('estado', 'Sin estado')}")
        
        # Verificar si hay empresas con datos completos
        empresas_completas = 0
        for empresa in empresas:
            if (empresa.get('nombre') and empresa.get('apellidos') and 
                empresa.get('email') and empresa.get('telefono')):
                empresas_completas += 1
        
        logger.info(f"✅ Empresas con datos completos: {empresas_completas}/{total_empresas}")
        
        # Recomendaciones
        logger.info("\n" + "="*60)
        logger.info("💡 RECOMENDACIONES")
        logger.info("="*60)
        
        if total_empresas >= 2000:
            logger.info("✅ El scraping parece estar completo (2000+ empresas)")
            logger.info("   - Puedes proceder con el análisis de datos")
            logger.info("   - Considera limpiar datos duplicados si los hay")
        elif total_empresas >= 1000:
            logger.info("🔄 El scraping está en progreso")
            logger.info("   - Puedes continuar con más páginas")
            logger.info("   - Verifica que no haya duplicados")
        else:
            logger.info("🚀 El scraping está en etapas iniciales")
            logger.info("   - Continúa con el proceso normal")
            logger.info("   - Monitorea el progreso regularmente")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("VERIFICADOR DE ESTADO DEL CSV")
    logger.info("=" * 60)
    
    verificar_estado_csv()
    
    logger.info("\n" + "="*60)
    logger.info("VERIFICACIÓN COMPLETADA")
    logger.info("="*60)

if __name__ == "__main__":
    main()
