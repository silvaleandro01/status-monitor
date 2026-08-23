"""Faz a checagem HTTP de um serviço."""

import time

import requests


def check_service(url: str, timeout_seconds: float = 5.0) -> dict:
    """Faz uma requisição GET em `url` e retorna o resultado do check."""
    start = time.monotonic()

    try:
        response = requests.get(url, timeout=timeout_seconds)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        return {
            "status": "up" if response.status_code < 400 else "down",
            "status_code": response.status_code,
            "response_time_ms": elapsed_ms,
            "error_message": None,
        }

    except requests.exceptions.RequestException as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)

        return {
            "status": "down",
            "status_code": None,
            "response_time_ms": elapsed_ms,
            "error_message": str(e),
        }
