"""Loop principal do worker: checa serviços, grava histórico, publica eventos."""

import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv

from checker import check_service
from database import (
    get_connection,
    get_active_services,
    save_check,
    get_last_check_status,
    open_incident,
    close_incident,
)
from redis_publisher import get_redis_client, publish_status_update


def run_check_cycle(conn, redis_client) -> None:
    """Executa um ciclo: checa todos os serviços ativos e processa cada resultado."""
    services = get_active_services(conn)
    up_count = 0
    down_count = 0

    for service in services:
        try:
            previous_status = get_last_check_status(conn, service["id"])
            result = check_service(service["url"])
            checked_at = datetime.now(timezone.utc)

            save_check(conn, service["id"], result)

            if result["status"] == "down" and previous_status != "down":
                open_incident(conn, service["id"], checked_at)
            elif result["status"] == "up" and previous_status == "down":
                close_incident(conn, service["id"], checked_at)

            publish_status_update(redis_client, service["id"], result, checked_at)

            if result["status"] == "up":
                up_count += 1
            else:
                down_count += 1

        except Exception as e:
            print(f"  [ERRO] Falha ao checar '{service['name']}': {e}")

    print(f"Ciclo concluído: {len(services)} serviços checados ({up_count} up, {down_count} down)")


def run() -> None:
    """Loop infinito: abre as conexões uma vez e roda um ciclo a cada N segundos."""
    conn = get_connection()
    redis_client = get_redis_client()
    interval = int(os.getenv("CHECK_LOOP_INTERVAL_SECONDS"))

    print(f"Worker iniciado. Intervalo entre ciclos: {interval}s")

    while True:
        run_check_cycle(conn, redis_client)
        time.sleep(interval)


if __name__ == "__main__":
    load_dotenv()
    run()
