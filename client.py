"""
Client - Discovers service instances from the registry and calls a random one.
Demonstrates client-side load balancing via random instance selection.
"""

import random
import time
import requests

REGISTRY_URL = "http://localhost:8500"
SERVICE_NAME = "order-service"


def discover_instances():
    resp = requests.get(f"{REGISTRY_URL}/discover/{SERVICE_NAME}")
    data = resp.json()
    return data["instances"]


def call_instance(instance):
    url = f"http://{instance['host']}:{instance['port']}/api/orders"
    resp = requests.get(url)
    return resp.json()


def main():
    print("=" * 60)
    print("  SERVICE DISCOVERY CLIENT")
    print("=" * 60)

    for i in range(1, 6):
        print(f"\n--- Request #{i} ---")

        # Step 1: Discover
        instances = discover_instances()
        if not instances:
            print("No instances available!")
            time.sleep(2)
            continue

        print(f"Discovered {len(instances)} instance(s):")
        for inst in instances:
            print(f"  - {inst['id']} @ {inst['host']}:{inst['port']}")

        # Step 2: Pick random instance
        chosen = random.choice(instances)
        print(f"Selected: {chosen['id']} (port {chosen['port']})")

        # Step 3: Call it
        result = call_instance(chosen)
        print(f"Response from {result['instance_id']}:")
        for order in result["orders"]:
            print(f"  Order #{order['id']}: {order['item']} (x{order['qty']}) - {order['status']}")

        time.sleep(1)

    print("\n" + "=" * 60)
    print("  DEMO COMPLETE - Client called random instances each time")
    print("=" * 60)


if __name__ == "__main__":
    main()
