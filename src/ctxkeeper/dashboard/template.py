from __future__ import annotations

from ..config import Settings


def render_dashboard_html(settings: Settings) -> str:
    return f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{settings.dashboard.title}</title>
<style>
:root {{ --bg:#090e1a; --sidebar:#0d1424; --panel:#111827; --card:#182132; --card-strong:#1f2937; --text:#e5e7eb; --muted:#94a3b8; --soft:#cbd5e1; --good:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; --accent-2:#818cf8; --line:#2d3a4f; --shadow:0 14px 34px rgba(0,0,0,.24); }}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; font-family:Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--text); }}
a {{ color:inherit; text-decoration:none; }}
.app-shell {{ min-height:100vh; display:grid; grid-template-columns:260px minmax(0,1fr); background:linear-gradient(135deg,#080d18,#0f172a 52%,#101827); }}
.sidebar {{ position:sticky; top:0; height:100vh; display:flex; flex-direction:column; gap:28px; padding:22px 18px; background:rgba(13,20,36,.96); border-right:1px solid rgba(255,255,255,.08); }}
.brand {{ display:flex; align-items:center; gap:12px; padding:6px 6px 14px; border-bottom:1px solid rgba(255,255,255,.08); }}
.brand-mark {{ display:grid; place-items:center; width:38px; height:38px; border-radius:10px; background:linear-gradient(135deg,var(--accent),var(--accent-2)); color:#020617; font-weight:900; }}
.brand-name {{ font-weight:800; }}
.brand-sub {{ color:var(--muted); font-size:12px; margin-top:2px; }}
.nav {{ display:grid; gap:6px; }}
.nav a {{ display:flex; align-items:center; gap:10px; min-height:38px; padding:8px 10px; border-radius:8px; color:var(--soft); font-size:14px; }}
.nav a:hover {{ background:rgba(148,163,184,.12); color:var(--text); }}
.nav-kicker {{ color:var(--muted); font-size:11px; text-transform:uppercase; font-weight:800; letter-spacing:.08em; margin:4px 10px; }}
.sidebar-footer {{ margin-top:auto; color:var(--muted); font-size:12px; line-height:1.5; padding:12px 10px; border-top:1px solid rgba(255,255,255,.08); }}
.workspace {{ min-width:0; }}
.topbar {{ position:sticky; top:0; z-index:5; display:flex; justify-content:space-between; align-items:center; gap:18px; padding:18px 28px; background:rgba(9,14,26,.88); backdrop-filter:blur(18px); border-bottom:1px solid rgba(255,255,255,.08); }}
.topbar-actions {{ display:flex; flex-wrap:wrap; justify-content:flex-end; gap:10px; color:var(--muted); font-size:13px; }}
.topbar-pill {{ display:inline-flex; align-items:center; min-height:30px; padding:5px 10px; border:1px solid rgba(255,255,255,.1); border-radius:999px; background:rgba(15,23,42,.62); }}
.dashboard-main {{ display:grid; gap:18px; padding:24px 28px 32px; }}
h1 {{ margin:0; font-size:28px; }}
.sub {{ color:var(--muted); margin-top:6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
.card {{ background:rgba(24,33,50,.92); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:16px; box-shadow:var(--shadow); transition:border-color .18s ease, transform .18s ease, background .18s ease; }}
.card:hover,.node:hover {{ border-color:rgba(56,189,248,.24); transform:translateY(-1px); }}
.card h2 {{ margin:0 0 10px; font-size:15px; }}
.ops {{ display:grid; grid-template-columns:repeat(3,minmax(180px,1fr)); gap:14px; }}
.command-center {{ display:grid; grid-template-columns:minmax(280px,.95fr) minmax(320px,1.4fr) repeat(2,minmax(220px,1fr)); gap:14px; align-items:stretch; }}
.command-brief {{ display:flex; flex-direction:column; justify-content:space-between; min-height:210px; padding:20px; border:1px solid rgba(255,255,255,.08); border-radius:12px; background:linear-gradient(145deg,rgba(17,24,39,.96),rgba(30,41,59,.82)); box-shadow:var(--shadow); }}
.command-kicker {{ color:var(--accent); font-size:12px; font-weight:900; text-transform:uppercase; letter-spacing:.12em; }}
.command-title {{ margin:12px 0 8px; font-size:30px; line-height:1.08; font-weight:850; }}
.command-text {{ color:var(--muted); line-height:1.5; }}
.command-meta {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }}
.signal-card {{ min-height:210px; display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.signal-card h2,.signal-node .node-title {{ color:var(--soft); font-size:13px; text-transform:uppercase; letter-spacing:.08em; }}
.signal-card .value,.signal-node .value {{ font-size:38px; line-height:1; }}
.signal-body {{ display:grid; grid-template-columns:minmax(0,1fr) 112px; gap:14px; align-items:center; }}
.signal-stack {{ display:grid; gap:8px; min-width:0; }}
.gauge {{ width:112px; height:112px; transform:rotate(-90deg); }}
.gauge-track {{ fill:none; stroke:rgba(148,163,184,.18); stroke-width:10; }}
.gauge-progress {{ fill:none; stroke:var(--accent); stroke-width:10; stroke-linecap:round; stroke-dasharray:100; stroke-dashoffset:100; transition:stroke-dashoffset .55s ease, stroke .25s ease; }}
.health-card.healthy .gauge-progress {{ stroke:var(--good); }} .health-card.busy .gauge-progress {{ stroke:var(--accent); }} .health-card.warning .gauge-progress {{ stroke:var(--warn); }} .health-card.critical .gauge-progress,.health-card.offline .gauge-progress {{ stroke:var(--bad); }}
.mini-chart {{ width:100%; height:48px; margin-top:10px; }}
.sparkline {{ fill:none; stroke:var(--accent); stroke-width:2.5; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 8px rgba(56,189,248,.28)); transition:points .3s ease; }}
.spark-area {{ fill:rgba(56,189,248,.08); }}
.value-pop {{ animation:valuePop .28s ease; }}
@keyframes valuePop {{ 0% {{ transform:translateY(0); color:var(--text); }} 45% {{ transform:translateY(-1px); color:#ffffff; }} 100% {{ transform:translateY(0); color:inherit; }} }}
.icon-label {{ display:inline-flex; align-items:center; gap:8px; }}
.icon-mark {{ color:var(--accent); font-size:14px; }}
.compact-signals .card {{ min-height:118px; }}
.health-card {{ border-left:5px solid var(--accent); }}
.health-card.healthy {{ border-left-color:var(--good); }} .health-card.busy {{ border-left-color:var(--accent); }} .health-card.warning {{ border-left-color:var(--warn); }} .health-card.critical,.health-card.offline {{ border-left-color:var(--bad); }}
.health-title {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.badge {{ display:inline-flex; align-items:center; min-height:24px; padding:3px 8px; border-radius:999px; font-size:12px; font-weight:700; text-transform:uppercase; background:rgba(148,163,184,.16); color:var(--muted); }}
.badge.positive,.badge.healthy,.badge.low {{ color:var(--good); background:rgba(34,197,94,.12); }} .badge.info,.badge.busy {{ color:var(--accent); background:rgba(56,189,248,.12); }} .badge.warning,.badge.medium {{ color:var(--warn); background:rgba(245,158,11,.12); }} .badge.critical,.badge.high,.badge.offline {{ color:var(--bad); background:rgba(239,68,68,.12); }}
.panel-list {{ display:grid; gap:8px; }}
.panel-item {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:9px 10px; transition:border-color .18s ease, background .18s ease; }}
.panel-item:hover,.timeline-item:hover,.message:hover {{ border-color:rgba(129,140,248,.24); background:rgba(15,23,42,.68); }}
.timeline-list {{ display:grid; gap:8px; }}
.timeline-item {{ display:grid; grid-template-columns:86px 1fr; gap:10px; align-items:start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:9px 10px; transition:border-color .18s ease, background .18s ease; }}
.panel-list > .muted,.timeline-list > .muted,#activeRecentMessages > .muted {{ min-height:76px; display:grid; place-items:center; border:1px dashed rgba(148,163,184,.28); border-radius:8px; background:rgba(15,23,42,.32); }}
.activity-card {{ overflow:auto; }}
.activity-card tbody:empty::after {{ content:"No request activity yet."; display:block; padding:18px; color:var(--muted); }}
.risk-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
.value {{ font-size:28px; font-weight:750; }}
.muted {{ color:var(--muted); }}
.ok {{ color:var(--good); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.bar {{ height:12px; border-radius:999px; background:#334155; overflow:hidden; margin:10px 0; }}
.fill {{ height:100%; background:var(--accent); width:0%; transition:width .25s ease; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:7px 8px; border-bottom:1px solid rgba(255,255,255,.08); }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }}
.flow {{ display:grid; grid-template-columns:1fr 56px 1fr 56px 1fr; gap:10px; align-items:center; }}
.node {{ background:rgba(24,33,50,.92); border:1px solid rgba(255,255,255,.1); border-radius:10px; padding:16px; min-height:112px; box-shadow:var(--shadow); transition:border-color .18s ease, transform .18s ease, background .18s ease; }}
.signal-node {{ min-height:210px; display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.node-title {{ font-weight:800; font-size:16px; margin-bottom:10px; }}
.dot {{ display:inline-block; width:12px; height:12px; border-radius:99px; background:var(--warn); margin-right:8px; box-shadow:0 0 16px currentColor; }}
.dot {{ animation:statusPulse 2s ease-in-out infinite; }}
.dot.online {{ background:var(--good); color:var(--good); }} .dot.waiting {{ background:var(--warn); color:var(--warn); }} .dot.offline {{ background:var(--bad); color:var(--bad); }}
@keyframes statusPulse {{ 0%,100% {{ opacity:.72; }} 50% {{ opacity:1; }} }}
.pipe {{ height:4px; background:linear-gradient(90deg,var(--line),var(--accent),var(--line)); border-radius:99px; opacity:.7; }}
.small {{ font-size:12px; color:var(--muted); overflow-wrap:anywhere; }}
.conversation-meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:14px; }}
.summary {{ background:rgba(15,23,42,.62); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:12px; white-space:pre-wrap; }}
.messages {{ display:grid; gap:10px; margin-top:12px; }}
.message {{ background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:10px 12px; }}
.message-role {{ color:var(--accent); font-size:12px; font-weight:700; text-transform:uppercase; }}
.message-content {{ margin-top:4px; white-space:pre-wrap; }}
@media (max-width: 1180px) {{ .command-center {{ grid-template-columns:1fr 1fr; }} }}
@media (max-width: 1000px) {{ .app-shell {{ grid-template-columns:1fr; }} .sidebar {{ position:relative; height:auto; gap:14px; }} .nav {{ grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); }} .sidebar-footer {{ display:none; }} .topbar {{ position:relative; align-items:flex-start; flex-direction:column; }} .dashboard-main {{ padding:18px; }} .command-center,.flow,.ops {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} .timeline-item {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="app-shell">
<aside class="sidebar">
  <div class="brand">
    <div class="brand-mark">CK</div>
    <div><div class="brand-name">ContextKeeper</div><div class="brand-sub">Local operations console</div></div>
  </div>
  <nav class="nav" aria-label="Dashboard sections">
    <div class="nav-kicker">Monitor</div>
    <a href="#overview">Overview</a>
    <a href="#connections">Connections</a>
    <a href="#resources">Resources</a>
    <a href="#intelligence">Intelligence</a>
    <a href="#conversation">Conversation</a>
    <a href="#activity">Activity</a>
  </nav>
  <div class="sidebar-footer">Browser-based admin UI served locally by ContextKeeper.</div>
</aside>
<div class="workspace">
<header class="topbar">
  <div>
<h1>ContextKeeper</h1>
<div class="sub">Transparent Ollama Proxy • Diagnostics • System Monitor</div>
  </div>
  <div class="topbar-actions">
    <span class="topbar-pill">Proxy port {settings.server.port}</span>
    <span class="topbar-pill">{settings.ollama.base_url}</span>
  </div>
</header>
<main class="dashboard-main">

<section id="overview" class="command-center">
  <div class="command-brief">
    <div>
      <div class="command-kicker">Mission Control</div>
      <div class="command-title">Local AI traffic under watch.</div>
      <div class="command-text">Monitor proxy health, Ollama reachability, context pressure, and live request flow from one console.</div>
    </div>
    <div class="command-meta">
      <span class="badge info">Local</span>
      <span class="badge busy">Live refresh</span>
    </div>
  </div>
  <div id="systemHealthCard" class="card health-card signal-card">
    <div class="health-title"><h2><span class="icon-label"><span class="icon-mark">◆</span>System Health</span></h2><span id="systemHealthBadge" class="badge">Checking</span></div>
    <div class="signal-body">
      <div class="signal-stack">
        <div id="systemHealthStatus" class="value">--</div>
        <div id="systemHealthMessage" class="muted">Dashboard intelligence is loading.</div>
      </div>
      <svg class="gauge" viewBox="0 0 120 120" aria-hidden="true">
        <circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle>
        <circle id="healthGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle>
      </svg>
    </div>
  </div>
  <div class="card signal-card"><h2><span class="icon-label"><span class="icon-mark">◉</span>Context Usage</span></h2><div class="signal-body"><div class="signal-stack"><div id="contextUsage" class="value">--%</div><div id="contextUsageText" class="muted">Context window usage will appear here.</div><div class="bar"><div id="contextUsageBar" class="fill"></div></div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="contextGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div></div>
  <div class="card signal-card"><h2><span class="icon-label"><span class="icon-mark">↗</span>Request Statistics</span></h2><div id="req" class="value">0</div><div class="muted">Total requests</div><svg class="mini-chart" viewBox="0 0 220 48" preserveAspectRatio="none" aria-hidden="true"><polygon id="requestSparkArea" class="spark-area" points="0,48 220,48"></polygon><polyline id="requestSparkline" class="sparkline" points="0,40 44,40 88,40 132,40 176,40 220,40"></polyline></svg></div>
  <div class="node signal-node"><div class="node-title"><span id="ollamaDot" class="dot waiting"></span>Ollama Status</div><div id="ollamaText" class="value">Checking</div><div id="ollamaSub" class="small">{settings.ollama.base_url}</div></div>
</section>

<section class="ops compact-signals">
  <div class="card"><h2><span class="icon-label"><span class="icon-mark">⇄</span>Request Trend</span></h2><div id="requestTrend" class="value">Flat</div><div id="requestTrendText" class="muted">Awaiting request data.</div></div>
  <div class="card"><h2><span class="icon-label"><span class="icon-mark">⧉</span>Average Rate</span></h2><div id="requestRate" class="value">0</div><div class="muted">requests / min</div></div>
  <div class="card"><h2><span class="icon-label"><span class="icon-mark">◷</span>Average Latency</span></h2><div class="signal-body"><div><div id="averageLatency" class="value">0 ms</div><div class="muted">recent requests</div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="latencyGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div></div>
</section>

<section id="connections" class="flow">
  <div class="node"><div class="node-title"><span id="clientDot" class="dot waiting"></span>Client</div><div id="clientText" class="value">Waiting</div><div id="clientSub" class="small">No clients seen yet</div></div>
  <div class="pipe"></div>
  <div class="node"><div class="node-title"><span id="proxyDot" class="dot online"></span>ContextKeeper Status</div><div class="value ok">Online</div><div id="proxySub" class="small">Listening on port {settings.server.port}</div></div>
  <div class="pipe"></div>
  <div class="node"><div class="node-title"><span id="modelDot" class="dot waiting"></span>Model</div><div id="modelText" class="value">Waiting</div><div id="modelSub" class="small">No active model yet</div></div>
</section>

<div id="activity" class="card activity-card"><h2><span class="icon-label"><span class="icon-mark">▦</span>Live Activity</span></h2><table><thead><tr><th>Time</th><th>Client</th><th>Endpoint</th><th>Model</th><th>Status</th><th>Latency</th></tr></thead><tbody id="recent"></tbody></table></div>

<div id="resources" class="grid">
  <div class="card"><h2>Status</h2><div class="value ok">Running</div><div class="muted">Proxy → {settings.ollama.base_url}</div></div>
  <div class="card"><h2>Errors</h2><div id="err" class="value">0</div><div class="muted">Total errors</div></div>
  <div class="card"><h2>CPU</h2><div id="cpu" class="value">--%</div><div class="bar"><div id="cpuBar" class="fill"></div></div></div>
  <div class="card"><h2>RAM</h2><div id="ram" class="value">--%</div><div id="ramText" class="muted"></div><div class="bar"><div id="ramBar" class="fill"></div></div></div>
  <div class="card"><h2>GPU / VRAM</h2><div id="gpu" class="value">--</div><div id="vramText" class="muted"></div><div class="bar"><div id="gpuBar" class="fill"></div></div></div>
  <div class="card"><h2>Compression History</h2><div id="compressionCount" class="value">0</div><div id="compressionText" class="muted">Compression events will appear here.</div></div>
</div>
<div id="intelligence" class="grid">
  <div class="card"><h2>Insights</h2><div id="insightsList" class="panel-list"><div class="muted">No insights yet.</div></div></div>
  <div class="card"><h2>Recommendations</h2><div id="recommendationsList" class="panel-list"><div class="muted">No recommendations yet.</div></div></div>
  <div class="card"><h2>Activity Timeline</h2><div id="timelineList" class="timeline-list"><div class="muted">No recent activity.</div></div></div>
  <div id="conversation" class="card" style="grid-column:1/-1">
    <h2>Active Conversation</h2>
    <div class="conversation-meta">
      <div><div class="small">Conversation ID</div><div id="activeConversationId" class="muted">None</div></div>
      <div><div class="small">Model</div><div id="activeModelName" class="muted">None</div></div>
      <div><div class="small">Context Usage</div><div id="activeContextUsage" class="muted">--</div></div>
      <div><div class="small">Risk</div><div id="conversationRisk" class="muted">--</div></div>
    </div>
    <div id="conversationRiskIndicators" class="risk-row"></div>
    <div class="small">Rolling Summary</div>
    <div id="activeRollingSummary" class="summary muted">No rolling summary available.</div>
    <div class="small" style="margin-top:14px">Recent Messages</div>
    <div id="activeRecentMessages" class="messages"><div class="muted">No recent messages.</div></div>
  </div>
</div>
</main>
</div>
</div>
<script>
const DASHBOARD_REFRESH_INTERVAL_MS = {settings.dashboard.refresh_interval_ms or 1000};
function escapeHtml(value) {{
  return String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
}}
function setDot(id, status) {{
  const el = document.getElementById(id);
  el.className = 'dot ' + (status === 'online' || status === 'active' ? 'online' : status === 'offline' ? 'offline' : 'waiting');
}}
function safeClass(value) {{
  return String(value || '').toLowerCase().replace(/[^a-z0-9_-]/g, '');
}}
function titleCase(value) {{
  return String(value || '').replace(/_/g, ' ').replace(/(^|\\s)([a-z])/g, match => match.toUpperCase());
}}
function setText(id, value) {{
  const el = document.getElementById(id);
  if (!el) return;
  const next = String(value);
  if (el.textContent !== next) {{
    el.textContent = next;
    el.classList.remove('value-pop');
    void el.offsetWidth;
    el.classList.add('value-pop');
  }}
}}
function setGauge(id, value) {{
  const el = document.getElementById(id);
  if (!el) return;
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  el.style.strokeDashoffset = 100 - clamped;
}}
function healthGaugeValue(status) {{
  return ({{healthy: 100, busy: 76, warning: 48, critical: 20, offline: 4}})[status] ?? 0;
}}
function latencyGaugeValue(latencyMs) {{
  const latency = Math.max(0, Number(latencyMs) || 0);
  return Math.max(0, 100 - Math.min(100, latency / 50));
}}
function renderSparkline(requests) {{
  const line = document.getElementById('requestSparkline');
  const area = document.getElementById('requestSparkArea');
  if (!line || !area) return;
  const values = (requests || []).slice(0, 18).reverse().map(item => Number(item.latency_ms)).filter(value => Number.isFinite(value));
  const series = values.length ? values : [0, 0, 0, 0, 0, 0];
  const max = Math.max(...series, 1);
  const width = 220;
  const height = 48;
  const points = series.map((value, index) => {{
    const x = series.length === 1 ? width : (index / (series.length - 1)) * width;
    const y = height - 6 - ((value / max) * (height - 12));
    return `${{x.toFixed(1)}},${{y.toFixed(1)}}`;
  }}).join(' ');
  line.setAttribute('points', points);
  area.setAttribute('points', `0,48 ${{points}} 220,48`);
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
  setText('req', r.total_requests);
  setText('err', r.total_errors);
  setText('cpu', s.cpu_percent + '%');
  document.getElementById('cpuBar').style.width = s.cpu_percent + '%';
  setText('ram', s.ram_percent + '%');
  document.getElementById('ramText').textContent = s.ram_used_gb + ' / ' + s.ram_total_gb + ' GB';
  document.getElementById('ramBar').style.width = s.ram_percent + '%';
  if (s.gpu) {{
    setText('gpu', s.gpu.gpu_percent + '%');
    document.getElementById('vramText').textContent = s.gpu.name + ' • ' + s.gpu.vram_used_gb + ' / ' + s.gpu.vram_total_gb + ' GB VRAM • ' + s.gpu.temperature_c + '°C';
    document.getElementById('gpuBar').style.width = s.gpu.gpu_percent + '%';
  }} else {{ setText('gpu', 'N/A'); document.getElementById('vramText').textContent = 'nvidia-smi not available'; }}
  renderSparkline(r.recent_requests);
  document.getElementById('recent').innerHTML = r.recent_requests.map(x => `<tr><td>${{new Date(x.timestamp).toLocaleTimeString()}}</td><td>${{x.client_host||''}}</td><td>${{x.endpoint}}</td><td>${{x.model||''}}</td><td>${{x.status_code}}</td><td>${{x.latency_ms}} ms</td></tr>`).join('');
}}
async function refreshDashboardData() {{
  const res = await fetch('/dashboard/data');
  const data = await res.json();
  const context = data.context;
  const compression = data.compression;
  const intelligence = data.intelligence || {{}};
  setText('contextUsage', context.usage_percent + '%');
  document.getElementById('contextUsageText').textContent = context.estimated_tokens + ' estimated tokens across ' + context.conversation_count + ' conversation(s)';
  document.getElementById('contextUsageBar').style.width = Math.min(context.usage_percent, 100) + '%';
  setGauge('contextGaugeArc', context.usage_percent);
  document.getElementById('compressionCount').textContent = compression.count;
  document.getElementById('compressionText').textContent = compression.history.length + ' recent compression event(s)';
  refreshIntelligence(intelligence);
  refreshActiveConversation(data.active_conversation, intelligence.conversation_risk);
}}
function refreshIntelligence(intelligence) {{
  const health = intelligence.health || {{}};
  const status = health.status || 'unknown';
  const healthCard = document.getElementById('systemHealthCard');
  healthCard.className = 'card health-card signal-card ' + safeClass(status);
  document.getElementById('systemHealthBadge').className = 'badge ' + safeClass(status);
  document.getElementById('systemHealthBadge').textContent = status;
  setText('systemHealthStatus', titleCase(status));
  document.getElementById('systemHealthMessage').textContent = health.message || 'Dashboard health evaluated.';
  setGauge('healthGaugeArc', healthGaugeValue(status));

  const trends = intelligence.trends || {{}};
  const direction = trends.request_direction || 'flat';
  setText('requestTrend', titleCase(direction));
  document.getElementById('requestTrendText').textContent = direction === 'up' ? 'Latency rising across recent requests.' : direction === 'down' ? 'Latency improving across recent requests.' : 'Latency trend is stable.';
  setText('requestRate', trends.average_request_rate ?? 0);
  setText('averageLatency', (trends.average_latency_ms ?? 0) + ' ms');
  setGauge('latencyGaugeArc', latencyGaugeValue(trends.average_latency_ms));

  renderPanelList('insightsList', intelligence.insights || [], 'severity', 'No insights yet.');
  renderPanelList('recommendationsList', intelligence.recommendations || [], 'priority', 'No recommendations yet.');
  renderTimeline(intelligence.timeline || []);
}}
function renderPanelList(id, items, badgeField, emptyText) {{
  const el = document.getElementById(id);
  el.innerHTML = items.length
    ? items.map(item => `<div class="panel-item"><span>${{escapeHtml(item.message)}}</span><span class="badge ${{safeClass(item[badgeField])}}">${{escapeHtml(item[badgeField])}}</span></div>`).join('')
    : `<div class="muted">${{escapeHtml(emptyText)}}</div>`;
}}
function renderTimeline(events) {{
  const el = document.getElementById('timelineList');
  el.innerHTML = events.length
    ? events.map(event => `<div class="timeline-item"><div class="small">${{escapeHtml(new Date(event.timestamp).toLocaleTimeString())}}</div><div>${{escapeHtml(event.message)}}</div></div>`).join('')
    : '<div class="muted">No recent activity.</div>';
}}
function refreshActiveConversation(active, risk) {{
  document.getElementById('activeConversationId').textContent = active.conversation_id || 'None';
  document.getElementById('activeModelName').textContent = active.model_name || 'None';
  if (active.context) {{
    document.getElementById('activeContextUsage').textContent = active.context.usage_percent + '% (' + active.context.estimated_tokens + ' / ' + active.context.context_window_tokens + ' tokens)';
  }} else {{
    document.getElementById('activeContextUsage').textContent = '--';
  }}
  refreshConversationRisk(risk);
  document.getElementById('activeRollingSummary').textContent = active.rolling_summary || 'No rolling summary available.';
  const messages = active.recent_messages || [];
  document.getElementById('activeRecentMessages').innerHTML = messages.length
    ? messages.map(message => `<div class="message"><div class="message-role">${{escapeHtml(message.role)}}</div><div class="message-content">${{escapeHtml(message.content)}}</div><div class="small">${{escapeHtml(new Date(message.timestamp).toLocaleTimeString())}}</div></div>`).join('')
    : '<div class="muted">No recent messages.</div>';
}}
function refreshConversationRisk(risk) {{
  const current = risk || {{}};
  document.getElementById('conversationRisk').textContent = current.message || 'No active conversation.';
  const indicators = current.indicators || [];
  document.getElementById('conversationRiskIndicators').innerHTML = indicators.length
    ? indicators.map(indicator => `<span class="badge ${{safeClass(indicator.severity)}}">${{escapeHtml(indicator.label)}}</span>`).join('')
    : '<span class="badge">No indicators</span>';
}}
async function refresh() {{ await Promise.all([refreshHealth(), refreshMetrics(), refreshDashboardData()]); }}
refresh(); setInterval(refresh, DASHBOARD_REFRESH_INTERVAL_MS);
</script>
</body>
</html>
"""
