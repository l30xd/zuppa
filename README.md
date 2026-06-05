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