#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el estado del CSV de dominios
"""

import csv
import os
import logging

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verificar_estado_dominios():
    """Verifica el estado actual del CSV de dominios"""
    csv_filename = 'generaweb_duda_dominios.csv'
    
    if not os.path.exists(csv_filename):
        logger.info("❌ El archivo CSV de dominios no existe")
        return
    
    # Contar líneas totales
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        total_lines = sum(1 for line in csvfile)
    
    logger.info(f"📊 Total de líneas en el CSV: {total_lines}")
    
    # Leer datos y analizar
    with open(csv_filename, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        
        dominios = list(reader)
        total_dominios = len(dominios)
        
        logger.info(f"📈 Total de dominios: {total_dominios}")
        
        if total_dominios == 0:
            logger.info("❌ No hay dominios en el CSV")
            return
        
        # Analizar IDs
        ids = []
        for dominio in dominios:
            if dominio.get('id') and dominio['id'].isdigit():
                ids.append(int(dominio['id']))
        
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
        
        # Analizar dominios únicos
        dominios_unicos = set()
        for dominio in dominios:
            if dominio.get('dominio'):
                dominios_unicos.add(dominio['dominio'])
        
        logger.info(f"🌐 Dominios únicos: {len(dominios_unicos)}")
        
        # Analizar estados
        estados = {}
        for dominio in dominios:
            estado = dominio.get('estado', 'Desconocido')
            estados[estado] = estados.get(estado, 0) + 1
        
        logger.info("📋 Distribución por estados:")
        for estado, cantidad in sorted(estados.items()):
            logger.info(f"   {estado}: {cantidad} dominios")
        
        # Mostrar últimos 5 dominios
        logger.info("🔍 Últimos 5 dominios procesados:")
        for i, dominio in enumerate(dominios[-5:], 1):
            logger.info(f"   {i}. ID: {dominio.get('id', 'N/A')} - {dominio.get('dominio', 'Sin dominio')} - {dominio.get('estado', 'Sin estado')}")
        
        # Verificar si hay dominios con datos completos
        dominios_completos = 0
        for dominio in dominios:
            if (dominio.get('nombre') and dominio.get('apellidos') and 
                dominio.get('email') and dominio.get('telefono')):
                dominios_completos += 1
        
        logger.info(f"✅ Dominios con datos completos: {dominios_completos}/{total_dominios}")
        
        # Análisis de dominios
        dominios_con_www = 0
        dominios_sin_www = 0
        for dominio in dominios:
            if dominio.get('dominio'):
                if dominio['dominio'].startswith('www.'):
                    dominios_con_www += 1
                else:
                    dominios_sin_www += 1
        
        logger.info(f"🌐 Dominios con www: {dominios_con_www}")
        logger.info(f"🌐 Dominios sin www: {dominios_sin_www}")
        
        # Recomendaciones
        logger.info("\n" + "="*60)
        logger.info("💡 RECOMENDACIONES")
        logger.info("="*60)
        
        if total_dominios >= 1000:
            logger.info("✅ El scraping de dominios parece estar completo")
            logger.info("   - Puedes proceder con el análisis de dominios")
            logger.info("   - Considera analizar la distribución de dominios")
        elif total_dominios >= 500:
            logger.info("🔄 El scraping de dominios está en progreso")
            logger.info("   - Puedes continuar con más páginas")
            logger.info("   - Verifica que no haya duplicados")
        else:
            logger.info("🚀 El scraping de dominios está en etapas iniciales")
            logger.info("   - Continúa con el proceso normal")
            logger.info("   - Monitorea el progreso regularmente")

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("VERIFICADOR DE ESTADO DEL CSV DE DOMINIOS")
    logger.info("=" * 60)
    
    verificar_estado_dominios()
    
    logger.info("\n" + "="*60)
    logger.info("VERIFICACIÓN COMPLETADA")
    logger.info("="*60)

if __name__ == "__main__":
    main()
