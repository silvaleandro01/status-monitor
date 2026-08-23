-- Schema combinado na sessão de planejamento. Rode isso manualmente no
-- Postgres (psql, DBeaver, etc) antes de rodar o worker.

CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    check_interval_seconds INTEGER NOT NULL DEFAULT 60,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE checks (
    id BIGSERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    status VARCHAR(10) NOT NULL,        -- 'up' | 'down'
    status_code INTEGER,
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_checks_service_id_checked_at ON checks(service_id, checked_at DESC);

CREATE TABLE incidents (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL,
    resolved_at TIMESTAMPTZ,
    cause TEXT
);
