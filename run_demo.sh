#!/bin/bash
# Demo script - runs registry, 2 service instances, then the client.
# Usage: bash run_demo.sh

set -e

cleanup() {
    echo ""
    echo "Shutting down all services..."
    kill $REGISTRY_PID $SVC1_PID $SVC2_PID 2>/dev/null
    wait $REGISTRY_PID $SVC1_PID $SVC2_PID 2>/dev/null
    echo "All services stopped."
}
trap cleanup EXIT

echo "=== Starting Service Registry on :8500 ==="
python3 registry.py &
REGISTRY_PID=$!
sleep 2

echo ""
echo "=== Starting Service Instance 1 on :8001 ==="
python3 service.py 8001 &
SVC1_PID=$!
sleep 1

echo ""
echo "=== Starting Service Instance 2 on :8002 ==="
python3 service.py 8002 &
SVC2_PID=$!
sleep 2

echo ""
echo "=== Running Client ==="
python3 client.py

echo ""
echo "Demo finished. Press Ctrl+C to stop all services."
wait
