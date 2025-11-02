# Scraper Nlocal.com

Este proyecto contiene un scraper automatizado para buscar organizaciones en [nlocal.com](https://admin.nlocal.com/) utilizando Selenium.

## 📋 Descripción

El scraper permite:
- ✅ Autenticarse automáticamente en nlocal.com
- ✅ Buscar organizaciones por DNI/CIF
- ✅ Procesar múltiples búsquedas desde un archivo CSV
- ✅ Extraer información completa de organizaciones (nombre, contacto, email, etc.)
- ✅ Guardar resultados en JSON y CSV
- ✅ Guardado incremental de resultados (se guardan a medida que se obtienen)

## 🛠️ Requisitos

- Python 3.8 o superior
- Google Chrome instalado
- ChromeDriver (se descarga automáticamente si usas webdriver-manager)

## 📦 Instalación

1. Clona o descarga este repositorio

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. (Opcional) Instala ChromeDriver manualmente si prefieres:
```bash
# macOS
brew install chromedriver

# Ubuntu/Debian
sudo apt-get install chromium-chromedriver
```

## 🔧 Configuración

### Opción 1: Archivo de configuración (Recomendado)

Edita el archivo `config.py` con tus credenciales:

```python
NLOCAL_USUARIO = "tu_usuario_real@ejemplo.com"
NLOCAL_PASSWORD = "tu_contraseña_real"
```

### Opción 2: Variables de entorno

```bash
export NLOCAL_USUARIO="tu_usuario_real@ejemplo.com"
export NLOCAL_PASSWORD="tu_contraseña_real"
```

## 📁 Estructura de archivos

```
nlocal/
├── scraper_nlocal.py     # Script principal del scraper
├── config.py             # Archivo de configuración (con credenciales)
├── config_ejemplo.py     # Archivo de ejemplo de configuración
├── requirements.txt      # Dependencias de Python
├── README.md            # Este archivo
├── codigos.csv          # Archivo con DNIs a buscar (335 DNIs)
├── resultados_nlocal.json  # Resultados completos (generado)
├── resultados_nlocal.csv   # Resultados exitosos con información (generado)
├── dnis_sin_informacion.csv # DNIs sin información (generado)
└── setup.sh             # Script de configuración inicial
```

## 📊 Formato del archivo CSV

El archivo `codigos.csv` debe tener una columna con los DNIs o CIFs. El scraper buscará automáticamente en las siguientes columnas:
- `DNI`
- `dni`
- `cif`

El script detecta automáticamente si el delimitador es punto y coma (`;`) o coma (`,`).

Ejemplo de `codigos.csv`:
```csv
DNI
01139656Y
6259725E
B12345678
```

## 🚀 Uso

### Ejecución básica

```bash
python scraper_nlocal.py
```

El script:
1. Iniciará el navegador Chrome
2. Se autenticará en nlocal.com con tus credenciales
3. Leerá el archivo `codigos.csv`
4. Buscará cada DNI en el sistema
5. Guardará los resultados en:
   - `resultados_nlocal.json` (todos los resultados, incluyendo errores)
   - `resultados_nlocal.csv` (solo resultados exitosos con información completa)
   - `dnis_sin_informacion.csv` (DNIs sin información encontrada)

### Configuración avanzada

En `config.py` puedes ajustar:

```python
SCRAPER_CONFIG = {
    'headless': False,  # True para ejecutar sin ventana visible
    'timeout': 20,  # Tiempo de espera máximo
    'delay_busquedas': 2,  # Pausa entre búsquedas
    'implicit_wait': 10  # Espera implícita para elementos
}
```

## 📤 Resultados

Los resultados se guardan en dos formatos:

### JSON (`resultados_nlocal.json`)
Todos los resultados incluyendo errores y campos completos:

```json
[
  {
    "dni": "6259725E",
    "url_busqueda": "https://admin.nlocal.com/orgs/search?...",
    "timestamp": "2025-01-14 10:30:45",
    "resultado_encontrado": true,
    "org_id": "316287",
    "estado_org": "Activa",
    "cif": "B18616896",
    "telefono": "958535538",
    "nombre_contacto": "José Antonio Ruiz",
    "email": "info@andaluzadeactividades.es",
    "direccion": "C/ Ancha de Gracia. 11 1 - Planta, Oficina 1..."
  }
]
```

### CSV (`resultados_nlocal.csv`)
Solo resultados exitosos con información parseada, separado por punto y coma (`;`):
- **Guardado incremental**: Los resultados se escriben inmediatamente cuando se obtienen

```csv
dni;org_id;nombre_organizacion;estado_org;cif;telefono;nombre_contacto;email;direccion;...
6259725E;316287;NOMBRE DE LA EMPRESA;Activa;B18616896;958535538;José Antonio Ruiz;info@andaluzadeactividades.es;C/ Ancha de Gracia...
```

## 🔍 Flujo de búsqueda

Para cada DNI en el CSV:

1. Se construye la URL de búsqueda: `https://admin.nlocal.com/orgs/search?utf8=%E2%9C%93&search%5Bvalue%5D={dni}&search%5Boption%5D=cif&commit=Buscar`
2. El navegador accede a la URL
3. Se captura el contenido de la página
4. Se verifica si hay resultados
5. Se guarda toda la información en el archivo JSON

## ⚠️ Consideraciones importantes

### Seguridad
- ⚠️ **NO** subas el archivo `config.py` con credenciales reales a repositorios públicos
- Usa variables de entorno en producción
- Considera usar un sistema de gestión de secretos

### Uso responsable
- ✅ Respeta los términos de servicio de nlocal.com
- ✅ No sobrecargues el servidor con búsquedas muy rápidas
- ✅ Usa pausas apropiadas entre búsquedas

### Troubleshooting

#### Error: "ChromeDriver no encontrado"
```bash
pip install webdriver-manager
```

#### Error: "Timeout esperando la página"
- Verifica tu conexión a internet
- Aumenta el `timeout` en la configuración
- Verifica que nlocal.com esté disponible

#### Error: "No se encontró el elemento"
- El sitio web podría haber cambiado
- Verifica que tus credenciales sean correctas
- Revisa los logs para más detalles

## 📝 Logs

El script muestra información detallada durante la ejecución:

```
============================================================
🚀 SCRAPER NLOCAL.COM
============================================================
✅ Configuración cargada desde config.py
🔧 Configurando navegador Chrome...
✅ Navegador iniciado correctamente
🔐 Intentando login en https://admin.nlocal.com/
📧 Buscando campo de email...
✅ Email ingresado: usuario@ejemplo.com
🔑 Buscando campo de contraseña...
✅ Contraseña ingresada
🔍 Buscando botón de login...
✅ Botón de login clickeado
✅ Login exitoso

📂 Leyendo archivo CSV: codigos.csv
📊 Total de DNIs encontrados: 3

============================================================
Procesando 1/3
============================================================
🔍 Buscando DNI: 6259725E
🌐 Accediendo a: https://admin.nlocal.com/orgs/search...
✅ Resultados encontrados para DNI: 6259725E
```

## 🤝 Contribuir

Si encuentras bugs o tienes sugerencias, puedes:
1. Reportar issues
2. Hacer pull requests
3. Contribuir con mejoras

## 📄 Licencia

Este proyecto es de uso interno. Respeta los términos de servicio del sitio web que estás scraping.

## 🙏 Créditos

Desarrollado con:
- [Selenium](https://selenium-python.readthedocs.io/) - Automatización del navegador
- [Python](https://www.python.org/) - Lenguaje de programación
