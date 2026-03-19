"""
Microservice instance - Registers itself with the registry and sends heartbeats.
Run multiple instances on different ports.
"""

import sys
import uuid
import threading
import time
import signal
import requests
from flask import Flask, jsonify

REGISTRY_URL = "http://localhost:8500"
SERVICE_NAME = "order-service"


def create_app(port, instance_id):
    app = Flask(__name__)

    @app.route("/api/orders", methods=["GET"])
    def get_orders():
        return jsonify({
            "instance_id": instance_id,
            "port": port,
            "orders": [
                {"id": 1, "item": "Laptop", "qty": 1, "status": "shipped"},
                {"id": 2, "item": "Mouse", "qty": 2, "status": "processing"},
                {"id": 3, "item": "Keyboard", "qty": 1, "status": "delivered"},
            ],
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy", "instance_id": instance_id, "port": port})

    return app


def register(instance_id, port):
    resp = requests.post(f"{REGISTRY_URL}/register", json={
        "service_name": SERVICE_NAME,
        "instance_id": instance_id,
        "host": "localhost",
        "port": port,
    })
    print(f"[SERVICE {instance_id}] Registered: {resp.json()}")


def heartbeat_loop(instance_id, port):
    while True:
        time.sleep(5)
        try:
            requests.post(f"{REGISTRY_URL}/heartbeat", json={
                "service_name": SERVICE_NAME,
                "instance_id": instance_id,
            })
        except Exception:
            print(f"[SERVICE {instance_id}] Failed to send heartbeat")


def deregister(instance_id):
    try:
        requests.post(f"{REGISTRY_URL}/deregister", json={
            "service_name": SERVICE_NAME,
            "instance_id": instance_id,
        })
        print(f"[SERVICE {instance_id}] Deregistered")
    except Exception:
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    instance_id = f"{SERVICE_NAME}-{port}-{uuid.uuid4().hex[:6]}"

    # Register with registry
    register(instance_id, port)

    # Start heartbeat thread
    hb = threading.Thread(target=heartbeat_loop, args=(instance_id, port), daemon=True)
    hb.start()

    # Graceful shutdown
    def shutdown_handler(sig, frame):
        print(f"\n[SERVICE {instance_id}] Shutting down...")
        deregister(instance_id)
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    app = create_app(port, instance_id)
    print(f"[SERVICE {instance_id}] Running on port {port}")
    app.run(host="0.0.0.0", port=port)
