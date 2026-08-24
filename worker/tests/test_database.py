from datetime import datetime, timezone

from database import (
    close_incident,
    get_active_services,
    get_last_check_status,
    open_incident,
    save_check,
)


def test_get_active_services_includes_test_service(conn, test_service):
    services = get_active_services(conn)
    ids = [s["id"] for s in services]
    assert test_service in ids


def test_save_check_and_get_last_status(conn, test_service):
    assert get_last_check_status(conn, test_service) is None

    save_check(
        conn,
        test_service,
        {"status": "up", "status_code": 200, "response_time_ms": 100, "error_message": None},
    )
    assert get_last_check_status(conn, test_service) == "up"

    save_check(
        conn,
        test_service,
        {"status": "down", "status_code": None, "response_time_ms": 50, "error_message": "timeout"},
    )
    assert get_last_check_status(conn, test_service) == "down"


def test_open_and_close_incident(conn, test_service):
    started = datetime.now(timezone.utc)
    open_incident(conn, test_service, started)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT resolved_at FROM incidents WHERE service_id = %s ORDER BY id DESC LIMIT 1",
            (test_service,),
        )
        assert cur.fetchone()[0] is None

    resolved = datetime.now(timezone.utc)
    close_incident(conn, test_service, resolved)

    with conn.cursor() as cur:
        cur.execute(
            "SELECT resolved_at FROM incidents WHERE service_id = %s ORDER BY id DESC LIMIT 1",
            (test_service,),
        )
        assert cur.fetchone()[0] is not None
