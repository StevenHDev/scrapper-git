#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para scraper de einforma.com
Permite buscar información de empresas por NIF
"""

import csv
import time
import json
import re
import os
from bs4 import BeautifulSoup
import requests

class EinformaScraper:
    def __init__(self):
        """Inicializa el scraper de Einforma"""
        self.base_url = "https://www.einforma.com"
        self.search_url_template = f"{self.base_url}/servlet/app/prod/ETIQUETA_EMPRESA/nif/{{nif}}"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.campos_csv = [
            'nif', 'denominacion', 'duns_number', 'domicilio_social', 'localidad', 
            'telefono', 'fax', 'fecha_ultimo_dato', 'accionistas', 'forma_juridica',
            'actividad_informa', 'cnae_2009', 'cnae_2025', 'objeto_social',
            'ultimo_balance', 'balances_disponibles', 'deposito_mercantil',
            'deposito_einforma', 'popularidad', 'ventas_2022', 'ventas_2023', 'ventas_2024'
        ]
        self.dnis_procesados = set()
        
    def obtener_dnis_procesados(self, archivo_csv='resultados_einforma.csv'):
        """
        Lee el archivo CSV de salida y obtiene los DNIs ya procesados
        
        Args:
            archivo_csv: Nombre del archivo CSV de salida
            
        Returns:
            set: Conjunto de DNIs ya procesados
        """
        dnis_procesados = set()
        
        if os.path.exists(archivo_csv):
            try:
                with open(archivo_csv, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f, delimiter=';')
                    for fila in reader:
                        if fila.get('nif'):
                            dnis_procesados.add(fila['nif'])
            except Exception as e:
                print(f"⚠️ Error al leer NIFs procesados: {str(e)}")
        
        return dnis_procesados
    
    def inicializar_csv_salida(self, archivo_csv='resultados_einforma.csv', reiniciar=False):
        """
        Inicializa el archivo CSV de salida con el encabezado
        
        Args:
            archivo_csv: Nombre del archivo CSV de salida
            reiniciar: Si True, borra el archivo existente. Si False, mantiene los datos existentes
        """
        try:
            self.archivo_csv = archivo_csv
            
            # Si el archivo existe y queremos reiniciar, lo eliminamos
            if reiniciar and os.path.exists(archivo_csv):
                os.remove(archivo_csv)
                print(f"📝 Inicializando CSV (reiniciando): {archivo_csv}")
                with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
                    escritor = csv.DictWriter(f, fieldnames=self.campos_csv, delimiter=';')
                    escritor.writeheader()
                print(f"✅ CSV inicializado correctamente")
                self.dnis_procesados = set()
            elif not os.path.exists(archivo_csv):
                # Si no existe el archivo, lo creamos
                print(f"📝 Creando CSV: {archivo_csv}")
                with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
                    escritor = csv.DictWriter(f, fieldnames=self.campos_csv, delimiter=';')
                    escritor.writeheader()
                print(f"✅ CSV creado correctamente")
                self.dnis_procesados = set()
            else:
                # El archivo ya existe y queremos continuar
                print(f"📝 Continuando con CSV existente: {archivo_csv}")
                self.dnis_procesados = self.obtener_dnis_procesados(archivo_csv)
                print(f"✅ CSV encontrado con {len(self.dnis_procesados)} registros anteriores")
            
        except Exception as e:
            print(f"❌ Error al inicializar CSV: {str(e)}")
    
    def parsear_informacion_empresa(self, html_content, nif):
        """
        Parsea la información de la empresa desde el HTML
        
        Args:
            html_content: Contenido HTML de la página
            nif: NIF de la empresa
            
        Returns:
            dict: Información extraída
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            datos = {campo: '' for campo in self.campos_csv}
            datos['nif'] = nif
            
            # Buscar la tabla con id="datos"
            tabla = soup.find('table', id='datos')
            if not tabla:
                print("   ⚠️ No se encontró la tabla de datos")
                return datos
            
            # Extraer filas de la tabla
            filas = tabla.find_all('tr')
            
            for fila in filas:
                td_left = fila.find('td', align='right')
                td_right = fila.find('td', align='left')
                
                if td_left and td_right:
                    etiqueta = td_left.get_text(strip=True)
                    valor = td_right.get_text(strip=True)
                    
                    # Limpiar el valor (quitar saltos de línea y espacios extra)
                    valor = ' '.join(valor.split())
                    
                    # Mapear campos según la etiqueta
                    if 'Denominación:' in etiqueta:
                        datos['denominacion'] = valor
                        print(f"   🏢 Denominación: {valor}")
                    elif 'Duns Number:' in etiqueta:
                        datos['duns_number'] = valor
                    elif 'Domicilio social' in etiqueta:
                        # Quitar el texto "Ver Mapa" si existe
                        valor = re.sub(r'\s*Ver Mapa.*', '', valor)
                        datos['domicilio_social'] = valor
                    elif 'Localidad:' in etiqueta:
                        datos['localidad'] = valor
                    elif 'Teléfono:' in etiqueta:
                        datos['telefono'] = valor.replace('\n', ' | ')
                    elif 'Fax:' in etiqueta:
                        datos['fax'] = valor
                    elif 'Fecha último dato:' in etiqueta:
                        datos['fecha_ultimo_dato'] = valor
                    elif 'Accionistas:' in etiqueta:
                        # Extraer número de accionistas
                        match = re.search(r'(\d+)', valor)
                        if match:
                            datos['accionistas'] = match.group(1)
                        else:
                            datos['accionistas'] = valor
                    elif 'Forma Jurídica:' in etiqueta:
                        datos['forma_juridica'] = valor
                    elif 'Actividad Informa:' in etiqueta:
                        datos['actividad_informa'] = valor
                    elif 'CNAE 2009:' in etiqueta:
                        datos['cnae_2009'] = valor
                    elif 'CNAE 2025:' in etiqueta:
                        datos['cnae_2025'] = valor
                    elif 'Objeto Social:' in etiqueta:
                        datos['objeto_social'] = valor
                    elif 'Último Balance' in etiqueta and 'cargado' in etiqueta:
                        # Extraer año y fecha
                        match = re.search(r'(\d{4})\s*\(Fecha Cierre\s+(\d{2}/\d{2}/\d{4})\)', valor)
                        if match:
                            datos['ultimo_balance'] = f"{match.group(1)} ({match.group(2)})"
                        else:
                            datos['ultimo_balance'] = valor
                    elif 'Balances disponibles:' in etiqueta:
                        # Extraer número de balances
                        match = re.search(r'(\d+)', valor)
                        if match:
                            datos['balances_disponibles'] = match.group(1)
                        else:
                            datos['balances_disponibles'] = valor
                    elif 'Depósito en R. Mercantil:' in etiqueta:
                        datos['deposito_mercantil'] = valor
                    elif 'Depósito en eInforma:' in etiqueta:
                        datos['deposito_einforma'] = valor
                    elif 'Popularidad:' in etiqueta:
                        # Extraer información de popularidad
                        match = re.search(r'última vez el (.+?) y (\d+) veces', valor)
                        if match:
                            datos['popularidad'] = f"{match.group(1)} - {match.group(2)} veces"
                        else:
                            datos['popularidad'] = valor
            
            # Extraer datos de ventas desde el script JavaScript
            script_grafico = tabla.find('script', type='text/javascript')
            if script_grafico:
                texto_script = script_grafico.text
                # Buscar data_y: [..., ..., ...]
                match_ventas = re.search(r'data_y:\s*\[(.*?)\]', texto_script)
                if match_ventas:
                    ventas = [v.strip() for v in match_ventas.group(1).split(',')]
                    if len(ventas) >= 3:
                        datos['ventas_2022'] = ventas[0]
                        datos['ventas_2023'] = ventas[1]
                        datos['ventas_2024'] = ventas[2]
                    elif len(ventas) == 2:
                        datos['ventas_2023'] = ventas[0]
                        datos['ventas_2024'] = ventas[1]
                    elif len(ventas) == 1:
                        datos['ventas_2024'] = ventas[0]
            
            return datos
            
        except Exception as e:
            print(f"❌ Error al parsear información: {str(e)}")
            return {campo: '' for campo in self.campos_csv}
    
    def buscar_por_nif(self, nif):
        """
        Busca información de una empresa por su NIF
        
        Args:
            nif: NIF de la empresa
            
        Returns:
            dict: Resultado de la búsqueda
        """
        try:
            print(f"\n🔍 Buscando NIF: {nif}")
            
            # Construir URL de búsqueda
            url = self.search_url_template.format(nif=nif)
            print(f"🌐 Accediendo a: {url}")
            
            # Realizar petición
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # Verificar si se encontraron resultados
            if 'No se encontraron resultados' in response.text or 'empresa no encontrada' in response.text.lower():
                print(f"⚠️ No se encontraron resultados para NIF: {nif}")
                return {
                    'nif': nif,
                    'resultado_encontrado': False,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Parsear información
            datos = self.parsear_informacion_empresa(response.text, nif)
            
            # Verificar si se extrajo información válida
            tiene_datos = any([
                datos.get('denominacion'),
                datos.get('domicilio_social'),
                datos.get('telefono'),
                datos.get('localidad')
            ])
            
            if tiene_datos:
                datos['resultado_encontrado'] = True
                datos['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"✅ Resultados encontrados para NIF: {nif}")
                if datos.get('telefono'):
                    print(f"   📞 Teléfono: {datos['telefono']}")
                if datos.get('domicilio_social'):
                    print(f"   📍 Dirección: {datos['domicilio_social']}")
                return datos
            else:
                print(f"⚠️ Se encontró entrada pero sin datos válidos para NIF: {nif}")
                return {
                    'nif': nif,
                    'resultado_encontrado': False,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout al buscar NIF {nif}")
            return {
                'nif': nif,
                'error': 'Timeout',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión al buscar NIF {nif}: {str(e)}")
            return {
                'nif': nif,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"❌ Error al buscar NIF {nif}: {str(e)}")
            return {
                'nif': nif,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def append_resultado_csv(self, resultado):
        """
        Añade un resultado al archivo CSV de salida
        
        Args:
            resultado: Diccionario con el resultado a añadir
        """
        try:
            # Solo añadir si el resultado tiene información válida
            if resultado.get('resultado_encontrado', False):
                with open(self.archivo_csv, 'a', newline='', encoding='utf-8') as f:
                    escritor = csv.DictWriter(f, fieldnames=self.campos_csv, delimiter=';')
                    fila = {}
                    for campo in self.campos_csv:
                        fila[campo] = resultado.get(campo, '')
                    escritor.writerow(fila)
                
                print(f"   ✅ Resultado guardado en CSV")
        except Exception as e:
            print(f"❌ Error al añadir resultado al CSV: {str(e)}")
    
    def procesar_csv(self, archivo_csv, delimitador=None):
        """
        Procesa un archivo CSV con NIFs
        
        Args:
            archivo_csv: Ruta al archivo CSV con los NIFs
            delimitador: Delimitador del CSV (por defecto detecta automáticamente)
            
        Returns:
            list: Lista con los resultados de las búsquedas
        """
        resultados = []
        
        try:
            print(f"\n📂 Leyendo archivo CSV: {archivo_csv}")
            
            # Detectar delimitador si no se especifica
            if delimitador is None:
                with open(archivo_csv, 'r', encoding='utf-8') as f:
                    primera_linea = f.readline()
                    if ';' in primera_linea:
                        delimitador = ';'
                        print("✅ Delimitador detectado: punto y coma (;)")
                    else:
                        delimitador = ','
                        print("✅ Delimitador detectado: coma (,)")
            
            with open(archivo_csv, 'r', encoding='utf-8') as f:
                lector = csv.reader(f, delimiter=delimitador)
                nifs = []
                
                for fila in lector:
                    if fila and fila[0].strip():
                        nif = fila[0].strip()
                        nifs.append(nif)
                
                print(f"📊 Total de NIFs encontrados: {len(nifs)}")
                
                # Filtrar NIFs ya procesados si existen
                if self.dnis_procesados:
                    nifs_originales = len(nifs)
                    nifs = [nif for nif in nifs if nif not in self.dnis_procesados]
                    nifs_omitidos = nifs_originales - len(nifs)
                    if nifs_omitidos > 0:
                        print(f"⏭️ Omitiendo {nifs_omitidos} NIFs ya procesados")
                        print(f"📊 NIFs pendientes: {len(nifs)}")
                
                # Procesar cada NIF
                for i, nif in enumerate(nifs, 1):
                    print(f"\n{'='*60}")
                    print(f"Procesando {i}/{len(nifs)}: {nif}")
                    print(f"{'='*60}")
                    
                    resultado = self.buscar_por_nif(nif)
                    resultados.append(resultado)
                    
                    # Añadir resultado al CSV inmediatamente si tiene información
                    self.append_resultado_csv(resultado)
                    
                    # Pausa entre búsquedas para no sobrecargar el servidor
                    if i < len(nifs):
                        time.sleep(3)  # Pausa de 3 segundos
                
                print(f"\n✅ Procesamiento completado: {len(resultados)} resultados nuevos")
                return resultados
                
        except FileNotFoundError:
            print(f"❌ Archivo CSV no encontrado: {archivo_csv}")
            return []
        except Exception as e:
            print(f"❌ Error al procesar el archivo CSV: {str(e)}")
            return []
    
    def guardar_resultados_json(self, resultados, archivo_salida='resultados_einforma.json'):
        """
        Guarda los resultados en un archivo JSON
        
        Args:
            resultados: Lista con los resultados
            archivo_salida: Nombre del archivo de salida
        """
        try:
            print(f"\n💾 Guardando resultados en JSON: {archivo_salida}")
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            print(f"✅ Resultados JSON guardados correctamente")
        except Exception as e:
            print(f"❌ Error al guardar resultados JSON: {str(e)}")


def main():
    """Función principal"""
    print("="*60)
    print("🚀 SCRAPER EINFORMA.COM")
    print("="*60)
    
    # Inicializar scraper
    scraper = EinformaScraper()
    
    try:
        # Inicializar CSV de salida (por defecto continúa desde donde quedó)
        scraper.inicializar_csv_salida(reiniciar=False)
        
        # Procesar archivo CSV
        archivo_csv = 'codigos_prueba.csv'  # Cambiar a 'codigos.csv' para procesamiento completo
        resultados = scraper.procesar_csv(archivo_csv)
        
        # Guardar resultados adicionales (JSON)
        if resultados:
            scraper.guardar_resultados_json(resultados)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ Proceso finalizado")
    print("="*60)


if __name__ == "__main__":
    main()

