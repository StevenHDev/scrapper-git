#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para scraper de nlocal.com
Permite autenticarse y buscar organizaciones por DNI
"""

import csv
import time
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

class NlocalScraper:
    def __init__(self, usuario, password, headless=False):
        """
        Inicializa el scraper de nlocal
        
        Args:
            usuario: Usuario para el login
            password: Contraseña para el login
            headless: Si True, ejecuta el navegador en modo headless
        """
        self.usuario = usuario
        self.password = password
        self.headless = headless
        self.driver = None
        self.base_url = "https://admin.nlocal.com"
        self.login_url = f"{self.base_url}/"
        self.search_url_template = "{self.base_url}/orgs/search?utf8=%E2%9C%93&search%5Bvalue%5D={dni}&search%5Boption%5D=cif&commit=Buscar"
        self.campos_csv = [
            'dni', 'org_id', 'nombre_organizacion', 'estado_org', 'cif', 'telefono', 'movil', 
            'web', 'direccion', 'nombre_contacto', 'email', 'estado_usuario', 
            'completada', 'ultima_modificacion', 'ultimo_login', 'total_logins'
        ]
        self.csv_escritor = None
        self.archivo_csv = 'resultados_nlocal.csv'
        self.dnis_procesados = set()  # Conjunto de DNIs ya procesados
        
    def obtener_dnis_procesados(self, archivo_csv='resultados_nlocal.csv'):
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
                        if fila.get('dni'):
                            dnis_procesados.add(fila['dni'])
            except Exception as e:
                print(f"⚠️ Error al leer DNIs procesados: {str(e)}")
        
        return dnis_procesados
    
    def iniciar_navegador(self):
        """Inicia el navegador Chrome con las opciones configuradas"""
        print("🔧 Configurando navegador Chrome...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
        
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✅ Navegador iniciado correctamente")
            return True
        except Exception as e:
            print(f"❌ Error al iniciar el navegador: {str(e)}")
            return False
    
    def login(self):
        """
        Realiza el login en nlocal
        
        Returns:
            bool: True si el login fue exitoso, False en caso contrario
        """
        try:
            print(f"🔐 Intentando login en {self.login_url}")
            self.driver.get(self.login_url)
            
            # Esperar un momento para que cargue la página
            time.sleep(3)
            
            # Buscar campos de login con múltiples estrategias
            username_field = None
            password_field = None
            
            # Estrategia 1: Buscar por name (email, usuario, username, etc.)
            print("🔍 Buscando campos de login...")
            name_attributes = ['admin_user[email]', 'email', 'usuario', 'username', 'user', 'admin_email']
            
            for name_attr in name_attributes:
                try:
                    username_field = self.driver.find_element(By.NAME, name_attr)
                    password_field = self.driver.find_element(By.NAME, "admin_user[password]")
                    print(f"✅ Campos encontrados por name='{name_attr}'")
                    break
                except NoSuchElementException:
                    try:
                        # Intentar solo con password si admin_user[email] no funciona
                        if name_attr != 'admin_user[email]':
                            password_field = self.driver.find_element(By.NAME, "password")
                            username_field = self.driver.find_element(By.NAME, name_attr)
                            print(f"✅ Campos encontrados por name='{name_attr}'")
                            break
                    except NoSuchElementException:
                        continue
            
            # Estrategia 2: Si no se encontraron por name, buscar por tipo
            if not username_field or not password_field:
                print("⚠️ No encontrados por name, buscando por tipo...")
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                for input_elem in inputs:
                    input_type = input_elem.get_attribute("type")
                    input_id = input_elem.get_attribute("id")
                    if input_type == "text" or input_type == "email":
                        if input_id and ("user" in input_id.lower() or "email" in input_id.lower()):
                            username_field = input_elem
                            print(f"✅ Campo usuario encontrado por tipo: {input_id}")
                    elif input_type == "password":
                        password_field = input_elem
                        print("✅ Campo password encontrado")
            
            # Si aún no se encontraron, usar el primer input de tipo text y password
            if not username_field or not password_field:
                inputs = self.driver.find_elements(By.TAG_NAME, "input")
                text_inputs = [inp for inp in inputs if inp.get_attribute("type") in ["text", "email"]]
                password_inputs = [inp for inp in inputs if inp.get_attribute("type") == "password"]
                
                if text_inputs:
                    username_field = text_inputs[0]
                    print("✅ Usando primer input de texto encontrado")
                if password_inputs:
                    password_field = password_inputs[0]
                    print("✅ Usando primer input de password encontrado")
            
            if not username_field or not password_field:
                print("❌ No se pudieron encontrar los campos de login")
                print("HTML de la página:")
                print(self.driver.page_source[:1000])
                return False
            
            # Llenar campos
            print(f"📧 Ingresando usuario: {self.usuario}")
            username_field.clear()
            username_field.send_keys(self.usuario)
            
            print("🔑 Ingresando contraseña")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Buscar botón de login
            print("🔍 Buscando botón de login...")
            login_button = None
            button_selectors = [
                "input[type='submit']",
                "button[type='submit']",
                "button",
                ".btn-primary",
                "[value*='Entrar']",
                "[value*='Login']"
            ]
            
            for selector in button_selectors:
                try:
                    login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Botón encontrado con selector: {selector}")
                    break
                except NoSuchElementException:
                    continue
            
            if not login_button:
                print("❌ No se encontró el botón de login")
                return False
            
            # Hacer clic
            login_button.click()
            print("✅ Botón de login clickeado")
            
            # Esperar a que cargue la siguiente página
            time.sleep(5)
            
            # Verificar si el login fue exitoso
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if "login" not in current_url.lower() or "entrar" not in page_source:
                print("✅ Login exitoso")
                return True
            else:
                print("⚠️ Posible fallo en el login, pero continuando...")
                # Guardar screenshot para debug
                try:
                    self.driver.save_screenshot("login_debug.png")
                    print("📸 Screenshot guardado: login_debug.png")
                except:
                    pass
                return True
                
        except TimeoutException:
            print("❌ Timeout esperando la página de login")
            return False
        except NoSuchElementException as e:
            print(f"❌ No se encontró el elemento: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Error durante el login: {str(e)}")
            return False
    
    def parsear_informacion_organizacion(self, html_content):
        """
        Parsea el HTML para extraer la información de la organización
        
        Args:
            html_content: Contenido HTML de la página
            
        Returns:
            dict: Información extraída
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            datos = {
                'org_id': '',
                'nombre_organizacion': '',
                'estado_org': '',
                'cif': '',
                'telefono': '',
                'movil': '',
                'web': '',
                'direccion': '',
                'nombre_contacto': '',
                'email': '',
                'estado_usuario': '',
                'completada': '',
                'ultima_modificacion': '',
                'metodo_pago': '',
                'ultimo_login': '',
                'total_logins': ''
            }
            
            # Extraer nombre de la organización
            h1_org = soup.find('h1', class_='admin_menu_3')
            if h1_org:
                span_nombre = h1_org.find('span')
                if span_nombre:
                    nombre_org = span_nombre.text.strip()
                    # Limpiar el nombre (quitar dos puntos al inicio si existen)
                    if nombre_org.startswith(':'):
                        nombre_org = nombre_org[1:].strip()
                    datos['nombre_organizacion'] = nombre_org
                    print(f"   🏢 Organización: {nombre_org}")
            
            # Extraer Org ID
            # Buscar cualquier h2 que contenga "Org" seguido de números
            h2_elements = soup.find_all('h2')
            for h2 in h2_elements:
                if h2.text and 'Org' in h2.text:
                    org_match = re.search(r'Org\s*(\d+)', h2.text)
                    if org_match:
                        datos['org_id'] = org_match.group(1)
                        print(f"   🆔 Org ID encontrado: {datos['org_id']}")
                        break
            
            # Extraer estado de la org
            estado_tag = soup.find('span', class_='tag_success')
            if estado_tag:
                datos['estado_org'] = estado_tag.text.strip()
            
            # Buscar todas las tablas
            tablas = soup.find_all('table', class_='table_left_aligned')
            
            for tabla in tablas:
                filas = tabla.find_all('tr')
                for fila in filas:
                    th = fila.find('th')
                    td = fila.find('td')
                    
                    if th and td:
                        campo = th.text.strip()
                        valor = td.text.strip()
                        
                        # Limpiar valor (quitar saltos de línea y espacios extra)
                        valor = ' '.join(valor.split())
                        
                        # Mapear campos
                        if campo == 'CIF':
                            datos['cif'] = valor
                        elif campo == 'Teléfono':
                            datos['telefono'] = valor
                        elif campo == 'Móvil':
                            datos['movil'] = valor
                        elif campo == 'Web':
                            datos['web'] = valor
                        elif campo == 'Dirección':
                            datos['direccion'] = valor
                        elif campo == 'Nombre':
                            nombre_link = td.find('a')
                            if nombre_link:
                                datos['nombre_contacto'] = nombre_link.text.strip()
                        elif campo == 'Email':
                            datos['email'] = valor
                        elif campo == 'Estado':
                            datos['estado_usuario'] = valor
                        elif campo == 'Completada':
                            datos['completada'] = valor
                        elif campo == 'Ultima modificación':
                            datos['ultima_modificacion'] = valor
                        elif campo == 'Ultimo login':
                            datos['ultimo_login'] = valor
                        elif campo == 'Logins':
                            datos['total_logins'] = valor
                        elif campo == 'Método de pago':
                            # El método de pago puede tener enlaces y saltos de línea
                            links = td.find_all('a')
                            if links:
                                metodos = []
                                for link in links:
                                    metodo = link.text.strip()
                                    if metodo:
                                        metodos.append(metodo)
                                datos['metodo_pago'] = ', '.join(metodos) if metodos else valor
                            else:
                                datos['metodo_pago'] = valor
            
            return datos
            
        except Exception as e:
            print(f"⚠️ Error al parsear HTML: {str(e)}")
            return {}
    
    def buscar_por_dni(self, dni):
        """
        Busca una organización por DNI
        
        Args:
            dni: DNI a buscar
            
        Returns:
            dict: Información de la búsqueda
        """
        try:
            print(f"\n🔍 Buscando DNI: {dni}")
            
            # Construir la URL de búsqueda
            search_url = f"{self.base_url}/orgs/search?utf8=%E2%9C%93&search%5Bvalue%5D={dni}&search%5Boption%5D=cif&commit=Buscar"
            
            print(f"🌐 Accediendo a: {search_url}")
            self.driver.get(search_url)
            
            # Esperar a que cargue la página de resultados
            time.sleep(3)
            
            # Obtener el contenido de la página
            page_source = self.driver.page_source
            
            # Preparar resultado
            resultado = {
                'dni': dni,
                'url_busqueda': search_url,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'resultado_encontrado': False
            }
            
            # Verificar si hay resultados
            if 'No se encontraron resultados' in page_source or 'sin resultados' in page_source.lower():
                print(f"⚠️ No se encontraron resultados para DNI: {dni}")
                resultado['resultado_encontrado'] = False
            else:
                # Parsear la información
                datos_parseados = self.parsear_informacion_organizacion(page_source)
                resultado.update(datos_parseados)
                
                # Verificar si realmente hay información valiosa
                tiene_datos = any([
                    datos_parseados.get('nombre_contacto'),
                    datos_parseados.get('email'),
                    datos_parseados.get('telefono'),
                    datos_parseados.get('cif'),
                    datos_parseados.get('org_id')
                ])
                
                if tiene_datos:
                    print(f"✅ Resultados encontrados para DNI: {dni}")
                    resultado['resultado_encontrado'] = True
                    
                    # Mostrar información encontrada
                    if datos_parseados.get('nombre_contacto'):
                        print(f"   📋 Contacto: {datos_parseados.get('nombre_contacto')}")
                    if datos_parseados.get('email'):
                        print(f"   📧 Email: {datos_parseados.get('email')}")
                    if datos_parseados.get('telefono'):
                        print(f"   📞 Teléfono: {datos_parseados.get('telefono')}")
                else:
                    print(f"⚠️ Se encontró entrada pero sin datos válidos para DNI: {dni}")
                    resultado['resultado_encontrado'] = False
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al buscar DNI {dni}: {str(e)}")
            return {
                'dni': dni,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def inicializar_csv_salida(self, archivo_csv='resultados_nlocal.csv', reiniciar=False):
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
        Procesa un archivo CSV con DNIs
        
        Args:
            archivo_csv: Ruta al archivo CSV con los DNIs
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
                lector = csv.DictReader(f, delimiter=delimitador)
                dnis = []
                
                for fila in lector:
                    # Buscar columna con DNI (puede estar en diferentes columnas)
                    if 'DNI' in fila:
                        dni = fila['DNI'].strip()
                    elif 'dni' in fila:
                        dni = fila['dni'].strip()
                    elif 'cif' in fila:
                        dni = fila['cif'].strip()
                    else:
                        # Tomar el primer campo que no esté vacío
                        dni = next((v for v in fila.values() if v.strip()), None)
                    
                    if dni:
                        dnis.append(dni)
                
                print(f"📊 Total de DNIs encontrados: {len(dnis)}")
                
                # Filtrar DNIs ya procesados si existen
                if self.dnis_procesados:
                    dnis_originales = len(dnis)
                    dnis = [dni for dni in dnis if dni not in self.dnis_procesados]
                    dnis_omitidos = dnis_originales - len(dnis)
                    if dnis_omitidos > 0:
                        print(f"⏭️ Omitiendo {dnis_omitidos} DNIs ya procesados")
                        print(f"📊 DNIs pendientes: {len(dnis)}")
                
                # Procesar cada DNI
                for i, dni in enumerate(dnis, 1):
                    print(f"\n{'='*60}")
                    print(f"Procesando {i}/{len(dnis)}: {dni}")
                    print(f"{'='*60}")
                    
                    resultado = self.buscar_por_dni(dni)
                    resultados.append(resultado)
                    
                    # Añadir resultado al CSV inmediatamente si tiene información
                    self.append_resultado_csv(resultado)
                    
                    # Pausa entre búsquedas para no sobrecargar el servidor
                    if i < len(dnis):
                        time.sleep(2)
                
                print(f"\n✅ Procesamiento completado: {len(resultados)} resultados nuevos")
                return resultados
                
        except FileNotFoundError:
            print(f"❌ Archivo CSV no encontrado: {archivo_csv}")
            return []
        except Exception as e:
            print(f"❌ Error al procesar el archivo CSV: {str(e)}")
            return []
    
    def cerrar_navegador(self):
        """Cierra el navegador"""
        if self.driver:
            print("\n🔒 Cerrando navegador...")
            self.driver.quit()
            print("✅ Navegador cerrado")
    
    def guardar_resultados_json(self, resultados, archivo_salida='resultados_nlocal.json'):
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
    
    def guardar_resultados_csv(self, resultados, archivo_salida='resultados_nlocal.csv'):
        """
        Guarda solo los resultados exitosos en un archivo CSV
        
        Args:
            resultados: Lista con los resultados
            archivo_salida: Nombre del archivo de salida
        """
        try:
            # Filtrar solo resultados exitosos
            resultados_exitosos = [
                r for r in resultados 
                if r.get('resultado_encontrado', False)
            ]
            
            if not resultados_exitosos:
                print("⚠️ No hay resultados exitosos para guardar en CSV")
                return
            
            print(f"\n💾 Guardando resultados en CSV: {archivo_salida}")
            
            # Definir campos del CSV
            campos_csv = [
                'dni', 'org_id', 'nombre_organizacion', 'estado_org', 'cif', 'telefono', 'movil', 
                'web', 'direccion', 'nombre_contacto', 'email', 'estado_usuario', 
                'completada', 'ultima_modificacion', 'ultimo_login', 'total_logins'
            ]
            
            with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=campos_csv, delimiter=';')
                escritor.writeheader()
                
                for resultado in resultados_exitosos:
                    fila = {}
                    for campo in campos_csv:
                        fila[campo] = resultado.get(campo, '')
                    escritor.writerow(fila)
            
            print(f"✅ Resultados CSV guardados correctamente ({len(resultados_exitosos)} registros)")
            
        except Exception as e:
            print(f"❌ Error al guardar resultados CSV: {str(e)}")
    
    def guardar_dnis_sin_informacion(self, resultados, archivo_salida='dnis_sin_informacion.csv'):
        """
        Guarda los DNIs que no encontraron información en un archivo CSV
        
        Args:
            resultados: Lista con los resultados
            archivo_salida: Nombre del archivo de salida
        """
        try:
            # Filtrar solo resultados sin información
            dnis_sin_info = [
                r for r in resultados 
                if not r.get('resultado_encontrado', False) and not r.get('error')
            ]
            
            if not dnis_sin_info:
                print("✅ Todos los DNIs encontraron información")
                return
            
            print(f"\n💾 Guardando DNIs sin información en CSV: {archivo_salida}")
            
            with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=['dni', 'timestamp'], delimiter=';')
                escritor.writeheader()
                
                for resultado in dnis_sin_info:
                    escritor.writerow({
                        'dni': resultado.get('dni', ''),
                        'timestamp': resultado.get('timestamp', '')
                    })
            
            print(f"⚠️ DNIs sin información guardados correctamente ({len(dnis_sin_info)} registros)")
            
        except Exception as e:
            print(f"❌ Error al guardar DNIs sin información: {str(e)}")
    
    def guardar_resultados(self, resultados, archivo_json='resultados_nlocal.json', archivo_csv='resultados_nlocal.csv'):
        """
        Guarda los resultados tanto en JSON como en CSV
        
        Args:
            resultados: Lista con los resultados
            archivo_json: Nombre del archivo JSON de salida
            archivo_csv: Nombre del archivo CSV de salida
        """
        self.guardar_resultados_json(resultados, archivo_json)
        self.guardar_resultados_csv(resultados, archivo_csv)
        self.guardar_dnis_sin_informacion(resultados)


def main():
    """Función principal"""
    print("="*60)
    print("🚀 SCRAPER NLOCAL.COM")
    print("="*60)
    
    # Intentar importar configuración
    try:
        from config import NLOCAL_USUARIO, NLOCAL_PASSWORD, SCRAPER_CONFIG
        usuario = NLOCAL_USUARIO
        password = NLOCAL_PASSWORD
        print("✅ Configuración cargada desde config.py")
    except ImportError:
        # Si no se puede importar, usar variables de entorno
        usuario = os.getenv('NLOCAL_USUARIO', '')
        password = os.getenv('NLOCAL_PASSWORD', '')
        print("⚠️ No se pudo importar config.py, usando variables de entorno")
    
    # Si no hay credenciales, pedir al usuario
    if not usuario or not password or usuario == 'tu_usuario@ejemplo.com' or password == 'tu_contraseña':
        print("\n❌ Error: No se encontraron credenciales válidas")
        print("\nPor favor, configura las credenciales en una de estas formas:")
        print("1. Edita el archivo config.py con tus credenciales")
        print("2. O establece las variables de entorno:")
        print("   export NLOCAL_USUARIO='tu_usuario@ejemplo.com'")
        print("   export NLOCAL_PASSWORD='tu_contraseña'")
        return
    
    # Inicializar scraper
    scraper = NlocalScraper(usuario, password, headless=False)
    
    try:
        # Iniciar navegador
        if not scraper.iniciar_navegador():
            print("❌ No se pudo iniciar el navegador")
            return
        
        # Realizar login
        if not scraper.login():
            print("❌ Error en el login. Verifique sus credenciales")
            scraper.cerrar_navegador()
            return
        
        # Inicializar CSV de salida (por defecto continúa desde donde quedó)
        scraper.inicializar_csv_salida(reiniciar=False)
        
        # Procesar archivo CSV
        # Cambiar a 'codigos_prueba.csv' para pruebas o 'codigos.csv' para procesamiento completo
        archivo_csv = 'codigos.csv'
        resultados = scraper.procesar_csv(archivo_csv)
        
        # Guardar resultados adicionales (JSON y DNIs sin información)
        if resultados:
            scraper.guardar_resultados_json(resultados)
            scraper.guardar_dnis_sin_informacion(resultados)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Proceso interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
    finally:
        # Cerrar navegador
        scraper.cerrar_navegador()
    
    print("\n" + "="*60)
    print("✅ Proceso finalizado")
    print("="*60)


if __name__ == "__main__":
    main()
