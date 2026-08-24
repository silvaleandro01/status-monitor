import time
from datetime import datetime, timezone

from redis_publisher import CHANNEL_NAME, get_redis_client, publish_status_update


def test_publish_status_update_reaches_subscriber():
    client = get_redis_client()
    pubsub = client.pubsub()
    pubsub.subscribe(CHANNEL_NAME)
    pubsub.get_message(timeout=2)  # descarta a confirmação da inscrição

    publish_status_update(
        client,
        service_id=999999,
        result={"status": "up", "status_code": 200, "response_time_ms": 42, "error_message": None},
        checked_at=datetime.now(timezone.utc),
    )

    time.sleep(0.3)
    message = pubsub.get_message(timeout=2)

    assert message is not None
    assert message["type"] == "message"
    assert '"service_id": 999999' in message["data"]

    pubsub.close()
