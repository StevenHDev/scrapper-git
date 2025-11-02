# Scrapper GeneraWeb Duda

Este scrapper está diseñado para extraer información de empresas del sistema GeneraWeb Duda con soporte completo para paginación.

## Características

- ✅ **Autenticación automática** con usuario y contraseña
- ✅ **Extracción de datos de tabla** de empresas
- ✅ **Paginación completa** - Extrae todas las 2310 empresas en solo 4 páginas
- ✅ **Optimización de rendimiento** - 1000 empresas por página
- ✅ **Navegación a perfiles individuales** usando los IDs
- ✅ **Exportación a CSV** con información completa
- ✅ **Manejo robusto de errores** y múltiples estrategias de detección

## Configuración

### Credenciales
- **Usuario**: `almudena.roman@nlocal.es`
- **Contraseña**: `aroman246`

### URLs
- **Login**: `http://generawebduda.nlocal.com/index.php`
- **Empresas**: `http://generawebduda.nlocal.com/index.php?ids=&searchCondition=CO&name=&count=5&dateNewFrom=&dateNewTo=&search=Buscar&s=home#empresas`

## Uso

### Extracción Completa (Todas las empresas)
```bash
python3 scrapper_generaweb_duda.py
```

### Extracción Limitada (Para pruebas)
Modifica el archivo `scrapper_generaweb_duda.py` en la función `main()`:

```python
# Para extraer TODAS las empresas (2310 en 4 páginas):
empresas = scraper.scrape_empresas(max_empresas=None, max_pages=4)

# Para pruebas limitadas:
empresas = scraper.scrape_empresas(max_empresas=1000, max_pages=2)
```

## Paginación

El scrapper está optimizado para manejar la paginación del sistema:

- **Total de empresas**: 2310 empresas
- **Páginas a procesar**: 3 páginas (2, 3 y 4) - La página 1 ya fue procesada
- **Empresas por página**: 1000 (optimizado)
- **Tiempo estimado**: ~10-15 minutos para extraer las páginas 2, 3 y 4

## Datos Extraídos

El scrapper extrae la siguiente información de cada empresa:

### Datos Básicos de la Tabla
- **ID**: Identificador único
- **Empresa**: Nombre de la empresa
- **Entrada**: Fecha de entrada
- **Estado**: Estado actual (Diseño, Publicación, etc.)

### URLs Asociadas
- **URL Perfil**: Enlace al perfil detallado de la empresa
- **URL Web**: Sitio web de la empresa
- **URL Panel**: Enlace al panel de control

### Datos Detallados del Perfil (si están disponibles)
- **Nombre Empresa**: Nombre completo
- **Dirección**: Dirección física
- **Teléfono**: Número de contacto
- **Email**: Correo electrónico
- **Web**: Sitio web
- **Descripción**: Descripción de la empresa
- **Servicios**: Servicios ofrecidos
- **Contacto**: Información de contacto

## Archivo de Salida

El scrapper genera un archivo CSV llamado `generaweb_duda_empresas.csv` con todos los datos extraídos.

## Requisitos

- Python 3.7+
- Selenium
- Chrome/Chromedriver
- BeautifulSoup4

## Instalación de Dependencias

```bash
pip install selenium beautifulsoup4
```

## Configuración del Navegador

El scrapper está configurado para ejecutarse en modo headless (sin interfaz gráfica) por defecto. Para ver el navegador durante la ejecución, cambia `headless=True` a `headless=False` en el código.

## Limitaciones

- Extrae solo las primeras 5 empresas por defecto
- Requiere conexión a internet
- Depende de la estructura HTML del sitio web
- Puede requerir ajustes si la estructura del sitio cambia

## Solución de Problemas

### Error de Login
- Verificar que las credenciales sean correctas
- Asegurar que el sitio web esté accesible
- Revisar que Chrome/Chromedriver estén instalados

### Error de Extracción
- Verificar que la tabla de empresas esté visible
- Comprobar que los selectores CSS sean correctos
- Revisar la estructura HTML del sitio

### Timeout Errors
- Aumentar los tiempos de espera en el código
- Verificar la velocidad de la conexión a internet
- Comprobar que el sitio web responda correctamente
