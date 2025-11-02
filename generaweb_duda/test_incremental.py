#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Scraper Incremental - Simulación sin login
"""

import csv
import time
import logging
import os

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestScraperIncremental:
    def __init__(self):
        self.csv_filename = 'generaweb_duda_empresas.csv'
        self.file_exists = os.path.exists(self.csv_filename)
        
    def save_empresa_incremental(self, empresa):
        """Guarda una empresa inmediatamente al CSV"""
        try:
            with open(self.csv_filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = [
                    'id', 'empresa', 'entrada', 'estado',
                    'nombre', 'apellidos', 'razon_social', 'login', 'password', 'cif_nif',
                    'direccion', 'provincia', 'ciudad', 'codigo_postal', 'pais',
                    'telefono', 'fax', 'telefono_movil', 'url', 'email',
                    'num_dominios', 'wordpress_url', 'gestor_proyecto',
                    'url_perfil', 'url_web', 'url_panel'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
                
                # Solo escribir header si el archivo no existe
                if not self.file_exists:
                    writer.writeheader()
                    self.file_exists = True
                    logger.info("✓ Header escrito en nuevo archivo CSV")
                
                writer.writerow(empresa)
                logger.info(f"✓ Empresa guardada: {empresa.get('empresa', 'Sin nombre')} (ID: {empresa.get('id', 'N/A')})")
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")
    
    def simulate_scraping(self):
        """Simula el proceso de scraping con datos de prueba"""
        
        # Datos de prueba para simular empresas
        empresas_prueba = [
            {
                'id': '10001',
                'empresa': 'EMPRESA INCREMENTAL 1',
                'entrada': '22/10/2025',
                'estado': 'Activo',
                'nombre': 'Ana',
                'apellidos': 'García López',
                'razon_social': 'EMPRESA INCREMENTAL 1 SL',
                'login': 'agarcia',
                'password': 'pass123',
                'cif_nif': '11111111A',
                'direccion': 'Calle Incremental 1',
                'provincia': 'Madrid',
                'ciudad': 'Madrid',
                'codigo_postal': '28001',
                'pais': 'Spain',
                'telefono': '911111111',
                'fax': '',
                'telefono_movil': '611111111',
                'url': 'https://www.incremental1.com',
                'email': 'info@incremental1.com',
                'num_dominios': '1',
                'wordpress_url': '',
                'gestor_proyecto': 'Gestor A',
                'url_perfil': 'http://generawebduda.nlocal.com/index.php?s=user_profile&id=10001',
                'url_web': 'https://www.incremental1.com',
                'url_panel': 'http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id=10001'
            },
            {
                'id': '10002',
                'empresa': 'EMPRESA INCREMENTAL 2',
                'entrada': '22/10/2025',
                'estado': 'Diseño',
                'nombre': 'Carlos',
                'apellidos': 'Martín Ruiz',
                'razon_social': 'EMPRESA INCREMENTAL 2 SL',
                'login': 'cmartin',
                'password': 'pass456',
                'cif_nif': '22222222B',
                'direccion': 'Avenida Incremental 2',
                'provincia': 'Barcelona',
                'ciudad': 'Barcelona',
                'codigo_postal': '08001',
                'pais': 'Spain',
                'telefono': '922222222',
                'fax': '',
                'telefono_movil': '622222222',
                'url': 'https://www.incremental2.com',
                'email': 'info@incremental2.com',
                'num_dominios': '2',
                'wordpress_url': '',
                'gestor_proyecto': 'Gestor B',
                'url_perfil': 'http://generawebduda.nlocal.com/index.php?s=user_profile&id=10002',
                'url_web': 'https://www.incremental2.com',
                'url_panel': 'http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id=10002'
            },
            {
                'id': '10003',
                'empresa': 'EMPRESA INCREMENTAL 3',
                'entrada': '22/10/2025',
                'estado': 'Publicación',
                'nombre': 'Laura',
                'apellidos': 'Fernández Sánchez',
                'razon_social': 'EMPRESA INCREMENTAL 3 SL',
                'login': 'lfernandez',
                'password': 'pass789',
                'cif_nif': '33333333C',
                'direccion': 'Plaza Incremental 3',
                'provincia': 'Valencia',
                'ciudad': 'Valencia',
                'codigo_postal': '46001',
                'pais': 'Spain',
                'telefono': '933333333',
                'fax': '',
                'telefono_movil': '633333333',
                'url': 'https://www.incremental3.com',
                'email': 'info@incremental3.com',
                'num_dominios': '3',
                'wordpress_url': '',
                'gestor_proyecto': 'Gestor C',
                'url_perfil': 'http://generawebduda.nlocal.com/index.php?s=user_profile&id=10003',
                'url_web': 'https://www.incremental3.com',
                'url_panel': 'http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id=10003'
            }
        ]
        
        logger.info("=" * 60)
        logger.info("SIMULACIÓN DE SCRAPING INCREMENTAL")
        logger.info("=" * 60)
        
        total_empresas = 0
        
        for i, empresa in enumerate(empresas_prueba, 1):
            logger.info(f"\nProcesando empresa {i}/{len(empresas_prueba)}")
            logger.info(f"Empresa: {empresa['empresa']}")
            logger.info(f"ID: {empresa['id']}")
            logger.info(f"Estado: {empresa['estado']}")
            
            # Simular tiempo de procesamiento
            time.sleep(2)
            
            # Guardar inmediatamente
            self.save_empresa_incremental(empresa)
            total_empresas += 1
            
            logger.info(f"✓ Empresa {i} guardada exitosamente")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SIMULACIÓN COMPLETADA")
        logger.info(f"{'='*60}")
        logger.info(f"Total de empresas procesadas: {total_empresas}")
        logger.info(f"Archivo CSV: {self.csv_filename}")

def main():
    """Función principal"""
    scraper = TestScraperIncremental()
    scraper.simulate_scraping()

if __name__ == "__main__":
    main()
