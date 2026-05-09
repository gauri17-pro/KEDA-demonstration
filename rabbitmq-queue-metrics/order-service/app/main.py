import json
import os
import time
import uuid
from typing import List

import pika
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://demo:demo@localhost:5672/")
ORDERS_QUEUE = os.getenv("ORDERS_QUEUE", "orders")

app = FastAPI(title="order-service", version="0.1.0")


class OrderItem(BaseModel):
    sku: str
    qty: int = Field(ge=1, le=1000)


class CreateOrderBody(BaseModel):
    items: List[OrderItem] = Field(min_length=1, max_length=50)


ORDERS = {}


def _publish_order_message(message: dict) -> None:
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.queue_declare(queue=ORDERS_QUEUE, durable=True)
    body = json.dumps(message).encode("utf-8")
    channel.basic_publish(
        exchange="",
        routing_key=ORDERS_QUEUE,
        body=body,
        properties=pika.BasicProperties(delivery_mode=2),  # persistent
    )
    connection.close()


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/orders")
def create_order(body: CreateOrderBody):
    order_id = str(uuid.uuid4())
    now = int(time.time())
    order = {
        "id": order_id,
        "created_at": now,
        "items": [i.model_dump() for i in body.items],
        "status": "queued",
    }
    ORDERS[order_id] = order

    _publish_order_message({"order_id": order_id, "created_at": now, "items": order["items"]})
    return order


@app.post("/orders/bulk")
def create_orders_bulk(n: int = Query(100, ge=1, le=50000)):
    """
    Load-generator endpoint: enqueue N orders as fast as possible.
    Use this to make the RabbitMQ queue depth spike and watch KEDA scale the worker.
    """
    created = 0
    for _ in range(n):
        order_id = str(uuid.uuid4())
        now = int(time.time())
        order = {
            "id": order_id,
            "created_at": now,
            "items": [{"sku": "sku-1", "qty": 1}],
            "status": "queued",
        }
        ORDERS[order_id] = order
        _publish_order_message({"order_id": order_id, "created_at": now, "items": order["items"]})
        created += 1
    return {"enqueued": created, "queue": ORDERS_QUEUE}


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    return ORDERS.get(order_id) or {"error": "not_found", "id": order_id}

