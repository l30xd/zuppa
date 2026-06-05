# Zuppa 🌿

Aplicación web fullstack que permite a los usuarios registrar sus ingredientes disponibles
y obtener recetas generadas por IA mediante OpenRouter.

## Stack

| Capa | Tecnología |
|------|------------|
| Backend | Python 3.12 + FastAPI + Uvicorn |
| Base de datos | PostgreSQL 16 (async con SQLAlchemy 2.0) |
| LLM | OpenRouter (GPT-4o-mini / Mistral / etc.) |
| Frontend | React 18 + Vite + React Router |
| Proxy / SSL | Nginx + Let's Encrypt (Certbot) |
| Contenedores | Docker + Docker Compose |

## Estructura del proyecto

```
zuppa/
├── backend/
│   ├── app/
│   │   ├── core/          # config, database, security (JWT)
│   │   ├── models/        # SQLAlchemy ORM
│   │   ├── schemas/       # Pydantic v2
│   │   ├── services/      # llm_service (OpenRouter)
│   │   ├── routers/       # auth, ingredients, recipes
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # RecipeCard
│   │   ├── pages/         # Login, Register, Dashboard, History
│   │   ├── hooks/         # useAuth (Context)
│   │   └── services/      # api.js (Axios)
│   ├── Dockerfile
│   └── vite.config.js
├── nginx/
│   ├── nginx.conf
│   └── conf.d/app.conf    # SSL + reverse proxy
├── scripts/
│   └── init.sql           # Esquema PostgreSQL
├── docker-compose.yml
├── .env.example
└── deploy.sh
```

## Desarrollo local

### 1. Clonar y configurar variables

```bash
cp .env.example .env
# Editar .env con tus valores (mínimo: OPENROUTER_API_KEY)
```

### 2. Levantar con Docker Compose

```bash
docker compose up --build
```

La app estará en `http://localhost` (Nginx redirige automáticamente).
- Frontend: `http://localhost`
- API: `http://localhost/api`
- Swagger: `http://localhost/docs`

### 3. Desarrollo frontend sin Docker

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
# Vite proxea /api → http://backend:8000 (ajusta en vite.config.js si usas localhost)
```

### 4. Desarrollo backend sin Docker

```bash
cd backend
pip install -r requirements.txt
# Necesitas PostgreSQL corriendo localmente
uvicorn app.main:app --reload
```

## Despliegue en VPS (producción)

### Requisitos del servidor
- Ubuntu 22.04+ con IP pública
- Dominio apuntando a esa IP (registro A en tu DNS)
- Puertos 80 y 443 abiertos

### Pasos

```bash
# 1. Clonar el proyecto en el VPS
git clone <tu-repo> zuppa && cd zuppa

# 2. Ejecutar script de deploy
bash deploy.sh tudominio.com tu@email.com

# El script instala Docker, obtiene SSL y levanta todo
```

### Comandos útiles en producción

```bash
# Ver logs
docker compose logs -f backend

# Reiniciar un servicio
docker compose restart backend

# Actualizar tras cambios
git pull && docker compose up --build -d

# Backup de base de datos
docker compose exec db pg_dump -U $DB_USER $DB_NAME > backup_$(date +%F).sql
```

## Endpoints de la API

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register` | Registrar usuario |
| POST | `/api/auth/login` | Login (devuelve JWT) |
| GET | `/api/auth/me` | Perfil del usuario actual |

### Ingredientes
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/ingredients/` | Listar inventario |
| POST | `/api/ingredients/` | Agregar ingrediente |
| POST | `/api/ingredients/bulk` | Agregar varios a la vez |
| PATCH | `/api/ingredients/{id}` | Actualizar cantidad/categoría |
| DELETE | `/api/ingredients/{id}` | Eliminar ingrediente |
| DELETE | `/api/ingredients/` | Vaciar inventario |

### Recetas
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/recipes/generate` | Generar recetas con LLM |
| GET | `/api/recipes/history` | Ver historial |
| PATCH | `/api/recipes/history/{id}/favorite` | Marcar como favorito |
| DELETE | `/api/recipes/history/{id}` | Eliminar del historial |

## Modelos LLM disponibles en OpenRouter (gratuitos o baratos)

| Modelo | ID para .env | Notas |
|--------|-------------|-------|
| GPT-4o mini | `openai/gpt-4o-mini` | Rápido y preciso |
| Mistral 7B | `mistralai/mistral-7b-instruct` | Gratis |
| Llama 3 8B | `meta-llama/llama-3-8b-instruct` | Gratis |
| Gemma 2 9B | `google/gemma-2-9b-it` | Gratis |
