#!/bin/bash
# Script de configuración inicial para el scraper de nlocal

echo "🚀 Configurando el scraper de nlocal..."
echo ""

# Verificar si existe config.py
if [ ! -f "config.py" ]; then
    echo "📝 Creando config.py desde config_ejemplo.py..."
    cp config_ejemplo.py config.py
    echo "✅ Archivo config.py creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita config.py con tus credenciales reales"
else
    echo "✅ config.py ya existe"
fi

# Verificar si existe venv
if [ ! -d "venv" ]; then
    echo "🐍 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual e instalar dependencias
echo "📦 Instalando dependencias..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "✅ Configuración completada!"
echo ""
echo "Para ejecutar el scraper:"
echo "  1. Activa el entorno virtual: source venv/bin/activate"
echo "  2. Edita config.py con tus credenciales"
echo "  3. Coloca los DNIs en codigos.csv"
echo "  4. Ejecuta: python scraper_nlocal.py"
echo ""
