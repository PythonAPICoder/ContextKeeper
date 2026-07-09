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
:root {{ --bg:#0f172a; --panel:#111827; --card:#1f2937; --text:#e5e7eb; --muted:#94a3b8; --good:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; --line:#334155; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Segoe UI, Arial, sans-serif; background:linear-gradient(135deg,#020617,#111827); color:var(--text); }}
header {{ padding:24px 32px; border-bottom:1px solid rgba(255,255,255,.08); }}
h1 {{ margin:0; font-size:28px; }}
.sub {{ color:var(--muted); margin-top:6px; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(260px,1fr)); gap:16px; padding:24px 32px; }}
.card {{ background:rgba(31,41,55,.86); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:18px; box-shadow:0 10px 30px rgba(0,0,0,.25); }}
.card h2 {{ margin:0 0 12px; font-size:17px; }}
.ops {{ display:grid; grid-template-columns:minmax(320px,1.3fr) repeat(3,minmax(180px,1fr)); gap:16px; padding:24px 32px 0; }}
.health-card {{ border-left:5px solid var(--accent); }}
.health-card.healthy {{ border-left-color:var(--good); }} .health-card.busy {{ border-left-color:var(--accent); }} .health-card.warning {{ border-left-color:var(--warn); }} .health-card.critical,.health-card.offline {{ border-left-color:var(--bad); }}
.health-title {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.badge {{ display:inline-flex; align-items:center; min-height:24px; padding:3px 8px; border-radius:999px; font-size:12px; font-weight:700; text-transform:uppercase; background:rgba(148,163,184,.16); color:var(--muted); }}
.badge.positive,.badge.healthy,.badge.low {{ color:var(--good); background:rgba(34,197,94,.12); }} .badge.info,.badge.busy {{ color:var(--accent); background:rgba(56,189,248,.12); }} .badge.warning,.badge.medium {{ color:var(--warn); background:rgba(245,158,11,.12); }} .badge.critical,.badge.high,.badge.offline {{ color:var(--bad); background:rgba(239,68,68,.12); }}
.panel-list {{ display:grid; gap:10px; }}
.panel-item {{ display:flex; justify-content:space-between; gap:12px; align-items:flex-start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:10px 12px; }}
.timeline-list {{ display:grid; gap:10px; }}
.timeline-item {{ display:grid; grid-template-columns:92px 1fr; gap:10px; align-items:start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:10px 12px; }}
.risk-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
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
.conversation-meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:14px; }}
.summary {{ background:rgba(15,23,42,.62); border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:12px; white-space:pre-wrap; }}
.messages {{ display:grid; gap:10px; margin-top:12px; }}
.message {{ background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:12px; padding:10px 12px; }}
.message-role {{ color:var(--accent); font-size:12px; font-weight:700; text-transform:uppercase; }}
.message-content {{ margin-top:4px; white-space:pre-wrap; }}
@media (max-width: 1000px) {{ .flow,.ops {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} .timeline-item {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<header>
<h1>ContextKeeper</h1>
<div class="sub">Transparent Ollama Proxy • Diagnostics • System Monitor</div>
</header>

<section class="ops">
  <div id="systemHealthCard" class="card health-card">
    <div class="health-title"><h2>System Health</h2><span id="systemHealthBadge" class="badge">Checking</span></div>
    <div id="systemHealthStatus" class="value">--</div>
    <div id="systemHealthMessage" class="muted">Dashboard intelligence is loading.</div>
  </div>
  <div class="card"><h2>Request Trend</h2><div id="requestTrend" class="value">Flat</div><div id="requestTrendText" class="muted">Awaiting request data.</div></div>
  <div class="card"><h2>Average Rate</h2><div id="requestRate" class="value">0</div><div class="muted">requests / min</div></div>
  <div class="card"><h2>Average Latency</h2><div id="averageLatency" class="value">0 ms</div><div class="muted">recent requests</div></div>
</section>

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
  <div class="card"><h2>Context Usage</h2><div id="contextUsage" class="value">--%</div><div id="contextUsageText" class="muted">Context window usage will appear here.</div><div class="bar"><div id="contextUsageBar" class="fill"></div></div></div>
  <div class="card"><h2>Compression History</h2><div id="compressionCount" class="value">0</div><div id="compressionText" class="muted">Compression events will appear here.</div></div>
</div>
<div class="grid">
  <div class="card"><h2>Insights</h2><div id="insightsList" class="panel-list"><div class="muted">No insights yet.</div></div></div>
  <div class="card"><h2>Recommendations</h2><div id="recommendationsList" class="panel-list"><div class="muted">No recommendations yet.</div></div></div>
  <div class="card"><h2>Activity Timeline</h2><div id="timelineList" class="timeline-list"><div class="muted">No recent activity.</div></div></div>
  <div class="card" style="grid-column:1/-1">
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
  <div class="card" style="grid-column:1/-1"><h2>Live Activity</h2><table><thead><tr><th>Time</th><th>Client</th><th>Endpoint</th><th>Model</th><th>Status</th><th>Latency</th></tr></thead><tbody id="recent"></tbody></table></div>
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
async function refreshDashboardData() {{
  const res = await fetch('/dashboard/data');
  const data = await res.json();
  const context = data.context;
  const compression = data.compression;
  const intelligence = data.intelligence || {{}};
  document.getElementById('contextUsage').textContent = context.usage_percent + '%';
  document.getElementById('contextUsageText').textContent = context.estimated_tokens + ' estimated tokens across ' + context.conversation_count + ' conversation(s)';
  document.getElementById('contextUsageBar').style.width = Math.min(context.usage_percent, 100) + '%';
  document.getElementById('compressionCount').textContent = compression.count;
  document.getElementById('compressionText').textContent = compression.history.length + ' recent compression event(s)';
  refreshIntelligence(intelligence);
  refreshActiveConversation(data.active_conversation, intelligence.conversation_risk);
}}
function refreshIntelligence(intelligence) {{
  const health = intelligence.health || {{}};
  const status = health.status || 'unknown';
  const healthCard = document.getElementById('systemHealthCard');
  healthCard.className = 'card health-card ' + safeClass(status);
  document.getElementById('systemHealthBadge').className = 'badge ' + safeClass(status);
  document.getElementById('systemHealthBadge').textContent = status;
  document.getElementById('systemHealthStatus').textContent = titleCase(status);
  document.getElementById('systemHealthMessage').textContent = health.message || 'Dashboard health evaluated.';

  const trends = intelligence.trends || {{}};
  const direction = trends.request_direction || 'flat';
  document.getElementById('requestTrend').textContent = titleCase(direction);
  document.getElementById('requestTrendText').textContent = direction === 'up' ? 'Latency rising across recent requests.' : direction === 'down' ? 'Latency improving across recent requests.' : 'Latency trend is stable.';
  document.getElementById('requestRate').textContent = trends.average_request_rate ?? 0;
  document.getElementById('averageLatency').textContent = (trends.average_latency_ms ?? 0) + ' ms';

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
