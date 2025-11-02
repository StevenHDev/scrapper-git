# Scraper Einforma.com

Este proyecto contiene un scraper automatizado para buscar información de empresas en [einforma.com](https://www.einforma.com) utilizando requests y BeautifulSoup.

## 📋 Descripción

El scraper permite:
- ✅ Buscar información de empresas por NIF
- ✅ Procesar múltiples búsquedas desde un archivo CSV
- ✅ Extraer información completa de empresas (denominación, dirección, teléfono, actividades, etc.)
- ✅ Guardar resultados en JSON y CSV
- ✅ Guardado incremental de resultados (se guardan a medida que se obtienen)

## 🛠️ Requisitos

- Python 3.8 o superior

## 📦 Instalación

Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura de archivos

```
einforma/
├── scraper_einforma.py     # Script principal del scraper
├── requirements.txt        # Dependencias de Python
├── README.md              # Este archivo
├── codigos.csv            # Archivo con NIFs a buscar
├── resultados_einforma.json  # Resultados completos (generado)
└── resultados_einforma.csv   # Resultados exitosos con información (generado)
```

## 📊 Formato del archivo CSV

El archivo `codigos.csv` debe tener una columna con los NIFs. Cada línea un NIF.

Ejemplo de `codigos.csv`:
```csv
01473547Y
03121808H
A28910495
B18616896
```

## 🚀 Uso

Ejecución básica:

```bash
python scraper_einforma.py
```

El script:
1. Leerá el archivo `codigos.csv`
2. Buscará cada NIF en el sistema de Einforma
3. Guardará los resultados en:
   - `resultados_einforma.json` (todos los resultados, incluyendo errores)
   - `resultados_einforma.csv` (solo resultados exitosos con información completa)

## 📤 Resultados

Los resultados se guardan en dos formatos:

### JSON (`resultados_einforma.json`)
Todos los resultados incluyendo errores y campos completos.

### CSV (`resultados_einforma.csv`)
Solo resultados exitosos con información parseada, separado por punto y coma (`;`):
- **Guardado incremental**: Los resultados se escriben inmediatamente cuando se obtienen

Campos extraídos:
- `nif`: NIF de la empresa
- `denominacion`: Nombre de la empresa
- `duns_number`: Número DUNS
- `domicilio_social`: Dirección
- `localidad`: Ciudad y provincia
- `telefono`: Teléfono
- `fax`: Fax
- `fecha_ultimo_dato`: Fecha de último dato
- `accionistas`: Número de accionistas
- `forma_juridica`: Forma jurídica
- `actividad_informa`: Actividad principal
- `cnae_2009`: CNAE 2009
- `cnae_2025`: CNAE 2025
- `objeto_social`: Objeto social
- `ultimo_balance`: Último balance cargado
- `balances_disponibles`: Número de balances disponibles
- `deposito_mercantil`: Depósito en Registro Mercantil
- `deposito_einforma`: Depósito en eInforma
- `popularidad`: Información de popularidad
- `ventas_2022`, `ventas_2023`, `ventas_2024`: Ventas de los últimos años

## 🔍 Flujo de búsqueda

Para cada NIF en el CSV:

1. Se construye la URL de búsqueda: `https://www.einforma.com/servlet/app/prod/ETIQUETA_EMPRESA/nif/{nif}`
2. Se realiza una petición HTTP GET
3. Se captura el contenido de la página
4. Se parsea la tabla con id="datos"
5. Se extrae la información relevante
6. Se guarda en el archivo CSV inmediatamente

## ⚠️ Consideraciones importantes

### Uso responsable
- ✅ Respeta los términos de servicio de einforma.com
- ✅ No sobrecargues el servidor con búsquedas muy rápidas
- ✅ Usa pausas apropiadas entre búsquedas (3 segundos por defecto)

### Continuación de procesamiento
- Si el script se interrumpe, puedes volverlo a ejecutar y continuará desde donde quedó
- Los NIFs ya procesados se omiten automáticamente

### Troubleshooting

#### Error: "Connection timeout"
- Verifica tu conexión a internet
- Aumenta el timeout en la configuración
- Verifica que einforma.com esté disponible

## 📝 Logs

El script muestra información detallada durante la ejecución:
- Progreso de procesamiento
- Resultados encontrados
- Errores si los hay

