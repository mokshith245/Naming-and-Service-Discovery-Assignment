"""Generate architecture diagram as PDF."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis("off")

# Title
ax.text(7, 9.5, "Microservice Discovery System — Architecture",
        ha="center", va="center", fontsize=18, fontweight="bold", color="#1a1a2e")

# Colors
REG_COLOR = "#4361ee"
SVC_COLOR = "#2ec4b6"
CLI_COLOR = "#e07a5f"
MESH_COLOR = "#8338ec"
BOX_ALPHA = 0.15
BORDER_WIDTH = 2

def draw_box(x, y, w, h, color, label, sublabel="", fontsize=13):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                         facecolor=color, alpha=BOX_ALPHA, edgecolor=color, linewidth=BORDER_WIDTH)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2 + (0.15 if sublabel else 0), label,
            ha="center", va="center", fontsize=fontsize, fontweight="bold", color=color)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.25, sublabel,
                ha="center", va="center", fontsize=9, color="#555555", style="italic")

def draw_arrow(x1, y1, x2, y2, color, label="", curve=0.0):
    style = f"arc3,rad={curve}" if curve else "arc3,rad=0.0"
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                            arrowstyle="-|>", color=color, linewidth=2,
                            mutation_scale=18, connectionstyle=style)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        offset_y = 0.2 if curve >= 0 else -0.2
        ax.text(mx, my + offset_y, label, ha="center", va="center",
                fontsize=9, color=color, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.15", facecolor="white", edgecolor="none", alpha=0.9))

# --- Service Registry ---
draw_box(5, 6.5, 4, 1.8, REG_COLOR, "Service Registry", "localhost:8500")

# Registry endpoints
endpoints = ["POST /register", "POST /heartbeat", "GET  /discover/<name>",
             "POST /deregister", "GET  /services"]
for i, ep in enumerate(endpoints):
    ax.text(10.5, 8.0 - i * 0.3, ep, ha="left", va="center", fontsize=8,
            fontfamily="monospace", color="#333333")
ax.text(10.5, 8.3, "Endpoints:", ha="left", va="center", fontsize=9,
        fontweight="bold", color=REG_COLOR)

# --- Service Instance 1 ---
draw_box(0.5, 6.5, 3.2, 1.8, SVC_COLOR, "Service Instance 1", "localhost:8001")

# --- Service Instance 2 ---
draw_box(0.5, 4.2, 3.2, 1.8, SVC_COLOR, "Service Instance 2", "localhost:8002")

# --- Client ---
draw_box(5, 2.5, 4, 1.5, CLI_COLOR, "Client", "client.py")

# --- Arrows: Services → Registry ---
draw_arrow(3.7, 7.8, 5.0, 7.8, SVC_COLOR, "1. Register", curve=0.0)
draw_arrow(3.7, 7.2, 5.0, 7.2, SVC_COLOR, "2. Heartbeat (5s)", curve=0.0)

draw_arrow(3.7, 5.5, 5.0, 7.0, SVC_COLOR, "1. Register", curve=-0.15)
draw_arrow(3.7, 4.9, 5.0, 6.7, SVC_COLOR, "2. Heartbeat (5s)", curve=-0.15)

# --- Arrow: Registry → Client (Discover) ---
draw_arrow(7.0, 6.5, 7.0, 4.0, REG_COLOR, "3. Discover instances")

# --- Arrow: Client → Service (Call) ---
draw_arrow(5.0, 3.2, 2.1, 4.2, CLI_COLOR, "4. Call random instance", curve=0.2)

# --- Arrow: Service → Client (Response) ---
draw_arrow(2.1, 4.5, 5.0, 3.6, "#888888", "5. Response", curve=0.2)

# --- Flow Summary Box ---
flow_box = FancyBboxPatch((0.3, 0.3), 9.0, 1.8, boxstyle="round,pad=0.2",
                          facecolor="#f0f0f0", edgecolor="#cccccc", linewidth=1)
ax.add_patch(flow_box)
ax.text(0.6, 1.85, "Flow Summary", fontsize=11, fontweight="bold", color="#333333")
steps = [
    "1. Service instances register with the registry on startup",
    "2. Instances send heartbeats every 5s (removed after 15s timeout)",
    "3. Client queries registry to discover available instances",
    "4. Client picks a random instance (client-side load balancing)",
    "5. Client calls the selected instance and receives a response",
]
for i, step in enumerate(steps):
    ax.text(0.8, 1.55 - i * 0.25, step, fontsize=8.5, color="#444444")

# --- Service Mesh Box (Optional) ---
mesh_box = FancyBboxPatch((9.8, 0.3), 3.9, 4.0, boxstyle="round,pad=0.2",
                          facecolor=MESH_COLOR, alpha=0.06, edgecolor=MESH_COLOR, linewidth=1.5)
ax.add_patch(mesh_box)
ax.text(11.75, 4.0, "Optional: Service Mesh", ha="center", fontsize=11,
        fontweight="bold", color=MESH_COLOR)
ax.text(11.75, 3.6, "(Istio / Linkerd)", ha="center", fontsize=9, color=MESH_COLOR, style="italic")

mesh_items = [
    ("Traffic Routing", "canary, blue-green deploys"),
    ("Observability", "metrics, tracing, logging"),
    ("Security", "mTLS between services"),
    ("Resilience", "retries, circuit breaking"),
]
for i, (title, desc) in enumerate(mesh_items):
    y = 3.1 - i * 0.55
    ax.text(10.2, y, f"• {title}", fontsize=9, fontweight="bold", color=MESH_COLOR)
    ax.text(10.5, y - 0.22, desc, fontsize=8, color="#666666")

ax.text(11.75, 0.6, "App → Sidecar Proxy → Mesh", ha="center",
        fontsize=9, fontfamily="monospace", color=MESH_COLOR,
        bbox=dict(boxstyle="round,pad=0.2", facecolor=MESH_COLOR, alpha=0.08, edgecolor=MESH_COLOR))

# Legend
legend_items = [
    (SVC_COLOR, "Service Instance"),
    (REG_COLOR, "Service Registry"),
    (CLI_COLOR, "Client"),
    (MESH_COLOR, "Service Mesh (Optional)"),
]
for i, (color, label) in enumerate(legend_items):
    ax.plot(10.2 + (i % 2) * 2, 9.2 - (i // 2) * 0.35, "s", color=color, markersize=8)
    ax.text(10.45 + (i % 2) * 2, 9.2 - (i // 2) * 0.35, label, fontsize=8, va="center", color="#333333")

plt.tight_layout()
plt.savefig("architecture_diagram.pdf", format="pdf", dpi=150, bbox_inches="tight")
plt.savefig("architecture_diagram.png", format="png", dpi=150, bbox_inches="tight")
print("Generated: architecture_diagram.pdf and architecture_diagram.png")
