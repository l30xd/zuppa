#!/bin/bash
# ============================================================
# SETUP SCRIPT - Zuppa
# Configura el proyecto para ejecutarse localmente
# ============================================================

set -e  # Exit on error

echo "🚀 Zuppa - Setup Script"
echo "=========================="

# 1. Verificar .env
if [ ! -f ".env" ]; then
    echo "✅ Archivo .env ya existe"
else
    echo "❌ .env no existe. Asegúrate de crear uno desde .env.example"
fi

# 2. Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi
echo "✅ Docker encontrado"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi
echo "✅ Docker Compose encontrado"

# 3. Verificar modelos importados
if grep -q "from app.models.user import User" backend/app/models/__init__.py; then
    echo "✅ Modelos correctamente importados"
else
    echo "❌ Modelos no están importados en __init__.py"
fi

# 4. Verificar nginx-spa.conf
if [ -f "frontend/nginx-spa.conf" ]; then
    echo "✅ nginx-spa.conf existe"
else
    echo "❌ nginx-spa.conf no existe"
fi

# 5. Verificar package-lock.json
if [ -f "frontend/package-lock.json" ]; then
    echo "✅ package-lock.json existe"
else
    echo "❌ package-lock.json no existe"
fi

echo ""
echo "📋 CONFIGURACIÓN REQUERIDA EN .env:"
echo "  - DB_USER: zuppa"
echo "  - DB_PASSWORD: (contraseña segura)"
echo "  - SECRET_KEY: (mínimo 64 caracteres)"
echo "  - OPENROUTER_API_KEY: (tu API key de OpenRouter)"
echo ""
echo "🚀 Para levantar el proyecto:"
echo "  docker compose up --build"
echo ""
echo "✨ El proyecto estará disponible en:"
echo "  - Frontend: http://localhost"
echo "  - API: http://localhost/api"
echo "  - Swagger: http://localhost/api/docs"
