# 📦 Guía de Importación de Productos - Bombas Bloch

## ✅ Archivos Generados

```
📁 bombas_bloch_productos.csv        (32 KB) - Datos completos extraídos
📁 bombas_bloch_woocommerce.csv      (27 KB) - Formato WooCommerce
📁 bombas_bloch_duda.csv             (24 KB) - Formato Duda.co
```

**Total:** 88 productos de 11 categorías principales

---

## 🛒 Importar en WooCommerce

### Pasos:

1. **Accede a tu panel de WordPress**
2. Ve a: **WooCommerce → Productos**
3. Haz clic en **"Importar"** (botón superior)
4. **Selecciona el archivo:** `bombas_bloch_woocommerce.csv`
5. Haz clic en **"Continuar"**
6. **Mapea las columnas** (WooCommerce lo hace automáticamente)
7. Haz clic en **"Ejecutar importación"**
8. ¡Listo! Los productos se importarán con:
   - ✅ SKU único
   - ✅ Nombre del producto
   - ✅ Imagen principal
   - ✅ Categoría asignada
   - ✅ Estado: Publicado y En Stock

### 📝 Notas WooCommerce:

- Las imágenes se cargarán automáticamente desde el servidor de Bombas Bloch
- Las categorías se crearán automáticamente si no existen
- Los precios deberán agregarse manualmente (el sitio no los muestra)
- Los productos quedarán publicados inmediatamente

---

## 🌐 Importar en Duda.co

### Pasos:

1. **Accede a tu panel de Duda.co**
2. Ve a: **eCommerce → Products**
3. Haz clic en **"Import Products"**
4. **Selecciona el archivo:** `bombas_bloch_duda.csv`
5. Haz clic en **"Upload"**
6. Duda.co procesará el archivo y mostrará una vista previa
7. Revisa los datos y haz clic en **"Import"**
8. ¡Listo! Los productos se importarán con:
   - ✅ Product Name (Nombre)
   - ✅ SKU (Código único)
   - ✅ Image URL (Imagen principal)
   - ✅ Category (Categoría)
   - ✅ Brand: "Bombas Bloch"
   - ✅ Stock: 999 unidades
   - ✅ Tax & Shipping: Habilitados

### 📝 Notas Duda.co:

- El formato incluye Meta Title y Meta Description para SEO
- Las imágenes se cargarán desde URLs externas
- Stock configurado en 999 por defecto (editable después)
- Brand está configurado como "Bombas Bloch"

---

## 📊 Información de los Productos

### Datos Incluidos:

| Campo | WooCommerce | Duda.co | Valor |
|-------|-------------|---------|-------|
| **Nombre** | ✅ | ✅ | Nombre de la serie |
| **SKU** | ✅ | ✅ | Código único (ej: cid_45207) |
| **Imagen Principal** | ✅ | ✅ | URL completa |
| **Categoría** | ✅ | ✅ | 11 categorías principales |
| **Precio** | ⚠️ Vacío | ⚠️ Vacío | Agregar manualmente |
| **Descripción** | ✅ | ✅ | Cuando disponible |
| **Stock** | ✅ En stock | ✅ 999 unidades | Editable |
| **Marca** | ⚠️ N/A | ✅ | Bombas Bloch |
| **Meta SEO** | ⚠️ N/A | ✅ | Title & Description |

---

## 🏷️ Categorías Incluidas

1. **Horizontales Domésticas de Superficie** (9 productos)
2. **Horizontales Industriales de Superficie** (10 productos)
3. **Verticales de Superficie** (4 productos)
4. **Sumergibles para Pozos** (7 productos)
5. **Sistemas Solar de Bombeo** (1 producto)
6. **Sumergibles para Achiques** (40 productos)
7. **Controladores de Presión** (0 productos - vacía)
8. **Equipos de Presión** (9 productos)
9. **Equipos Contra Incendios** (2 productos)
10. **Cuadros Eléctricos** (6 productos)
11. **Accesorios** (0 productos - vacía)

---

## ⚙️ Configuraciones Recomendadas

### Después de Importar:

1. **Agregar precios manualmente**
   - Los productos no tienen precio en el CSV
   - Edita cada producto o usa importación masiva de precios

2. **Revisar categorías**
   - Verifica que las categorías se crearon correctamente
   - Ajusta subcategorías si es necesario

3. **Optimizar imágenes** (opcional)
   - Las imágenes están en servidor externo
   - Considera descargarlas y subirlas a tu hosting para mejor rendimiento

4. **Configurar envíos y impuestos**
   - Configura las reglas de envío según tu región
   - Ajusta los impuestos según legislación local

5. **SEO** (solo Duda.co)
   - Los productos ya tienen Meta Title y Meta Description básicos
   - Personaliza para mejor posicionamiento

---

## 🔄 Actualizar Productos

### Si necesitas actualizar los productos:

1. **Extrae nuevamente** ejecutando:
   ```bash
   python3 scrapper-blonch.py
   ```

2. **Convierte a tu plataforma:**
   ```bash
   # Para WooCommerce
   python3 -c "from convertir_a_woocommerce import WooCommerceConverter; converter = WooCommerceConverter(); converter.convert_csv('bombas_bloch_productos.csv', 'bombas_bloch_woocommerce.csv')"
   
   # Para Duda.co
   python3 -c "from convertir_a_woocommerce import WooCommerceConverter; converter = WooCommerceConverter(); converter.convert_to_duda('bombas_bloch_productos.csv', 'bombas_bloch_duda.csv')"
   ```

3. **Importa el archivo actualizado**
   - Los productos existentes se actualizarán si el SKU coincide

---

## 💡 Tips y Mejores Prácticas

### WooCommerce:

- ✅ Usa un plugin de backup antes de importar
- ✅ Importa en una tienda de prueba primero
- ✅ Verifica que las imágenes se carguen correctamente
- ✅ Configura las dimensiones de imagen en Ajustes → Multimedia

### Duda.co:

- ✅ Verifica el límite de productos de tu plan
- ✅ Las imágenes externas deben estar accesibles públicamente
- ✅ Usa el preview antes de confirmar la importación
- ✅ Configura las variantes de producto si es necesario

---

## 🆘 Solución de Problemas

### "Las imágenes no cargan"
- Verifica que las URLs de imagen sean accesibles
- Algunas imágenes pueden requerir parámetros específicos
- Considera descargar y subir las imágenes manualmente

### "Los productos no se importan"
- Verifica que el formato CSV sea UTF-8 con BOM
- Asegúrate de que no haya caracteres especiales problemáticos
- Revisa que el archivo no esté corrupto

### "Faltan campos en la importación"
- Algunos campos son opcionales
- Puedes editar el CSV antes de importar para agregar información
- Los precios deben agregarse manualmente o en una segunda importación

---

## 📧 Soporte

Para problemas con:
- **El scraper**: Revisa el archivo scrapper-blonch.py
- **WooCommerce**: Consulta la documentación oficial de WooCommerce
- **Duda.co**: Visita https://support.duda.co/

---

**Última actualización:** 15 de Octubre, 2025  
**Versión:** 1.0  
**Productos extraídos:** 88 de 11 categorías principales

