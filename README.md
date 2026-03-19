# Microservice Discovery System

A Python-based microservice discovery system demonstrating service registration, health checking, dynamic discovery, and client-side load balancing.

## Project Overview

This project implements a **Service Discovery** pattern where:
- Multiple service instances register themselves with a central registry
- A client discovers available instances at runtime
- The client performs client-side load balancing by calling a random instance

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    SERVICE DISCOVERY SYSTEM                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    1. Register        ┌──────────────────┐       │
│   │ Service  │ ───────────────────►  │                  │       │
│   │ Instance │    2. Heartbeat       │  SERVICE REGISTRY │       │
│   │ :8001    │ ───────────────────►  │     :8500        │       │
│   └──────────┘                       │                  │       │
│                                      │  Endpoints:      │       │
│   ┌──────────┐    1. Register        │  POST /register  │       │
│   │ Service  │ ───────────────────►  │  POST /heartbeat │       │
│   │ Instance │    2. Heartbeat       │  GET  /discover  │       │
│   │ :8002    │ ───────────────────►  │  POST /deregister│       │
│   └──────────┘                       │  GET  /services  │       │
│                                      └────────┬─────────┘       │
│                                               │                 │
│                                    3. Discover│                  │
│                                               │                 │
│                                      ┌────────▼─────────┐       │
│                                      │                  │       │
│                                      │     CLIENT       │       │
│                                      │                  │       │
│                                      │  1. GET /discover│       │
│                  4. Call random       │  2. Pick random  │       │
│   ┌──────────┐  ◄──────────────────  │  3. Call instance│       │
│   │ Instance │                       │                  │       │
│   │ :8001 or │  ──────────────────►  │                  │       │
│   │ :8002    │     5. Response       └──────────────────┘       │
│   └──────────┘                                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  FLOW:                                                          │
│  1. Service instances register with the registry on startup     │
│  2. Instances send heartbeats every 5s (stale after 15s)        │
│  3. Client queries registry to discover available instances     │
│  4. Client picks a random instance (client-side load balancing) │
│  5. Client calls the selected instance directly                 │
│  6. On shutdown, instances deregister gracefully                │
└─────────────────────────────────────────────────────────────────┘
```

## Demo Video

[Watch the Demo](https://drive.google.com/file/d/1AspZQG_Zo2DMpY0Rl3ogYu9Iu6dL3_Ce/view?usp=share_link)

## Components

| Component | File | Port | Description |
|-----------|------|------|-------------|
| **Service Registry** | `registry.py` | 8500 | Central registry with health checking. Stores registered instances and removes stale ones after 15s without a heartbeat. |
| **Service Instance** | `service.py` | 8001, 8002 | Order service that registers on startup, sends heartbeats every 5s, and deregisters on shutdown. |
| **Client** | `client.py` | — | Discovers instances from the registry and calls a random one each request (client-side load balancing). |
| **Demo Script** | `run_demo.sh` | — | Starts all components and runs the client automatically. |

## Requirements

- Python 3.7+
- Flask
- Requests

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full demo (starts registry, 2 services, and client)
bash run_demo.sh
```

## Manual Start (4 Terminals)

```bash
# Terminal 1 — Start the Service Registry
python3 registry.py

# Terminal 2 — Start Service Instance 1
python3 service.py 8001

# Terminal 3 — Start Service Instance 2
python3 service.py 8002

# Terminal 4 — Run the Client
python3 client.py
```

## How It Works

### 1. Service Registration
Each service instance starts up and sends a `POST /register` request to the registry with its instance ID, host, and port. The registry stores this information.

### 2. Health Checking (Heartbeats)
Every 5 seconds, each service instance sends a `POST /heartbeat` to the registry. If the registry does not receive a heartbeat within 15 seconds, it automatically removes the stale instance.

### 3. Service Discovery
The client sends a `GET /discover/order-service` request to the registry, which returns a list of all healthy registered instances.

### 4. Client-Side Load Balancing
The client picks a **random instance** from the discovered list and sends the API request directly to that instance. Each request may hit a different instance.

### 5. Graceful Shutdown
When a service instance receives SIGINT/SIGTERM, it sends a `POST /deregister` to the registry before exiting.

## API Endpoints

### Registry (`localhost:8500`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register a service instance |
| POST | `/heartbeat` | Send a heartbeat to keep registration alive |
| GET | `/discover/<service_name>` | Discover all instances of a service |
| GET | `/services` | List all registered services and instance counts |
| POST | `/deregister` | Remove a service instance from the registry |

### Service Instance (`localhost:8001` or `localhost:8002`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders` | Returns sample order data with the instance ID |
| GET | `/health` | Health check endpoint |

## Sample Output

```
=== Starting Service Registry on :8500 ===
=== Starting Service Instance 1 on :8001 ===
[SERVICE order-service-8001-a1b2c3] Registered
=== Starting Service Instance 2 on :8002 ===
[SERVICE order-service-8002-d4e5f6] Registered

=== Running Client ===
--- Request #1 ---
Discovered 2 instance(s):
  - order-service-8001-a1b2c3 @ localhost:8001
  - order-service-8002-d4e5f6 @ localhost:8002
Selected: order-service-8002-d4e5f6 (port 8002)
Response from order-service-8002-d4e5f6:
  Order #1: Laptop (x1) - shipped
  Order #2: Mouse (x2) - processing
  Order #3: Keyboard (x1) - delivered
```

## Service Mesh Discovery (Optional)

For production environments, a **service mesh** (Istio or Linkerd) replaces client-side discovery with proxy-based routing:

```
App ──► Sidecar Proxy ──► Service Mesh Control Plane
```

| Benefit | Description |
|---------|-------------|
| **Traffic Routing** | Canary deployments, blue-green releases, traffic splitting |
| **Observability** | Automatic metrics, distributed tracing, access logging |
| **Security** | Mutual TLS (mTLS) between services without code changes |
| **Resilience** | Retries, circuit breaking, timeouts handled by the proxy |

With a service mesh, applications call a virtual service name and the sidecar proxy handles instance selection, health checking, and load balancing transparently.

## Project Structure

```
microservice-discovery/
├── registry.py        # Service Registry (port 8500)
├── service.py         # Service Instance (ports 8001, 8002)
├── client.py          # Discovery Client
├── run_demo.sh        # Demo automation script
├── requirements.txt   # Python dependencies
├── architecture.md    # Detailed architecture diagram
└── README.md          # This file
```
