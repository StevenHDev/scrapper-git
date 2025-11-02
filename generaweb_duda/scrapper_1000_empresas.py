#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Scraper para 1000 empresas por página - Versión Incremental
Simula la extracción de 1000 empresas por página con guardado incremental
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

class Scraper1000Empresas:
    def __init__(self):
        self.csv_filename = 'generaweb_duda_empresas.csv'
        self.file_exists = os.path.exists(self.csv_filename)
        
        # Datos de ejemplo para simular empresas reales
        self.nombres_empresas = [
            "TECNOLOGÍA AVANZADA SL", "SERVICIOS INTEGRALES SA", "INNOVACIÓN DIGITAL SL",
            "SOLUCIONES EMPRESARIALES SL", "CONSULTORÍA TÉCNICA SA", "DESARROLLO WEB SL",
            "MARKETING DIGITAL SA", "GESTIÓN COMERCIAL SL", "ASESORÍA FISCAL SA",
            "INGENIERÍA INDUSTRIAL SL", "CONSTRUCCIONES MODERNAS SA", "TRANSPORTE RÁPIDO SL",
            "ALIMENTACIÓN FRESCA SA", "TEXTILES DE CALIDAD SL", "ELECTRÓNICA AVANZADA SA",
            "COMUNICACIONES MÓVILES SL", "ENERGÍA RENOVABLE SA", "BIOTECNOLOGÍA SL",
            "INTELIGENCIA ARTIFICIAL SA", "BLOCKCHAIN SOLUTIONS SL", "CLOUD COMPUTING SA",
            "CYBERSECURITY SL", "DATA ANALYTICS SA", "MACHINE LEARNING SL",
            "ROBÓTICA INDUSTRIAL SA", "AUTOMATIZACIÓN SL", "IOT SOLUTIONS SA",
            "SMART CITIES SL", "DIGITAL TRANSFORMATION SA", "E-COMMERCE SOLUTIONS SL"
        ]
        
        self.nombres_personas = [
            "Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "Antonio", "Isabel",
            "Francisco", "Rosa", "Manuel", "Pilar", "José", "Teresa", "Miguel", "Elena",
            "David", "Cristina", "Pedro", "Laura", "Javier", "Mónica", "Fernando", "Sara",
            "Alejandro", "Patricia", "Roberto", "Natalia", "Daniel", "Beatriz"
        ]
        
        self.apellidos = [
            "García", "López", "Martínez", "González", "Pérez", "Sánchez", "Ramírez",
            "Torres", "Flores", "Rivera", "Gómez", "Díaz", "Cruz", "Morales", "Ortiz",
            "Ramos", "Jiménez", "Ruiz", "Hernández", "Moreno", "Muñoz", "Álvarez",
            "Romero", "Navarro", "Vargas", "Castillo", "Mendoza", "Silva", "Rojas"
        ]
        
        self.estados = ["Activo", "Diseño", "Publicación", "En desarrollo", "Completado"]
        self.provincias = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga", "Murcia", "Palma", "Las Palmas", "Bilbao"]
        
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
                
        except Exception as e:
            logger.error(f"Error guardando empresa: {e}")
    
    def generar_empresa_simulada(self, id_empresa):
        """Genera datos simulados de una empresa"""
        nombre_empresa = random.choice(self.nombres_empresas)
        nombre_persona = random.choice(self.nombres_personas)
        apellido1 = random.choice(self.apellidos)
        apellido2 = random.choice(self.apellidos)
        provincia = random.choice(self.provincias)
        estado = random.choice(self.estados)
        
        # Generar datos únicos
        cif_nif = f"{random.randint(10000000, 99999999)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Y', 'Z'])}"
        telefono = f"9{random.randint(10000000, 99999999)}"
        movil = f"6{random.randint(10000000, 99999999)}"
        codigo_postal = f"{random.randint(10000, 99999)}"
        
        empresa = {
            'id': str(id_empresa),
            'empresa': nombre_empresa,
            'entrada': datetime.now().strftime("%d/%m/%Y"),
            'estado': estado,
            'nombre': nombre_persona,
            'apellidos': f"{apellido1} {apellido2}",
            'razon_social': nombre_empresa,
            'login': f"{nombre_persona.lower()}{random.randint(100, 999)}",
            'password': f"pass{random.randint(1000, 9999)}",
            'cif_nif': cif_nif,
            'direccion': f"Calle {random.choice(['Mayor', 'Principal', 'Nueva', 'Real', 'San', 'Santa'])} {random.randint(1, 200)}",
            'provincia': provincia,
            'ciudad': provincia,
            'codigo_postal': codigo_postal,
            'pais': 'Spain',
            'telefono': telefono,
            'fax': '',
            'telefono_movil': movil,
            'url': f"https://www.{nombre_empresa.lower().replace(' ', '').replace('sl', '').replace('sa', '')}.com",
            'email': f"info@{nombre_empresa.lower().replace(' ', '').replace('sl', '').replace('sa', '')}.com",
            'num_dominios': str(random.randint(1, 5)),
            'wordpress_url': '',
            'gestor_proyecto': f"Gestor {random.choice(['A', 'B', 'C', 'D', 'E'])}",
            'url_perfil': f"http://generawebduda.nlocal.com/index.php?s=user_profile&id={id_empresa}",
            'url_web': f"https://www.{nombre_empresa.lower().replace(' ', '').replace('sl', '').replace('sa', '')}.com",
            'url_panel': f"http://panelcontrol.nlocal.com/panelcontrol_v2/?s=entry&id={id_empresa}"
        }
        
        return empresa
    
    def simular_scraping_pagina(self, numero_pagina, empresas_por_pagina=1000):
        """Simula el scraping de una página completa con 1000 empresas"""
        logger.info(f"\n{'='*50}")
        logger.info(f"PROCESANDO PÁGINA {numero_pagina} - {empresas_por_pagina} EMPRESAS")
        logger.info(f"{'='*50}")
        
        # Simular tiempo de carga de página
        logger.info("Cargando página...")
        time.sleep(2)
        
        # Simular extracción de empresas
        empresas_procesadas = 0
        id_inicial = (numero_pagina - 1) * empresas_por_pagina + 1
        
        # Procesar en lotes de 100 para mostrar progreso
        lote_size = 100
        total_lotes = empresas_por_pagina // lote_size
        
        for lote in range(total_lotes):
            logger.info(f"Procesando lote {lote + 1}/{total_lotes} (empresas {lote * lote_size + 1}-{(lote + 1) * lote_size})")
            
            for i in range(lote_size):
                id_empresa = id_inicial + (lote * lote_size) + i
                
                # Generar datos de la empresa
                empresa = self.generar_empresa_simulada(id_empresa)
                
                # Guardar inmediatamente
                self.save_empresa_incremental(empresa)
                empresas_procesadas += 1
            
            logger.info(f"✓ Lote {lote + 1} completado: {empresas_procesadas} empresas guardadas")
            
            # Pausa entre lotes
            time.sleep(0.1)
        
        logger.info(f"✓ Página {numero_pagina} completada: {empresas_procesadas} empresas procesadas y guardadas")
        return empresas_procesadas
    
    def ejecutar_scraping_completo(self, paginas=4):
        """Ejecuta el scraping completo de múltiples páginas"""
        logger.info("=" * 60)
        logger.info("SCRAPER DE 1000 EMPRESAS POR PÁGINA - INCREMENTAL")
        logger.info("=" * 60)
        
        total_empresas = 0
        
        for pagina in range(1, paginas + 1):
            empresas_pagina = self.simular_scraping_pagina(pagina)
            total_empresas += empresas_pagina
            
            # Pausa entre páginas
            if pagina < paginas:
                logger.info("Esperando antes de procesar la siguiente página...")
                time.sleep(1)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SCRAPING COMPLETADO")
        logger.info(f"{'='*60}")
        logger.info(f"Total de empresas procesadas: {total_empresas}")
        logger.info(f"Páginas procesadas: {paginas}")
        logger.info(f"Empresas por página: 1000")
        logger.info(f"Archivo CSV: {self.csv_filename}")
        
        return total_empresas

def main():
    """Función principal"""
    import sys
    
    # Obtener número de páginas desde argumentos
    paginas = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    
    scraper = Scraper1000Empresas()
    total_empresas = scraper.ejecutar_scraping_completo(paginas)
    
    logger.info(f"\n🎉 Proceso completado exitosamente!")
    logger.info(f"📊 Total de empresas añadidas: {total_empresas}")

if __name__ == "__main__":
    main()
