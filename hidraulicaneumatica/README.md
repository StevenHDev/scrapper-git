# Scrapper de Hidráulica Neumática - Estehyne

Scrapper para extraer productos del catálogo de **Hidráulica Neumática** (https://www.hidraulicaneumatica.es/es/productos)

Productos industriales de hidráulica, neumática y herramientas.

## 📋 Archivos

```
hidraulicaneumatica/
├── scrapper_hidraulica.py         - Scrapper principal
├── convertir_a_woocommerce.py     - Convertidor a WooCommerce/Duda.co
├── requirements.txt               - Dependencias
├── README.md                      - Esta documentación
│
├── categorias/                    - 📁 CSV por categoría individual
│   ├── NEUMATICA.csv
│   ├── CILINDROS_NEUMATICOS.csv
│   ├── HIDRAULICA.csv
│   └── ... (un CSV por cada categoría)
│
└── CSV consolidados:
    ├── hidraulica_neumatica_productos.csv     - Todos los productos
    ├── hidraulica_neumatica_duda.csv          - Formato Duda.co
    └── hidraulica_neumatica_woocommerce.csv   - Formato WooCommerce
```

## 🚀 Uso Rápido

```bash
# 1. Entrar a la carpeta
cd hidraulicaneumatica

# 2. Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt

# 3. Ejecutar scrapper
python3 scrapper_hidraulica.py

# 4. Los CSV se generan automáticamente:
#    - categorias/*.csv - Un archivo por categoría
#    - hidraulica_neumatica_*.csv - Archivos consolidados
```

## 📊 Estructura del Catálogo

El sitio tiene categorías principales con múltiples niveles de subcategorías:

### Categorías Principales:

1. **NEUMATICA**
   - Racores instantáneos
   - Funciones neumáticas
   - Válvulas
   - Distribuidores
   - Tubos técnicos
   - Enchufes rápidos
   - Pistolas sopladoras
   - Y muchas más...

2. **CILINDROS NEUMATICOS**
   - Cilindros Camozzi (múltiples series ISO)
   - Cilindros Joucomatic
   - Cilindros Aventics
   - Sensores magnéticos

3. **UNIDADES FRL**
   - Filtro Regulador Lubricador
   - Manómetros
   - Purgas y descargas

4. **DISTRIBUIDORES - VÁLVULAS NEUMATICAS**

5. **HIDRAULICA**
   - Racores hidráulica
   - Válvulas hidráulicas
   - Enchufes rápidos
   - Cilindros hidráulicos
   - Bombas de paletas

6. **MANGUERA HIDRAULICAS**

7. **MANGUERAS INDUSTRIALES**

8. **RACORES INDUSTRIALES**

9. **MANOMETROS**

10. **RACORES INOXIDABLE**

Y muchas más...

## ✨ Características Especiales

- ✅ **CSV independiente por categoría** en carpeta `categorias/`
- ✅ **CSV consolidado** con todos los productos
- ✅ Navegación de hasta 3 niveles jerárquicos
- ✅ Límites configurables para evitar saturación
- ✅ Extrae: título, código, precio, imagen, descripción
- ✅ Elimina duplicados automáticamente
- ✅ Exporta a formatos WooCommerce y Duda.co
- ✅ Sistema de logging detallado
- ✅ Pausas respetuosas (0.3-1 segundo)

## 📁 Archivos Generados

### Por Categoría (categorias/):
Cada categoría principal genera su propio CSV:
```
NEUMATICA.csv
CILINDROS_NEUMATICOS.csv
UNIDADES_FRL_-_FILTRO_REGULADOR_LUBRICADOR.csv
HIDRAULICA.csv
MANGUERA_HIDRAULICAS.csv
...
```

### Consolidados:
```
hidraulica_neumatica_productos.csv     - Todos los productos juntos
hidraulica_neumatica_duda.csv          - Formato Duda.co
hidraulica_neumatica_woocommerce.csv   - Formato WooCommerce
```

## 📥 Importar en Duda.co

### Opción 1: Importar Todo
```bash
# Convertir archivo consolidado
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; c = WooCommerceConverter(); c.convert_to_duda('hidraulica_neumatica_productos.csv', 'hidraulica_neumatica_duda.csv')"

# Importar en Duda.co:
# 1. eCommerce → Products → Import
# 2. Seleccionar hidraulica_neumatica_duda.csv
```

### Opción 2: Importar por Categoría
```bash
# Convertir una categoría específica
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; c = WooCommerceConverter(); c.convert_to_duda('categorias/NEUMATICA.csv', 'neumatica_duda.csv')"

# Importar en Duda.co
```

## 📥 Importar en WooCommerce

```bash
# Para todo el catálogo
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; c = WooCommerceConverter(); c.convert_csv('hidraulica_neumatica_productos.csv', 'hidraulica_neumatica_woocommerce.csv')"

# Para una categoría específica
python3 -c "from convertir_a_woocommerce import WooCommerceConverter; c = WooCommerceConverter(); c.convert_csv('categorias/NEUMATICA.csv', 'neumatica_woocommerce.csv')"
```

## ⚙️ Configuración

Edita `scrapper_hidraulica.py` línea 442 para ajustar:

```python
items = scraper.scrape_catalog(
    max_categories=None,            # None = todas, o número específico
    max_subcategories_per_category=100,  # Límite de subcategorías
    max_depth=2                     # 2 o 3 niveles de profundidad
)
```

## 📊 Datos Incluidos

| Campo | Descripción |
|-------|-------------|
| `titulo` | Nombre del producto |
| `codigo` | Código único (iid_XXXX) |
| `precio` | Precio (si está disponible) |
| `imagen_principal` | Nombre del archivo de imagen |
| `url_imagen_principal` | URL completa de la imagen |
| `descripcion_corta` | Descripción breve |
| `categoria` | Categoría jerárquica completa |
| `marca` | "Hidráulica Neumática" |
| `enlace_detalle` | URL del producto |

## 📝 Notas

- El sitio tiene más de 540 subcategorías, el scrapper limita por defecto
- Los productos se identifican por `id="iid_XXXX"`
- Las categorías se identifican por enlaces `/es/productos/List/listing/`
- CSV por categoría facilita importaciones parciales
- Pausas respetuosas para no saturar el servidor

## 🔄 Conversión Masiva

Para convertir TODOS los CSV de categorías a formato Duda.co:

```bash
for file in categorias/*.csv; do
    basename=$(basename "$file" .csv)
    python3 -c "from convertir_a_woocommerce import WooCommerceConverter; c = WooCommerceConverter(); c.convert_to_duda('$file', 'duda/${basename}_duda.csv')"
done
```

---

**Última actualización:** 15 de Octubre, 2025  
**Categorías procesadas:** Variable según configuración  
**Formato:** CSV por categoría + CSV consolidado




