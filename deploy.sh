#!/bin/bash
# =============================================================
#  deploy.sh — Script de despliegue en VPS
#  Uso: bash deploy.sh tudominio.com tu@email.com
# =============================================================
set -e

DOMAIN="${1:?Falta dominio. Uso: bash deploy.sh tudominio.com tu@email.com}"
EMAIL="${2:?Falta email para Let's Encrypt.}"

echo "==> [1/6] Actualizando sistema..."
apt-get update -q && apt-get upgrade -y -q

echo "==> [2/6] Instalando Docker y Docker Compose..."
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
fi
if ! command -v docker compose &>/dev/null; then
    apt-get install -y docker-compose-plugin
fi

echo "==> [3/6] Copiando configuración..."
# Reemplaza el dominio en nginx
sed -i "s/tudominio.com/$DOMAIN/g" nginx/conf.d/app.conf

echo "==> [4/6] Creando .env desde .env.example..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales."
    echo "   Especialmente: DB_PASSWORD, SECRET_KEY, OPENROUTER_API_KEY"
    echo "   Luego vuelve a ejecutar este script."
    exit 0
fi

echo "==> [5/6] Obteniendo certificado SSL con Certbot..."
# Levanta solo nginx en modo HTTP primero
docker compose up -d nginx certbot
sleep 5

docker compose run --rm certbot certonly \
    --webroot \
    --webroot-path=/var/www/certbot \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "www.$DOMAIN"

echo "==> [6/6] Levantando todos los servicios..."
docker compose up -d --build

echo ""
echo "✅ Zuppa desplegado exitosamente en https://$DOMAIN"
echo "   API docs: https://$DOMAIN/docs"
