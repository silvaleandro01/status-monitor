"""Publica eventos de status no Redis para a API Node consumir."""

import json
import os

import redis

CHANNEL_NAME = "service_status_updates"


def get_redis_client():
    """Cria um cliente Redis usando as variáveis de ambiente."""
    return redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=int(os.getenv("REDIS_PORT")),
        decode_responses=True,
    )


def publish_status_update(redis_client, service_id: int, result: dict, checked_at) -> None:
    """Publica o evento de status no canal CHANNEL_NAME."""
    payload = {
        "service_id": service_id,
        "status": result["status"],
        "status_code": result["status_code"],
        "response_time_ms": result["response_time_ms"],
        "checked_at": checked_at.isoformat(),
    }
    redis_client.publish(CHANNEL_NAME, json.dumps(payload))
