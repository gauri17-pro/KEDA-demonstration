import json
import os
import random
import time

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://demo:demo@localhost:5672/")
ORDERS_QUEUE = os.getenv("ORDERS_QUEUE", "orders")
WORKER_SLEEP_MS = int(os.getenv("WORKER_SLEEP_MS", "250"))


def main() -> None:
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=ORDERS_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=10)

            print(f"[worker] connected; consuming queue={ORDERS_QUEUE}")

            def on_message(ch, method, properties, body: bytes):
                msg = json.loads(body.decode("utf-8"))
                # simulate variable work time so scaling is visible
                time.sleep((WORKER_SLEEP_MS + random.randint(0, WORKER_SLEEP_MS)) / 1000.0)
                print(f"[worker] processed order_id={msg.get('order_id')}")
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_consume(queue=ORDERS_QUEUE, on_message_callback=on_message)
            channel.start_consuming()
        except Exception as e:
            print(f"[worker] error: {e} (retrying in 2s)")
            time.sleep(2)


if __name__ == "__main__":
    main()

