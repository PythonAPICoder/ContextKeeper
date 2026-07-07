from __future__ import annotations

import time

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from ..config import Settings
from ..diagnostics.metrics import metrics_store


async def _check_ollama(settings: Settings) -> dict[str, object]:
    started = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.ollama.base_url.rstrip('/')}/api/version")
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        if response.status_code == 200:
            version = response.json().get("version", "unknown")
            return {"status": "online", "version": version, "latency_ms": latency_ms}
        return {"status": "warning", "version": None, "latency_ms": latency_ms, "detail": f"HTTP {response.status_code}"}
    except Exception as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return {"status": "offline", "version": None, "latency_ms": latency_ms, "detail": str(exc)}


def create_dashboard_router(settings: Settings) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health(request: Request) -> dict[str, object]:
        snapshot = metrics_store.snapshot()
        requests = snapshot["requests"]
        recent = requests.get("recent_requests", [])
        client_count = len({r.get("client_host") for r in recent if r.get("client_host")})
        last_model = requests.get("last_model")
        ollama_status = await _check_ollama(settings)
        client_status = "online" if client_count > 0 else "waiting"
        model_status = "active" if last_model else "waiting"
        return {
            "app": settings.app.name,
            "status": "running",
            "proxy_url": str(request.base_url).rstrip("/"),
            "ollama_base_url": settings.ollama.base_url,
            "connections": {
                "client": {"status": client_status, "count": client_count},
                "proxy": {"status": "online", "listen": f"{settings.server.host}:{settings.server.port}"},
                "ollama": ollama_status,
                "model": {"status": model_status, "name": last_model},
            },
        }

    @router.get("/metrics")
    async def metrics() -> dict[str, object]:
        return metrics_store.snapshot()

    @router.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        return f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{settings.dashboard.title}</title>
<style>
:root {{ --bg:#0f172a; --panel:#111827; --card:#1f2937; --text:#e5e7eb; --muted:#94a3b8; --good:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; --line:#334155; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Segoe UI, Arial, sans-serif; background:linear-gradient(135deg,#020617,#111827); color:var(--text); }}
header {{ padding:24px 32px; border-bottom:1px solid rgba(255,255,255,.08); }}
h1 {{ margin:0; font-size:28px; }}
.sub {{ color:var(--muted); margin-top:6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; padding:24px 32px; }}
.card {{ background:rgba(31,41,55,.86); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.25); }}
.card h2 {{ margin:0 0 12px; font-size:17px; }}
.value {{ font-size:30px; font-weight:700; }}
.muted {{ color:var(--muted); }}
.ok {{ color:var(--good); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.bar {{ height:12px; border-radius:999px; background:#334155; overflow:hidden; margin:10px 0; }}
.fill {{ height:100%; background:var(--accent); width:0%; transition:width .25s ease; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:8px; border-bottom:1px solid rgba(255,255,255,.08); }}
.flow {{ display:grid; grid-template-columns:1fr 56px 1fr 56px 1fr 56px 1fr; gap:10px; align-items:center; padding:24px 32px 0; }}
.node {{ background:rgba(31,41,55,.9); border:1px solid rgba(255,255,255,.1); border-radius:18px; padding:16px; min-height:112px; }}
.node-title {{ font-weight:800; font-size:16px; margin-bottom:10px; }}
.dot {{ display:inline-block; width:12px; height:12px; border-radius:99px; background:var(--warn); margin-right:8px; box-shadow:0 0 16px currentColor; }}
.dot.online {{ background:var(--good); color:var(--good); }} .dot.waiting {{ background:var(--warn); color:var(--warn); }} .dot.offline {{ background:var(--bad); color:var(--bad); }}
.pipe {{ height:4px; background:linear-gradient(90deg,var(--line),var(--accent),var(--line)); border-radius:99px; opacity:.7; }}
.small {{ font-size:12px; color:var(--muted); overflow-wrap:anywhere; }}
@media (max-width: 1000px) {{ .flow {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} }}
</style>
</head>
<body>
<header>
<h1>ContextKeeper</h1>
<div class="sub">Transparent Ollama Proxy • Diagnostics • System Monitor</div>
</header>

<section class="flow">
  <div class="node"><div class="node-title"><span id="clientDot" class="dot waiting"></span>Client</div><div id="clientText" class="value">Waiting</div><div id="clientSub" class="small">No clients seen yet</div></div>
  <div class="pipe"></div>
  <div class="node"><div class="node-title"><span id="proxyDot" class="dot online"></span>ContextKeeper Status</div><div class="value ok">Online</div><div id="proxySub" class="small">Listening on port {settings.server.port}</div></div>
  <div class="pipe"></div>
  <div class="node"><div class="node-title"><span id="ollamaDot" class="dot waiting"></span>Ollama Status</div><div id="ollamaText" class="value">Checking</div><div id="ollamaSub" class="small">{settings.ollama.base_url}</div></div>
  <div class="pipe"></div>
  <div class="node"><div class="node-title"><span id="modelDot" class="dot waiting"></span>Model</div><div id="modelText" class="value">Waiting</div><div id="modelSub" class="small">No active model yet</div></div>
</section>

<div class="grid">
  <div class="card"><h2>Status</h2><div class="value ok">Running</div><div class="muted">Proxy → {settings.ollama.base_url}</div></div>
  <div class="card"><h2>Request Statistics</h2><div id="req" class="value">0</div><div class="muted">Total requests</div></div>
  <div class="card"><h2>Errors</h2><div id="err" class="value">0</div><div class="muted">Total errors</div></div>
  <div class="card"><h2>CPU</h2><div id="cpu" class="value">--%</div><div class="bar"><div id="cpuBar" class="fill"></div></div></div>
  <div class="card"><h2>RAM</h2><div id="ram" class="value">--%</div><div id="ramText" class="muted"></div><div class="bar"><div id="ramBar" class="fill"></div></div></div>
  <div class="card"><h2>GPU / VRAM</h2><div id="gpu" class="value">--</div><div id="vramText" class="muted"></div><div class="bar"><div id="gpuBar" class="fill"></div></div></div>
  <div class="card"><h2>Context Usage</h2><div class="value">--</div><div class="muted">Context window usage will appear here.</div></div>
  <div class="card"><h2>Compression History</h2><div class="value">--</div><div class="muted">Compression events will appear here.</div></div>
</div>
<div class="grid">
  <div class="card" style="grid-column:1/-1"><h2>Live Activity</h2><table><thead><tr><th>Time</th><th>Client</th><th>Endpoint</th><th>Model</th><th>Status</th><th>Latency</th></tr></thead><tbody id="recent"></tbody></table></div>
</div>
<script>
function setDot(id, status) {{
  const el = document.getElementById(id);
  el.className = 'dot ' + (status === 'online' || status === 'active' ? 'online' : status === 'offline' ? 'offline' : 'waiting');
}}
async function refreshHealth() {{
  const res = await fetch('/health');
  const h = await res.json();
  const c = h.connections;
  setDot('clientDot', c.client.status);
  document.getElementById('clientText').textContent = c.client.count > 0 ? 'Connected' : 'Waiting';
  document.getElementById('clientSub').textContent = c.client.count + ' client(s) seen recently';
  setDot('proxyDot', c.proxy.status);
  document.getElementById('proxySub').textContent = 'Listening at ' + c.proxy.listen;
  setDot('ollamaDot', c.ollama.status);
  document.getElementById('ollamaText').textContent = c.ollama.status === 'online' ? 'Online' : c.ollama.status;
  document.getElementById('ollamaSub').textContent = h.ollama_base_url + (c.ollama.version ? ' • v' + c.ollama.version : '') + ' • ' + c.ollama.latency_ms + ' ms';
  setDot('modelDot', c.model.status);
  document.getElementById('modelText').textContent = c.model.name ? 'Active' : 'Waiting';
  document.getElementById('modelSub').textContent = c.model.name || 'No active model yet';
}}
async function refreshMetrics() {{
  const res = await fetch('/metrics');
  const data = await res.json();
  const r = data.requests;
  const s = data.system;
  document.getElementById('req').textContent = r.total_requests;
  document.getElementById('err').textContent = r.total_errors;
  document.getElementById('cpu').textContent = s.cpu_percent + '%';
  document.getElementById('cpuBar').style.width = s.cpu_percent + '%';
  document.getElementById('ram').textContent = s.ram_percent + '%';
  document.getElementById('ramText').textContent = s.ram_used_gb + ' / ' + s.ram_total_gb + ' GB';
  document.getElementById('ramBar').style.width = s.ram_percent + '%';
  if (s.gpu) {{
    document.getElementById('gpu').textContent = s.gpu.gpu_percent + '%';
    document.getElementById('vramText').textContent = s.gpu.name + ' • ' + s.gpu.vram_used_gb + ' / ' + s.gpu.vram_total_gb + ' GB VRAM • ' + s.gpu.temperature_c + '°C';
    document.getElementById('gpuBar').style.width = s.gpu.gpu_percent + '%';
  }} else {{ document.getElementById('gpu').textContent = 'N/A'; document.getElementById('vramText').textContent = 'nvidia-smi not available'; }}
  document.getElementById('recent').innerHTML = r.recent_requests.map(x => `<tr><td>${{new Date(x.timestamp).toLocaleTimeString()}}</td><td>${{x.client_host||''}}</td><td>${{x.endpoint}}</td><td>${{x.model||''}}</td><td>${{x.status_code}}</td><td>${{x.latency_ms}} ms</td></tr>`).join('');
}}
async function refresh() {{ await Promise.all([refreshHealth(), refreshMetrics()]); }}
refresh(); setInterval(refresh, 2000);
</script>
</body>
</html>
"""

    return router
