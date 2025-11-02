#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper Simulado para GeneraWeb Duda - DOMINIOS
Este scrapper simula la extracción de dominios para demostrar la funcionalidad
"""

import csv
import time
import logging
import os
import random
from datetime import datetime

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneraWebDudaScraperDominiosSimulado:
    def __init__(self):
        self.csv_filename = 'generaweb_duda_dominios.csv'
        
    def save_dominio_incremental(self, dominio):
        """Guarda un dominio inmediatamente al CSV"""
        try:
            file_exists = os.path.exists(self.csv_filename)
            
            with open(self.csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'entrada', 'empresa', 'dominio', 'estado',
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
                
                writer.writerow(dominio)
                logger.info(f"✓ Dominio guardado: {dominio.get('dominio', 'Sin dominio')} (ID: {dominio.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando dominio: {e}")
    
    def generar_dominio_simulado(self, id_dominio):
        """Genera datos simulados de un dominio"""
        dominios = [
            'empresa1.com', 'negocio2.es', 'servicios3.org', 'consultoria4.net',
            'tecnologia5.com', 'marketing6.es', 'diseno7.org', 'construccion8.net',
            'inmobiliaria9.com', 'restaurante10.es', 'hotel11.org', 'tienda12.net',
            'clinica13.com', 'abogados14.es', 'contadores15.org', 'ingenieros16.net',
            'arquitectos17.com', 'medicos18.es', 'dentistas19.org', 'veterinarios20.net'
        ]
        
        empresas = [
            'Empresa Tecnológica SL', 'Negocio Digital S.A.', 'Servicios Profesionales SL',
            'Consultoría Empresarial S.L.', 'Tecnología Avanzada S.A.', 'Marketing Online SL',
            'Diseño Creativo S.L.', 'Construcciones Modernas S.A.', 'Inmobiliaria Premium SL',
            'Restaurante Gourmet S.L.', 'Hotel Boutique S.A.', 'Tienda Online SL',
            'Clínica Especializada S.L.', 'Bufete de Abogados S.A.', 'Contadores Asociados SL',
            'Ingenieros Consultores S.L.', 'Arquitectos Unidos S.A.', 'Centro Médico SL',
            'Clínica Dental S.L.', 'Veterinaria Animal Care S.A.'
        ]
        
        nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Carmen', 'Pedro', 'Laura', 'Miguel', 'Isabel']
        apellidos = ['García', 'Rodríguez', 'Martín', 'López', 'González', 'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores']
        
        provincias = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao']
        ciudades = ['Madrid', 'Barcelona', 'Valencia', 'Sevilla', 'Zaragoza', 'Málaga', 'Murcia', 'Palma', 'Las Palmas', 'Bilbao']
        
        estados = ['Activo', 'Pendiente', 'En proceso', 'Completado', 'Cancelado']
        
        # Generar datos básicos
        dominio = {
            'id': str(id_dominio),
            'entrada': datetime.now().strftime('%d/%m/%Y'),
            'empresa': random.choice(empresas),
            'dominio': random.choice(dominios),
            'estado': random.choice(estados),
            'nombre': random.choice(nombres),
            'apellidos': f"{random.choice(apellidos)} {random.choice(apellidos)}",
            'razon_social': f"{random.choice(empresas)}",
            'login': f"user{id_dominio}",
            'password': f"pass{id_dominio}",
            'cif_nif': f"{random.randint(10000000, 99999999)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])}",
            'direccion': f"Calle {random.choice(['Mayor', 'Real', 'Nueva', 'Vieja', 'Principal'])} {random.randint(1, 100)}",
            'provincia': random.choice(provincias),
            'ciudad': random.choice(ciudades),
            'codigo_postal': f"{random.randint(10000, 99999)}",
            'pais': 'España',
            'telefono': f"9{random.randint(10000000, 99999999)}",
            'fax': f"9{random.randint(10000000, 99999999)}",
            'telefono_movil': f"6{random.randint(10000000, 99999999)}",
            'url': f"https://www.{random.choice(dominios)}",
            'email': f"info{id_dominio}@{random.choice(dominios)}",
            'num_dominios': str(random.randint(1, 5)),
            'wordpress_url': f"https://{random.choice(dominios)}/wp-admin",
            'gestor_proyecto': f"Gestor {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            'url_perfil': f"http://generawebduda.nlocal.com/index.php?s=user_profile&id={id_dominio}",
            'url_web': f"https://www.{random.choice(dominios)}",
            'url_panel': f"http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id={id_dominio}"
        }
        
        return dominio
    
    def scrape_dominios_simulado(self, total_dominios=100):
        """Simula el scraping de dominios"""
        logger.info(f"🚀 Iniciando scraping simulado de {total_dominios} dominios")
        
        dominios_procesados = 0
        
        for i in range(1, total_dominios + 1):
            # Generar datos del dominio
            dominio_data = self.generar_dominio_simulado(i)
            
            # Guardar inmediatamente
            self.save_dominio_incremental(dominio_data)
            dominios_procesados += 1
            
            # Simular tiempo de procesamiento
            time.sleep(0.1)
            
            if i % 10 == 0:
                logger.info(f"📊 Progreso: {i}/{total_dominios} dominios procesados")
        
        logger.info(f"✅ Scraping simulado completado: {dominios_procesados} dominios procesados")
        return dominios_procesados

def main():
    """Función principal"""
    logger.info("=" * 60)
    logger.info("Scraper Simulado de GeneraWeb Duda - DOMINIOS")
    logger.info("=" * 60)
    
    scraper = GeneraWebDudaScraperDominiosSimulado()
    
    # Simular scraping de 100 dominios
    total_dominios = scraper.scrape_dominios_simulado(total_dominios=100)
    
    if total_dominios > 0:
        logger.info("")
        logger.info(f"✓ Total de dominios simulados: {total_dominios}")
        logger.info("✓ Todos los dominios se guardaron incrementalmente en el CSV")
        logger.info("✓ Archivo CSV: generaweb_duda_dominios.csv")
    else:
        logger.info("")
        logger.info("No se generaron dominios simulados")

if __name__ == "__main__":
    main()
