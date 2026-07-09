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
.app-shell {{ min-height:100vh; display:grid; grid-template-columns:240px minmax(0,1fr); background:linear-gradient(135deg,#080d18,#0f172a 52%,#101827); }}
.sidebar {{ position:sticky; top:0; height:100vh; display:flex; flex-direction:column; gap:28px; padding:22px 18px; background:rgba(13,20,36,.96); border-right:1px solid rgba(255,255,255,.08); }}
.brand {{ display:flex; align-items:center; gap:12px; padding:6px 6px 14px; border-bottom:1px solid rgba(255,255,255,.08); }}
.brand-mark {{ display:grid; place-items:center; width:38px; height:38px; border-radius:10px; background:linear-gradient(135deg,var(--accent),var(--accent-2)); color:#020617; font-weight:900; }}
.brand-name {{ font-weight:800; }}
.brand-sub {{ color:var(--muted); font-size:12px; margin-top:2px; }}
.nav {{ display:grid; gap:7px; }}
.nav a {{ position:relative; display:flex; align-items:center; gap:10px; min-height:40px; padding:8px 10px 8px 12px; border-radius:8px; color:var(--soft); font-size:14px; border:1px solid transparent; transition:background .18s ease,border-color .18s ease,color .18s ease,transform .18s ease; }}
.nav a:hover {{ background:rgba(148,163,184,.12); color:var(--text); transform:translateX(1px); }}
.nav a.active {{ background:linear-gradient(90deg,rgba(56,189,248,.18),rgba(129,140,248,.08)); border-color:rgba(56,189,248,.26); color:#fff; box-shadow:inset 3px 0 0 var(--accent); }}
.nav-kicker {{ color:var(--muted); font-size:11px; text-transform:uppercase; font-weight:800; letter-spacing:.08em; margin:4px 10px; }}
.sidebar-footer {{ margin-top:auto; color:var(--muted); font-size:12px; line-height:1.5; padding:12px 10px; border-top:1px solid rgba(255,255,255,.08); }}
.workspace {{ min-width:0; }}
.topbar {{ position:sticky; top:0; z-index:5; display:flex; justify-content:space-between; align-items:center; gap:16px; padding:12px 22px; background:rgba(9,14,26,.88); backdrop-filter:blur(18px); border-bottom:1px solid rgba(255,255,255,.08); }}
.topbar-actions {{ display:flex; flex-wrap:wrap; justify-content:flex-end; gap:10px; color:var(--muted); font-size:13px; }}
.topbar-pill {{ display:inline-flex; align-items:center; min-height:30px; padding:5px 10px; border:1px solid rgba(255,255,255,.1); border-radius:999px; background:rgba(15,23,42,.62); }}
.dashboard-main {{ min-height:calc(100vh - 63px); min-width:0; padding:10px 16px 18px; }}
h1 {{ margin:0; font-size:25px; }}
.sub {{ color:var(--muted); margin-top:3px; }}
.page {{ display:none; }}
.page.active {{ display:grid; gap:10px; }}
.page-header {{ display:flex; justify-content:space-between; align-items:end; gap:18px; }}
.page-title {{ margin:0; font-size:22px; }}
.page-sub {{ color:var(--muted); margin-top:4px; }}
.command-meta {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
.operations-page {{ grid-template-rows:auto auto auto; min-height:calc(100vh - 91px); overflow:visible; }}
.ops-hero {{ display:grid; grid-template-columns:minmax(360px,1.08fr) repeat(3,minmax(170px,.72fr)); gap:10px; align-items:stretch; min-width:0; }}
.hero-status {{ position:relative; overflow:hidden; min-height:104px; min-width:0; display:grid; align-content:center; padding:14px 18px; background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(17,24,39,.92)); border-left:5px solid var(--accent); }}
.hero-status::after {{ content:""; position:absolute; inset:auto -22% -70% 38%; height:180px; background:radial-gradient(circle,rgba(56,189,248,.18),transparent 68%); pointer-events:none; }}
.hero-status.healthy {{ border-left-color:var(--good); }} .hero-status.warning,.hero-status.busy {{ border-left-color:var(--warn); }} .hero-status.critical,.hero-status.offline {{ border-left-color:var(--bad); }}
.hero-kicker {{ color:var(--muted); font-size:11px; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }}
.hero-title {{ display:flex; align-items:center; gap:10px; margin-top:5px; font-size:clamp(20px,1.25vw,26px); line-height:1.05; font-weight:850; text-transform:uppercase; white-space:nowrap; }}
.hero-title span:last-child {{ min-width:0; overflow:hidden; text-overflow:ellipsis; }}
.hero-icon {{ font-size:20px; }}
.hero-copy {{ max-width:780px; margin-top:5px; color:var(--soft); font-size:13px; line-height:1.3; }}
.operations-lower {{ display:grid; grid-template-columns:minmax(300px,.82fr) minmax(360px,1fr) minmax(340px,1fr); gap:14px; min-height:0; min-width:0; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
.card {{ background:rgba(24,33,50,.92); border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:12px; box-shadow:var(--shadow); transition:border-color .18s ease, transform .18s ease, background .18s ease; }}
.card:hover,.node:hover {{ border-color:rgba(56,189,248,.24); transform:translateY(-1px); background:rgba(27,38,57,.94); }}
.card h2 {{ margin:0 0 7px; font-size:13px; letter-spacing:.02em; }}
.ops-panel {{ min-height:0; overflow:hidden; }}
.compact-card {{ min-height:0; padding:11px; }}
.signal-card {{ min-height:112px; min-width:170px; display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.signal-card h2,.signal-node .node-title {{ color:var(--soft); font-size:13px; text-transform:uppercase; letter-spacing:.08em; }}
.signal-card .value,.signal-node .value {{ font-size:29px; line-height:1; }}
.signal-body {{ display:grid; grid-template-columns:minmax(0,1fr) 68px; gap:9px; align-items:center; }}
.signal-stack {{ display:grid; gap:5px; min-width:0; }}
.gauge {{ width:68px; height:68px; transform:rotate(-90deg); }}
.gauge-track {{ fill:none; stroke:rgba(148,163,184,.18); stroke-width:10; }}
.gauge-progress {{ fill:none; stroke:var(--accent); stroke-width:10; stroke-linecap:round; stroke-dasharray:100; stroke-dashoffset:100; transition:stroke-dashoffset .55s ease, stroke .25s ease; }}
.health-card {{ border-left:5px solid var(--accent); }}
.health-card.healthy {{ border-left-color:var(--good); }} .health-card.busy {{ border-left-color:var(--accent); }} .health-card.warning {{ border-left-color:var(--warn); }} .health-card.critical,.health-card.offline {{ border-left-color:var(--bad); }}
.health-card.healthy .gauge-progress {{ stroke:var(--good); }} .health-card.busy .gauge-progress {{ stroke:var(--accent); }} .health-card.warning .gauge-progress {{ stroke:var(--warn); }} .health-card.critical .gauge-progress,.health-card.offline .gauge-progress {{ stroke:var(--bad); }}
.health-title {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.mini-chart {{ width:100%; height:30px; margin-top:5px; }}
.sparkline {{ fill:none; stroke:var(--accent); stroke-width:2.5; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 8px rgba(56,189,248,.28)); transition:points .3s ease; }}
.spark-area {{ fill:rgba(56,189,248,.08); }}
.value-pop {{ animation:valuePop .28s ease; }}
@keyframes valuePop {{ 0% {{ transform:translateY(0); color:var(--text); }} 45% {{ transform:translateY(-1px); color:#ffffff; }} 100% {{ transform:translateY(0); color:inherit; }} }}
.icon-label {{ display:inline-flex; align-items:center; gap:8px; }}
.icon-mark {{ color:var(--accent); font-size:14px; }}
.badge {{ display:inline-flex; align-items:center; min-height:22px; padding:2px 7px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; background:rgba(148,163,184,.16); color:var(--muted); }}
.badge.positive,.badge.healthy,.badge.low {{ color:var(--good); background:rgba(34,197,94,.12); }} .badge.info,.badge.busy {{ color:var(--accent); background:rgba(56,189,248,.12); }} .badge.warning,.badge.medium {{ color:var(--warn); background:rgba(245,158,11,.12); }} .badge.critical,.badge.high,.badge.offline {{ color:var(--bad); background:rgba(239,68,68,.12); }}
.panel-list {{ display:grid; gap:8px; }}
.panel-item {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:7px 9px; transition:border-color .18s ease, background .18s ease; }}
.panel-item:hover,.timeline-item:hover,.message:hover {{ border-color:rgba(129,140,248,.24); background:rgba(15,23,42,.68); }}
.timeline-list {{ display:grid; gap:8px; }}
.timeline-item {{ display:grid; grid-template-columns:86px 1fr; gap:10px; align-items:start; background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:8px; padding:9px 10px; transition:border-color .18s ease, background .18s ease; }}
.panel-list > .muted,.timeline-list > .muted,#activeRecentMessages > .muted {{ min-height:48px; display:grid; place-items:center; text-align:center; border:1px dashed rgba(148,163,184,.28); border-radius:8px; background:rgba(15,23,42,.32); color:#aebbd0; }}
.action-panel .panel-list {{ max-height:58px; overflow:hidden; }}
.action-panel .small {{ display:none; }}
.activity-card {{ overflow:auto; }}
.activity-card tbody:empty::after {{ content:"No request activity yet."; display:block; padding:18px; color:var(--muted); }}
.risk-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
.value {{ font-size:28px; font-weight:750; overflow-wrap:anywhere; }}
.muted {{ color:var(--muted); overflow-wrap:anywhere; }}
.ok {{ color:var(--good); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.bar {{ height:12px; border-radius:999px; background:#334155; overflow:hidden; margin:10px 0; }}
.fill {{ height:100%; background:var(--accent); width:0%; transition:width .25s ease; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:7px 8px; border-bottom:1px solid rgba(255,255,255,.08); }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }}
.flow-panel {{ position:relative; display:grid; grid-template-rows:auto 1fr; gap:12px; min-height:0; overflow:visible; padding:18px; background:linear-gradient(145deg,rgba(15,23,42,.96),rgba(24,33,50,.86)); }}
.flow-panel::before {{ content:""; position:absolute; inset:54px 18px 18px; border:1px solid rgba(56,189,248,.08); border-radius:8px; pointer-events:none; }}
.flow-stage {{ position:relative; display:grid; grid-template-columns:minmax(150px,1fr) 44px minmax(150px,1fr) 44px minmax(150px,1fr) 44px minmax(150px,1fr); gap:10px; align-items:center; min-width:0; min-height:0; }}
.flow-note {{ color:var(--muted); font-size:12px; }}
.node {{ position:relative; background:radial-gradient(circle at 50% 0%,rgba(56,189,248,.13),transparent 46%),rgba(15,23,42,.92); border:1px solid rgba(255,255,255,.1); border-radius:8px; padding:14px; min-width:0; min-height:142px; box-shadow:var(--shadow); transition:border-color .18s ease, transform .18s ease, background .18s ease; }}
.node::before {{ content:""; display:block; width:46px; height:46px; margin:0 auto 10px; border-radius:50%; border:1px solid rgba(56,189,248,.32); background:rgba(2,6,23,.44); box-shadow:0 0 0 8px rgba(56,189,248,.06); }}
.node .node-title,.node .value,.node .small {{ position:relative; text-align:center; }}
.signal-node {{ display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.node-title {{ font-weight:800; font-size:14px; margin-bottom:8px; }}
.dot {{ display:inline-block; width:12px; height:12px; border-radius:99px; background:var(--warn); margin-right:8px; box-shadow:0 0 16px currentColor; animation:statusPulse 2s ease-in-out infinite; }}
.dot.online {{ background:var(--good); color:var(--good); }} .dot.waiting {{ background:var(--warn); color:var(--warn); }} .dot.offline {{ background:var(--bad); color:var(--bad); }}
@keyframes statusPulse {{ 0%,100% {{ opacity:.72; }} 50% {{ opacity:1; }} }}
.pipe {{ position:relative; height:2px; background:linear-gradient(90deg,rgba(45,58,79,.35),rgba(56,189,248,.85),rgba(45,58,79,.35)); border-radius:99px; opacity:.9; }}
.pipe::after {{ content:""; position:absolute; left:50%; top:50%; width:10px; height:10px; border-radius:50%; transform:translate(-50%,-50%); background:rgba(56,189,248,.5); box-shadow:0 0 18px rgba(56,189,248,.42); }}
.small {{ font-size:12px; color:var(--muted); overflow-wrap:anywhere; }}
.traffic-panel {{ display:grid; grid-template-rows:auto auto 1fr; gap:10px; }}
.traffic-stats {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }}
.resource-stack {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(112px,1fr)); gap:12px; align-items:start; }}
.resource-error {{ display:flex; justify-content:space-between; align-items:center; gap:12px; margin-top:12px; padding-top:10px; border-top:1px solid rgba(255,255,255,.08); }}
.speedometer {{ display:grid; justify-items:center; gap:4px; min-width:112px; overflow:visible; }}
.speedometer-label {{ color:var(--muted); font-size:11px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
.speedometer-shell {{ position:relative; width:clamp(92px,7vw,112px); min-width:92px; max-width:112px; aspect-ratio:2 / 1; overflow:hidden; }}
.speedometer-arc {{ --fill:0%; position:absolute; inset:0; border-radius:112px 112px 0 0; background:conic-gradient(from 270deg at 50% 100%, var(--accent) var(--fill), rgba(51,65,85,.72) 0 50%, transparent 0); }}
.speedometer-arc::after {{ content:""; position:absolute; left:14px; right:14px; bottom:-42px; height:84px; border-radius:84px 84px 0 0; background:rgba(24,33,50,.98); border:1px solid rgba(255,255,255,.06); }}
.speedometer-value {{ position:relative; margin-top:-38px; min-height:28px; font-size:22px; font-weight:800; white-space:nowrap; }}
.speedometer-detail {{ min-height:28px; text-align:center; font-size:11px; color:var(--muted); overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }}
.conversation-meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:14px; }}
.conversation-meta.compact {{ grid-template-columns:repeat(2,minmax(0,1fr)); margin-bottom:0; }}
.conversation-compact {{ display:grid; gap:10px; }}
.conversation-compact .summary {{ max-height:62px; overflow:hidden; }}
.summary {{ background:rgba(15,23,42,.62); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:12px; white-space:pre-wrap; }}
.messages {{ display:grid; gap:10px; margin-top:12px; }}
.message {{ background:rgba(15,23,42,.46); border:1px solid rgba(255,255,255,.08); border-radius:10px; padding:10px 12px; }}
.message-role {{ color:var(--accent); font-size:12px; font-weight:700; text-transform:uppercase; }}
.message-content {{ margin-top:4px; white-space:pre-wrap; }}
@media (min-width: 1901px) {{ .operations-page {{ gap:14px; }} }}
@media (max-width: 1900px) {{
  .app-shell {{ grid-template-columns:220px minmax(0,1fr); }}
  .sidebar {{ padding:18px 14px; }}
  .topbar {{ padding:10px 18px; }}
  .topbar-pill {{ min-height:26px; padding:3px 8px; }}
  .dashboard-main {{ padding:8px 12px 14px; }}
  .page.active {{ gap:8px; }}
  .ops-hero {{ grid-template-columns:minmax(280px,.9fr) repeat(3,minmax(132px,1fr)); grid-template-rows:auto auto; gap:8px; }}
  .hero-status {{ grid-column:1; grid-row:1; min-height:74px; padding:10px 14px; }}
  .hero-title {{ font-size:18px; white-space:nowrap; margin-top:3px; }}
  .hero-icon {{ font-size:17px; }}
  .hero-copy {{ max-width:none; margin-top:3px; font-size:11px; line-height:1.22; display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }}
  .hero-kicker {{ font-size:10px; }}
  .hero-status .command-meta {{ display:none; }}
  .command-meta {{ margin-top:5px; }}
  #systemHealthCard {{ grid-column:2; grid-row:1; }}
  #overview > .signal-card:nth-of-type(3) {{ grid-column:3; grid-row:1; }}
  #overview > .signal-card:nth-of-type(4) {{ grid-column:4; grid-row:1; }}
  .action-panel {{ grid-column:1; grid-row:2; }}
  .signal-card {{ min-height:78px; min-width:0; }}
  .signal-card .value,.signal-node .value {{ font-size:22px; }}
  .signal-card h2,.signal-node .node-title {{ font-size:12px; }}
  .signal-body {{ grid-template-columns:minmax(0,1fr) 46px; gap:6px; }}
  .gauge {{ width:46px; height:46px; }}
  .mini-chart {{ height:20px; margin-top:2px; }}
  .action-panel {{ min-height:0; }}
  .action-panel .health-title {{ margin-bottom:4px; }}
  .action-panel .panel-list {{ max-height:36px; }}
  .action-panel .panel-item {{ padding:5px 7px; font-size:12px; }}
  .flow-panel {{ padding:10px; gap:6px; }}
  .flow-panel::before {{ inset:36px 10px 10px; }}
  .flow-stage {{ grid-template-columns:minmax(126px,1fr) 28px minmax(126px,1fr); grid-auto-rows:auto; gap:8px; }}
  .flow-stage > :nth-child(1) {{ grid-column:1; grid-row:1; }}
  .flow-stage > :nth-child(2) {{ grid-column:2; grid-row:1; }}
  .flow-stage > :nth-child(3) {{ grid-column:3; grid-row:1; }}
  .flow-stage > :nth-child(4) {{ grid-column:3; grid-row:2; width:4px; height:18px; justify-self:center; align-self:center; }}
  .flow-stage > :nth-child(5) {{ grid-column:3; grid-row:3; }}
  .flow-stage > :nth-child(6) {{ grid-column:2; grid-row:3; }}
  .flow-stage > :nth-child(7) {{ grid-column:1; grid-row:3; }}
  .node {{ min-height:78px; padding:7px; }}
  .node::before {{ width:20px; height:20px; margin-bottom:4px; box-shadow:0 0 0 4px rgba(56,189,248,.05); }}
  .node-title {{ font-size:11px; margin-bottom:3px; }}
  .node .value {{ font-size:18px; }}
  .node .small {{ font-size:10px; line-height:1.16; }}
  .operations-lower {{ grid-template-columns:minmax(260px,.85fr) minmax(280px,1fr) minmax(280px,1fr); gap:8px; }}
  .traffic-panel {{ gap:6px; }}
  .traffic-stats {{ gap:7px; }}
  .resource-stack {{ grid-template-columns:repeat(3,minmax(78px,1fr)); gap:6px; }}
  .speedometer {{ min-width:78px; }}
  .speedometer-shell {{ width:78px; min-width:78px; max-width:78px; }}
  .speedometer-value {{ margin-top:-28px; min-height:22px; font-size:16px; }}
  .speedometer-detail {{ min-height:18px; font-size:9px; }}
  .resource-error {{ margin-top:7px; padding-top:6px; }}
  .conversation-compact {{ gap:6px; }}
  .conversation-compact .summary {{ max-height:38px; }}
}}
@media (max-width: 1500px) {{
  .ops-hero {{ grid-template-columns:minmax(250px,.85fr) repeat(3,minmax(108px,1fr)); gap:7px; }}
  .hero-title {{ white-space:normal; }}
  .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }}
  .operations-lower {{ grid-template-columns:minmax(250px,.85fr) minmax(270px,1fr); }}
  .flow-stage {{ grid-template-columns:minmax(118px,1fr) 24px minmax(118px,1fr); gap:8px; }}
  .resource-stack {{ grid-template-columns:repeat(auto-fit,minmax(96px,1fr)); }}
}}
@media (max-width: 1350px) {{
  .app-shell {{ grid-template-columns:200px minmax(0,1fr); }}
  .sidebar {{ padding:14px 12px; gap:18px; }}
  .brand {{ padding-bottom:10px; }}
  .nav a {{ min-height:34px; padding:6px 8px 6px 10px; font-size:13px; }}
  .topbar {{ padding:7px 12px; }}
  .topbar-pill {{ min-height:24px; padding:2px 7px; font-size:12px; }}
  h1 {{ font-size:22px; }}
  .sub {{ display:none; }}
  .dashboard-main {{ min-height:calc(100vh - 47px); padding:6px 10px 12px; }}
  .page.active {{ gap:6px; }}
  .operations-page {{ min-height:calc(100vh - 59px); }}
  .ops-hero {{ grid-template-columns:minmax(220px,.82fr) repeat(2,minmax(118px,1fr)); grid-template-rows:auto auto; gap:6px; }}
  .hero-status {{ grid-column:1; grid-row:1; min-height:58px; padding:8px 10px; }}
  .hero-kicker {{ font-size:9px; }}
  .hero-title {{ gap:7px; margin-top:2px; font-size:16px; line-height:1.05; }}
  .hero-icon {{ font-size:15px; }}
  .hero-copy {{ display:none; }}
  #systemHealthCard {{ grid-column:2; grid-row:1; }}
  #overview > .signal-card:nth-of-type(3) {{ grid-column:3; grid-row:1; }}
  #overview > .signal-card:nth-of-type(4) {{ grid-column:2/4; grid-row:2; }}
  .action-panel {{ grid-column:1; grid-row:2; padding:8px 10px; }}
  .action-panel .health-title {{ margin-bottom:3px; }}
  .action-panel .panel-list {{ max-height:none; }}
  .action-panel .panel-item {{ padding:4px 6px; font-size:11px; line-height:1.2; }}
  .card {{ padding:9px; }}
  .card h2 {{ margin-bottom:4px; font-size:12px; }}
  .badge {{ min-height:19px; padding:1px 6px; font-size:10px; }}
  .signal-card {{ min-height:58px; }}
  .signal-card .value,.signal-node .value {{ font-size:19px; }}
  .signal-card h2,.signal-node .node-title {{ font-size:10px; letter-spacing:.05em; }}
  .signal-body {{ grid-template-columns:minmax(0,1fr) 38px; gap:5px; }}
  .signal-stack {{ gap:3px; }}
  .gauge {{ width:38px; height:38px; }}
  .mini-chart {{ height:18px; margin-top:1px; }}
  .muted,.small {{ font-size:11px; line-height:1.2; }}
  .flow-panel {{ padding:8px; gap:4px; }}
  .flow-panel::before {{ inset:30px 8px 8px; }}
  .flow-panel .health-title h2 {{ margin:0; }}
  .flow-note {{ font-size:10px; }}
  .flow-stage {{ grid-template-columns:minmax(104px,1fr) 20px minmax(104px,1fr); gap:5px; }}
  .flow-stage > :nth-child(4) {{ height:12px; }}
  .node {{ min-height:56px; padding:5px; }}
  .node::before {{ width:14px; height:14px; margin-bottom:2px; box-shadow:0 0 0 3px rgba(56,189,248,.05); }}
  .node-title {{ font-size:10px; margin-bottom:2px; }}
  .node .value {{ font-size:15px; }}
  .node .small {{ font-size:9px; line-height:1.1; }}
  .dot {{ width:9px; height:9px; margin-right:5px; }}
  .pipe::after {{ width:7px; height:7px; }}
  .operations-lower {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:6px; }}
  .traffic-panel {{ gap:4px; }}
  .traffic-stats {{ gap:5px; }}
  .resource-stack {{ grid-template-columns:repeat(3,minmax(68px,1fr)); gap:5px; }}
  .speedometer {{ min-width:68px; gap:2px; }}
  .speedometer-label {{ font-size:9px; }}
  .speedometer-shell {{ width:68px; min-width:68px; max-width:68px; }}
  .speedometer-arc::after {{ left:10px; right:10px; bottom:-32px; height:64px; }}
  .speedometer-value {{ margin-top:-24px; min-height:19px; font-size:14px; }}
  .speedometer-detail {{ min-height:14px; font-size:9px; -webkit-line-clamp:1; }}
  .resource-error {{ margin-top:4px; padding-top:4px; }}
  .conversation-compact {{ grid-column:1/-1; gap:5px; }}
  .conversation-meta.compact {{ grid-template-columns:repeat(4,minmax(0,1fr)); gap:8px; }}
  .conversation-compact .summary {{ max-height:32px; padding:8px; }}
}}
@media (max-width: 1000px) {{ .app-shell {{ grid-template-columns:220px minmax(0,1fr); }} .dashboard-main {{ padding:14px 16px 18px; }} .ops-hero,.operations-lower {{ grid-template-columns:1fr; }} .hero-title {{ white-space:normal; }} .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }} .flow-stage {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} .resource-stack {{ grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); }} }}
@media (max-width: 1000px) {{ .app-shell {{ grid-template-columns:1fr; }} .sidebar {{ position:relative; height:auto; gap:14px; }} .nav {{ grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); }} .sidebar-footer {{ display:none; }} .topbar {{ position:relative; align-items:flex-start; flex-direction:column; }} .dashboard-main {{ padding:18px; }} .page.active,.ops-hero,.operations-lower {{ grid-template-columns:1fr; }} .operations-page {{ min-height:auto; }} .timeline-item {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<div class="app-shell">
<aside class="sidebar">
  <div class="brand">
    <div class="brand-mark">CK</div>
    <div><div class="brand-name">ContextKeeper</div><div class="brand-sub">Local operations console</div></div>
  </div>
  <nav class="nav" aria-label="Dashboard pages">
    <div class="nav-kicker">Console</div>
    <a href="#operations" class="active" data-page-link="operations">🏠 Operations</a>
    <a href="#conversations" data-page-link="conversations">💬 Conversations</a>
    <a href="#context" data-page-link="context">🧠 Context</a>
    <a href="#analytics" data-page-link="analytics">📊 Analytics</a>
    <a href="#logs" data-page-link="logs">📝 Logs</a>
    <a href="#settings" data-page-link="settings">⚙ Settings</a>
  </nav>
  <div class="sidebar-footer">Browser-based admin UI served locally by ContextKeeper.</div>
</aside>
<div class="workspace">
<header class="topbar">
  <div>
<h1>ContextKeeper</h1>
<div class="sub">Transparent Ollama Proxy - Diagnostics - System Monitor</div>
  </div>
  <div class="topbar-actions">
    <span class="topbar-pill">Proxy port {settings.server.port}</span>
    <span class="topbar-pill">{settings.ollama.base_url}</span>
  </div>
</header>
<main class="dashboard-main">

<section id="operations" class="page operations-page active" data-page="operations">
  <section id="overview" class="ops-hero">
    <div id="opsHeroStatus" class="card hero-status">
      <div class="hero-kicker">AI Operations Center</div>
      <div id="opsHeroTitle" class="hero-title"><span id="opsHeroIcon" class="hero-icon">🟡</span><span id="opsHeroText">Checking Systems</span></div>
      <div id="opsHeroMessage" class="hero-copy">ContextKeeper is evaluating proxy health, traffic flow, and required operator actions.</div>
      <div class="command-meta">
        <span class="badge info">Local</span>
        <span class="badge busy">Live refresh</span>
      </div>
    </div>
    <div id="systemHealthCard" class="card health-card signal-card compact-card">
      <div class="health-title"><h2><span class="icon-label"><span class="icon-mark">*</span>System Health</span></h2><span id="systemHealthBadge" class="badge">Checking</span></div>
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
    <div class="card signal-card compact-card"><h2><span class="icon-label"><span class="icon-mark">%</span>Context Usage</span></h2><div class="signal-body"><div class="signal-stack"><div id="contextUsage" class="value">--%</div><div id="contextUsageText" class="muted">Context window usage will appear here.</div><div class="bar"><div id="contextUsageBar" class="fill"></div></div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="contextGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div></div>
    <div class="card signal-card compact-card"><h2><span class="icon-label"><span class="icon-mark">#</span>Request Statistics</span></h2><div id="req" class="value">0</div><div class="muted">Total requests</div><svg class="mini-chart" viewBox="0 0 220 48" preserveAspectRatio="none" aria-hidden="true"><polygon id="requestSparkArea" class="spark-area" points="0,48 220,48"></polygon><polyline id="requestSparkline" class="sparkline" points="0,40 44,40 88,40 132,40 176,40 220,40"></polyline></svg></div>
    <div class="card compact-card action-panel"><div class="health-title"><h2><span class="icon-label"><span class="icon-mark">!</span>Recommendations</span></h2><span class="badge">Action</span></div><div id="recommendationsList" class="panel-list"><div class="muted">No operator action queued.</div></div><div class="small">Open Analytics for full insight history.</div></div>
  </section>

  <section id="connections" class="card flow-panel ops-panel">
    <div class="health-title">
      <h2>Connection Flow</h2>
      <span class="flow-note">Static topology now; connector placeholders are reserved for animated traffic flow.</span>
    </div>
    <div class="flow-stage">
      <div class="node"><div class="node-title"><span id="clientDot" class="dot waiting"></span>Client</div><div id="clientText" class="value">Waiting</div><div id="clientSub" class="small">No clients seen yet</div></div>
      <div class="pipe"></div>
      <div class="node"><div class="node-title"><span id="proxyDot" class="dot online"></span>ContextKeeper Status</div><div class="value ok">Online</div><div id="proxySub" class="small">Listening on port {settings.server.port}</div></div>
      <div class="pipe"></div>
      <div class="node signal-node"><div class="node-title"><span id="ollamaDot" class="dot waiting"></span>Ollama Status</div><div id="ollamaText" class="value">Checking</div><div id="ollamaSub" class="small">{settings.ollama.base_url}</div></div>
      <div class="pipe"></div>
      <div class="node"><div class="node-title"><span id="modelDot" class="dot waiting"></span>Model</div><div id="modelText" class="value">Waiting</div><div id="modelSub" class="small">No active model yet</div></div>
    </div>
  </section>

  <section class="operations-lower">
    <div class="card traffic-panel ops-panel">
      <h2>Traffic</h2>
      <div class="traffic-stats">
        <div><div class="small">Request Trend</div><div id="requestTrend" class="value">Flat</div><div id="requestTrendText" class="muted">Awaiting request data.</div></div>
        <div><div class="small">Rate</div><div id="requestRate" class="value">0</div><div class="muted">requests / min</div></div>
      </div>
      <div class="signal-body"><div><div class="small">Average Latency</div><div id="averageLatency" class="value">0 ms</div><div class="muted">recent requests</div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="latencyGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div>
    </div>
    <div id="resources" class="card ops-panel">
      <h2>Resources</h2>
      <div class="resource-stack">
        <div class="speedometer"><div class="speedometer-label">CPU</div><div class="speedometer-shell"><div id="cpuBar" class="speedometer-arc"></div></div><div id="cpu" class="speedometer-value">--%</div><div class="speedometer-detail">Processor load</div></div>
        <div class="speedometer"><div class="speedometer-label">RAM</div><div class="speedometer-shell"><div id="ramBar" class="speedometer-arc"></div></div><div id="ram" class="speedometer-value">--%</div><div id="ramText" class="speedometer-detail"></div></div>
        <div class="speedometer"><div class="speedometer-label">VRAM</div><div class="speedometer-shell"><div id="gpuBar" class="speedometer-arc"></div></div><div id="gpu" class="speedometer-value">--</div><div id="vramText" class="speedometer-detail"></div></div>
      </div>
      <div class="resource-error"><span class="small">Errors</span><div id="err" class="value">0</div></div>
    </div>
    <div class="card conversation-compact ops-panel">
      <div class="health-title"><h2>Active Conversation</h2><a class="badge info" href="#conversations" data-page-link="conversations">Open</a></div>
      <div class="conversation-meta compact">
        <div><div class="small">Conversation ID</div><div id="opsActiveConversationId" class="muted">None</div></div>
        <div><div class="small">Model</div><div id="opsActiveModelName" class="muted">None</div></div>
        <div><div class="small">Context Usage</div><div id="opsActiveContextUsage" class="muted">--</div></div>
        <div><div class="small">Risk</div><div id="opsConversationRisk" class="muted">--</div></div>
      </div>
      <div id="opsConversationRiskIndicators" class="risk-row"></div>
      <div id="opsActiveRollingSummary" class="summary muted">No rolling summary available.</div>
    </div>
  </section>
</section>

<section id="conversations" class="page" data-page="conversations">
  <div class="page-header"><div><h2 class="page-title">Conversations</h2><div class="page-sub">Active conversation state and recent message context.</div></div></div>
  <div id="conversation" class="card">
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
</section>

<section id="context" class="page" data-page="context">
  <div class="page-header"><div><h2 class="page-title">Context</h2><div class="page-sub">Context pressure, compression history, and token estimates.</div></div></div>
  <div class="grid">
    <div class="card"><h2>Status</h2><div class="value ok">Running</div><div class="muted">Proxy -> {settings.ollama.base_url}</div></div>
    <div class="card"><h2>Compression History</h2><div id="compressionCount" class="value">0</div><div id="compressionText" class="muted">Compression events will appear here.</div></div>
  </div>
</section>

<section id="analytics" class="page" data-page="analytics">
  <div class="page-header"><div><h2 class="page-title">Analytics</h2><div class="page-sub">Insights and trends derived from recent proxy activity.</div></div></div>
  <div id="intelligence" class="grid">
    <div class="card"><h2>Insights</h2><div id="insightsList" class="panel-list"><div class="muted">No insights yet.</div></div></div>
    <div class="card"><h2>Activity Timeline</h2><div id="timelineList" class="timeline-list"><div class="muted">No recent activity.</div></div></div>
  </div>
</section>

<section id="logs" class="page" data-page="logs">
  <div class="page-header"><div><h2 class="page-title">Logs</h2><div class="page-sub">Recent request activity from the local proxy.</div></div></div>
  <div id="activity" class="card activity-card"><h2><span class="icon-label"><span class="icon-mark">#</span>Live Activity</span></h2><table><thead><tr><th>Time</th><th>Client</th><th>Endpoint</th><th>Model</th><th>Status</th><th>Latency</th></tr></thead><tbody id="recent"></tbody></table></div>
</section>

<section id="settings" class="page" data-page="settings">
  <div class="page-header"><div><h2 class="page-title">Settings</h2><div class="page-sub">Current dashboard and upstream connection settings.</div></div></div>
  <div class="grid">
    <div class="card"><h2>Proxy</h2><div class="value ok">Running</div><div class="muted">Listening on port {settings.server.port}</div></div>
    <div class="card"><h2>Ollama</h2><div class="value">Configured</div><div class="muted">{settings.ollama.base_url}</div></div>
    <div class="card"><h2>Refresh</h2><div class="value">{settings.dashboard.refresh_interval_ms or 1000} ms</div><div class="muted">Dashboard polling interval</div></div>
  </div>
</section>
</main>
</div>
</div>
<script>
const DASHBOARD_REFRESH_INTERVAL_MS = {settings.dashboard.refresh_interval_ms or 1000};
function byId(id) {{
  return document.getElementById(id);
}}
function escapeHtml(value) {{
  return String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
}}
function setDot(id, status) {{
  const el = byId(id);
  if (!el) return;
  el.className = 'dot ' + (status === 'online' || status === 'active' ? 'online' : status === 'offline' ? 'offline' : 'waiting');
}}
function safeClass(value) {{
  return String(value || '').toLowerCase().replace(/[^a-z0-9_-]/g, '');
}}
function titleCase(value) {{
  return String(value || '').replace(/_/g, ' ').replace(/(^|\\s)([a-z])/g, match => match.toUpperCase());
}}
function setText(id, value) {{
  const el = byId(id);
  if (!el) return;
  const next = String(value);
  if (el.textContent !== next) {{
    el.textContent = next;
    el.classList.remove('value-pop');
    void el.offsetWidth;
    el.classList.add('value-pop');
  }}
}}
function setHtml(id, html) {{
  const el = byId(id);
  if (el) el.innerHTML = html;
}}
function setGauge(id, value) {{
  const el = byId(id);
  if (!el) return;
  const clamped = Math.max(0, Math.min(100, Number(value) || 0));
  el.style.strokeDashoffset = 100 - clamped;
}}
function setWidth(id, value) {{
  const el = byId(id);
  if (!el) return;
  if (el.classList.contains('speedometer-arc')) {{
    const numeric = Math.max(0, Math.min(100, Number.parseFloat(String(value)) || 0));
    el.style.setProperty('--fill', (numeric / 2) + '%');
    return;
  }}
  el.style.width = value;
}}
function heroStateForStatus(status) {{
  if (status === 'healthy') return {{ icon:'🟢', title:'All Systems Operational' }};
  if (status === 'critical' || status === 'offline') return {{ icon:'🔴', title:'System Degraded' }};
  return {{ icon:'🟡', title:'Attention Required' }};
}}
function healthGaugeValue(status) {{
  return ({{healthy: 100, busy: 76, warning: 48, critical: 20, offline: 4}})[status] ?? 0;
}}
function latencyGaugeValue(latencyMs) {{
  const latency = Math.max(0, Number(latencyMs) || 0);
  return Math.max(0, 100 - Math.min(100, latency / 50));
}}
function renderSparkline(requests) {{
  const line = byId('requestSparkline');
  const area = byId('requestSparkArea');
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
function showPage(pageName) {{
  const target = pageName || 'operations';
  document.querySelectorAll('[data-page]').forEach(page => page.classList.toggle('active', page.dataset.page === target));
  document.querySelectorAll('[data-page-link]').forEach(link => link.classList.toggle('active', link.dataset.pageLink === target));
  if (location.hash !== '#' + target) history.replaceState(null, '', '#' + target);
}}
function initializePages() {{
  document.querySelectorAll('[data-page-link]').forEach(link => {{
    link.addEventListener('click', event => {{
      event.preventDefault();
      showPage(link.dataset.pageLink);
    }});
  }});
  const initial = (location.hash || '#operations').slice(1);
  showPage(byId(initial) ? initial : 'operations');
}}
async function refreshHealth() {{
  const res = await fetch('/health');
  const h = await res.json();
  const c = h.connections;
  setDot('clientDot', c.client.status);
  setText('clientText', c.client.count > 0 ? 'Connected' : 'Waiting');
  setText('clientSub', c.client.count + ' client(s) seen recently');
  setDot('proxyDot', c.proxy.status);
  setText('proxySub', 'Listening at ' + c.proxy.listen);
  setDot('ollamaDot', c.ollama.status);
  setText('ollamaText', c.ollama.status === 'online' ? 'Online' : c.ollama.status);
  setText('ollamaSub', h.ollama_base_url + (c.ollama.version ? ' - v' + c.ollama.version : '') + ' - ' + c.ollama.latency_ms + ' ms');
  setDot('modelDot', c.model.status);
  setText('modelText', c.model.name ? 'Active' : 'Waiting');
  setText('modelSub', c.model.name || 'No active model yet');
}}
async function refreshMetrics() {{
  const res = await fetch('/metrics');
  const data = await res.json();
  const r = data.requests;
  const s = data.system;
  setText('req', r.total_requests);
  setText('err', r.total_errors);
  setText('cpu', s.cpu_percent + '%');
  setWidth('cpuBar', s.cpu_percent + '%');
  setText('ram', s.ram_percent + '%');
  setText('ramText', s.ram_used_gb + ' / ' + s.ram_total_gb + ' GB');
  setWidth('ramBar', s.ram_percent + '%');
  if (s.gpu) {{
    setText('gpu', s.gpu.gpu_percent + '%');
    setText('vramText', s.gpu.name + ' - ' + s.gpu.vram_used_gb + ' / ' + s.gpu.vram_total_gb + ' GB VRAM - ' + s.gpu.temperature_c + ' C');
    setWidth('gpuBar', s.gpu.gpu_percent + '%');
  }} else {{
    setText('gpu', 'N/A');
    setText('vramText', 'nvidia-smi not available');
    setWidth('gpuBar', '0%');
  }}
  renderSparkline(r.recent_requests);
  setHtml('recent', r.recent_requests.map(x => `<tr><td>${{escapeHtml(new Date(x.timestamp).toLocaleTimeString())}}</td><td>${{escapeHtml(x.client_host||'')}}</td><td>${{escapeHtml(x.endpoint)}}</td><td>${{escapeHtml(x.model||'')}}</td><td>${{escapeHtml(x.status_code)}}</td><td>${{escapeHtml(x.latency_ms)}} ms</td></tr>`).join(''));
}}
async function refreshDashboardData() {{
  const res = await fetch('/dashboard/data');
  const data = await res.json();
  const context = data.context;
  const compression = data.compression;
  const intelligence = data.intelligence || {{}};
  setText('contextUsage', context.usage_percent + '%');
  setText('contextUsageText', context.estimated_tokens + ' estimated tokens across ' + context.conversation_count + ' conversation(s)');
  setWidth('contextUsageBar', Math.min(context.usage_percent, 100) + '%');
  setGauge('contextGaugeArc', context.usage_percent);
  setText('compressionCount', compression.count);
  setText('compressionText', compression.history.length + ' recent compression event(s)');
  refreshIntelligence(intelligence);
  refreshActiveConversation(data.active_conversation, intelligence.conversation_risk);
}}
function refreshIntelligence(intelligence) {{
  const health = intelligence.health || {{}};
  const status = health.status || 'unknown';
  const healthCard = byId('systemHealthCard');
  if (healthCard) healthCard.className = 'card health-card signal-card compact-card ' + safeClass(status);
  const hero = byId('opsHeroStatus');
  if (hero) hero.className = 'card hero-status ' + safeClass(status);
  const heroState = heroStateForStatus(status);
  setText('opsHeroIcon', heroState.icon);
  setText('opsHeroText', heroState.title);
  setText('opsHeroMessage', health.message || 'Dashboard health evaluated.');
  const healthBadge = byId('systemHealthBadge');
  if (healthBadge) healthBadge.className = 'badge ' + safeClass(status);
  setText('systemHealthBadge', status);
  setText('systemHealthStatus', titleCase(status));
  setText('systemHealthMessage', health.message || 'Dashboard health evaluated.');
  setGauge('healthGaugeArc', healthGaugeValue(status));

  const trends = intelligence.trends || {{}};
  const direction = trends.request_direction || 'flat';
  setText('requestTrend', titleCase(direction));
  setText('requestTrendText', direction === 'up' ? 'Latency rising across recent requests.' : direction === 'down' ? 'Latency improving across recent requests.' : 'Latency trend is stable.');
  setText('requestRate', trends.average_request_rate ?? 0);
  setText('averageLatency', (trends.average_latency_ms ?? 0) + ' ms');
  setGauge('latencyGaugeArc', latencyGaugeValue(trends.average_latency_ms));

  renderPanelList('insightsList', intelligence.insights || [], 'severity', 'No insights yet.');
  renderPanelList('recommendationsList', intelligence.recommendations || [], 'priority', 'No operator action queued.');
  renderTimeline(intelligence.timeline || []);
}}
function renderPanelList(id, items, badgeField, emptyText) {{
  const html = items.length
    ? items.map(item => `<div class="panel-item"><span>${{escapeHtml(item.message)}}</span><span class="badge ${{safeClass(item[badgeField])}}">${{escapeHtml(item[badgeField])}}</span></div>`).join('')
    : `<div class="muted">${{escapeHtml(emptyText)}}</div>`;
  setHtml(id, html);
}}
function renderTimeline(events) {{
  const html = events.length
    ? events.map(event => `<div class="timeline-item"><div class="small">${{escapeHtml(new Date(event.timestamp).toLocaleTimeString())}}</div><div>${{escapeHtml(event.message)}}</div></div>`).join('')
    : '<div class="muted">No recent activity.</div>';
  setHtml('timelineList', html);
}}
function refreshActiveConversation(active, risk) {{
  const current = active || {{}};
  setText('activeConversationId', current.conversation_id || 'None');
  setText('activeModelName', current.model_name || 'None');
  setText('opsActiveConversationId', current.conversation_id || 'None');
  setText('opsActiveModelName', current.model_name || 'None');
  if (current.context) {{
    const contextText = current.context.usage_percent + '% (' + current.context.estimated_tokens + ' / ' + current.context.context_window_tokens + ' tokens)';
    setText('activeContextUsage', contextText);
    setText('opsActiveContextUsage', contextText);
  }} else {{
    setText('activeContextUsage', '--');
    setText('opsActiveContextUsage', '--');
  }}
  refreshConversationRisk(risk);
  setText('activeRollingSummary', current.rolling_summary || 'No rolling summary available.');
  setText('opsActiveRollingSummary', current.rolling_summary || 'No rolling summary available.');
  const messages = current.recent_messages || [];
  setHtml('activeRecentMessages', messages.length
    ? messages.map(message => `<div class="message"><div class="message-role">${{escapeHtml(message.role)}}</div><div class="message-content">${{escapeHtml(message.content)}}</div><div class="small">${{escapeHtml(new Date(message.timestamp).toLocaleTimeString())}}</div></div>`).join('')
    : '<div class="muted">No recent messages.</div>');
}}
function refreshConversationRisk(risk) {{
  const current = risk || {{}};
  setText('conversationRisk', current.message || 'No active conversation.');
  setText('opsConversationRisk', current.message || 'No active conversation.');
  const indicators = current.indicators || [];
  const html = indicators.length
    ? indicators.map(indicator => `<span class="badge ${{safeClass(indicator.severity)}}">${{escapeHtml(indicator.label)}}</span>`).join('')
    : '<span class="badge">No indicators</span>';
  setHtml('conversationRiskIndicators', html);
  setHtml('opsConversationRiskIndicators', html);
}}
async function refresh() {{ await Promise.all([refreshHealth(), refreshMetrics(), refreshDashboardData()]); }}
initializePages();
refresh(); setInterval(refresh, DASHBOARD_REFRESH_INTERVAL_MS);
</script>
</body>
</html>
"""
