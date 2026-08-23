"""Script manual pra testar database.py na mão. Não é o test suite final,
é só pra você ver cada função funcionando. Pode apagar depois."""

from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from database import (
    get_connection,
    get_active_services,
    save_check,
    get_last_check_status,
    open_incident,
    close_incident,
)

conn = get_connection()
print("1. Conexão aberta com sucesso.\n")

# Insere um serviço de teste direto (database.py não tem add_service —
# quem vai criar serviços de verdade é a API Node, não o worker).
with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO services (name, url)
        VALUES ('Teste Google', 'https://www.google.com')
        ON CONFLICT (url) DO NOTHING
        RETURNING id
        """
    )
    row = cur.fetchone()
conn.commit()

if row:
    service_id = row[0]
    print(f"2. Serviço de teste criado com id={service_id}\n")
else:
    # já existia de uma execução anterior deste script
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM services WHERE url = 'https://www.google.com'")
        service_id = cur.fetchone()[0]
    print(f"2. Serviço de teste já existia, id={service_id}\n")

services = get_active_services(conn)
print(f"3. get_active_services() -> {services}\n")

print(f"4. get_last_check_status() antes de qualquer check -> {get_last_check_status(conn, service_id)}\n")

fake_result_up = {
    "status": "up",
    "status_code": 200,
    "response_time_ms": 123,
    "error_message": None,
}
save_check(conn, service_id, fake_result_up)
print("5. save_check() com status 'up' -> gravado")
print(f"   get_last_check_status() agora -> {get_last_check_status(conn, service_id)}\n")

fake_result_down = {
    "status": "down",
    "status_code": None,
    "response_time_ms": 50,
    "error_message": "timeout simulado",
}
save_check(conn, service_id, fake_result_down)
print("6. save_check() com status 'down' -> gravado")
print(f"   get_last_check_status() agora -> {get_last_check_status(conn, service_id)}\n")

open_incident(conn, service_id, datetime.now(timezone.utc))
print("7. open_incident() chamado.")
with conn.cursor() as cur:
    cur.execute(
        "SELECT id, started_at, resolved_at FROM incidents WHERE service_id = %s ORDER BY id DESC LIMIT 1",
        (service_id,),
    )
    print(f"   Último incidente -> {cur.fetchone()}\n")

close_incident(conn, service_id, datetime.now(timezone.utc))
print("8. close_incident() chamado.")
with conn.cursor() as cur:
    cur.execute(
        "SELECT id, started_at, resolved_at FROM incidents WHERE service_id = %s ORDER BY id DESC LIMIT 1",
        (service_id,),
    )
    print(f"   Último incidente -> {cur.fetchone()}\n")

conn.close()
print("Conexão fechada. Fim do teste.")
