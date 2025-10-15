# Scrapper de Evolución-A Competición

Scrapper para extraer productos del catálogo de **Evolución-A** (https://www.evolucion-a.com/es/catalogo)

Especialistas en productos para automovilismo de competición: Mitsubishi Lancer Evo, Renault, BMW, Citroën, Peugeot, Ford, Fiat y SEAT.

## 📋 Archivos

```
evolucionaa/
├── scrapper_evolucion_a.py           - Scrapper principal
├── scrapper_evolucion_a_completo.py  - Scrapper alternativo con detalles
├── convertir_a_woocommerce.py        - Convertidor a WooCommerce/Duda.co
├── requirements.txt                  - Dependencias
└── README.md                         - Esta documentación
```

## 🚀 Uso Rápido

```bash
# 1. Entrar a la carpeta
cd evolucionaa

# 2. Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt

# 3. Ejecutar scrapper
python3 scrapper_evolucion_a.py

# 4. Convertir a formato Duda.co
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; converter = WooCommerceConverter(); converter.convert_to_duda('evolucion_a_productos.csv', 'evolucion_a_duda.csv')"
```

## 📊 Estructura del Catálogo

El sitio tiene **8 categorías principales** con subcategorías:

### 1. RENAULT (10 subcategorías)
- RENAULT 11 TURBO
- RENAULT 21 TURBO
- RENAULT 5 GT TURBO
- RENAULT 5 TURBO 1/2 MAXI
- RENAULT CLIO 16S / WILLIAMS
- RENAULT CLIO R27 (R3)
- RENAULT CLIO RS 172/182CV
- RENAULT MEGANE COUPE
- RENAULT MEGANE II RS SPORT
- RENAULT MEGANE III RS

### 2. MITSUBISHI (4 subcategorías)
- EVOLUCION 5-6
- EVOLUCION 7-8
- EVOLUCION 9
- EVOLUCION X

### 3. BMW (2 subcategorías)
- M3 E30
- M3 E46

### 4. CITROËN (3 subcategorías)
- AX
- CITROËN C2
- SAXO

### 5. PEUGEOT (4 subcategorías)
- PEUGEOT 106 RALLYE / GTI
- PEUGEOT 205 RALLYE / GTI
- PEUGEOT 206 XS DESAFIO/S1600
- PEUGEOT 306 MAXI

### 6. FORD (3 subcategorías)
- ESCORT RS COSWORTH
- FORD MUSTANG
- FORD SIERRA

### 7. FIAT (2 subcategorías)
- FIAT 124 - 131
- FIAT 600

### 8. SEAT (5 subcategorías)
- SEAT 124
- SEAT 600
- SEAT CORDOBA
- SEAT IBIZA
- SEAT LEON

## ✨ Características

- ✅ Extrae categorías y subcategorías jerárquicamente
- ✅ Estructura de categorías: "CATEGORIA > SUBCATEGORIA"
- ✅ Detecta productos en sección "Listado de destacados"
- ✅ Fallback a productos individuales (id="iid_XXX")
- ✅ Extrae: título, código, precio, imagen, descripción
- ✅ Elimina duplicados automáticamente
- ✅ Exporta a CSV para WooCommerce y Duda.co
- ✅ Sistema de logging detallado
- ✅ Pausas respetuosas entre peticiones

## 📁 Archivos Generados

Después de ejecutar el scrapper:

```
evolucion_a_productos.csv  - Datos completos extraídos
evolucion_a_duda.csv       - Formato Duda.co (listo para importar)
```

## 📥 Importar en Duda.co

1. Accede a tu panel de **Duda.co**
2. Ve a: **eCommerce → Products**
3. Haz clic en **"Import Products"**
4. Selecciona: `evolucion_a_duda.csv`
5. Revisa la vista previa
6. Haz clic en **"Import"**

## ⚙️ Configuración

Edita `scrapper_evolucion_a.py` línea 366 para ajustar:

```python
# Procesar solo las primeras N categorías (prueba rápida)
items = scraper.scrape_catalog(max_categories=2)

# Procesar todas las categorías (completo)
items = scraper.scrape_catalog(max_categories=None)
```

## 📊 Datos Incluidos

| Campo | Descripción |
|-------|-------------|
| `titulo` | Nombre del producto |
| `codigo` | Código único del producto |
| `precio` | Precio en euros |
| `imagen_principal` | Nombre del archivo de imagen |
| `url_imagen_principal` | URL completa de la imagen |
| `descripcion_corta` | Descripción breve |
| `categoria` | Categoría jerárquica completa |
| `marca` | "Evolución-A" |
| `enlace_detalle` | URL del producto |

## 📝 Notas

- El scrapper respeta el sitio con pausas de 0.5-1 segundo entre peticiones
- Las categorías jerárquicas mantienen la estructura: "PADRE > HIJO"
- Los productos duplicados se eliminan automáticamente por código
- Algunos productos pueden no tener precio si no está en el listado

## 🔄 Conversión a Formatos

### Para WooCommerce:
```bash
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; converter = WooCommerceConverter(); converter.convert_csv('evolucion_a_productos.csv', 'evolucion_a_woocommerce.csv')"
```

### Para Duda.co:
```bash
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; converter = WooCommerceConverter(); converter.convert_to_duda('evolucion_a_productos.csv', 'evolucion_a_duda.csv')"
```

---

**Última actualización:** 15 de Octubre, 2025  
**Productos extraídos:** 7 productos de 8 categorías principales

