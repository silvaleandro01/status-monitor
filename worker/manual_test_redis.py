"""Script manual pra testar redis_publisher.py. Descartável, não é o test suite final."""

import time
from datetime import datetime, timezone

from dotenv import load_dotenv

load_dotenv()

from redis_publisher import get_redis_client, publish_status_update, CHANNEL_NAME

client = get_redis_client()
print(f"1. Cliente Redis criado. Ping -> {client.ping()}\n")

pubsub = client.pubsub()
pubsub.subscribe(CHANNEL_NAME)
print(f"2. Inscrito no canal '{CHANNEL_NAME}'.\n")

# a primeira mensagem que chega é sempre a confirmação da inscrição, não dado de verdade
confirm = pubsub.get_message(timeout=2)
print(f"3. Mensagem de confirmação da inscrição -> {confirm}\n")

fake_result = {
    "status": "up",
    "status_code": 200,
    "response_time_ms": 87,
}
publish_status_update(client, service_id=1, result=fake_result, checked_at=datetime.now(timezone.utc))
print("4. publish_status_update() chamado.\n")

time.sleep(0.5)  # dá um tempinho pro Redis entregar a mensagem
message = pubsub.get_message(timeout=2)
print(f"5. Mensagem recebida pelo subscriber -> {message}\n")

pubsub.close()
print("Fim do teste.")
