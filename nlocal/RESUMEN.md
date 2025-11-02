# Resumen del Proyecto Nlocal Scraper

## ✅ Proyecto Completado

Se ha creado un scraper automatizado para buscar información de organizaciones en nlocal.com.

## 📊 Archivos de Entrada

- **Archivo CSV**: `codigos.csv`
- **Total de DNIs**: 335 DNIs a buscar
- **Formato**: Separador coma (`,`)
- **Credenciales**: Configuradas en `config.py`

## 🎯 Funcionalidades Implementadas

### 1. Autenticación Automática
- ✅ Login automático en https://admin.nlocal.com/
- ✅ Credenciales configuradas: ignacio@captto.com
- ✅ Manejo de errores de autenticación

### 2. Búsqueda de Organizaciones
- ✅ Construcción automática de URLs de búsqueda por CIF
- ✅ Formato: `https://admin.nlocal.com/orgs/search?utf8=%E2%9C%93&search%5Bvalue%5D={dni}&search%5Boption%5D=cif&commit=Buscar`
- ✅ Detección de resultados encontrados vs no encontrados

### 3. Parseo de Información HTML
- ✅ Extracción automática de datos usando BeautifulSoup
- ✅ Campos extraídos:
  - Org ID
  - **Nombre de la organización** (extraído de `<h1 class="admin_menu_3">`)
  - Estado de la organización
  - CIF
  - Teléfono y Móvil
  - Dirección
  - Contacto (Nombre)
  - Email
  - Estado del usuario
  - Fechas (Completada, Última modificación, Último login)
  - Total de logins

### 4. Procesamiento de Archivos CSV
- ✅ Detección automática del delimitador (`;` o `,`)
- ✅ Lectura masiva de DNIs
- ✅ Pausa entre búsquedas para no sobrecargar el servidor

### 5. Exportación de Resultados
- ✅ **JSON**: Todos los resultados (exitosos y errores)
- ✅ **CSV**: Solo resultados exitosos con información completa
- ✅ **DNIs sin información**: Archivo CSV separado con DNIs que no encontraron datos
- ✅ Separador punto y coma para compatibilidad con Excel
- ✅ **Guardado incremental**: Los resultados se guardan en el CSV inmediatamente cuando se obtienen

## 📦 Dependencias

```bash
selenium>=4.15.0          # Automatización del navegador
beautifulsoup4>=4.12.0    # Parseo de HTML
webdriver-manager>=4.0.0  # Gestión de ChromeDriver
```

## 🚀 Cómo Ejecutar

### Instalación
```bash
cd nlocal
pip install -r requirements.txt
```

### Ejecución
```bash
python scraper_nlocal.py
```

### Nota Importante
⚠️ **Se requiere Google Chrome instalado** para que funcione Selenium.

## 📤 Archivos de Salida

Tras la ejecución se generarán:

1. **resultados_nlocal.json**: JSON con todos los resultados
2. **resultados_nlocal.csv**: CSV solo con resultados exitosos (con información completa)
3. **dnis_sin_informacion.csv**: CSV con DNIs que no encontraron información

## 🔍 Campos del CSV de Salida

```
dni;org_id;nombre_organizacion;estado_org;cif;telefono;movil;web;direccion;nombre_contacto;email;estado_usuario;completada;ultima_modificacion;ultimo_login;total_logins
```

## ⏱️ Tiempo Estimado

- **335 DNIs** × **~3-5 segundos por búsqueda** = **~17-28 minutos**
- Tiempo incluye: carga de página, parseo de datos, pausa entre búsquedas

## 🛡️ Consideraciones de Seguridad

- ✅ Credenciales en archivo separado (`config.py`)
- ✅ `config.py` agregado a `.gitignore`
- ✅ Script de ejemplo sin credenciales reales (`config_ejemplo.py`)

## 📋 Log de Ejecución

El script muestra información detallada:
- Progreso de búsquedas
- DNIs encontrados vs no encontrados
- Información resumida de cada resultado exitoso
- Estadísticas finales

## 🎓 Próximos Pasos Sugeridos

1. **Instalar Chrome** si no está disponible
2. **Ejecutar una prueba** con pocos DNIs primero
3. **Verificar resultados** en los archivos generados
4. **Procesar todos los DNIs** si la prueba es exitosa
5. **Analizar datos** en Excel/Google Sheets

## 📞 Soporte

Si encuentras problemas:
1. Verifica que Chrome esté instalado
2. Revisa las credenciales en `config.py`
3. Verifica la conexión a internet
4. Consulta los mensajes de error en la consola

---

**Proyecto creado**: Noviembre 2024  
**Estado**: ✅ Listo para usar
