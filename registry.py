"""
Service Registry - Central registry where services register and clients discover them.
Supports health checks with automatic deregistration of unhealthy instances.
"""

from flask import Flask, jsonify, request
import threading
import time
import requests

app = Flask(__name__)

# {service_name: [{id, host, port, registered_at, last_heartbeat}]}
registry = {}
lock = threading.Lock()

HEARTBEAT_TIMEOUT = 15  # seconds


@app.route("/register", methods=["POST"])
def register():
    data = request.json
    service_name = data["service_name"]
    instance = {
        "id": data["instance_id"],
        "host": data["host"],
        "port": data["port"],
        "registered_at": time.time(),
        "last_heartbeat": time.time(),
    }
    with lock:
        if service_name not in registry:
            registry[service_name] = []
        # Update if exists, else add
        existing = [i for i in registry[service_name] if i["id"] == instance["id"]]
        if existing:
            existing[0].update(instance)
        else:
            registry[service_name].append(instance)
    print(f"[REGISTRY] Registered {instance['id']} for '{service_name}' at {instance['host']}:{instance['port']}")
    return jsonify({"status": "registered", "instance_id": instance["id"]})


@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    data = request.json
    service_name = data["service_name"]
    instance_id = data["instance_id"]
    with lock:
        instances = registry.get(service_name, [])
        for inst in instances:
            if inst["id"] == instance_id:
                inst["last_heartbeat"] = time.time()
                return jsonify({"status": "ok"})
    return jsonify({"status": "not_found"}), 404


@app.route("/discover/<service_name>", methods=["GET"])
def discover(service_name):
    with lock:
        instances = registry.get(service_name, [])
        result = [{"id": i["id"], "host": i["host"], "port": i["port"]} for i in instances]
    return jsonify({"service": service_name, "instances": result})


@app.route("/services", methods=["GET"])
def list_services():
    with lock:
        summary = {name: len(instances) for name, instances in registry.items()}
    return jsonify(summary)


@app.route("/deregister", methods=["POST"])
def deregister():
    data = request.json
    service_name = data["service_name"]
    instance_id = data["instance_id"]
    with lock:
        if service_name in registry:
            registry[service_name] = [i for i in registry[service_name] if i["id"] != instance_id]
            if not registry[service_name]:
                del registry[service_name]
    print(f"[REGISTRY] Deregistered {instance_id} from '{service_name}'")
    return jsonify({"status": "deregistered"})


def health_checker():
    """Remove instances that haven't sent a heartbeat within the timeout."""
    while True:
        time.sleep(5)
        now = time.time()
        with lock:
            for service_name in list(registry.keys()):
                before = len(registry[service_name])
                registry[service_name] = [
                    i for i in registry[service_name]
                    if now - i["last_heartbeat"] < HEARTBEAT_TIMEOUT
                ]
                removed = before - len(registry[service_name])
                if removed:
                    print(f"[REGISTRY] Removed {removed} stale instance(s) from '{service_name}'")
                if not registry[service_name]:
                    del registry[service_name]


if __name__ == "__main__":
    checker = threading.Thread(target=health_checker, daemon=True)
    checker.start()
    print("[REGISTRY] Service Registry running on port 8500")
    app.run(host="0.0.0.0", port=8500)
