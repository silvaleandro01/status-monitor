from dotenv import load_dotenv

load_dotenv()

import pytest

from database import get_connection


@pytest.fixture
def conn():
    connection = get_connection()
    yield connection
    connection.close()


@pytest.fixture
def test_service(conn):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO services (name, url) VALUES (%s, %s) RETURNING id",
            ("Serviço de Teste (pytest)", "https://pytest.exemplo.invalid"),
        )
        service_id = cur.fetchone()[0]
    conn.commit()

    yield service_id

    with conn.cursor() as cur:
        cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
    conn.commit()
