"""Acesso ao Postgres: services, checks e incidents."""

import os

import psycopg2
import psycopg2.extras


def get_connection():
    """Abre uma conexão com o Postgres usando as variáveis de ambiente."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def get_active_services(conn) -> list[dict]:
    """Retorna todos os serviços com is_active = true."""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT id, name, url FROM services WHERE is_active = true")
        return cur.fetchall()


def save_check(conn, service_id: int, result: dict) -> None:
    """Insere uma linha em `checks` a partir do resultado de check_service()."""
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO checks (service_id, status, status_code, response_time_ms, error_message)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                service_id,
                result["status"],
                result["status_code"],
                result["response_time_ms"],
                result["error_message"],
            ),
        )
    conn.commit()


def get_last_check_status(conn, service_id: int) -> str | None:
    """Retorna o status do check mais recente deste serviço, ou None se não há nenhum."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT status FROM checks
            WHERE service_id = %s
            ORDER BY checked_at DESC
            LIMIT 1
            """,
            (service_id,),
        )
        row = cur.fetchone()
        return row[0] if row else None


def open_incident(conn, service_id: int, started_at) -> None:
    """Cria um incidente aberto (resolved_at NULL) para este serviço."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO incidents (service_id, started_at) VALUES (%s, %s)",
            (service_id, started_at),
        )
    conn.commit()


def close_incident(conn, service_id: int, resolved_at) -> None:
    """Fecha o incidente aberto mais recente deste serviço."""
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE incidents
            SET resolved_at = %s
            WHERE id = (
                SELECT id FROM incidents
                WHERE service_id = %s AND resolved_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1
            )
            """,
            (resolved_at, service_id),
        )
    conn.commit()
