# Status Monitor

Serviço de monitoramento de disponibilidade (estilo UptimeRobot/Instatus, simplificado): checa a saúde de URLs periodicamente, guarda histórico de uptime/incidentes e transmite o status ao vivo via WebSocket.

Projeto de estudo com um objetivo deliberado: usar Python e Node.js em papéis genuinamente diferentes, não como duas implementações paralelas da mesma coisa.

## Arquitetura

```
┌──────────────┐        ┌────────────┐        ┌──────────────────┐
│   worker     │──────▶ │  Postgres  │ ◀───── │       api         │
│  (Python)    │        │ (histórico)│        │ (Node/Express)    │
│              │        └────────────┘        │  REST + WebSocket │
│ checa URLs   │                               └────────┬──────────┘
│ a cada N seg │        ┌────────────┐                  │
└──────┬───────┘──────▶ │   Redis    │─────────────────▶│
       publica          │ (pub/sub)  │   assina e retransmite
                         └────────────┘   ao vivo pro WebSocket
```

- **worker (Python)** — loop que lê os serviços ativos no Postgres, faz o check HTTP de cada um, grava o resultado (`checks`) e abre/fecha incidentes (`incidents`) conforme o status muda, e publica cada evento no Redis.
- **api (Node.js)** — REST para CRUD de serviços monitorados e histórico de checks; um servidor WebSocket assina o canal Redis que o worker publica e retransmite cada evento em tempo real para os clientes conectados.
- **Postgres** — histórico de checks e incidentes.
- **Redis** — ponte pub/sub entre worker e api (não é cache).

## Rodando

Requer Docker e Docker Compose.

```bash
cp .env.example .env
docker compose up -d --build
```

Isso sobe os 4 serviços: `postgres`, `redis`, `worker`, `api`. A API fica em `http://localhost:3000`.

```bash
docker compose logs -f worker   # acompanhar os ciclos de checagem
docker compose logs -f api      # acompanhar a API
docker compose down             # parar tudo
```

## API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/services` | Lista os serviços monitorados |
| `POST` | `/api/services` | Cria um novo serviço (`{ "name", "url" }`) |
| `GET` | `/api/services/:id/checks` | Histórico dos últimos 50 checks de um serviço |
| `WS` | `/` | Conexão WebSocket — recebe cada evento de status ao vivo |

Exemplo de evento recebido via WebSocket (mesmo payload publicado pelo worker no Redis):
```json
{
  "service_id": 1,
  "status": "up",
  "status_code": 200,
  "response_time_ms": 143,
  "checked_at": "2026-08-23T21:45:14.310321+00:00"
}
```

## Schema

```sql
services   (id, name, url, check_interval_seconds, is_active, created_at)
checks     (id, service_id, status, status_code, response_time_ms, error_message, checked_at)
incidents  (id, service_id, started_at, resolved_at, cause)
```

`incidents` é derivado de `checks`: o worker abre um incidente quando o status vira `down` vindo de `up` (ou nenhum check anterior), e fecha quando volta a `up`.

## Stack

Python · psycopg2 · Node.js · Express · `ws` · PostgreSQL · Redis · Docker · Docker Compose
