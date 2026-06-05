-- ============================================================
--  Zuppa — Esquema de base de datos
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Usuarios
CREATE TABLE IF NOT EXISTS users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    username    VARCHAR(100) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Ingredientes del inventario por usuario
CREATE TABLE IF NOT EXISTS ingredients (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(150) NOT NULL,
    quantity    VARCHAR(100),           -- "2 kg", "1 litro", "al gusto"
    category    VARCHAR(80),            -- "proteína", "vegetal", "lácteo"...
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Historial de recetas generadas
CREATE TABLE IF NOT EXISTS recipe_history (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         VARCHAR(300) NOT NULL,
    ingredients_used TEXT[],            -- array de nombres usados
    preferences   JSONB,               -- {time, difficulty, diet}
    result        JSONB NOT NULL,       -- respuesta completa del LLM
    is_favorite   BOOLEAN DEFAULT FALSE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Índices de rendimiento
CREATE INDEX IF NOT EXISTS idx_ingredients_user  ON ingredients(user_id);
CREATE INDEX IF NOT EXISTS idx_history_user      ON recipe_history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_fav       ON recipe_history(user_id, is_favorite);
