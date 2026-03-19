# Architecture Diagram

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
├─────────────────────────────────────────────────────────────────┤
│  OPTIONAL: SERVICE MESH (Istio/Linkerd)                         │
│                                                                 │
│  App ──► Sidecar Proxy ──► Service Mesh Control Plane           │
│                                                                 │
│  Benefits: traffic routing, mTLS, observability, retries        │
│  The mesh replaces client-side discovery with proxy-based       │
│  routing — apps call a virtual service name, the proxy          │
│  handles instance selection and health checking.                │
└─────────────────────────────────────────────────────────────────┘
```
