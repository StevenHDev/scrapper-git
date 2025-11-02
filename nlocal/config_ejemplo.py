#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo de configuración de EJEMPLO para el scraper de nlocal
COPIA este archivo a config.py y edita con tus credenciales reales

IMPORTANTE: 
- config.py está en .gitignore para proteger tus credenciales
- NO subas config.py a repositorios públicos
"""

# Credenciales de acceso a nlocal.com
NLOCAL_USUARIO = "tu_usuario@ejemplo.com"
NLOCAL_PASSWORD = "tu_contraseña"

# Configuración del scraper
SCRAPER_CONFIG = {
    'headless': False,  # Si True, el navegador se ejecuta en modo headless
    'timeout': 20,  # Tiempo de espera máximo en segundos
    'delay_busquedas': 2,  # Pausa entre búsquedas en segundos
    'implicit_wait': 10  # Tiempo de espera implícito para elementos
}

# Rutas de archivos
ARCHIVO_ENTRADA = "codigos.csv"
ARCHIVO_SALIDA = "resultados_nlocal.json"

# Configuración de la búsqueda
SEARCH_CONFIG = {
    'url_base': "https://admin.nlocal.com",
    'tipo_busqueda': 'cif'  # Tipo de búsqueda: cif, nombre, etc.
}
