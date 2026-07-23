from __future__ import annotations

from html import escape

from ..config import Settings


def render_dashboard_html(settings: Settings) -> str:
    ollama_base_url_html = escape(settings.ollama.base_url)
    return f"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{settings.dashboard.title}</title>
<link rel="icon" href="data:," />
<style>
:root {{ --bg:#090e1a; --sidebar:#0d1424; --panel:#111827; --card:#182132; --card-strong:#1f2937; --text:#e5e7eb; --muted:#94a3b8; --soft:#cbd5e1; --good:#22c55e; --warn:#f59e0b; --bad:#ef4444; --accent:#38bdf8; --accent-2:#818cf8; --line:#2d3a4f; --glass:rgba(15,23,42,.66); --glass-strong:rgba(24,33,50,.88); --border-card:rgba(203,213,225,.11); --border-card-hot:rgba(56,189,248,.28); --surface-inset-highlight:inset 0 1px 0 rgba(255,255,255,.055); --shadow:0 18px 46px rgba(0,0,0,.28); --shadow-soft:0 10px 24px rgba(0,0,0,.2); --shadow-neutral-soft:0 14px 32px rgba(2,6,23,.24); --glow-good:0 0 0 1px rgba(34,197,94,.07),0 0 18px rgba(34,197,94,.12); --glow-info:0 0 0 1px rgba(56,189,248,.07),0 0 18px rgba(56,189,248,.12); --glow-warn:0 0 0 1px rgba(245,158,11,.07),0 0 18px rgba(245,158,11,.12); --glow-bad:0 0 0 1px rgba(239,68,68,.07),0 0 18px rgba(239,68,68,.12); }}
* {{ box-sizing:border-box; }}
html {{ height:100%; overflow:hidden; scroll-behavior:smooth; }}
body {{ margin:0; width:100%; height:100%; min-width:320px; overflow:hidden; font-family:"Segoe UI Variable", Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--text); }}
body::before {{ content:""; position:fixed; inset:0; z-index:-1; pointer-events:none; background:radial-gradient(circle at 18% 8%,rgba(56,189,248,.16),transparent 28%),radial-gradient(circle at 84% 18%,rgba(129,140,248,.12),transparent 30%),linear-gradient(135deg,#070b14,#0b1220 45%,#101827); }}
a {{ color:inherit; text-decoration:none; }}
:where(a,button,[tabindex]):focus-visible {{ outline:2px solid rgba(56,189,248,.68); outline-offset:2px; }}
button,a.badge {{ font:inherit; }}
button:disabled,[aria-disabled="true"] {{ cursor:not-allowed; opacity:.48; filter:saturate(.72); }}
.app-shell {{ height:100vh; height:100dvh; min-height:0; overflow:hidden; display:grid; grid-template-columns:240px minmax(0,1fr); background:linear-gradient(90deg,rgba(13,20,36,.72),transparent 38%); }}
.sidebar {{ position:relative; top:0; height:100%; min-height:0; overflow:hidden; display:flex; flex-direction:column; gap:26px; padding:20px 16px; background:linear-gradient(180deg,rgba(13,20,36,.94),rgba(9,14,26,.9)); border-right:1px solid rgba(203,213,225,.09); box-shadow:8px 0 34px rgba(0,0,0,.18); backdrop-filter:blur(18px); }}
.brand {{ display:flex; align-items:center; gap:12px; padding:6px 6px 14px; border-bottom:1px solid rgba(203,213,225,.09); }}
.brand-mark {{ display:grid; place-items:center; width:38px; height:38px; border-radius:8px; background:linear-gradient(135deg,var(--accent),var(--accent-2)); color:#020617; font-weight:900; box-shadow:0 10px 24px rgba(56,189,248,.18); }}
.brand-name {{ font-weight:800; letter-spacing:.01em; }}
.brand-sub {{ color:var(--muted); font-size:12px; margin-top:2px; }}
.nav {{ display:grid; gap:7px; }}
.nav a {{ position:relative; display:flex; align-items:center; gap:10px; min-height:40px; padding:8px 10px 8px 12px; border-radius:8px; color:var(--soft); font-size:14px; border:1px solid transparent; transition:background .18s ease,border-color .18s ease,color .18s ease,transform .18s ease,box-shadow .18s ease; }}
.nav a::before {{ content:""; position:absolute; left:0; top:50%; width:2px; height:18px; border-radius:999px; background:var(--accent); opacity:0; transform:translateY(-50%) scaleY(.55); transition:opacity .18s ease,transform .18s ease; }}
.nav a:hover {{ background:rgba(148,163,184,.12); color:var(--text); transform:translateX(1px); border-color:rgba(203,213,225,.08); }}
.nav a:hover::before,.nav a:focus-visible::before {{ opacity:.48; transform:translateY(-50%) scaleY(.86); }}
.nav a:focus-visible {{ background:rgba(56,189,248,.13); border-color:rgba(56,189,248,.34); box-shadow:0 0 0 3px rgba(56,189,248,.12); }}
.nav a:active {{ transform:translateX(1px) scale(.995); }}
.nav a.active {{ background:linear-gradient(90deg,rgba(56,189,248,.18),rgba(129,140,248,.08)); border-color:rgba(56,189,248,.26); color:#fff; box-shadow:inset 3px 0 0 var(--accent),0 8px 20px rgba(2,6,23,.18); }}
.nav a.active::before {{ opacity:1; transform:translateY(-50%) scaleY(1); }}
.nav-kicker {{ color:var(--muted); font-size:11px; text-transform:uppercase; font-weight:800; letter-spacing:.08em; margin:4px 10px; }}
.sidebar-footer {{ margin-top:auto; color:var(--muted); font-size:12px; line-height:1.5; padding:12px 10px; border-top:1px solid rgba(203,213,225,.09); }}
.workspace {{ min-width:0; height:100%; min-height:0; overflow:hidden; display:grid; grid-template-rows:auto minmax(0,1fr); }}
.topbar {{ position:relative; z-index:5; display:flex; justify-content:space-between; align-items:center; gap:18px; margin:8px 12px 0; padding:10px 14px; background:linear-gradient(135deg,rgba(15,23,42,.84),rgba(24,33,50,.72)); backdrop-filter:blur(20px); border:1px solid var(--border-card); border-radius:12px; box-shadow:var(--shadow-soft),var(--surface-inset-highlight); }}
.topbar-left {{ min-width:0; display:flex; align-items:center; gap:14px; }}
.topbar-title {{ min-width:0; }}
.topbar-status {{ display:inline-flex; align-items:center; gap:8px; min-height:28px; padding:4px 9px; border:1px solid rgba(34,197,94,.2); border-radius:999px; background:rgba(34,197,94,.09); color:#86efac; font-size:12px; font-weight:800; text-transform:uppercase; transition:background .18s ease,border-color .18s ease,color .18s ease,box-shadow .18s ease; }}
.topbar-status-dot {{ width:8px; height:8px; border-radius:50%; background:var(--good); box-shadow:0 0 14px rgba(34,197,94,.7); transition:opacity .18s ease,box-shadow .18s ease,transform .18s ease; }}
body.is-refreshing .topbar-status {{ border-color:rgba(56,189,248,.26); background:rgba(56,189,248,.09); color:#bae6fd; box-shadow:var(--surface-inset-highlight),0 0 16px rgba(56,189,248,.08); }}
body.is-refreshing .topbar-status-dot {{ opacity:.58; box-shadow:0 0 10px rgba(56,189,248,.44); transform:scale(.9); }}
.topbar-actions {{ display:flex; flex-wrap:wrap; justify-content:flex-end; gap:10px; color:var(--muted); font-size:13px; }}
.topbar-pill {{ display:inline-flex; align-items:center; min-height:30px; padding:5px 10px; border:1px solid var(--border-card); border-radius:999px; background:rgba(15,23,42,.7); box-shadow:var(--surface-inset-highlight); }}
.dashboard-main {{ height:100%; min-height:0; min-width:0; overflow:hidden; display:grid; grid-template-rows:minmax(0,1fr); padding:10px 14px 14px; }}
h1 {{ margin:0; font-size:25px; }}
.sub {{ color:var(--muted); margin-top:3px; }}
.page {{ display:none; }}
.page.active {{ height:100%; min-height:0; min-width:0; overflow:auto; display:grid; align-content:start; gap:8px; }}
.page-header {{ display:flex; justify-content:space-between; align-items:end; gap:18px; }}
.page-header > * {{ min-width:0; }}
.page-title {{ margin:0; font-size:22px; }}
.page-sub {{ color:var(--muted); margin-top:4px; }}
.command-meta {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
.page.active.operations-page {{ height:100%; min-height:0; overflow:hidden; grid-template-rows:auto auto auto minmax(0,1fr); align-content:stretch; }}
.ops-hero {{ min-height:0; overflow:visible; display:grid; grid-template-columns:minmax(360px,1.35fr) minmax(280px,.65fr); grid-template-areas:"hero actions" "stats stats"; gap:8px; align-items:stretch; min-width:0; }}
.hero-status {{ --hero-state-color:var(--accent); --hero-state-border:rgba(56,189,248,.2); --hero-state-wash:rgba(56,189,248,.14); --hero-state-glow:var(--glow-info); position:relative; overflow:hidden; min-height:68px; min-width:0; display:grid; align-content:start; padding:8px 12px; background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(17,24,39,.92)); border-left:5px solid var(--hero-state-color); }}
.ops-hero > .hero-status {{ grid-area:hero; }}
.hero-status::before {{ content:""; position:absolute; inset:0 0 auto; height:1px; background:linear-gradient(90deg,transparent,var(--hero-state-wash),rgba(255,255,255,.1),transparent); opacity:.9; pointer-events:none; z-index:0; }}
.hero-status::after {{ content:""; position:absolute; inset:auto -22% -70% 38%; height:180px; background:radial-gradient(circle,var(--hero-state-wash),transparent 68%); pointer-events:none; z-index:0; transition:background .22s ease,opacity .22s ease; }}
.hero-status > * {{ position:relative; z-index:1; }}
.hero-status.healthy {{ --hero-state-color:var(--good); --hero-state-border:rgba(34,197,94,.22); --hero-state-wash:rgba(34,197,94,.14); --hero-state-glow:var(--glow-good); border-left-color:var(--good); }} .hero-status.warning,.hero-status.busy {{ --hero-state-color:var(--warn); --hero-state-border:rgba(245,158,11,.22); --hero-state-wash:rgba(245,158,11,.13); --hero-state-glow:var(--glow-warn); border-left-color:var(--warn); }} .hero-status.critical,.hero-status.offline {{ --hero-state-color:var(--bad); --hero-state-border:rgba(239,68,68,.22); --hero-state-wash:rgba(239,68,68,.13); --hero-state-glow:var(--glow-bad); border-left-color:var(--bad); }}
.hero-kicker {{ color:var(--muted); font-size:11px; font-weight:800; letter-spacing:.11em; text-transform:uppercase; }}
.hero-title {{ display:flex; align-items:center; gap:10px; margin-top:3px; font-size:18px; line-height:1.05; font-weight:850; text-transform:uppercase; white-space:nowrap; }}
.hero-title span:last-child {{ min-width:0; overflow:hidden; text-overflow:ellipsis; }}
.hero-icon {{ font-size:17px; }}
.hero-copy {{ max-width:none; margin-top:3px; color:var(--soft); font-size:11px; line-height:1.22; }}
.hero-status .command-meta {{ gap:5px; margin-top:4px; }}
.hero-status .command-meta .badge {{ min-height:18px; padding:1px 6px; font-size:10px; }}
.hero-status #systemHealthCard {{ position:relative; z-index:1; margin-top:5px; min-height:0; padding:7px; background:linear-gradient(145deg,rgba(15,23,42,.72),rgba(30,41,59,.58)); box-shadow:none; }}
.ops-health-panel {{ display:grid; grid-template-rows:auto auto minmax(min-content,1fr); gap:8px; }}
.ops-health-panel::before {{ content:""; position:absolute; inset:0; background:radial-gradient(circle at 86% 10%,rgba(56,189,248,.14),transparent 38%); pointer-events:none; }}
.ops-health-panel > * {{ position:relative; z-index:1; }}
.ops-health-heading {{ display:flex; align-items:center; gap:8px; }}
.ops-health-heading svg,.ops-health-row svg {{ width:16px; height:16px; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; color:var(--row-state-color,var(--accent)); }}
.ops-health-row svg {{ grid-column:1; grid-row:1; align-self:center; width:14px; height:14px; }}
.ops-health-body {{ display:grid; grid-template-columns:minmax(0,1fr) 56px; gap:6px; align-items:center; }}
.ops-health-primary {{ display:grid; gap:4px; min-width:0; }}
.ops-state-pair {{ display:grid; grid-template-columns:minmax(0,.9fr) minmax(0,1fr); gap:6px; align-items:stretch; min-width:0; }}
.ops-state-column {{ min-width:0; display:grid; align-content:start; gap:2px; padding:5px 6px; border:1px solid rgba(203,213,225,.08); border-radius:8px; background:rgba(15,23,42,.34); box-shadow:var(--surface-inset-highlight); }}
.ops-state-kicker {{ color:var(--muted); font-size:9px; line-height:1; font-weight:850; letter-spacing:.08em; text-transform:uppercase; }}
.ops-health-status {{ font-size:18px; line-height:1; font-weight:850; }}
.ops-activity-summary {{ --activity-state-color:var(--accent); --activity-state-wash:rgba(56,189,248,.1); position:relative; overflow:hidden; border-color:rgba(56,189,248,.16); background:linear-gradient(135deg,var(--activity-state-wash),rgba(15,23,42,.34)); transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
.ops-activity-summary::after {{ content:""; position:absolute; inset:auto -28% -52% 42%; height:58px; background:radial-gradient(circle,var(--activity-state-wash),transparent 68%); opacity:.8; pointer-events:none; }}
.ops-activity-summary > * {{ position:relative; z-index:1; }}
.ops-activity-summary .ops-health-status {{ color:var(--activity-state-color); }}
.ops-activity-summary.starting,.ops-activity-summary.thinking,.ops-activity-summary.streaming,.ops-activity-summary.receiving,.ops-activity-summary.finalizing {{ --activity-state-color:var(--accent); --activity-state-wash:rgba(56,189,248,.12); border-color:rgba(56,189,248,.2); }}
.ops-activity-summary.ready,.ops-activity-summary.idle {{ --activity-state-color:var(--good); --activity-state-wash:rgba(34,197,94,.09); border-color:rgba(34,197,94,.16); }}
.ops-activity-summary.connecting {{ --activity-state-color:var(--warn); --activity-state-wash:rgba(245,158,11,.11); border-color:rgba(245,158,11,.2); }}
.ops-activity-summary.receiving,.ops-activity-summary.finalizing {{ animation:activityStatePulse .72s ease-out 1; }}
.ops-activity-summary.connecting .ops-health-status,.ops-activity-summary.thinking .ops-health-status {{ animation:activityStatusPulse 2.6s ease-in-out infinite; }}
.ops-activity-summary.streaming::after {{ animation:activityFlowWash 2.4s ease-in-out infinite; }}
@keyframes activityStatePulse {{ 0% {{ box-shadow:var(--surface-inset-highlight),0 0 0 0 rgba(56,189,248,.22); }} 100% {{ box-shadow:var(--surface-inset-highlight),0 0 0 8px rgba(56,189,248,0); }} }}
@keyframes activityStatusPulse {{ 0%,100% {{ opacity:.82; }} 50% {{ opacity:1; }} }}
@keyframes activityFlowWash {{ 0%,100% {{ transform:translateX(-8%); opacity:.36; }} 50% {{ transform:translateX(8%); opacity:.72; }} }}
.ops-health-message {{ font-size:11px; line-height:1.22; color:var(--soft); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.ops-activity-details {{ font-size:10px; line-height:1.15; color:var(--muted); display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }}
.ops-health-gauge {{ display:grid; justify-items:center; gap:3px; }}
.ops-health-gauge .gauge {{ width:40px; height:40px; }}
.ops-health-gauge-label {{ color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
.ops-health-details {{ display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:4px; align-items:stretch; min-height:0; }}
.ops-health-row {{ --row-state-color:var(--accent); --row-state-border:rgba(56,189,248,.18); --row-state-glow:var(--glow-info); position:relative; display:grid; grid-template-columns:14px minmax(0,1fr) max-content; grid-template-rows:auto auto auto; column-gap:5px; row-gap:2px; align-items:center; min-width:0; min-height:54px; height:auto; overflow:hidden; padding:4px 5px; border:1px solid var(--border-card); border-radius:8px; background:linear-gradient(180deg,rgba(15,23,42,.42),rgba(2,6,23,.24)); box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
.ops-health-row::before {{ content:""; position:absolute; left:0; top:0; bottom:0; width:2px; background:var(--row-state-color); opacity:.32; pointer-events:none; }}
.ops-health-row:has(.badge.positive),.ops-health-row:has(.badge.healthy),.ops-health-row:has(.badge.low),.ops-health-row:has(.badge.online),.ops-health-row:has(.badge.active),.ops-health-row:has(.badge.running) {{ --row-state-color:var(--good); --row-state-border:rgba(34,197,94,.2); --row-state-glow:var(--glow-good); }}
.ops-health-row:has(.badge.info),.ops-health-row:has(.badge.busy) {{ --row-state-color:var(--accent); --row-state-border:rgba(56,189,248,.2); --row-state-glow:var(--glow-info); }}
.ops-health-row:has(.badge.warning),.ops-health-row:has(.badge.medium),.ops-health-row:has(.badge.waiting),.ops-health-row:has(.badge.pending) {{ --row-state-color:var(--warn); --row-state-border:rgba(245,158,11,.2); --row-state-glow:var(--glow-warn); }}
.ops-health-row:has(.badge.critical),.ops-health-row:has(.badge.high),.ops-health-row:has(.badge.offline),.ops-health-row:has(.badge.error) {{ --row-state-color:var(--bad); --row-state-border:rgba(239,68,68,.2); --row-state-glow:var(--glow-bad); }}
.ops-health-row:hover,.ops-health-row:focus-within {{ border-color:var(--row-state-border); background:linear-gradient(180deg,rgba(30,41,59,.52),rgba(2,6,23,.3)); box-shadow:var(--surface-inset-highlight),var(--row-state-glow); }}
.ops-health-row-main {{ display:contents; min-width:0; }}
.ops-health-row-label {{ grid-column:2/4; grid-row:1; min-width:0; min-height:0; color:var(--soft); font-size:9px; line-height:1.08; font-weight:800; text-transform:uppercase; letter-spacing:.035em; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; text-overflow:clip; white-space:normal; }}
.ops-health-row-detail {{ grid-column:1/4; grid-row:2; position:static; min-width:0; color:var(--muted); font-size:9px; line-height:1.15; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.ops-health-row::after {{ grid-column:1/3; grid-row:3; align-self:center; min-width:0; color:var(--muted); font-size:7px; line-height:1; font-weight:800; letter-spacing:.04em; text-transform:uppercase; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.ops-health-row:nth-child(1)::after {{ content:"Proxy"; }}
.ops-health-row:nth-child(2)::after {{ content:"API"; }}
.ops-health-row:nth-child(3)::after {{ content:"Model"; }}
.ops-health-row:nth-child(4)::after {{ content:"Runtime"; }}
.ops-health-row:nth-child(5)::after {{ content:"Poll"; }}
.ops-health-row .badge {{ grid-column:3; grid-row:3; justify-self:end; align-self:center; position:static; max-width:100%; min-height:13px; padding:1px 5px; font-size:8px; line-height:1; white-space:nowrap; }}
.ops-hero > .action-panel {{ grid-area:actions; }}
.hero-stats-grid {{ grid-area:stats; display:grid; grid-template-columns:repeat(4,minmax(132px,1fr)); gap:8px; min-width:0; }}
.hero-stat-card {{ position:relative; overflow:hidden; min-height:74px; display:grid; align-content:space-between; gap:5px; padding:8px 10px; }}
.hero-stat-card::before {{ content:""; position:absolute; inset:0; background:linear-gradient(135deg,rgba(56,189,248,.1),transparent 42%); opacity:.82; pointer-events:none; }}
.hero-stat-card > * {{ position:relative; z-index:1; }}
.hero-stat-card:hover .hero-stat-icon,.hero-stat-card:focus-within .hero-stat-icon,.hero-stat-card:focus-visible .hero-stat-icon {{ transform:translateY(-1px); border-color:rgba(56,189,248,.34); background:rgba(56,189,248,.14); box-shadow:0 0 0 3px rgba(56,189,248,.06),var(--glow-info); }}
.hero-stat-card:focus-visible {{ outline:2px solid rgba(56,189,248,.68); outline-offset:2px; }}
.hero-stat-top {{ display:flex; align-items:center; justify-content:space-between; gap:10px; }}
.hero-stat-label {{ color:var(--soft); font-size:12px; font-weight:850; letter-spacing:.08em; text-transform:uppercase; }}
.hero-stat-icon {{ display:grid; place-items:center; width:30px; height:30px; border-radius:9px; color:var(--accent); background:rgba(56,189,248,.1); border:1px solid rgba(56,189,248,.2); transition:transform .18s ease,border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
.hero-stat-icon svg {{ width:18px; height:18px; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
.hero-stat-value {{ font-size:24px; line-height:.95; font-weight:850; letter-spacing:0; overflow-wrap:anywhere; transition:color .18s ease; }}
.hero-stat-desc {{ color:var(--muted); font-size:10px; line-height:1.12; }}
.hero-stat-hidden-binding {{ display:none; }}
.operations-lower {{ display:grid; grid-template-columns:minmax(0,2.2fr) minmax(240px,1.35fr) minmax(280px,1.45fr); grid-auto-rows:minmax(0,1fr); gap:10px; align-items:stretch; height:100%; min-height:0; min-width:0; overflow:hidden; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
.card {{ background:linear-gradient(180deg,rgba(24,33,50,.82),rgba(15,23,42,.76)); border:1px solid var(--border-card); border-radius:10px; padding:12px; box-shadow:var(--shadow),var(--surface-inset-highlight); backdrop-filter:blur(18px); transition:border-color .18s ease, transform .18s ease, background .18s ease,box-shadow .18s ease; }}
.card:hover {{ border-color:rgba(203,213,225,.16); background:linear-gradient(180deg,rgba(28,38,56,.86),rgba(15,23,42,.78)); box-shadow:var(--shadow-soft),var(--surface-inset-highlight); }}
.card:focus-within {{ border-color:rgba(56,189,248,.28); box-shadow:var(--shadow-soft),var(--surface-inset-highlight),0 0 0 1px rgba(56,189,248,.08); }}
.node:hover {{ border-color:var(--border-card-hot); transform:translateY(-1px); background:linear-gradient(180deg,rgba(30,41,59,.88),rgba(15,23,42,.8)); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--glow-info); }}
.card.hero-status,.card.hero-status:hover {{ background:radial-gradient(circle at 92% 0%,var(--hero-state-wash),transparent 38%),linear-gradient(135deg,rgba(15,23,42,.96),rgba(17,24,39,.92)); border-color:var(--hero-state-border); box-shadow:inset 5px 0 0 var(--hero-state-color),var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--hero-state-glow); transition:border-color .22s ease,background .22s ease,box-shadow .22s ease; }}
.card.hero-status:hover {{ transform:none; }}
.hero-stat-card:hover,.hero-stat-card:focus-within,.hero-stat-card:focus-visible {{ border-color:var(--border-card-hot); background:linear-gradient(180deg,rgba(30,41,59,.9),rgba(15,23,42,.82)); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--glow-info); transform:none; }}
.hero-stat-card:hover::before,.hero-stat-card:focus-within::before,.hero-stat-card:focus-visible::before {{ opacity:.92; }}
.hero-stat-card:hover .hero-stat-value,.hero-stat-card:focus-within .hero-stat-value,.hero-stat-card:focus-visible .hero-stat-value {{ color:#fff; }}
.card h2 {{ margin:0 0 7px; font-size:13px; letter-spacing:.02em; }}
.dashboard-card-header {{ display:flex; align-items:center; justify-content:space-between; gap:5px; min-width:0; min-height:18px; }}
.dashboard-card-title,.card h2.dashboard-card-title {{ flex:1 1 auto; min-width:0; margin:0; color:var(--soft); font-family:inherit; font-size:9.5px; line-height:18px; font-weight:850; letter-spacing:.055em; text-transform:uppercase; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.dashboard-card-header-actions {{ flex:0 0 auto; display:flex; align-items:center; justify-content:flex-end; gap:4px; min-width:0; }}
.dashboard-header-badge {{ display:inline-flex; align-items:center; justify-content:center; min-width:0; max-width:46px; min-height:16px; padding:0 5px; border-radius:999px; border:1px solid rgba(56,189,248,.18); color:#bfdbfe; background:rgba(56,189,248,.08); box-shadow:inset 0 1px 0 rgba(255,255,255,.05); font-size:9.5px; line-height:1; font-weight:850; letter-spacing:.015em; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.dashboard-header-badge.is-neutral {{ border-color:rgba(148,163,184,.16); color:var(--muted); background:rgba(15,23,42,.42); box-shadow:inset 0 1px 0 rgba(255,255,255,.035); }}
.ops-panel {{ min-height:0; overflow:hidden; }}
.operations-lower > .ops-panel {{ height:100%; overflow:hidden; }}
.compact-card {{ min-height:0; padding:11px; }}
.signal-card {{ min-height:112px; min-width:170px; display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.signal-card.ops-health-panel {{ display:grid; justify-content:stretch; }}
.signal-card h2,.signal-node .node-title {{ color:var(--soft); font-size:13px; text-transform:uppercase; letter-spacing:.08em; }}
.signal-card .value,.signal-node .value {{ font-size:29px; line-height:1; }}
.signal-body {{ display:grid; grid-template-columns:minmax(0,1fr) 46px; gap:6px; align-items:center; }}
.signal-stack {{ display:grid; gap:5px; min-width:0; }}
.gauge {{ width:46px; height:46px; transform:rotate(-90deg); }}
.gauge-track {{ fill:none; stroke:rgba(148,163,184,.18); stroke-width:10; }}
.gauge-progress {{ fill:none; stroke:var(--accent); stroke-width:10; stroke-linecap:round; stroke-dasharray:100; stroke-dashoffset:100; transition:stroke-dashoffset .55s ease, stroke .25s ease; }}
.instrument-panel {{ display:grid; grid-template-columns:repeat(5,minmax(148px,1fr)); gap:8px; min-width:0; align-items:stretch; }}
.system-activity-grid {{ display:grid; grid-template-columns:minmax(240px,.85fr) minmax(0,2.4fr); gap:8px; min-width:0; align-items:stretch; }}
.instrument-card {{ --instrument-accent:var(--accent); --instrument-gauge-w:128px; --instrument-gauge-h:74px; --instrument-support-line-h:14px; --instrument-reading-h:23px; position:relative; overflow:hidden; min-width:0; min-height:148px; display:grid; grid-template-rows:18px var(--instrument-gauge-h) var(--instrument-reading-h) calc((var(--instrument-support-line-h) * 3) + 4px); gap:5px; align-content:start; padding:10px; background:radial-gradient(circle at 50% -18%,rgba(56,189,248,.12),transparent 42%),linear-gradient(180deg,rgba(18,27,43,.96),rgba(12,18,31,.94)); border-color:rgba(148,163,184,.14); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight); }}
.instrument-card::before {{ content:""; position:absolute; inset:0 0 auto; height:1px; background:linear-gradient(90deg,transparent,rgba(203,213,225,.16),transparent); pointer-events:none; }}
.instrument-card > * {{ position:relative; z-index:1; }}
.instrument-card.healthy,.instrument-card.available,.instrument-card.completed,.instrument-card.ready {{ --instrument-accent:var(--good); }}
.instrument-card.moderate,.instrument-card.partial,.instrument-card.monitoring,.instrument-card.collecting {{ --instrument-accent:var(--accent); }}
.instrument-card.warning,.instrument-card.approaching,.instrument-card.waiting {{ --instrument-accent:var(--warn); }}
.instrument-card.critical,.instrument-card.error {{ --instrument-accent:var(--bad); }}
.instrument-card.disabled,.instrument-card.unavailable,.instrument-card.empty {{ --instrument-accent:var(--muted); }}
.instrument-info {{ flex:0 0 auto; display:grid; place-items:center; width:18px; height:18px; border-radius:50%; border:1px solid rgba(148,163,184,.18); color:var(--muted); font-size:11px; font-weight:850; background:rgba(15,23,42,.58); }}
.instrument-body {{ display:grid; justify-items:center; align-content:center; min-width:0; min-height:var(--instrument-gauge-h); }}
.instrument-reading {{ display:flex; align-items:center; justify-content:center; flex-wrap:nowrap; gap:5px 7px; min-width:0; min-height:var(--instrument-reading-h); text-align:center; }}
.instrument-reading.is-neutral {{ visibility:hidden; }}
.instrument-reading .badge {{ flex:0 0 auto; white-space:nowrap; }}
.instrument-card-value {{ color:#f8fafc; font-size:22px; line-height:1; font-weight:850; letter-spacing:-.02em; overflow-wrap:anywhere; white-space:nowrap; transition:color .18s ease; }}
.instrument-support {{ display:grid; grid-template-rows:repeat(3,var(--instrument-support-line-h)); gap:2px; min-width:0; min-height:calc((var(--instrument-support-line-h) * 3) + 4px); align-content:start; }}
.instrument-support-row {{ min-width:0; color:var(--muted); font-size:10px; line-height:var(--instrument-support-line-h); text-align:center; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.instrument-support-row.primary {{ color:#dbeafe; font-weight:750; }}
.instrument-support-row.model-source {{ display:flex; align-items:center; justify-content:center; gap:4px; }}
.instrument-support-model {{ min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.instrument-support-separator,.instrument-support-source {{ flex:0 0 auto; white-space:nowrap; }}
.instrument-support-source {{ color:#cbd5e1; }}
.instrument-gauge-shell {{ width:var(--instrument-gauge-w); max-width:100%; height:var(--instrument-gauge-h); display:grid; place-items:center; overflow:visible; }}
.instrument-gauge-svg {{ width:var(--instrument-gauge-w); max-width:100%; height:var(--instrument-gauge-h); overflow:visible; shape-rendering:geometricPrecision; }}
.instrument-gauge-segment {{ fill:none; stroke-width:9; stroke-linecap:butt; vector-effect:non-scaling-stroke; opacity:.9; }}
.instrument-gauge-segment.good {{ stroke:#22c55e; }} .instrument-gauge-segment.warn {{ stroke:#f59e0b; }} .instrument-gauge-segment.orange {{ stroke:#f97316; }} .instrument-gauge-segment.bad {{ stroke:#ef4444; }}
.instrument-gauge-baseline {{ fill:none; stroke:rgba(148,163,184,.16); stroke-width:11; stroke-linecap:round; vector-effect:non-scaling-stroke; }}
.instrument-gauge-tick {{ stroke:rgba(203,213,225,.22); stroke-width:1; vector-effect:non-scaling-stroke; }}
.instrument-gauge-needle {{ stroke:#e5e7eb; stroke-width:2.4; stroke-linecap:round; transform-origin:60px 60px; transform:rotate(-90deg); transition:transform .55s cubic-bezier(.2,0,0,1),stroke .18s ease,opacity .18s ease; filter:drop-shadow(0 0 5px rgba(226,232,240,.22)); vector-effect:non-scaling-stroke; }}
.instrument-gauge-pivot {{ fill:#0f172a; stroke:var(--instrument-accent); stroke-width:2; vector-effect:non-scaling-stroke; filter:drop-shadow(0 0 6px rgba(56,189,248,.24)); transition:stroke .18s ease; }}
.instrument-gauge-center {{ fill:#f8fafc; font-size:12px; font-weight:850; text-anchor:middle; dominant-baseline:middle; }}
.instrument-gauge-shell.is-unavailable .instrument-gauge-needle {{ opacity:.32; }}
.instrument-gauge-shell.is-unavailable .instrument-gauge-center {{ fill:var(--muted); }}
.instrument-trend-card {{ min-width:240px; grid-template-rows:auto 1fr; gap:7px; }}
.trend-body {{ display:grid; grid-template-rows:auto 1fr auto; gap:6px; min-width:0; }}
.trend-summary {{ display:flex; align-items:center; justify-content:space-between; gap:8px; min-width:0; }}
.trend-current {{ color:#f8fafc; font-size:20px; line-height:1; font-weight:850; }}
.trend-chart-wrap {{ position:relative; min-height:72px; border:1px solid rgba(148,163,184,.12); border-radius:8px; background:linear-gradient(180deg,rgba(15,23,42,.54),rgba(2,6,23,.28)); overflow:hidden; }}
.trend-chart {{ width:100%; height:72px; display:block; overflow:visible; }}
.trend-grid {{ stroke:rgba(148,163,184,.13); stroke-width:1; vector-effect:non-scaling-stroke; }}
.trend-threshold.warn {{ stroke:rgba(245,158,11,.62); }} .trend-threshold.critical {{ stroke:rgba(239,68,68,.58); }}
.trend-threshold {{ stroke-width:1; stroke-dasharray:4 5; vector-effect:non-scaling-stroke; }}
.trend-line {{ fill:none; stroke:var(--accent); stroke-width:2.4; stroke-linecap:round; stroke-linejoin:round; vector-effect:non-scaling-stroke; filter:drop-shadow(0 0 7px rgba(56,189,248,.26)); transition:points .28s ease,opacity .18s ease; }}
.trend-area {{ fill:rgba(56,189,248,.08); transition:points .28s ease,opacity .18s ease; }}
.trend-empty {{ position:absolute; inset:0; display:grid; place-items:center; padding:8px; color:#aebbd0; font-size:11px; text-align:center; background:rgba(15,23,42,.48); }}
.trend-footer {{ display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:6px; color:var(--muted); font-size:9px; line-height:1.15; }}
.sr-only {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }}
.health-card {{ --health-card-glow:var(--glow-info); border-left:5px solid var(--accent); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--health-card-glow); }}
.health-card.healthy {{ --health-card-glow:var(--glow-good); border-left-color:var(--good); }} .health-card.busy {{ --health-card-glow:var(--glow-info); border-left-color:var(--accent); }} .health-card.warning {{ --health-card-glow:var(--glow-warn); border-left-color:var(--warn); }} .health-card.critical,.health-card.offline {{ --health-card-glow:var(--glow-bad); border-left-color:var(--bad); }}
.health-card.healthy .gauge-progress {{ stroke:var(--good); }} .health-card.busy .gauge-progress {{ stroke:var(--accent); }} .health-card.warning .gauge-progress {{ stroke:var(--warn); }} .health-card.critical .gauge-progress,.health-card.offline .gauge-progress {{ stroke:var(--bad); }}
.health-title {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.mini-chart {{ width:100%; height:30px; margin-top:5px; }}
.sparkline {{ fill:none; stroke:var(--accent); stroke-width:2.5; stroke-linecap:round; stroke-linejoin:round; filter:drop-shadow(0 0 8px rgba(56,189,248,.28)); transition:points .3s ease; }}
.spark-area {{ fill:rgba(56,189,248,.08); }}
.value-pop {{ animation:valuePop .28s ease; }}
@keyframes valuePop {{ 0% {{ transform:translateY(0); color:var(--text); }} 45% {{ transform:translateY(-1px); color:#ffffff; }} 100% {{ transform:translateY(0); color:inherit; }} }}
.icon-label {{ display:inline-flex; align-items:center; gap:8px; }}
.icon-mark {{ color:var(--accent); font-size:14px; }}
.badge {{ --badge-ring:rgba(148,163,184,.18); --badge-glow:0 0 12px rgba(148,163,184,.07); display:inline-flex; align-items:center; min-height:22px; padding:2px 7px; border-radius:999px; font-size:11px; font-weight:700; text-transform:uppercase; background:rgba(148,163,184,.16); color:var(--muted); box-shadow:inset 0 0 0 1px var(--badge-ring),var(--surface-inset-highlight),var(--badge-glow); transition:background .18s ease,box-shadow .18s ease,color .18s ease,opacity .18s ease,transform .14s ease; }}
.badge.positive,.badge.healthy,.badge.low,.badge.online,.badge.active,.badge.running,.badge.ready,.badge.idle,.badge.available,.badge.completed {{ --badge-ring:rgba(34,197,94,.22); --badge-glow:0 0 14px rgba(34,197,94,.1); color:var(--good); background:rgba(34,197,94,.12); }} .badge.info,.badge.busy,.badge.starting,.badge.receiving,.badge.thinking,.badge.streaming,.badge.finalizing,.badge.moderate,.badge.partial,.badge.monitoring,.badge.collecting {{ --badge-ring:rgba(56,189,248,.22); --badge-glow:0 0 14px rgba(56,189,248,.1); color:var(--accent); background:rgba(56,189,248,.12); }} .badge.warning,.badge.medium,.badge.waiting,.badge.pending,.badge.connecting,.badge.approaching {{ --badge-ring:rgba(245,158,11,.24); --badge-glow:0 0 14px rgba(245,158,11,.1); color:var(--warn); background:rgba(245,158,11,.12); }} .badge.critical,.badge.high,.badge.offline,.badge.error {{ --badge-ring:rgba(239,68,68,.24); --badge-glow:0 0 14px rgba(239,68,68,.1); color:var(--bad); background:rgba(239,68,68,.12); }} .badge.disabled,.badge.unavailable,.badge.empty {{ --badge-ring:rgba(148,163,184,.2); --badge-glow:0 0 10px rgba(148,163,184,.06); color:var(--muted); background:rgba(148,163,184,.12); }}
a.badge:hover {{ transform:translateY(-1px); box-shadow:inset 0 0 0 1px var(--badge-ring),var(--surface-inset-highlight),var(--badge-glow),0 0 0 3px rgba(56,189,248,.08); }}
a.badge:active {{ transform:translateY(0); opacity:.86; }}
a.badge:focus-visible {{ outline:2px solid rgba(56,189,248,.72); outline-offset:2px; box-shadow:inset 0 0 0 1px var(--badge-ring),var(--surface-inset-highlight),var(--badge-glow),0 0 0 3px rgba(56,189,248,.12); }}
.badge-update {{ animation:badgeSettle .3s ease-out 1; }}
@keyframes badgeSettle {{ 0% {{ transform:scale(.985); }} 45% {{ transform:scale(1.015); }} 100% {{ transform:scale(1); }} }}
.panel-list {{ display:grid; gap:8px; }}
.panel-item {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; background:rgba(15,23,42,.46); border:1px solid var(--border-card); border-radius:8px; padding:7px 9px; box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease, background .18s ease,box-shadow .18s ease; }}
.panel-item > * {{ min-width:0; }}
.panel-item span:first-child {{ overflow-wrap:anywhere; }}
.panel-item:hover,.timeline-item:hover,.message:hover {{ border-color:rgba(129,140,248,.24); background:rgba(15,23,42,.68); box-shadow:var(--surface-inset-highlight),0 0 16px rgba(129,140,248,.09); }}
.timeline-list {{ display:grid; gap:8px; }}
.timeline-item {{ display:grid; grid-template-columns:86px 1fr; gap:10px; align-items:start; background:rgba(15,23,42,.46); border:1px solid var(--border-card); border-radius:8px; padding:9px 10px; box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease, background .18s ease,box-shadow .18s ease; }}
.panel-list > .muted,.timeline-list > .muted,#activeRecentMessages > .muted {{ min-height:48px; display:grid; place-items:center; text-align:center; border:1px dashed rgba(148,163,184,.28); border-radius:8px; background:rgba(15,23,42,.32); color:#aebbd0; }}
.action-panel .panel-list {{ max-height:none; overflow:visible; }}
.action-panel .small {{ display:none; }}
.activity-card {{ overflow-y:auto; overflow-x:hidden; }}
.activity-card tbody:empty::after {{ content:"No request activity yet."; display:block; padding:18px; color:var(--muted); }}
.risk-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }}
.risk-row:empty {{ display:none; }}
.value {{ font-size:28px; font-weight:750; overflow-wrap:anywhere; }}
.muted {{ color:var(--muted); overflow-wrap:anywhere; }}
.ok {{ color:var(--good); }} .warn {{ color:var(--warn); }} .bad {{ color:var(--bad); }}
.settings-page {{ gap:12px; padding-bottom:2px; }}
.settings-page [hidden] {{ display:none !important; }}
.settings-runtime-notice {{ display:grid; grid-template-columns:auto minmax(0,1fr); gap:10px; align-items:start; padding:12px 14px; border:1px solid rgba(245,158,11,.28); border-left:4px solid var(--warn); border-radius:10px; background:linear-gradient(135deg,rgba(245,158,11,.12),rgba(15,23,42,.62)); box-shadow:var(--surface-inset-highlight),var(--glow-warn); }}
.settings-runtime-icon {{ display:grid; place-items:center; width:26px; height:26px; border-radius:50%; color:#fde68a; background:rgba(245,158,11,.16); border:1px solid rgba(245,158,11,.28); font-weight:900; }}
.settings-runtime-title {{ margin:0; color:#fde68a; font-size:13px; line-height:1.35; font-weight:850; }}
.settings-runtime-copy {{ margin:3px 0 0; color:var(--soft); font-size:12px; line-height:1.45; overflow-wrap:anywhere; }}
.settings-status,.settings-feedback {{ min-width:0; padding:9px 11px; border:1px solid rgba(56,189,248,.16); border-radius:8px; background:rgba(56,189,248,.07); color:#bae6fd; font-size:12px; line-height:1.4; overflow-wrap:anywhere; }}
.settings-status.success {{ border-color:rgba(34,197,94,.22); background:rgba(34,197,94,.08); color:#bbf7d0; }}
.settings-status.warning {{ border-color:rgba(245,158,11,.24); background:rgba(245,158,11,.08); color:#fde68a; }}
.settings-feedback-error {{ border-color:rgba(239,68,68,.28); background:rgba(239,68,68,.1); color:#fecaca; }}
.settings-connection-test {{ min-width:0; display:grid; gap:9px; padding:11px; border:1px solid rgba(56,189,248,.16); border-radius:9px; background:rgba(2,6,23,.34); box-shadow:var(--surface-inset-highlight); }}
.settings-connection-test-header {{ min-width:0; display:flex; align-items:flex-start; justify-content:space-between; gap:10px; }}
.settings-connection-test-heading {{ min-width:0; }}
.settings-connection-test-title {{ margin:0; color:var(--soft); font-size:13px; line-height:1.3; font-weight:850; }}
.settings-connection-test-copy {{ margin:3px 0 0; color:var(--muted); font-size:11px; line-height:1.4; overflow-wrap:anywhere; }}
.settings-connection-result {{ min-width:0; display:grid; gap:7px; padding:10px; border:1px solid rgba(148,163,184,.2); border-radius:8px; background:rgba(15,23,42,.52); }}
.settings-connection-result.testing {{ border-color:rgba(56,189,248,.25); color:#bae6fd; }}
.settings-connection-result.success {{ border-color:rgba(34,197,94,.26); background:rgba(34,197,94,.07); }}
.settings-connection-result.failure {{ border-color:rgba(239,68,68,.28); background:rgba(239,68,68,.08); }}
.settings-connection-result-title {{ color:var(--soft); font-size:12px; line-height:1.35; font-weight:850; }}
.settings-connection-result.success .settings-connection-result-title {{ color:#bbf7d0; }}
.settings-connection-result.failure .settings-connection-result-title {{ color:#fecaca; }}
.settings-connection-result-message,.settings-connection-result-note {{ color:var(--soft); font-size:11px; line-height:1.4; overflow-wrap:anywhere; }}
.settings-connection-result-note {{ color:var(--muted); }}
.settings-connection-result-details {{ display:grid; grid-template-columns:minmax(100px,max-content) minmax(0,1fr); gap:4px 10px; margin:0; font-size:10px; line-height:1.35; }}
.settings-connection-result-details dt {{ color:var(--muted); font-weight:800; }}
.settings-connection-result-details dd {{ min-width:0; margin:0; color:var(--soft); overflow-wrap:anywhere; }}
.settings-state {{ min-height:150px; display:grid; place-items:center; align-content:center; gap:10px; padding:24px; border:1px dashed rgba(148,163,184,.28); border-radius:10px; background:rgba(15,23,42,.38); text-align:center; }}
.settings-state-title {{ color:var(--soft); font-size:15px; font-weight:800; }}
.settings-state-detail {{ max-width:620px; color:var(--muted); font-size:12px; line-height:1.45; }}
.settings-form {{ display:grid; gap:12px; min-width:0; }}
.settings-categories {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr)); gap:12px; min-width:0; align-items:start; }}
.settings-category {{ min-width:0; display:grid; gap:12px; align-content:start; padding:14px; }}
.settings-category-header {{ min-width:0; display:flex; align-items:flex-start; justify-content:space-between; gap:10px; padding-bottom:10px; border-bottom:1px solid rgba(203,213,225,.1); }}
.settings-category-heading {{ min-width:0; }}
.settings-category-title {{ margin:0; color:#f8fafc; font-size:16px; line-height:1.25; }}
.settings-category-description {{ margin:4px 0 0; color:var(--muted); font-size:12px; line-height:1.4; overflow-wrap:anywhere; }}
.settings-list {{ display:grid; gap:10px; min-width:0; }}
.settings-list-connection {{ container-name:settings-connection; container-type:inline-size; }}
.settings-item {{ min-width:0; display:grid; grid-template-columns:minmax(0,1fr) minmax(180px,260px); gap:14px; align-items:start; padding:11px; border:1px solid rgba(203,213,225,.1); border-radius:9px; background:rgba(15,23,42,.42); box-shadow:var(--surface-inset-highlight); }}
.settings-item:focus-within {{ border-color:rgba(56,189,248,.3); box-shadow:var(--surface-inset-highlight),0 0 0 2px rgba(56,189,248,.08); }}
.settings-item-meta,.settings-control-panel {{ min-width:0; }}
.settings-label-row {{ display:flex; flex-wrap:wrap; align-items:center; gap:6px; }}
.settings-label {{ color:var(--text); font-size:13px; line-height:1.3; font-weight:800; cursor:pointer; overflow-wrap:anywhere; }}
.settings-item-description {{ margin:4px 0 0; color:var(--muted); font-size:11px; line-height:1.4; overflow-wrap:anywhere; }}
.settings-metadata {{ min-width:0; display:flex; flex-wrap:wrap; gap:6px 10px; margin-top:7px; color:#aebbd0; font-size:10px; line-height:1.35; }}
.settings-metadata > span {{ min-width:0; overflow-wrap:anywhere; }}
.settings-control-panel {{ display:grid; gap:6px; align-content:start; }}
.settings-reset-setting {{ justify-self:start; min-height:30px; padding:5px 9px; font-size:11px; }}
.settings-input {{ width:100%; min-width:0; height:38px; padding:7px 9px; border:1px solid rgba(148,163,184,.28); border-radius:8px; outline:none; background:rgba(2,6,23,.52); color:var(--text); font:inherit; font-size:13px; transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
.settings-input:hover:not(:disabled) {{ border-color:rgba(148,163,184,.46); background:rgba(2,6,23,.68); }}
.settings-input:focus-visible,.settings-checkbox:focus-visible {{ outline:2px solid rgba(56,189,248,.72); outline-offset:2px; }}
.settings-input:focus {{ border-color:rgba(56,189,248,.52); box-shadow:0 0 0 3px rgba(56,189,248,.1); }}
.settings-input[aria-invalid="true"] {{ border-color:rgba(239,68,68,.62); box-shadow:0 0 0 2px rgba(239,68,68,.1); }}
.settings-input:disabled,.settings-checkbox:disabled {{ cursor:not-allowed; opacity:.62; }}
.settings-checkbox-row {{ min-height:38px; display:flex; align-items:center; gap:9px; padding:7px 9px; border:1px solid rgba(148,163,184,.2); border-radius:8px; background:rgba(2,6,23,.38); }}
.settings-checkbox {{ width:19px; height:19px; flex:0 0 auto; margin:0; accent-color:var(--accent); }}
.settings-checkbox-state {{ color:var(--soft); font-size:12px; font-weight:750; }}
.settings-field-note {{ color:var(--muted); font-size:10px; line-height:1.35; overflow-wrap:anywhere; }}
.settings-difference {{ color:var(--muted); font-size:10px; line-height:1.35; overflow-wrap:anywhere; }}
.settings-difference.warning {{ color:#fde68a; }}
.settings-difference.success {{ color:#bbf7d0; }}
.settings-field-error {{ color:#fecaca; font-size:11px; line-height:1.35; overflow-wrap:anywhere; }}
.settings-action-bar {{ position:sticky; z-index:3; bottom:0; min-width:0; display:flex; align-items:center; justify-content:space-between; gap:12px; padding:11px 12px; border:1px solid rgba(203,213,225,.13); border-radius:10px; background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(24,33,50,.94)); box-shadow:0 -10px 28px rgba(2,6,23,.3),var(--surface-inset-highlight); backdrop-filter:blur(18px); }}
.settings-dirty-summary {{ min-width:0; color:var(--muted); font-size:12px; line-height:1.35; overflow-wrap:anywhere; }}
.settings-actions {{ flex:0 0 auto; display:flex; flex-wrap:wrap; justify-content:flex-end; gap:8px; }}
.settings-button {{ min-height:36px; padding:7px 13px; border:1px solid rgba(148,163,184,.28); border-radius:8px; color:var(--soft); background:rgba(15,23,42,.72); font-weight:800; cursor:pointer; transition:border-color .18s ease,background .18s ease,color .18s ease,box-shadow .18s ease,transform .14s ease; }}
.settings-button:hover:not(:disabled) {{ border-color:rgba(56,189,248,.38); background:rgba(56,189,248,.12); color:#fff; transform:translateY(-1px); }}
.settings-button.primary {{ border-color:rgba(56,189,248,.4); background:linear-gradient(135deg,rgba(14,165,233,.78),rgba(79,70,229,.74)); color:#fff; box-shadow:0 8px 18px rgba(14,165,233,.16); }}
.settings-button.primary:hover:not(:disabled) {{ background:linear-gradient(135deg,rgba(14,165,233,.92),rgba(79,70,229,.88)); }}
.settings-button.recovery {{ border-color:rgba(245,158,11,.3); color:#fde68a; background:rgba(245,158,11,.08); }}
.settings-button.recovery:hover:not(:disabled) {{ border-color:rgba(245,158,11,.5); background:rgba(245,158,11,.14); color:#fff7d6; }}
.settings-button.compact {{ min-height:30px; flex:0 0 auto; padding:5px 9px; font-size:11px; }}
.settings-button:disabled {{ cursor:not-allowed; opacity:.5; box-shadow:none; transform:none; }}
.settings-button:focus-visible {{ outline:2px solid rgba(56,189,248,.72); outline-offset:2px; }}
@media (prefers-reduced-motion: reduce) {{ .settings-button,.settings-input {{ transition:none; }} .settings-button:hover:not(:disabled) {{ transform:none; }} }}
@container settings-connection (max-width: 480px) {{ .settings-item {{ grid-template-columns:1fr; gap:9px; }} }}
@media (max-width: 700px) {{ .settings-runtime-notice {{ grid-template-columns:1fr; }} .settings-runtime-icon {{ display:none; }} .settings-category {{ padding:11px; }} .settings-category-header,.settings-connection-test-header {{ align-items:stretch; flex-direction:column; }} .settings-category-header .settings-button,.settings-connection-test-header .settings-button {{ align-self:flex-start; }} .settings-item {{ grid-template-columns:1fr; gap:9px; }} .settings-connection-result-details {{ grid-template-columns:1fr; gap:2px; }} .settings-connection-result-details dd + dt {{ margin-top:4px; }} .settings-action-bar {{ align-items:stretch; flex-direction:column; }} .settings-actions {{ width:100%; }} .settings-button {{ flex:1 1 130px; }} .settings-reset-setting,.settings-button.compact {{ flex:0 0 auto; }} }}
.bar {{ height:12px; border-radius:999px; background:#334155; overflow:hidden; margin:10px 0; }}
.fill {{ height:100%; background:var(--accent); width:0%; transition:width .25s ease; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; table-layout:fixed; }}
th,td {{ text-align:left; vertical-align:top; padding:7px 8px; border-bottom:1px solid rgba(255,255,255,.08); overflow-wrap:anywhere; word-break:break-word; }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }}
.flow-panel {{ --topology-flow-duration:1300ms; --topology-return-duration:1200ms; position:relative; display:grid; grid-template-rows:auto auto; gap:10px; min-height:0; overflow:hidden; padding:13px 14px; background:linear-gradient(145deg,rgba(15,23,42,.96),rgba(24,33,50,.86)); }}
.flow-panel::before {{ content:""; position:absolute; inset:46px 14px 14px; border:1px solid rgba(56,189,248,.08); border-radius:10px; pointer-events:none; }}
.flow-panel::after {{ content:""; position:absolute; inset:0; background:radial-gradient(circle at 50% 0%,rgba(56,189,248,.11),transparent 42%); pointer-events:none; }}
.flow-panel > * {{ position:relative; z-index:1; }}
.flow-heading {{ display:flex; align-items:center; gap:9px; }}
.flow-heading svg {{ width:17px; height:17px; stroke:var(--accent); fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
.flow-stage {{ position:relative; display:grid; grid-template-columns:minmax(126px,1fr) 24px minmax(126px,1fr) 24px minmax(126px,1fr) 24px minmax(126px,1fr); gap:6px; align-items:stretch; min-width:0; min-height:auto; }}
.flow-stage::after {{ content:""; position:absolute; inset:-2px 0; z-index:0; pointer-events:none; border-radius:12px; background:linear-gradient(90deg,transparent,rgba(56,189,248,.2),transparent); opacity:0; transform:translateX(-70%); }}
.flow-svg-layer {{ position:absolute; inset:0; width:100%; height:100%; pointer-events:none; z-index:0; overflow:visible; }}
.flow-stage > .flow-node,.flow-stage > .pipe {{ position:relative; z-index:1; }}
.flow-svg-line {{ fill:none; stroke:rgba(148,163,184,.22); stroke-width:2; stroke-linecap:round; vector-effect:non-scaling-stroke; transition:stroke .24s cubic-bezier(.2,0,0,1),filter .24s cubic-bezier(.2,0,0,1),opacity .24s ease; }}
.flow-svg-line.flow-line-active {{ stroke:rgba(56,189,248,.72); filter:drop-shadow(0 0 5px rgba(56,189,248,.28)); }}
.flow-svg-line.flow-line-waiting {{ stroke:rgba(245,158,11,.42); stroke-dasharray:5 8; }}
.flow-svg-line.flow-line-offline {{ stroke:rgba(239,68,68,.36); stroke-dasharray:3 8; }}
.flow-svg-packet,.flow-svg-packet-halo {{ opacity:0; offset-path:path("M 55 90 C 180 90 200 90 325 90 C 450 90 470 90 595 90 C 720 90 740 90 945 90"); offset-rotate:0deg; }}
.flow-svg-packet {{ fill:#f0f9ff; stroke:var(--accent); stroke-width:2; filter:drop-shadow(0 0 9px rgba(56,189,248,.72)); }}
.flow-svg-packet-halo {{ fill:rgba(56,189,248,.16); stroke:rgba(186,230,253,.68); stroke-width:1.6; filter:drop-shadow(0 0 12px rgba(56,189,248,.38)); }}
.flow-panel.flow-active .flow-svg-packet,.flow-panel.flow-active .flow-svg-packet-halo,.flow-panel.flow-waiting .flow-svg-packet,.flow-panel.flow-waiting .flow-svg-packet-halo,.flow-panel.flow-offline .flow-svg-packet,.flow-panel.flow-offline .flow-svg-packet-halo,.flow-panel.traffic-idle .flow-svg-packet,.flow-panel.traffic-idle .flow-svg-packet-halo,.flow-panel.traffic-processing .flow-svg-packet,.flow-panel.traffic-processing .flow-svg-packet-halo {{ opacity:0; animation:none; }}
.flow-panel.flow-waiting .flow-svg-packet {{ fill:#fffbeb; stroke:var(--warn); }}
.flow-panel.activity-thinking .flow-svg-line.flow-line-active,.flow-panel.activity-receiving .flow-svg-line.flow-line-active {{ stroke:rgba(125,211,252,.78); filter:drop-shadow(0 0 6px rgba(56,189,248,.3)); }}
.flow-panel.activity-finalizing .pipe::after {{ background:rgba(125,211,252,.72); box-shadow:0 0 18px rgba(56,189,248,.4); }}
.flow-panel.traffic-outbound .flow-stage::after {{ animation:flowStageOutbound var(--topology-flow-duration) ease-out 1; }}
.flow-panel.traffic-inbound .flow-stage::after {{ animation:flowStageInbound var(--topology-return-duration) ease-out 1; background:linear-gradient(90deg,transparent,rgba(167,139,250,.2),transparent); }}
.flow-panel.traffic-outbound .flow-svg-packet {{ fill:#f0f9ff; stroke:var(--accent); opacity:.98; animation:flowPacketOutbound var(--topology-flow-duration) cubic-bezier(.2,0,0,1) 1; }}
.flow-panel.traffic-outbound .flow-svg-packet-halo {{ fill:rgba(56,189,248,.16); stroke:rgba(186,230,253,.72); opacity:.74; animation:flowPacketOutbound var(--topology-flow-duration) cubic-bezier(.2,0,0,1) 1; }}
.flow-panel.traffic-inbound .flow-svg-packet {{ fill:#faf5ff; stroke:#a78bfa; opacity:.98; animation:flowPacketInbound var(--topology-return-duration) cubic-bezier(.2,0,0,1) 1; }}
.flow-panel.traffic-inbound .flow-svg-packet-halo {{ fill:rgba(167,139,250,.16); stroke:rgba(221,214,254,.72); opacity:.74; animation:flowPacketInbound var(--topology-return-duration) cubic-bezier(.2,0,0,1) 1; }}
.flow-panel.traffic-outbound .flow-svg-line.flow-line-active,.flow-panel.traffic-outbound .flow-svg-line.flow-line-waiting {{ stroke:rgba(125,211,252,.86); filter:drop-shadow(0 0 7px rgba(56,189,248,.36)); }}
.flow-panel.traffic-inbound .flow-svg-line.flow-line-active,.flow-panel.traffic-inbound .flow-svg-line.flow-line-waiting {{ stroke:rgba(167,139,250,.82); filter:drop-shadow(0 0 7px rgba(167,139,250,.32)); }}
.flow-panel.traffic-outbound [data-flow-link] {{ background:linear-gradient(90deg,rgba(45,58,79,.35),rgba(125,211,252,.9),rgba(45,58,79,.35)); }}
.flow-panel.traffic-inbound [data-flow-link] {{ background:linear-gradient(270deg,rgba(45,58,79,.35),rgba(167,139,250,.86),rgba(45,58,79,.35)); }}
.flow-panel.traffic-outbound [data-flow-link]::after {{ animation:pipeTrafficPulse var(--topology-flow-duration) ease-out 1; background:rgba(125,211,252,.82); box-shadow:0 0 22px rgba(56,189,248,.54); }}
.flow-panel.traffic-inbound [data-flow-link]::after {{ animation:pipeTrafficPulse var(--topology-return-duration) ease-out 1; background:rgba(167,139,250,.78); box-shadow:0 0 22px rgba(167,139,250,.46); }}
.flow-panel.traffic-processing [data-flow-segment="ollama-model"] {{ stroke:rgba(125,211,252,.86); filter:drop-shadow(0 0 8px rgba(56,189,248,.32)); animation:processingLinePulse 2400ms ease-in-out infinite; }}
.flow-panel.traffic-processing [data-flow-link="ollama-model"]::after {{ background:rgba(125,211,252,.7); box-shadow:0 0 18px rgba(56,189,248,.36); animation:processingNodePulse 2600ms ease-in-out infinite; }}
.flow-panel.traffic-processing [data-flow-node="ollama"],.flow-panel.traffic-processing [data-flow-node="model"] {{ border-color:rgba(56,189,248,.28); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),0 0 14px rgba(56,189,248,.12); }}
.flow-panel.traffic-outbound .flow-node,.flow-panel.traffic-inbound .flow-node {{ border-color:rgba(56,189,248,.32); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--glow-info); }}
.flow-panel.traffic-inbound .flow-node {{ border-color:rgba(167,139,250,.28); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),0 0 18px rgba(167,139,250,.14); }}
.flow-panel.traffic-outbound .flow-node-icon,.flow-panel.traffic-inbound .flow-node-icon {{ border-color:rgba(56,189,248,.34); background:rgba(56,189,248,.14); box-shadow:0 0 0 3px rgba(56,189,248,.06),var(--glow-info); }}
.flow-panel.traffic-inbound .flow-node-icon {{ border-color:rgba(167,139,250,.3); background:rgba(167,139,250,.12); box-shadow:0 0 0 3px rgba(167,139,250,.06),0 0 18px rgba(167,139,250,.16); }}
.flow-node.status-pulse {{ animation:nodeStatusPulse 700ms ease-out 1; }}
@keyframes flowPacketOutbound {{ 0% {{ offset-distance:0%; opacity:0; }} 12% {{ opacity:1; }} 82% {{ opacity:1; }} 100% {{ offset-distance:100%; opacity:0; }} }}
@keyframes flowPacketInbound {{ 0% {{ offset-distance:100%; opacity:0; }} 12% {{ opacity:1; }} 82% {{ opacity:1; }} 100% {{ offset-distance:0%; opacity:0; }} }}
@keyframes flowStageOutbound {{ 0% {{ opacity:0; transform:translateX(-70%); }} 18% {{ opacity:.68; }} 72% {{ opacity:.26; }} 100% {{ opacity:0; transform:translateX(70%); }} }}
@keyframes flowStageInbound {{ 0% {{ opacity:0; transform:translateX(70%); }} 18% {{ opacity:.62; }} 72% {{ opacity:.24; }} 100% {{ opacity:0; transform:translateX(-70%); }} }}
@keyframes pipeTrafficPulse {{ 0% {{ transform:translate(-50%,-50%) scale(.92); opacity:.74; }} 32% {{ transform:translate(-50%,-50%) scale(1.28); opacity:1; }} 100% {{ transform:translate(-50%,-50%) scale(1); opacity:.86; }} }}
@keyframes processingLinePulse {{ 0%,100% {{ opacity:.8; }} 50% {{ opacity:1; }} }}
@keyframes processingNodePulse {{ 0%,100% {{ transform:translate(-50%,-50%) scale(.96); opacity:.72; }} 50% {{ transform:translate(-50%,-50%) scale(1.16); opacity:1; }} }}
@keyframes nodeStatusPulse {{ 0% {{ transform:translateY(0); }} 35% {{ transform:translateY(-1px); border-color:rgba(56,189,248,.38); }} 100% {{ transform:translateY(0); }} }}
.flow-note {{ color:var(--muted); font-size:12px; }}
.node {{ position:relative; background:radial-gradient(circle at 50% 0%,rgba(56,189,248,.13),transparent 46%),rgba(15,23,42,.92); border:1px solid var(--border-card); border-radius:8px; padding:12px; min-width:0; min-height:118px; box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight); transition:border-color .18s ease, transform .18s ease, background .18s ease,box-shadow .18s ease; }}
.node::before {{ content:""; display:block; width:46px; height:46px; margin:0 auto 10px; border-radius:50%; border:1px solid rgba(56,189,248,.32); background:rgba(2,6,23,.44); box-shadow:0 0 0 8px rgba(56,189,248,.06); }}
.node .node-title,.node .value,.node .small {{ position:relative; text-align:center; }}
.flow-node {{ display:grid; grid-template-rows:auto 1fr auto; gap:4px; min-height:114px; padding:6px; border-radius:10px; border-color:var(--border-card); background:linear-gradient(180deg,rgba(30,41,59,.72),rgba(15,23,42,.9)); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight); transition:border-color .18s ease,transform .18s ease,background .18s ease,box-shadow .18s ease; }}
.flow-node::before {{ display:none; }}
.flow-node-head {{ display:flex; align-items:center; justify-content:space-between; gap:10px; }}
.flow-node-title {{ display:flex; align-items:center; gap:8px; min-width:0; color:var(--soft); font-size:10px; font-weight:850; letter-spacing:.05em; text-transform:uppercase; }}
.flow-node-icon {{ display:grid; place-items:center; width:24px; height:24px; border-radius:7px; color:var(--accent); background:rgba(56,189,248,.1); border:1px solid rgba(56,189,248,.18); }}
.flow-node-icon svg {{ width:14px; height:14px; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
.flow-node-main {{ display:grid; align-content:center; gap:5px; min-width:0; }}
.flow-node-main .value {{ font-size:16px; line-height:1; font-weight:850; text-align:left; }}
.flow-node-main .small {{ text-align:left; font-size:10px; line-height:1.16; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
.flow-node-foot {{ display:flex; align-items:center; justify-content:space-between; gap:8px; padding-top:5px; border-top:1px solid rgba(203,213,225,.08); }}
.flow-endpoint {{ min-width:0; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--muted); font-size:11px; }}
.flow-status {{ flex:0 0 auto; }}
.signal-node {{ display:flex; flex-direction:column; justify-content:space-between; background:linear-gradient(180deg,rgba(30,41,59,.96),rgba(15,23,42,.92)); }}
.signal-node.flow-node {{ display:grid; justify-content:stretch; }}
.node-title {{ font-weight:800; font-size:14px; margin-bottom:8px; }}
.dot {{ display:inline-block; width:12px; height:12px; border-radius:99px; background:var(--warn); margin-right:8px; box-shadow:0 0 16px currentColor; animation:statusPulse 2.4s ease-in-out infinite; transition:background .2s ease,color .2s ease,box-shadow .2s ease,opacity .2s ease; }}
.dot.online {{ background:var(--good); color:var(--good); }} .dot.waiting {{ background:var(--warn); color:var(--warn); }} .dot.offline {{ background:var(--bad); color:var(--bad); animation:none; opacity:.86; }}
@keyframes statusPulse {{ 0%,100% {{ opacity:.72; }} 50% {{ opacity:1; }} }}
.pipe {{ position:relative; height:2px; align-self:center; background:linear-gradient(90deg,rgba(45,58,79,.35),rgba(56,189,248,.85),rgba(45,58,79,.35)); border-radius:99px; opacity:.9; }}
.pipe::before {{ content:""; position:absolute; inset:-12px 0; border-top:1px dashed rgba(148,163,184,.22); top:50%; }}
.pipe::after {{ content:""; position:absolute; left:50%; top:50%; width:10px; height:10px; border-radius:50%; transform:translate(-50%,-50%); background:rgba(56,189,248,.5); box-shadow:0 0 18px rgba(56,189,248,.42); }}
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior:auto; }} .flow-panel.flow-active .flow-svg-packet,.flow-panel.flow-active .flow-svg-packet-halo,.flow-panel.flow-waiting .flow-svg-packet,.flow-panel.flow-waiting .flow-svg-packet-halo,.flow-panel.traffic-outbound .flow-svg-packet,.flow-panel.traffic-outbound .flow-svg-packet-halo,.flow-panel.traffic-inbound .flow-svg-packet,.flow-panel.traffic-inbound .flow-svg-packet-halo,.flow-panel.traffic-outbound .flow-stage::after,.flow-panel.traffic-inbound .flow-stage::after,.flow-panel.traffic-outbound [data-flow-link]::after,.flow-panel.traffic-inbound [data-flow-link]::after,.flow-panel.traffic-processing [data-flow-segment="ollama-model"],.flow-panel.traffic-processing [data-flow-link="ollama-model"]::after,.flow-node.status-pulse,.dot,.value-pop,.badge-update,.ops-activity-summary,.ops-activity-summary .ops-health-status,.ops-activity-summary::after {{ animation:none; }} .flow-svg-packet,.flow-svg-packet-halo,.flow-stage::after {{ opacity:0; }} .nav a,.nav a::before,.topbar-status,.topbar-status-dot,.card,.node,.hero-status,.hero-status::before,.hero-status::after,.hero-stat-card,.hero-stat-icon,.hero-stat-value,.badge,.flow-svg-line,.gauge-progress,.fill,.ops-health-row,.ops-activity-summary,.panel-item,.timeline-item,.live-timeline-event,.conversation-inspector-drawer,.conversation-inspector-backdrop,.conversation-inspector-close,.message,.instrument-gauge-needle,.instrument-gauge-pivot,.instrument-card-value,.trend-line,.trend-area,.request-traffic-bar {{ transition:none; }} .nav a:hover,.nav a:active,.card:hover,.node:hover,.hero-stat-card:hover,.hero-stat-card:focus-within,.hero-stat-card:focus-visible,.hero-stat-card:hover .hero-stat-icon,.hero-stat-card:focus-within .hero-stat-icon,.hero-stat-card:focus-visible .hero-stat-icon,a.badge:hover,a.badge:active,body.is-refreshing .topbar-status-dot {{ transform:none; }} }}
.small {{ font-size:12px; color:var(--muted); overflow-wrap:anywhere; }}
.traffic-panel {{ display:grid; grid-template-rows:auto auto 1fr; gap:12px; align-content:start; padding:14px; }}
.traffic-stats {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; align-items:stretch; }}
.traffic-stat {{ min-width:0; display:grid; align-content:start; gap:5px; padding:10px 11px; border:1px solid rgba(203,213,225,.08); border-radius:9px; background:linear-gradient(180deg,rgba(15,23,42,.48),rgba(2,6,23,.26)); box-shadow:var(--surface-inset-highlight); }}
.traffic-stat .small {{ font-size:11px; font-weight:850; letter-spacing:.06em; text-transform:uppercase; }}
.traffic-stat .value {{ font-size:28px; line-height:1; }}
.traffic-stat .muted {{ font-size:11px; line-height:1.22; }}
.request-traffic-viz {{ min-height:82px; display:grid; grid-template-rows:1fr auto; gap:8px; padding:10px 11px; border:1px solid rgba(203,213,225,.08); border-radius:11px; background:linear-gradient(180deg,rgba(15,23,42,.42),rgba(2,6,23,.22)); box-shadow:var(--surface-inset-highlight); overflow:hidden; }}
.request-traffic-svg {{ width:100%; height:48px; display:block; overflow:visible; }}
.request-traffic-grid {{ stroke:rgba(148,163,184,.12); stroke-width:1; vector-effect:non-scaling-stroke; }}
.request-traffic-baseline {{ stroke:rgba(148,163,184,.24); stroke-width:1.2; vector-effect:non-scaling-stroke; }}
.request-traffic-bar {{ fill:rgba(56,189,248,.42); filter:drop-shadow(0 0 5px rgba(56,189,248,.18)); transition:height .2s ease,y .2s ease,fill .2s ease,opacity .2s ease; }}
.request-traffic-bar.idle {{ fill:rgba(71,85,105,.38); opacity:.55; filter:none; }}
.request-traffic-bar.active {{ fill:rgba(125,211,252,.76); opacity:.96; }}
.request-traffic-bar.burst {{ fill:rgba(167,139,250,.84); opacity:1; filter:drop-shadow(0 0 8px rgba(167,139,250,.28)); }}
.request-traffic-now {{ stroke:rgba(125,211,252,.5); stroke-width:1; stroke-dasharray:2 3; vector-effect:non-scaling-stroke; }}
.request-traffic-footer {{ display:flex; justify-content:space-between; gap:12px; align-items:center; min-width:0; }}
.request-traffic-status {{ min-width:0; font-size:11px; color:var(--text); font-weight:850; letter-spacing:.055em; text-transform:uppercase; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.request-traffic-caption {{ min-width:0; text-align:right; font-size:11px; color:var(--muted); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.traffic-note {{ align-self:end; padding-top:8px; border-top:1px solid rgba(203,213,225,.08); line-height:1.35; }}
.conversation-meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; margin-bottom:14px; }}
.conversation-meta.compact {{ grid-template-columns:repeat(2,minmax(0,1fr)); margin-bottom:0; }}
.conversation-compact {{ display:grid; grid-template-rows:auto auto auto minmax(0,1fr); gap:12px; padding:14px; }}
.conversation-compact .health-title {{ align-items:center; }}
.conversation-compact .conversation-meta.compact {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; margin-bottom:0; }}
.conversation-compact .conversation-meta.compact > div {{ min-width:0; display:grid; gap:3px; padding:8px 9px; border:1px solid rgba(203,213,225,.08); border-radius:8px; background:rgba(15,23,42,.34); box-shadow:var(--surface-inset-highlight); }}
.conversation-compact .conversation-meta.compact .muted {{ line-height:1.25; white-space:normal; overflow-wrap:anywhere; }}
.conversation-compact .summary {{ min-height:0; max-height:92px; overflow:hidden; line-height:1.28; }}
.live-timeline-card {{ display:grid; grid-template-rows:auto minmax(0,1fr); gap:10px; padding:14px; }}
.live-timeline-list {{ min-height:0; overflow-y:auto; overflow-x:hidden; display:grid; align-content:start; gap:8px; padding-right:2px; scrollbar-width:thin; scrollbar-color:rgba(148,163,184,.32) transparent; }}
.live-timeline-event {{ --timeline-accent:var(--accent); min-width:0; display:grid; grid-template-columns:14px minmax(54px,.34fr) minmax(0,1fr); gap:8px; align-items:start; padding:8px 9px; border:1px solid rgba(203,213,225,.09); border-radius:9px; background:linear-gradient(180deg,rgba(15,23,42,.48),rgba(2,6,23,.24)); box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
button.live-timeline-event {{ width:100%; color:inherit; font:inherit; text-align:left; cursor:pointer; appearance:none; -webkit-appearance:none; }}
.live-timeline-event:hover {{ border-color:rgba(129,140,248,.24); background:rgba(15,23,42,.68); box-shadow:var(--surface-inset-highlight),0 0 16px rgba(129,140,248,.09); }}
.live-timeline-event:focus-visible {{ outline:2px solid rgba(56,189,248,.68); outline-offset:2px; }}
.live-timeline-event.is-selected {{ border-color:rgba(56,189,248,.46); background:linear-gradient(180deg,rgba(14,116,144,.2),rgba(15,23,42,.58)); box-shadow:var(--surface-inset-highlight),0 0 0 1px rgba(56,189,248,.12),0 0 18px rgba(56,189,248,.12); }}
.live-timeline-event.success {{ --timeline-accent:var(--good); }}
.live-timeline-event.warning {{ --timeline-accent:var(--warn); }}
.live-timeline-event.error {{ --timeline-accent:var(--bad); }}
.live-timeline-marker {{ width:10px; height:10px; margin-top:3px; border-radius:999px; background:var(--timeline-accent); box-shadow:0 0 0 3px rgba(56,189,248,.08),0 0 12px rgba(56,189,248,.18); }}
.live-timeline-event.success .live-timeline-marker {{ box-shadow:0 0 0 3px rgba(34,197,94,.08),0 0 12px rgba(34,197,94,.18); }}
.live-timeline-event.warning .live-timeline-marker {{ box-shadow:0 0 0 3px rgba(245,158,11,.08),0 0 12px rgba(245,158,11,.18); }}
.live-timeline-event.error .live-timeline-marker {{ box-shadow:0 0 0 3px rgba(239,68,68,.08),0 0 12px rgba(239,68,68,.18); }}
.live-timeline-time {{ color:var(--muted); font-size:10px; line-height:1.2; font-weight:800; letter-spacing:.035em; white-space:nowrap; }}
.live-timeline-copy {{ min-width:0; display:grid; gap:2px; }}
.live-timeline-title {{ min-width:0; color:#e2e8f0; font-size:12px; line-height:1.18; font-weight:800; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.live-timeline-detail {{ min-width:0; color:var(--muted); font-size:10px; line-height:1.2; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.live-timeline-empty {{ min-height:100%; display:grid; place-items:center; align-content:center; gap:6px; padding:16px 12px; text-align:center; border:1px dashed rgba(148,163,184,.28); border-radius:9px; background:rgba(15,23,42,.32); color:#aebbd0; }}
.live-timeline-empty-title {{ color:#dbeafe; font-size:12px; font-weight:850; letter-spacing:.03em; text-transform:uppercase; }}
.live-timeline-empty-detail {{ max-width:280px; color:var(--muted); font-size:11px; line-height:1.35; }}
.conversation-inspector-backdrop {{ position:fixed; inset:0; z-index:18; background:rgba(2,6,23,.42); opacity:0; pointer-events:none; transition:opacity .2s ease; }}
.conversation-inspector-drawer {{ position:fixed; top:0; right:0; z-index:19; width:min(660px,calc(100vw - 28px)); height:100vh; height:100dvh; min-width:0; display:grid; grid-template-rows:auto minmax(0,1fr); gap:0; padding:0; overflow:hidden; transform:translateX(calc(100% + 18px)); opacity:.98; pointer-events:none; background:linear-gradient(180deg,rgba(15,23,42,.98),rgba(9,14,26,.96)); border-left:1px solid rgba(203,213,225,.14); box-shadow:-20px 0 52px rgba(2,6,23,.42),var(--surface-inset-highlight); transition:transform .22s cubic-bezier(.2,0,0,1),opacity .18s ease; }}
body.conversation-inspector-open .conversation-inspector-drawer {{ transform:translateX(0); opacity:1; pointer-events:auto; }}
.conversation-inspector-header {{ min-width:0; display:grid; gap:10px; padding:18px 20px 14px; border-bottom:1px solid rgba(203,213,225,.1); background:linear-gradient(135deg,rgba(15,23,42,.96),rgba(30,41,59,.78)); box-shadow:var(--surface-inset-highlight); }}
.conversation-inspector-title-row {{ min-width:0; display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.conversation-inspector-title {{ margin:0; color:#f8fafc; font-size:15px; line-height:1.2; font-weight:850; letter-spacing:.045em; text-transform:uppercase; }}
.conversation-inspector-close {{ flex:0 0 auto; width:32px; height:32px; display:grid; place-items:center; border:1px solid rgba(203,213,225,.14); border-radius:9px; color:#dbeafe; background:rgba(15,23,42,.62); box-shadow:var(--surface-inset-highlight); cursor:pointer; transition:border-color .18s ease,background .18s ease,color .18s ease; }}
.conversation-inspector-close:hover,.conversation-inspector-close:focus-visible {{ border-color:rgba(56,189,248,.42); background:rgba(56,189,248,.12); color:#f8fafc; }}
.conversation-inspector-close svg {{ width:16px; height:16px; stroke:currentColor; fill:none; stroke-width:2; stroke-linecap:round; }}
.conversation-inspector-kicker {{ min-width:0; display:flex; flex-wrap:wrap; align-items:center; gap:7px; color:var(--soft); font-size:12px; line-height:1.3; }}
.conversation-inspector-meta-line {{ min-width:0; color:var(--muted); font-size:11px; line-height:1.35; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.conversation-inspector-body {{ min-height:0; overflow-y:auto; overflow-x:hidden; display:grid; align-content:start; gap:12px; padding:14px 20px 22px; scrollbar-width:thin; scrollbar-color:rgba(148,163,184,.32) transparent; }}
.conversation-inspector-state {{ min-height:92px; display:grid; place-items:center; align-content:center; gap:4px; padding:12px 14px; text-align:center; border:1px dashed rgba(148,163,184,.22); border-radius:10px; background:rgba(15,23,42,.3); color:#aebbd0; }}
.conversation-inspector-state[hidden],.conversation-inspector-section[hidden] {{ display:none; }}
.conversation-inspector-state-title {{ color:#dbeafe; font-size:12px; font-weight:850; letter-spacing:.035em; text-transform:uppercase; }}
.conversation-inspector-state-detail {{ max-width:380px; color:var(--muted); font-size:11px; line-height:1.35; }}
.conversation-inspector-section {{ display:grid; gap:12px; min-width:0; }}
.conversation-inspector-subsection {{ display:grid; gap:10px; min-width:0; }}
.conversation-inspector-section-title {{ margin:0; padding-bottom:4px; border-bottom:1px solid rgba(203,213,225,.09); color:#dbeafe; font-size:11.5px; line-height:1.2; font-weight:850; letter-spacing:.06em; text-transform:uppercase; }}
.conversation-inspector-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; min-width:0; }}
.conversation-inspector-field {{ min-width:0; display:grid; gap:4px; padding:10px 11px; border:1px solid rgba(203,213,225,.09); border-radius:10px; background:rgba(15,23,42,.42); box-shadow:var(--surface-inset-highlight); }}
.conversation-inspector-label {{ color:var(--muted); font-size:10px; line-height:1.1; font-weight:850; letter-spacing:.07em; text-transform:uppercase; }}
.conversation-inspector-value {{ min-width:0; color:#e2e8f0; font-size:12px; line-height:1.28; overflow-wrap:anywhere; }}
.conversation-inspector-intelligence-card {{ --inspector-intelligence-accent:var(--accent); display:grid; gap:8px; min-width:0; padding:11px 12px; border:1px solid rgba(203,213,225,.09); border-left:3px solid var(--inspector-intelligence-accent); border-radius:10px; background:linear-gradient(180deg,rgba(15,23,42,.44),rgba(2,6,23,.24)); box-shadow:var(--surface-inset-highlight); }}
.conversation-inspector-intelligence-card.success {{ --inspector-intelligence-accent:var(--good); }}
.conversation-inspector-intelligence-card.warning {{ --inspector-intelligence-accent:var(--warn); }}
.conversation-inspector-intelligence-card.error {{ --inspector-intelligence-accent:var(--bad); }}
.conversation-inspector-intelligence-card.info {{ --inspector-intelligence-accent:#a78bfa; }}
.conversation-inspector-intelligence-card.unavailable {{ --inspector-intelligence-accent:var(--muted); }}
.conversation-inspector-intelligence-head {{ display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center; gap:8px; min-width:0; }}
.conversation-inspector-intelligence-title {{ min-width:0; color:#f8fafc; font-size:13px; line-height:1.2; font-weight:850; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.conversation-inspector-intelligence-explanation {{ color:#cbd5e1; font-size:12px; line-height:1.4; }}
.conversation-inspector-signals {{ display:flex; flex-wrap:wrap; gap:6px; min-width:0; }}
.conversation-inspector-signal {{ display:inline-flex; align-items:center; gap:5px; max-width:100%; padding:4px 7px; border:1px solid rgba(203,213,225,.08); border-radius:999px; background:rgba(15,23,42,.4); color:var(--muted); font-size:10px; line-height:1.15; }}
.conversation-inspector-signal strong {{ color:#dbeafe; font-weight:850; }}
.conversation-inspector-recommendation {{ color:#fecaca; font-size:11px; line-height:1.35; padding:7px 9px; border:1px solid rgba(239,68,68,.16); border-radius:8px; background:rgba(127,29,29,.18); }}
.conversation-inspector-note {{ color:rgba(148,163,184,.78); font-size:10px; line-height:1.35; padding:7px 9px; border:1px solid rgba(203,213,225,.055); border-radius:8px; background:rgba(15,23,42,.2); }}
.conversation-inspector-live-region {{ position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; }}
.summary {{ background:rgba(15,23,42,.62); border:1px solid var(--border-card); border-radius:10px; padding:12px; white-space:pre-wrap; box-shadow:var(--surface-inset-highlight); }}
.messages {{ display:grid; gap:10px; margin-top:12px; }}
.message {{ background:rgba(15,23,42,.46); border:1px solid var(--border-card); border-radius:10px; padding:10px 12px; box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease,background .18s ease,box-shadow .18s ease; }}
.message-role {{ color:var(--accent); font-size:12px; font-weight:700; text-transform:uppercase; }}
.message-content {{ margin-top:4px; white-space:pre-wrap; }}
@media (min-width: 1901px) {{ .operations-page {{ gap:14px; }} }}
@media (max-width: 1900px) {{
  .app-shell {{ grid-template-columns:220px minmax(0,1fr); }}
  .sidebar {{ padding:18px 14px; }}
  .topbar {{ padding:8px 14px; }}
  .topbar-pill {{ min-height:26px; padding:3px 8px; }}
  .dashboard-main {{ padding:6px 12px 12px; }}
  .page.active {{ gap:6px; }}
  .ops-hero {{ grid-template-columns:minmax(280px,1.15fr) minmax(240px,.85fr); gap:8px; }}
  .hero-stats-grid {{ grid-template-columns:repeat(4,minmax(132px,1fr)); gap:6px; }}
  .hero-stat-card {{ min-height:74px; padding:8px 10px; gap:5px; }}
  .hero-stat-icon {{ width:30px; height:30px; }}
  .hero-stat-value {{ font-size:24px; }}
  .hero-stat-desc {{ font-size:10px; line-height:1.12; }}
  .hero-status {{ grid-column:1; grid-row:1; min-height:68px; padding:8px 12px; }}
  .hero-title {{ font-size:18px; white-space:nowrap; margin-top:3px; }}
  .hero-icon {{ font-size:17px; }}
  .hero-copy {{ max-width:none; margin-top:3px; font-size:11px; line-height:1.22; display:-webkit-box; -webkit-line-clamp:1; -webkit-box-orient:vertical; overflow:hidden; }}
  .hero-kicker {{ font-size:10px; }}
  .hero-status .command-meta {{ display:none; }}
  .hero-status #systemHealthCard {{ margin-top:5px; padding:7px; }}
  .instrument-panel {{ gap:6px; }}
  .instrument-card {{ --instrument-gauge-w:112px; --instrument-gauge-h:66px; --instrument-support-line-h:13px; --instrument-reading-h:22px; min-height:136px; padding:9px; }}
  .instrument-card-value {{ font-size:20px; }}
  .instrument-support-row {{ font-size:9px; }}
  .ops-health-panel {{ gap:6px; }}
  .ops-health-body {{ grid-template-columns:minmax(0,1fr) 56px; gap:6px; }}
  .ops-health-status {{ font-size:18px; }}
  .ops-state-pair {{ gap:5px; }}
  .ops-state-column {{ padding:4px 5px; }}
  .ops-health-message {{ font-size:11px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }}
  .ops-health-gauge .gauge {{ width:40px; height:40px; }}
  .ops-health-details {{ grid-template-columns:repeat(5,minmax(0,1fr)); gap:4px; }}
  .ops-health-row {{ min-height:54px; padding:4px 5px; }}
  .ops-health-row-detail {{ font-size:10px; }}
  .command-meta {{ margin-top:5px; }}
  .action-panel {{ grid-area:actions; }}
  .signal-card {{ min-height:78px; min-width:0; }}
  .signal-card .value,.signal-node .value {{ font-size:22px; }}
  .signal-card h2,.signal-node .node-title {{ font-size:12px; }}
  .signal-body {{ grid-template-columns:minmax(0,1fr) 46px; gap:6px; }}
  .gauge {{ width:46px; height:46px; }}
  .mini-chart {{ height:20px; margin-top:2px; }}
  .action-panel {{ min-height:0; }}
  .action-panel .health-title {{ margin-bottom:4px; }}
  .action-panel .panel-list {{ max-height:none; }}
  .action-panel .panel-item {{ padding:5px 7px; font-size:12px; }}
  .flow-panel {{ padding:8px 9px; gap:5px; }}
  .flow-panel::before {{ inset:32px 9px 9px; }}
  .flow-stage {{ grid-template-columns:minmax(126px,1fr) 24px minmax(126px,1fr) 24px minmax(126px,1fr) 24px minmax(126px,1fr); gap:6px; }}
  .node {{ min-height:78px; padding:7px; }}
  .flow-node {{ min-height:70px; padding:6px; gap:4px; }}
  .flow-node-icon {{ width:24px; height:24px; border-radius:7px; }}
  .flow-node-icon svg {{ width:14px; height:14px; }}
  .flow-node-title {{ font-size:10px; letter-spacing:.05em; }}
  .flow-node-main .value {{ font-size:16px; }}
  .flow-node-main .small {{ font-size:10px; line-height:1.16; }}
  .flow-node-foot {{ padding-top:5px; }}
  .flow-endpoint {{ font-size:9px; }}
  .node::before {{ width:20px; height:20px; margin-bottom:4px; box-shadow:0 0 0 4px rgba(56,189,248,.05); }}
  .node-title {{ font-size:11px; margin-bottom:3px; }}
  .node .value {{ font-size:18px; }}
  .node .small {{ font-size:10px; line-height:1.16; }}
  .operations-lower {{ grid-template-columns:minmax(0,2.1fr) minmax(220px,1.35fr) minmax(250px,1.45fr); gap:8px; }}
  .traffic-panel,.conversation-compact,.live-timeline-card {{ gap:8px; padding:10px; }}
  .traffic-stats {{ gap:8px; }}
  .traffic-stat {{ padding:8px 9px; }}
  .traffic-stat .value {{ font-size:24px; }}
  .conversation-compact .conversation-meta.compact {{ gap:8px; }}
  .conversation-compact .summary {{ max-height:54px; }}
}}
@media (max-width: 1500px) {{
  .ops-hero {{ grid-template-columns:minmax(250px,1fr) minmax(220px,.78fr); gap:7px; }}
  .instrument-panel {{ grid-template-columns:repeat(3,minmax(0,1fr)); }}
  .system-activity-grid {{ grid-template-columns:minmax(220px,.82fr) minmax(0,2.18fr); }}
  .hero-stats-grid {{ grid-template-columns:repeat(4,minmax(132px,1fr)); gap:7px; }}
  .hero-stat-card {{ min-height:68px; }}
  .hero-title {{ white-space:normal; }}
  .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }}
  .operations-lower {{ grid-template-columns:minmax(0,2fr) minmax(210px,1.35fr) minmax(230px,1.45fr); gap:6px; }}
  .flow-stage {{ grid-template-columns:minmax(118px,1fr) 20px minmax(118px,1fr) 20px minmax(118px,1fr) 20px minmax(118px,1fr); gap:6px; }}
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
  .dashboard-main {{ padding:6px 10px 12px; }}
  .page.active {{ gap:6px; }}
  .operations-page {{ min-height:calc(100% - 2px); }}
  .ops-hero {{ grid-template-columns:minmax(220px,.9fr) minmax(200px,.72fr); grid-template-rows:auto auto; gap:6px; }}
  .hero-stats-grid {{ grid-template-columns:repeat(4,minmax(0,1fr)); }}
  .hero-stat-card {{ min-height:62px; padding:7px 9px; gap:4px; }}
  .hero-stat-label {{ font-size:10px; letter-spacing:.06em; }}
  .hero-stat-icon {{ width:26px; height:26px; border-radius:7px; }}
  .hero-stat-icon svg {{ width:15px; height:15px; }}
  .hero-stat-value {{ font-size:24px; }}
  .hero-stat-desc {{ font-size:10px; line-height:1.15; }}
  .hero-status {{ grid-column:1; grid-row:1; min-height:58px; padding:8px 10px; }}
  .hero-kicker {{ font-size:9px; }}
  .hero-title {{ gap:7px; margin-top:2px; font-size:16px; line-height:1.05; }}
  .hero-icon {{ font-size:15px; }}
  .hero-copy {{ display:none; }}
  .ops-health-body {{ grid-template-columns:minmax(0,1fr) 54px; }}
  .ops-health-status {{ font-size:18px; }}
  .ops-state-pair {{ gap:4px; }}
  .ops-state-column {{ padding:4px 5px; gap:1px; }}
  .ops-state-kicker {{ font-size:8px; }}
  .ops-activity-details {{ display:none; }}
  .ops-health-gauge .gauge {{ width:40px; height:40px; }}
  .ops-health-gauge-label {{ display:none; }}
  .ops-health-details {{ grid-template-columns:repeat(5,minmax(0,1fr)); }}
  .ops-health-row {{ grid-template-columns:14px minmax(0,1fr) max-content; min-height:52px; padding:4px 5px; }}
  .ops-health-row svg {{ width:14px; height:14px; }}
  .ops-health-row-label {{ font-size:9px; }}
  .action-panel {{ grid-area:actions; padding:8px 10px; }}
  .instrument-panel {{ gap:6px; }}
  .instrument-card {{ --instrument-gauge-w:98px; --instrument-gauge-h:58px; --instrument-support-line-h:12px; --instrument-reading-h:21px; min-height:126px; padding:8px; }}
  .dashboard-card-title,.card h2.dashboard-card-title {{ font-size:9.5px; }}
  .instrument-card-value {{ font-size:18px; }}
  .instrument-support-row {{ font-size:9px; }}
  .trend-chart,.trend-chart-wrap {{ min-height:62px; height:62px; }}
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
  .flow-panel {{ padding:7px; gap:4px; }}
  .flow-panel::before {{ inset:28px 7px 7px; }}
  .flow-panel .health-title h2 {{ margin:0; }}
  .flow-note {{ font-size:10px; }}
  .flow-stage {{ grid-template-columns:minmax(104px,1fr) 18px minmax(104px,1fr) 18px minmax(104px,1fr) 18px minmax(104px,1fr); gap:5px; }}
  .node {{ min-height:56px; padding:5px; }}
  .flow-node {{ min-height:58px; padding:5px; gap:3px; }}
  .flow-node-head {{ gap:6px; }}
  .flow-node-icon {{ width:20px; height:20px; }}
  .flow-node-title {{ font-size:9px; }}
  .flow-node-main {{ gap:3px; }}
  .flow-node-main .value {{ font-size:15px; }}
  .flow-node-main .small {{ font-size:9px; line-height:1.1; }}
  .flow-node-foot {{ gap:5px; padding-top:4px; }}
  .flow-endpoint {{ font-size:8px; }}
  .node::before {{ width:14px; height:14px; margin-bottom:2px; box-shadow:0 0 0 3px rgba(56,189,248,.05); }}
  .node-title {{ font-size:10px; margin-bottom:2px; }}
  .node .value {{ font-size:15px; }}
  .node .small {{ font-size:9px; line-height:1.1; }}
  .dot {{ width:9px; height:9px; margin-right:5px; }}
  .pipe::after {{ width:7px; height:7px; }}
  .operations-lower {{ grid-template-columns:minmax(0,2fr) minmax(190px,1.35fr) minmax(210px,1.45fr); gap:6px; }}
  .traffic-panel,.conversation-compact,.live-timeline-card {{ gap:5px; padding:8px; }}
  .traffic-stats {{ gap:5px; }}
  .traffic-stat {{ padding:6px 7px; gap:3px; }}
  .traffic-stat .value {{ font-size:20px; }}
  .traffic-note {{ padding-top:5px; }}
  .conversation-compact,.live-timeline-card {{ grid-column:auto; }}
  .conversation-meta.compact {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
  .conversation-compact .conversation-meta.compact > div {{ padding:6px 7px; }}
  .conversation-compact .summary {{ max-height:32px; padding:8px; }}
}}
@media (min-width: 1001px) and (max-height: 900px) {{
  .topbar {{ margin-top:4px; padding-top:6px; padding-bottom:6px; }}
  .sub {{ display:none; }}
  .dashboard-main {{ padding-top:4px; padding-bottom:8px; }}
  .page.active,.operations-page {{ gap:4px; }}
  .ops-hero {{ gap:6px; }}
  .hero-status {{ padding-top:7px; padding-bottom:7px; }}
  .hero-title {{ margin-top:3px; }}
  .hero-copy {{ margin-top:3px; line-height:1.2; }}
  .hero-status #systemHealthCard {{ margin-top:4px; padding:6px; }}
  .instrument-card {{ --instrument-support-line-h:12px; min-height:122px; gap:4px; }}
  .instrument-support-row {{ font-size:9px; }}
  .ops-health-panel {{ gap:5px; }}
  .ops-health-body {{ gap:6px; }}
  .hero-stats-grid {{ gap:5px; }}
  .flow-panel {{ padding-top:7px; padding-bottom:7px; gap:4px; }}
  .flow-panel::before {{ inset:30px 9px 7px; }}
  .flow-stage {{ gap:5px; }}
  .operations-lower {{ gap:6px; }}
  .traffic-panel,.conversation-compact,.live-timeline-card {{ gap:5px; }}
  .traffic-stat {{ padding:6px 7px; }}
}}
@media (min-width: 1001px) and (max-height: 800px) {{
  .topbar {{ margin:4px 10px 0; padding:5px 10px; border-radius:10px; }}
  .topbar-status {{ min-height:24px; padding:2px 7px; }}
  .topbar-pill {{ min-height:24px; padding:2px 8px; }}
  .dashboard-main {{ padding:3px 10px 6px; }}
  .page.active,.operations-page {{ gap:3px; }}
  .ops-hero {{ gap:4px; }}
  .hero-status {{ padding:6px 10px; }}
  .hero-title {{ margin-top:2px; }}
  .hero-copy {{ margin-top:2px; line-height:1.15; }}
  .hero-status #systemHealthCard {{ margin-top:3px; padding:5px; }}
  .instrument-card {{ --instrument-gauge-w:88px; --instrument-gauge-h:52px; --instrument-support-line-h:11px; --instrument-reading-h:19px; min-height:112px; padding:7px; gap:4px; }}
  .instrument-card-value {{ font-size:16px; }}
  .instrument-info {{ display:none; }}
  .trend-chart,.trend-chart-wrap {{ min-height:52px; height:52px; }}
  .ops-health-panel {{ gap:4px; }}
  .ops-health-body {{ gap:5px; }}
  .ops-health-details {{ gap:3px; }}
  .ops-health-row {{ min-height:50px; padding:3px 5px; }}
  .hero-stats-grid {{ gap:4px; }}
  .hero-stat-card {{ min-height:64px; padding:6px 8px; gap:3px; }}
  .hero-stat-icon {{ width:24px; height:24px; border-radius:7px; }}
  .hero-stat-icon svg {{ width:15px; height:15px; }}
  .signal-body {{ gap:5px; }}
  .flow-panel {{ padding:6px 7px; gap:3px; }}
  .flow-panel::before {{ inset:26px 7px 6px; }}
  .flow-stage {{ gap:4px; }}
  .flow-node {{ min-height:64px; padding:5px; gap:3px; }}
  .flow-node-head {{ gap:6px; }}
  .flow-node-icon {{ width:20px; height:20px; border-radius:7px; }}
  .flow-node-main {{ gap:2px; }}
  .flow-node-foot {{ gap:5px; padding-top:3px; }}
  .operations-lower {{ gap:5px; }}
  .operations-lower .card {{ padding:8px; }}
  .traffic-panel,.conversation-compact,.live-timeline-card {{ gap:4px; }}
  .traffic-stats {{ gap:5px; }}
  .traffic-stat {{ padding:5px 6px; }}
  .conversation-meta.compact {{ gap:6px; }}
}}
@media (min-width: 1351px) and (max-width: 1500px) and (max-height: 800px) {{
  .topbar {{ margin:1px 10px 0; padding:2px 10px; }}
  .dashboard-main {{ padding:1px 8px; }}
  .page.active,.operations-page {{ gap:0; }}
  .ops-hero {{ gap:2px; }}
  .hero-status {{ padding:5px 9px; }}
  .hero-title {{ margin-top:1px; }}
  .hero-copy {{ margin-top:1px; line-height:1.12; }}
  .hero-status #systemHealthCard {{ margin-top:2px; padding:4px; }}
  .ops-health-panel {{ gap:3px; }}
  .ops-health-body {{ grid-template-columns:minmax(0,1fr) 56px; gap:4px; }}
  .ops-health-details {{ gap:2px; }}
  .ops-health-row {{ min-height:48px; padding:3px 4px; }}
  .ops-health-row .badge {{ min-height:13px; padding:1px 5px; }}
  .hero-stats-grid {{ gap:3px; }}
  .hero-stat-card {{ min-height:56px; padding:5px 7px; gap:2px; }}
  .hero-stat-top {{ gap:6px; }}
  .hero-stat-icon {{ width:22px; height:22px; }}
  .hero-stat-icon svg {{ width:14px; height:14px; }}
  .signal-body {{ gap:4px; }}
  .action-panel {{ padding:8px 9px; }}
  .action-panel .health-title {{ margin-bottom:2px; }}
  .action-panel .panel-list {{ gap:5px; }}
  .action-panel .panel-item {{ padding:3px 6px; font-size:11px; line-height:1.15; }}
  .flow-panel {{ padding:4px 6px; gap:2px; }}
  .flow-panel::before {{ inset:22px 6px 4px; }}
  .flow-stage {{ gap:3px; }}
  .flow-node {{ min-height:52px; padding:4px; gap:2px; }}
  .flow-node-head {{ gap:4px; }}
  .flow-node-icon {{ width:18px; height:18px; }}
  .flow-node-icon svg {{ width:13px; height:13px; }}
  .flow-node-main {{ gap:1px; }}
  .flow-node-main .small {{ line-height:1.05; }}
  .flow-node-foot {{ gap:4px; padding-top:2px; }}
  .operations-lower {{ gap:4px; }}
  .operations-lower .card {{ padding:6px; }}
  .traffic-panel,.conversation-compact,.live-timeline-card {{ gap:3px; }}
  .traffic-stats {{ gap:4px; }}
  .traffic-stat {{ padding:4px 5px; }}
  .conversation-meta.compact {{ gap:4px; }}
  .risk-row {{ margin-top:4px; gap:4px; }}
  .conversation-compact .summary {{ padding:8px; }}
  .badge {{ min-height:19px; padding:1px 6px; }}
}}
@media (max-width: 1000px) {{ .app-shell {{ grid-template-columns:220px minmax(0,1fr); }} .dashboard-main {{ padding:14px 16px 18px; }} .ops-hero,.system-activity-grid,.operations-lower {{ grid-template-columns:1fr; }} .hero-title {{ white-space:normal; }} .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }} .ops-health-details {{ grid-template-columns:1fr; }} .ops-health-row {{ grid-template-columns:16px minmax(0,1fr) auto; }} .flow-svg-layer {{ display:none; }} .flow-stage {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} body.conversation-inspector-open .conversation-inspector-backdrop {{ opacity:1; pointer-events:auto; }} }}
@media (max-width: 1000px) {{ .app-shell {{ height:100vh; overflow-y:auto; overflow-x:hidden; grid-template-columns:1fr; }} .workspace {{ height:auto; min-height:0; overflow:visible; }} .sidebar {{ position:relative; height:auto; gap:14px; }} .nav {{ grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); }} .sidebar-footer {{ display:none; }} .topbar {{ position:relative; align-items:flex-start; flex-direction:column; }} .dashboard-main {{ height:auto; overflow:visible; padding:18px; }} .page.active,.ops-hero,.system-activity-grid,.operations-lower {{ height:auto; overflow:visible; grid-template-columns:1fr; }} .ops-hero {{ grid-template-areas:"hero" "actions" "stats"; }} .hero-stats-grid {{ grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); }} .traffic-stats {{ grid-template-columns:1fr; }} .instrument-panel {{ grid-template-columns:1fr; }} .instrument-trend-card {{ grid-column:auto; }} .conversation-inspector-drawer {{ width:100vw; border-left:0; }} .conversation-inspector-grid {{ grid-template-columns:1fr; }} .operations-page {{ min-height:auto; grid-template-rows:none; }} .timeline-item {{ grid-template-columns:1fr; }} }}
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
  <div class="topbar-left">
    <div class="topbar-title">
      <h1>ContextKeeper</h1>
      <div class="sub">Transparent Ollama Proxy - Diagnostics - System Monitor</div>
    </div>
    <div class="topbar-status"><span class="topbar-status-dot"></span>Operations</div>
  </div>
  <div class="topbar-actions">
    <span class="topbar-pill">Proxy port {settings.server.port}</span>
    <span class="topbar-pill">{ollama_base_url_html}</span>
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
      <div id="systemHealthCard" class="card health-card signal-card compact-card ops-health-panel">
        <div class="health-title dashboard-card-header">
          <h2 class="ops-health-heading dashboard-card-title"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 4 6v6c0 5 3.4 8 8 9 4.6-1 8-4 8-9V6z"></path><path d="m9 12 2 2 4-5"></path></svg>System Health</h2>
          <div class="dashboard-card-header-actions"><span id="systemHealthBadge" class="badge">Checking</span></div>
        </div>
        <div class="ops-health-body">
          <div class="ops-health-primary">
            <div class="ops-state-pair" aria-label="Health and activity states">
              <div class="ops-state-column">
                <div class="ops-state-kicker">System Health</div>
                <div id="systemHealthStatus" class="ops-health-status">--</div>
              </div>
              <div id="currentActivitySummary" class="ops-state-column ops-activity-summary starting">
                <div class="ops-state-kicker">Current Activity</div>
                <div id="currentActivityStatus" class="ops-health-status">Starting</div>
              </div>
            </div>
            <div id="systemHealthMessage" class="ops-health-message">Dashboard intelligence is loading.</div>
            <div id="currentActivityDetails" class="ops-activity-details">ContextKeeper is initializing.</div>
          </div>
          <div class="ops-health-gauge">
            <svg class="gauge" viewBox="0 0 120 120" aria-hidden="true">
              <circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle>
              <circle id="healthGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle>
            </svg>
            <div class="ops-health-gauge-label">Health</div>
          </div>
        </div>
        <div class="ops-health-details" aria-label="System health details">
          <div class="ops-health-row"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16"></path><path d="M4 12h16"></path><path d="M4 18h16"></path></svg><div class="ops-health-row-main"><div class="ops-health-row-label">Context<wbr>Keeper</div><div id="opsContextKeeperDetail" class="ops-health-row-detail">Listening locally</div></div><span id="opsContextKeeperStatus" class="badge healthy">Online</span></div>
          <div class="ops-health-row"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2v4"></path><path d="M12 18v4"></path><path d="M4.9 4.9 7.8 7.8"></path><path d="m16.2 16.2 2.9 2.9"></path><path d="M2 12h4"></path><path d="M18 12h4"></path><circle cx="12" cy="12" r="4"></circle></svg><div class="ops-health-row-main"><div class="ops-health-row-label">Ollama</div><div id="opsOllamaDetail" class="ops-health-row-detail">Checking upstream</div></div><span id="opsOllamaStatus" class="badge">Checking</span></div>
          <div class="ops-health-row"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 7h8"></path><path d="M8 12h8"></path><path d="M8 17h5"></path><rect x="4" y="3" width="16" height="18" rx="2"></rect></svg><div class="ops-health-row-main"><div class="ops-health-row-label">Active Model</div><div id="opsModelDetail" class="ops-health-row-detail">No model observed yet</div></div><span id="opsModelStatus" class="badge">Waiting</span></div>
          <div class="ops-health-row"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h4"></path><path d="M16 12h4"></path><path d="M8 12a4 4 0 0 1 8 0"></path><path d="M12 8v8"></path></svg><div class="ops-health-row-main"><div class="ops-health-row-label">Current Activity</div><div id="opsActivityDetail" class="ops-health-row-detail">ContextKeeper is initializing.</div></div><span id="opsActivityBadge" class="badge starting">Starting</span></div>
          <div class="ops-health-row"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a9 9 0 1 1-2.6-6.4"></path><path d="M21 3v6h-6"></path></svg><div class="ops-health-row-main"><div class="ops-health-row-label">Last Refresh</div><div id="opsLastRefreshDetail" class="ops-health-row-detail">Every {settings.dashboard.refresh_interval_ms or 1000} ms</div></div><span id="opsLastRefreshStatus" class="badge info">Pending</span></div>
        </div>
      </div>
    </div>
    <div class="card compact-card action-panel"><div class="health-title dashboard-card-header"><h2 class="dashboard-card-title"><span class="icon-label"><span class="icon-mark">!</span>Recommendations</span></h2><div class="dashboard-card-header-actions"><span class="badge">Action</span></div></div><div id="recommendationsList" class="panel-list"><div class="muted">No operator action queued.</div></div><div class="small">Open Analytics for full insight history.</div></div>
    <div class="hero-stats-grid" aria-label="Hero statistics">
      <div class="card hero-stat-card">
        <div class="hero-stat-top"><div class="hero-stat-label">Total Requests</div><div class="hero-stat-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 7h10"></path><path d="M4 12h16"></path><path d="M4 17h7"></path><path d="m16 15 3-3-3-3"></path></svg></div></div>
        <div id="req" class="hero-stat-value">0</div>
        <div class="hero-stat-desc">Request Statistics across the local proxy.</div>
        <svg class="mini-chart hero-stat-hidden-binding" viewBox="0 0 220 48" preserveAspectRatio="none" aria-hidden="true"><polygon id="requestSparkArea" class="spark-area" points="0,48 220,48"></polygon><polyline id="requestSparkline" class="sparkline" points="0,40 44,40 88,40 132,40 176,40 220,40"></polyline></svg>
      </div>
      <div class="card hero-stat-card">
        <div class="hero-stat-top"><div class="hero-stat-label">Active Conversations</div><div class="hero-stat-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 8h10"></path><path d="M7 12h7"></path><path d="M5 18 3 21v-4a7 7 0 0 1-1-4V9a6 6 0 0 1 6-6h8a6 6 0 0 1 6 6v4a6 6 0 0 1-6 6H8z"></path></svg></div></div>
        <div id="activeConversationCount" class="hero-stat-value">0</div>
        <div class="hero-stat-desc">Conversation windows currently tracked.</div>
      </div>
      <div class="card hero-stat-card">
        <div class="hero-stat-top"><div class="hero-stat-label">Compression Savings</div><div class="hero-stat-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 3v5H3"></path><path d="M16 21v-5h5"></path><path d="M3 8a8 8 0 0 1 13.7-4.7L21 8"></path><path d="M21 16a8 8 0 0 1-13.7 4.7L3 16"></path></svg></div></div>
        <div id="compressionCount" class="hero-stat-value">0</div>
        <div id="compressionText" class="hero-stat-desc">Compression events will appear here.</div>
      </div>
      <div class="card hero-stat-card">
        <div class="hero-stat-top"><div class="hero-stat-label">Average Response Time</div><div class="hero-stat-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 8v5l3 2"></path><circle cx="12" cy="12" r="9"></circle></svg></div></div>
        <div class="signal-body"><div><div id="averageLatency" class="hero-stat-value">0 ms</div><div class="hero-stat-desc">Recent request latency.</div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="latencyGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div>
      </div>
    </div>
  </section>

  <section id="instrumentPanel" class="instrument-panel" aria-label="Dashboard instrument panel">
    <div id="cpuInstrumentCard" class="card instrument-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">CPU Usage</div><div class="instrument-head-actions dashboard-card-header-actions"><div class="instrument-info" title="Processor utilization and hardware detail">i</div></div></div>
      <div class="instrument-body"><div id="cpuInstrumentGauge" class="instrument-gauge-shell" data-gauge-label="CPU Usage"></div></div>
      <div class="instrument-reading"><div id="cpuInstrumentValue" class="instrument-card-value" data-live-value="true">--</div><span id="cpuInstrumentStatus" class="badge">Loading</span></div>
      <div id="cpuInstrumentSupport" class="instrument-support" data-instrument-support="cpu" aria-label="CPU supporting details">
        <div class="instrument-support-row primary" data-support-slot="1">CPU telemetry is loading.</div>
        <div class="instrument-support-row" data-support-slot="2">Thread count pending.</div>
        <div class="instrument-support-row" data-support-slot="3">Temperature pending.</div>
      </div>
    </div>
    <div id="gpuInstrumentCard" class="card instrument-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">GPU Usage</div><div class="instrument-head-actions dashboard-card-header-actions"><div class="instrument-info" title="GPU utilization, VRAM, and temperature when available">i</div></div></div>
      <div class="instrument-body"><div id="gpuInstrumentGauge" class="instrument-gauge-shell" data-gauge-label="GPU Usage"></div></div>
      <div class="instrument-reading"><div id="gpuInstrumentValue" class="instrument-card-value" data-live-value="true">--</div><span id="gpuInstrumentStatus" class="badge">Loading</span></div>
      <div id="gpuInstrumentSupport" class="instrument-support" data-instrument-support="gpu" aria-label="GPU supporting details">
        <div class="instrument-support-row primary" data-support-slot="1">GPU telemetry is loading.</div>
        <div class="instrument-support-row" data-support-slot="2">VRAM pending.</div>
        <div class="instrument-support-row" data-support-slot="3">Temperature pending.</div>
      </div>
    </div>
    <div id="memoryInstrumentCard" class="card instrument-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">Memory Usage</div><div class="instrument-head-actions dashboard-card-header-actions"><div class="instrument-info" title="System memory utilization">i</div></div></div>
      <div class="instrument-body"><div id="memoryInstrumentGauge" class="instrument-gauge-shell" data-gauge-label="Memory Usage"></div></div>
      <div class="instrument-reading"><div id="memoryInstrumentValue" class="instrument-card-value" data-live-value="true">--</div><span id="memoryInstrumentStatus" class="badge">Loading</span></div>
      <div id="memoryInstrumentSupport" class="instrument-support" data-instrument-support="memory" aria-label="Memory supporting details">
        <div class="instrument-support-row primary" data-support-slot="1">Memory telemetry is loading.</div>
        <div class="instrument-support-row" data-support-slot="2">Capacity pending.</div>
        <div class="instrument-support-row" data-support-slot="3">Status pending.</div>
      </div>
    </div>
    <div id="contextInstrumentCard" class="card instrument-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">Context Usage</div><div class="instrument-head-actions dashboard-card-header-actions"><span id="contextInstrumentCapacity" class="instrument-header-badge dashboard-header-badge" title="Effective context window capacity">--</span><div class="instrument-info" title="Active conversation token pressure">i</div></div></div>
      <div class="instrument-body"><div id="contextInstrumentGauge" class="instrument-gauge-shell" data-gauge-label="Context Usage"></div></div>
      <div class="instrument-reading"><div id="contextInstrumentValue" class="instrument-card-value" data-live-value="true">--</div><span id="contextInstrumentStatus" class="badge">Loading</span></div>
      <div id="contextInstrumentSupport" class="instrument-support" data-instrument-support="context" aria-label="Context supporting details">
        <div class="instrument-support-row primary" data-support-slot="1">Active context telemetry is loading.</div>
        <div class="instrument-support-row" data-support-slot="2">Model pending.</div>
        <div class="instrument-support-row" data-support-slot="3">Thresholds pending.</div>
      </div>
    </div>
    <div id="compressionInstrumentCard" class="card instrument-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">Compression Status</div><div class="instrument-head-actions dashboard-card-header-actions"><div class="instrument-info" title="Compression readiness and threshold proximity">i</div></div></div>
      <div class="instrument-body"><div id="compressionInstrumentGauge" class="instrument-gauge-shell" data-gauge-label="Compression Status"></div></div>
      <div class="instrument-reading"><div id="compressionInstrumentValue" class="instrument-card-value" data-live-value="true">--</div><span id="compressionInstrumentStatus" class="badge">Loading</span></div>
      <div id="compressionInstrumentSupport" class="instrument-support" data-instrument-support="compression" aria-label="Compression supporting details">
        <div class="instrument-support-row primary" data-support-slot="1">Compression state is loading.</div>
        <div class="instrument-support-row" data-support-slot="2">Event count pending.</div>
        <div class="instrument-support-row" data-support-slot="3">Readiness pending.</div>
      </div>
    </div>
  </section>

  <section class="system-activity-grid" aria-label="System activity">
    <div id="contextTrendCard" class="card instrument-card instrument-trend-card">
      <div class="instrument-head dashboard-card-header"><div class="instrument-title dashboard-card-title">Context Trend</div><div class="instrument-head-actions dashboard-card-header-actions"><div class="instrument-info" title="Rolling active-context history">i</div></div></div>
      <div class="trend-body">
        <div class="trend-summary"><div id="contextTrendValue" class="trend-current" data-live-value="true">0%</div><span id="contextTrendStatus" class="badge waiting">Waiting</span></div>
        <div class="trend-chart-wrap">
          <svg id="contextTrendChart" class="trend-chart" viewBox="0 0 260 72" preserveAspectRatio="none" role="img" aria-labelledby="contextTrendA11y">
            <title id="contextTrendA11y">Awaiting context history.</title>
            <line class="trend-grid" x1="0" y1="36" x2="260" y2="36"></line>
            <line id="contextTrendWarning" class="trend-threshold warn" x1="0" y1="72" x2="260" y2="72"></line>
            <line id="contextTrendCompression" class="trend-threshold critical" x1="0" y1="72" x2="260" y2="72"></line>
            <polygon id="contextTrendArea" class="trend-area" points=""></polygon>
            <polyline id="contextTrendLine" class="trend-line" points=""></polyline>
          </svg>
          <div id="contextTrendEmpty" class="trend-empty">Awaiting context history.</div>
        </div>
        <div class="trend-footer"><span id="contextTrendDetail">Estimate unavailable</span><span id="contextTrendThresholds">Warn -- • Compress --</span></div>
      </div>
    </div>

  <section id="connections" class="card flow-panel ops-panel traffic-idle" data-traffic-state="idle" data-active-requests="0">
    <div class="health-title dashboard-card-header">
      <h2 class="flow-heading dashboard-card-title"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M18 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M6 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M8.6 6.5 15.4 10.5"></path><path d="M15.4 13.5 8.6 17.5"></path></svg>Connection Flow</h2>
      <span id="flowNote" class="flow-note">Topology idle; connected paths show availability.</span>
    </div>
    <div class="flow-stage">
      <svg class="flow-svg-layer" viewBox="0 0 1000 180" preserveAspectRatio="none" aria-hidden="true">
        <path id="flowLineClientProxy" class="flow-svg-line" data-flow-segment="client-proxy" d="M 55 90 C 180 90 200 90 325 90"></path>
        <path id="flowLineProxyOllama" class="flow-svg-line" data-flow-segment="proxy-ollama" d="M 325 90 C 450 90 470 90 595 90"></path>
        <path id="flowLineOllamaModel" class="flow-svg-line" data-flow-segment="ollama-model" d="M 595 90 C 720 90 740 90 945 90"></path>
        <circle id="flowPacketHalo" class="flow-svg-packet-halo" r="10" cx="0" cy="0"></circle>
        <circle id="flowPacket" class="flow-svg-packet" r="6.5" cx="0" cy="0"></circle>
      </svg>
      <div class="node flow-node" data-flow-node="client">
        <div class="flow-node-head"><div class="flow-node-title"><span id="clientDot" class="dot waiting"></span>Client</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"></rect><path d="M8 20h8"></path><path d="M12 16v4"></path></svg></div></div>
        <div class="flow-node-main"><div id="clientText" class="value">Waiting</div><div id="clientSub" class="small">No clients seen yet</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Inbound requests</span><span id="clientStatusBadge" class="badge waiting flow-status">Waiting</span></div>
      </div>
      <div class="pipe" data-flow-link="client-proxy"></div>
      <div class="node flow-node" data-flow-node="proxy">
        <div class="flow-node-head"><div class="flow-node-title"><span id="proxyDot" class="dot online"></span>ContextKeeper Status</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3 4 6v6c0 5 3.4 8 8 9 4.6-1 8-4 8-9V6z"></path><path d="m9 12 2 2 4-5"></path></svg></div></div>
        <div class="flow-node-main"><div class="value ok">Online</div><div id="proxySub" class="small">Listening on port {settings.server.port}</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Local proxy</span><span id="proxyStatusBadge" class="badge online flow-status">Online</span></div>
      </div>
      <div class="pipe" data-flow-link="proxy-ollama"></div>
      <div class="node flow-node signal-node" data-flow-node="ollama">
        <div class="flow-node-head"><div class="flow-node-title"><span id="ollamaDot" class="dot waiting"></span>Ollama Status</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2v4"></path><path d="M12 18v4"></path><path d="M4.9 4.9 7.8 7.8"></path><path d="m16.2 16.2 2.9 2.9"></path><path d="M2 12h4"></path><path d="M18 12h4"></path><circle cx="12" cy="12" r="4"></circle></svg></div></div>
        <div class="flow-node-main"><div id="ollamaText" class="value">Checking</div><div id="ollamaSub" class="small">{ollama_base_url_html}</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Upstream runtime</span><span id="ollamaStatusBadge" class="badge waiting flow-status">Checking</span></div>
      </div>
      <div class="pipe" data-flow-link="ollama-model"></div>
      <div class="node flow-node" data-flow-node="model">
        <div class="flow-node-head"><div class="flow-node-title"><span id="modelDot" class="dot waiting"></span>Model</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 7h8"></path><path d="M8 12h8"></path><path d="M8 17h5"></path><rect x="4" y="3" width="16" height="18" rx="2"></rect></svg></div></div>
        <div class="flow-node-main"><div id="modelText" class="value">Waiting</div><div id="modelSub" class="small">No model observed yet</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Active model</span><span id="modelStatusBadge" class="badge waiting flow-status">Waiting</span></div>
      </div>
    </div>
  </section>
  </section>

  <section class="operations-lower">
    <div class="card traffic-panel ops-panel">
      <div class="dashboard-card-header"><h2 class="dashboard-card-title">Traffic</h2></div>
      <div class="traffic-stats">
        <div class="traffic-stat"><div class="small">Request Trend</div><div id="requestTrend" class="value">Flat</div><div id="requestTrendText" class="muted">Awaiting request data.</div></div>
        <div class="traffic-stat"><div class="small">Rate</div><div id="requestRate" class="value">0</div><div class="muted">requests / min</div></div>
        <div class="traffic-stat"><div class="small">Errors</div><div id="err" class="value">0</div><div class="muted">proxy request errors</div></div>
      </div>
      <div class="request-traffic-viz" aria-label="Live request traffic over the last minute">
        <svg id="requestTrafficSvg" class="request-traffic-svg" viewBox="0 0 240 48" preserveAspectRatio="none" role="img" aria-label="Recent request frequency"></svg>
        <div class="request-traffic-footer">
          <div id="requestTrafficStatus" class="request-traffic-status">Idle</div>
          <div id="requestTrafficCaption" class="request-traffic-caption">Waiting for request traffic</div>
        </div>
      </div>
      <div class="muted traffic-note">Average response time is summarized in the hero statistics row. Errors are tracked with request statistics.</div>
    </div>
    <div class="card conversation-compact ops-panel">
      <div class="health-title dashboard-card-header"><h2 class="dashboard-card-title">Active Conversation</h2><div class="dashboard-card-header-actions"><a class="badge info" href="#conversations" data-page-link="conversations">Open</a></div></div>
      <div class="conversation-meta compact">
        <div><div class="small">Conversation ID</div><div id="opsActiveConversationId" class="muted">None</div></div>
        <div><div class="small">Model</div><div id="opsActiveModelName" class="muted">None</div></div>
        <div><div class="small">Context Usage</div><div id="opsActiveContextUsage" class="muted">--</div></div>
        <div><div class="small">Risk</div><div id="opsConversationRisk" class="muted">--</div></div>
      </div>
      <div id="opsConversationRiskIndicators" class="risk-row"></div>
      <div id="opsActiveRollingSummary" class="summary muted">No rolling summary available.</div>
    </div>
    <div class="card live-timeline-card ops-panel" aria-labelledby="liveConversationTimelineTitle">
      <div class="dashboard-card-header">
        <h2 id="liveConversationTimelineTitle" class="dashboard-card-title">Live Conversation Timeline</h2>
        <div class="dashboard-card-header-actions"><span id="liveConversationTimelineStatus" class="badge waiting">Waiting</span></div>
      </div>
      <div id="liveConversationTimelineList" class="live-timeline-list" aria-live="polite">
        <div class="live-timeline-empty">
          <div class="live-timeline-empty-title">Waiting for conversation activity</div>
          <div class="live-timeline-empty-detail">Request, context, and compression events will appear here without prompt or response content.</div>
        </div>
      </div>
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
    <div class="card signal-card compact-card"><h2><span class="icon-label"><span class="icon-mark">%</span>Context Usage</span></h2><div class="signal-body"><div class="signal-stack"><div id="contextUsage" class="value">--%</div><div id="contextUsageText" class="muted">Context window usage will appear here.</div><div class="bar"><div id="contextUsageBar" class="fill"></div></div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="contextGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div></div>
    <div class="card"><h2>Status</h2><div class="value ok">Running</div><div class="muted">Proxy -> {ollama_base_url_html}</div></div>
    <div class="card"><h2>Compression History</h2><div class="value">Tracked</div><div class="muted">Compression activity is summarized in the Operations hero statistics row.</div></div>
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

<section id="settings" class="page settings-page" data-page="settings" aria-labelledby="settingsPageTitle">
  <div class="page-header">
    <div><h2 id="settingsPageTitle" class="page-title">Settings</h2><div class="page-sub">Review active runtime, saved configuration, built-in defaults, and draft candidates, then manage approved settings safely.</div></div>
  </div>
  <aside class="settings-runtime-notice" role="note" aria-labelledby="settingsRuntimeNoticeTitle">
    <div class="settings-runtime-icon" aria-hidden="true">!</div>
    <div>
      <h3 id="settingsRuntimeNoticeTitle" class="settings-runtime-title">Runtime and saved configuration are separate</h3>
      <p class="settings-runtime-copy">Save runtime changes applies only runtime-editable drafts to the current ContextKeeper process. Reset stages built-in defaults: runtime-editable defaults are applied to the current process, while restart-required defaults remain browser drafts until saved. Save to configuration writes eligible drafts to contextkeeper.yaml without changing runtime or restarting ContextKeeper. Higher-priority environment or command-line overrides may still take precedence after restart.</p>
    </div>
  </aside>
  <div id="settingsStatus" class="settings-status" role="status" aria-live="polite" aria-atomic="true" tabindex="-1">Settings load when this page is opened.</div>
  <div id="settingsErrorSummary" class="settings-feedback settings-feedback-error" role="alert" aria-live="assertive" tabindex="-1" hidden></div>
  <div id="settingsLoadState" class="settings-state" hidden>
    <div id="settingsLoadStateTitle" class="settings-state-title">Loading settings</div>
    <div id="settingsLoadStateDetail" class="settings-state-detail">Requesting current runtime and persisted settings from ContextKeeper.</div>
    <button id="settingsRetryButton" class="settings-button" type="button" hidden>Retry loading settings</button>
  </div>
  <form id="settingsForm" class="settings-form" novalidate hidden>
    <div id="settingsCategories" class="settings-categories" aria-label="ContextKeeper settings categories"></div>
    <div class="settings-action-bar">
      <div id="settingsDirtySummary" class="settings-dirty-summary">No unsaved changes.</div>
      <div class="settings-actions">
        <button id="settingsResetAllButton" class="settings-button recovery" type="button" disabled>Reset managed settings to defaults</button>
        <button id="settingsDiscardButton" class="settings-button" type="button" disabled>Discard changes</button>
        <button id="settingsPersistButton" class="settings-button" type="button" disabled>Save to configuration</button>
        <button id="settingsSaveButton" class="settings-button primary" type="submit" disabled>Save runtime changes</button>
      </div>
    </div>
  </form>
</section>
</main>
</div>
</div>
<div id="conversationInspectorBackdrop" class="conversation-inspector-backdrop" hidden></div>
<aside id="conversationInspectorDrawer" class="conversation-inspector-drawer" role="complementary" aria-labelledby="conversationInspectorTitle" aria-hidden="true">
  <header class="conversation-inspector-header">
    <div class="conversation-inspector-title-row">
      <h2 id="conversationInspectorTitle" class="conversation-inspector-title">Conversation Inspector</h2>
      <button id="conversationInspectorClose" type="button" class="conversation-inspector-close" aria-label="Close Conversation Inspector">
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12"></path><path d="M18 6 6 18"></path></svg>
      </button>
    </div>
    <div class="conversation-inspector-kicker">
      <span id="conversationInspectorConversationId">No conversation selected</span>
      <span id="conversationInspectorStatusBadge" class="badge waiting">Closed</span>
    </div>
    <div id="conversationInspectorModelLine" class="conversation-inspector-meta-line">Model not available</div>
    <div id="conversationInspectorStartedLine" class="conversation-inspector-meta-line">Start time not available</div>
  </header>
  <div class="conversation-inspector-body">
    <div id="conversationInspectorLiveRegion" class="conversation-inspector-live-region" aria-live="polite"></div>
    <section id="conversationInspectorLoading" class="conversation-inspector-state" aria-live="polite" hidden>
      <div class="conversation-inspector-state-title">Loading conversation details…</div>
      <div class="conversation-inspector-state-detail">ContextKeeper is preparing the currently selected conversation metadata.</div>
    </section>
    <section id="conversationInspectorUnavailable" class="conversation-inspector-state" aria-live="polite" hidden>
      <div class="conversation-inspector-state-title">Conversation details unavailable</div>
      <div class="conversation-inspector-state-detail">The selected conversation is not available in the current dashboard snapshot. Select another timeline entry or wait for fresh activity.</div>
    </section>
    <section id="conversationInspectorDetails" class="conversation-inspector-section" aria-label="Selected conversation overview and intelligence" hidden>
      <section class="conversation-inspector-subsection" aria-labelledby="conversationInspectorOverviewTitle">
        <h3 id="conversationInspectorOverviewTitle" class="conversation-inspector-section-title">Overview</h3>
        <div id="conversationInspectorOverviewGrid" class="conversation-inspector-grid"></div>
      </section>
      <section class="conversation-inspector-subsection" aria-labelledby="conversationInspectorIntelligenceTitle">
        <h3 id="conversationInspectorIntelligenceTitle" class="conversation-inspector-section-title">Intelligence</h3>
        <div id="conversationInspectorIntelligenceCard" class="conversation-inspector-intelligence-card unavailable">
          <div class="conversation-inspector-intelligence-head">
            <div id="conversationInspectorIntelligenceStatus" class="conversation-inspector-intelligence-title">Insufficient data</div>
            <span id="conversationInspectorIntelligenceBadge" class="badge unavailable">Unavailable</span>
          </div>
          <div id="conversationInspectorIntelligenceExplanation" class="conversation-inspector-intelligence-explanation">Conversation intelligence will appear when sufficient conversation data exists.</div>
          <div id="conversationInspectorIntelligenceSignals" class="conversation-inspector-signals"></div>
          <div id="conversationInspectorRecommendation" class="conversation-inspector-recommendation" hidden></div>
        </div>
      </section>
      <div class="conversation-inspector-note">B5.5.2 shows deterministic metadata and context intelligence only. Prompt text, responses, rolling summaries, request bodies, and retrieved content are deliberately excluded.</div>
    </section>
  </div>
</aside>
<script>
const DASHBOARD_REFRESH_INTERVAL_MS = {settings.dashboard.refresh_interval_ms or 1000};
const SETTINGS_ENDPOINT = '/api/dashboard/settings';
const SETTINGS_CONFIG_ENDPOINT = '/api/dashboard/settings/config';
const SETTINGS_CONNECTION_TEST_ENDPOINT = '/api/dashboard/settings/connection/test';
const CONNECTION_SETTINGS_CATEGORY_ID = 'ollama';
const CONNECTION_ENDPOINT_SETTING_ID = 'ollama.base_url';
const CONNECTION_TIMEOUT_SETTING_ID = 'ollama.timeout_seconds';
const CONNECTION_SETTING_IDS = [CONNECTION_ENDPOINT_SETTING_ID, CONNECTION_TIMEOUT_SETTING_ID];
const TOPOLOGY_OUTBOUND_DURATION_MS = 1300;
const TOPOLOGY_INBOUND_DURATION_MS = 1200;
const REQUEST_TRAFFIC_BUCKETS = 24;
const REQUEST_TRAFFIC_WINDOW_MS = 60000;
const REDUCED_MOTION_QUERY = window.matchMedia('(prefers-reduced-motion: reduce)');
const ACTIVITY_TOPOLOGY_CLASSES = ['activity-starting','activity-connecting','activity-ready','activity-receiving','activity-thinking','activity-streaming','activity-finalizing','activity-idle'];
const TOPOLOGY_FLOW_CLASSES = ['traffic-idle','traffic-outbound','traffic-processing','traffic-inbound'];
const TOPOLOGY_FLOW_LABELS = {{
  idle:'Topology idle; connected paths show availability.',
  outbound:'Outbound request: Client -> ContextKeeper -> Ollama -> Model.',
  processing:'Generation active; Ollama and the model are processing.',
  inbound:'Inbound response: Model -> Ollama -> ContextKeeper -> Client.'
}};
const SVG_NS = 'http://www.w3.org/2000/svg';
const INSTRUMENT_GAUGE_SEGMENTS = [
  {{ start:0, end:55, className:'good' }},
  {{ start:55, end:75, className:'warn' }},
  {{ start:75, end:90, className:'orange' }},
  {{ start:90, end:100, className:'bad' }}
];
let lastTopologyActiveRequestCount = null;
let topologyFlowTimer = null;
let refreshInFlight = false;
let refreshAfterCurrent = false;
let dashboardRefreshTimer = null;
let dashboardRefreshIntervalMs = DASHBOARD_REFRESH_INTERVAL_MS;
const settingsPageState = {{
  confirmedSnapshot:null,
  draftSnapshot:null,
  confirmedSettingsById:new Map(),
  draftSettingsById:new Map(),
  controlsById:new Map(),
  resetButtonsById:new Map(),
  categoryResetButtonsById:new Map(),
  errorElementsById:new Map(),
  differenceElementsById:new Map(),
  fieldErrors:new Map(),
  loaded:false,
  loading:false,
  saving:false,
  persisting:false,
  resetting:false,
  discarding:false,
  testingConnection:false,
  connectionTestResult:null,
  confirmationRequired:false,
  confirmationAction:null,
  confirmationPreservedDraftValues:null
}};
const conversationInspectorState = {{
  selectedConversationId:null,
  inspectorOpen:false,
  inspectorLoading:false,
  inspectorError:null,
  selectedTimelineEventId:null,
  lastDashboardData:null
}};
function byId(id) {{
  return document.getElementById(id);
}}
function motionAllowed() {{
  return !REDUCED_MOTION_QUERY.matches;
}}
function restartAnimation(el, className) {{
  if (!el || !motionAllowed()) return;
  el.classList.remove(className);
  void el.offsetWidth;
  el.classList.add(className);
}}
function escapeHtml(value) {{
  return String(value ?? '').replace(/[&<>"']/g, char => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[char]));
}}
function setDot(id, status) {{
  const el = byId(id);
  if (!el) return;
  const nextClass = 'dot ' + (status === 'online' || status === 'active' ? 'online' : status === 'offline' ? 'offline' : 'waiting');
  if (el.className !== nextClass) el.className = nextClass;
}}
function safeClass(value) {{
  return String(value || '').toLowerCase().replace(/[^a-z0-9_-]/g, '');
}}
function titleCase(value) {{
  return String(value || '').replace(/_/g, ' ').replace(/(^|\\s)([a-z])/g, match => match.toUpperCase());
}}
function shouldAnimateTextUpdate(el) {{
  if (!motionAllowed()) return false;
  return el.matches('.value,.hero-stat-value,.ops-health-status') || el.dataset.liveValue === 'true';
}}
function setText(id, value, animate) {{
  const el = byId(id);
  if (!el) return;
  const next = String(value);
  if (el.textContent !== next) {{
    el.textContent = next;
    const shouldAnimate = animate ?? shouldAnimateTextUpdate(el);
    if (shouldAnimate) restartAnimation(el, 'value-pop');
  }}
}}
function setStatusBadge(id, value, label) {{
  const el = byId(id);
  if (!el) return;
  const extraClass = el.classList.contains('flow-status') ? ' flow-status' : '';
  const nextClass = 'badge ' + safeClass(value) + extraClass;
  const currentClass = Array.from(el.classList).filter(name => name !== 'badge-update').join(' ');
  const changed = currentClass !== nextClass;
  if (changed) el.className = nextClass;
  setText(id, label ?? titleCase(value || 'unknown'), false);
  if (changed) restartAnimation(el, 'badge-update');
  const node = el.closest ? el.closest('.flow-node') : null;
  if (changed && node) {{
    restartAnimation(node, 'status-pulse');
  }}
}}
function setInstrumentReadingNeutral(valueId, neutral) {{
  const valueEl = byId(valueId);
  const reading = valueEl ? valueEl.closest('.instrument-reading') : null;
  if (reading) reading.classList.toggle('is-neutral', Boolean(neutral));
}}
function updateContextHeaderBadge(current) {{
  const badge = byId('contextInstrumentCapacity');
  if (!badge) return;
  const label = current && (current.header_badge || current.context_window_label)
    ? String(current.header_badge || current.context_window_label)
    : '--';
  const title = current && current.header_badge_title
    ? String(current.header_badge_title)
    : 'Effective context window capacity';
  setText('contextInstrumentCapacity', label, false);
  badge.setAttribute('title', title);
  badge.setAttribute('aria-label', title);
  badge.classList.toggle('is-neutral', label === '--' || (current && current.context_window_state === 'waiting'));
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
  el.style.width = value;
}}
function heroStateForStatus(status) {{
  if (status === 'healthy') return {{ icon:'🟢', title:'All Systems Operational' }};
  if (status === 'critical' || status === 'offline') return {{ icon:'🔴', title:'System Degraded' }};
  return {{ icon:'🟡', title:'Attention Required' }};
}}
function heroStateForHealth(health) {{
  const reasons = Array.isArray(health?.reasons) ? health.reasons : [];
  if (reasons[0] === 'model_warming' || health?.label === 'Model warming') return {{ icon:'🔵', title:'Model Warming' }};
  return heroStateForStatus(health?.status || 'unknown');
}}
function healthGaugeValue(status) {{
  return ({{healthy: 100, busy: 76, warning: 48, critical: 20, offline: 4}})[status] ?? 0;
}}
function latencyGaugeValue(latencyMs) {{
  const latency = Math.max(0, Number(latencyMs) || 0);
  return Math.max(0, 100 - Math.min(100, latency / 50));
}}
function connectorClass(status) {{
  const normalized = safeClass(status);
  if (normalized === 'offline' || normalized === 'error' || normalized === 'critical') return 'flow-svg-line flow-line-offline';
  if (normalized === 'online' || normalized === 'active' || normalized === 'healthy' || normalized === 'running') return 'flow-svg-line flow-line-active';
  return 'flow-svg-line flow-line-waiting';
}}
function setConnectorState(id, status) {{
  const line = byId(id);
  if (line) line.setAttribute('class', connectorClass(status));
}}
function clearTopologyFlowTimer() {{
  if (topologyFlowTimer !== null) {{
    clearTimeout(topologyFlowTimer);
    topologyFlowTimer = null;
  }}
}}
function setTopologyTrafficState(panel, state) {{
  if (!panel) return;
  const next = TOPOLOGY_FLOW_CLASSES.includes('traffic-' + safeClass(state)) ? safeClass(state) : 'idle';
  panel.classList.remove(...TOPOLOGY_FLOW_CLASSES);
  panel.classList.add('traffic-' + next);
  panel.dataset.trafficState = next;
  setText('flowNote', TOPOLOGY_FLOW_LABELS[next] || TOPOLOGY_FLOW_LABELS.idle, false);
}}
function settleTopologyTraffic(panel) {{
  const activeCount = Number(panel?.dataset?.activeRequests || 0);
  setTopologyTrafficState(panel, activeCount > 0 ? 'processing' : 'idle');
}}
function scheduleTopologySettle(panel, durationMs) {{
  clearTopologyFlowTimer();
  topologyFlowTimer = setTimeout(() => {{
    topologyFlowTimer = null;
    settleTopologyTraffic(panel);
  }}, durationMs);
}}
function updateTopologyTraffic(activity) {{
  const panel = byId('connections');
  if (!panel) return;
  const current = activity || {{}};
  const numericCount = Number(current.active_request_count || 0);
  const activeCount = Number.isFinite(numericCount) && numericCount > 0 ? numericCount : 0;
  const previousCount = lastTopologyActiveRequestCount;
  panel.dataset.activeRequests = String(activeCount);
  panel.dataset.activeEndpoint = current.active_endpoint || '';
  panel.dataset.activeGenerationSequence = current.active_generation_sequence ?? '';
  panel.dataset.activeRequestId = current.active_request_id || '';

  if (previousCount === null) {{
    clearTopologyFlowTimer();
    setTopologyTrafficState(panel, activeCount > 0 ? 'processing' : 'idle');
  }} else if (previousCount <= 0 && activeCount > 0) {{
    clearTopologyFlowTimer();
    setTopologyTrafficState(panel, 'outbound');
    scheduleTopologySettle(panel, TOPOLOGY_OUTBOUND_DURATION_MS);
  }} else if (previousCount > 0 && activeCount > 0) {{
    if (!panel.classList.contains('traffic-outbound')) {{
      clearTopologyFlowTimer();
      setTopologyTrafficState(panel, 'processing');
    }}
  }} else if (previousCount > 0 && activeCount <= 0) {{
    clearTopologyFlowTimer();
    setTopologyTrafficState(panel, 'inbound');
    scheduleTopologySettle(panel, TOPOLOGY_INBOUND_DURATION_MS);
  }} else if (!panel.classList.contains('traffic-inbound')) {{
    clearTopologyFlowTimer();
    setTopologyTrafficState(panel, 'idle');
  }}
  lastTopologyActiveRequestCount = activeCount;
}}
function updateTopologyState(connections, activity) {{
  const panel = byId('connections');
  if (!panel || !connections) return;
  const clientStatus = connections.client?.status || 'waiting';
  const proxyStatus = connections.proxy?.status || 'online';
  const ollamaStatus = connections.ollama?.status || 'waiting';
  const modelStatus = connections.model?.status || 'waiting';
  setConnectorState('flowLineClientProxy', clientStatus === 'online' && proxyStatus === 'online' ? 'online' : clientStatus);
  setConnectorState('flowLineProxyOllama', ollamaStatus);
  setConnectorState('flowLineOllamaModel', ollamaStatus === 'online' && modelStatus === 'active' ? 'active' : modelStatus === 'offline' ? 'offline' : 'waiting');
  const flowState = ollamaStatus === 'offline' || proxyStatus === 'offline' ? 'flow-offline' : ollamaStatus === 'online' ? 'flow-active' : 'flow-waiting';
  panel.classList.remove('flow-active', 'flow-waiting', 'flow-offline');
  panel.classList.add(flowState);
  updateActivityTopology(activity);
}}
function updateActivityTopology(activity) {{
  const panel = byId('connections');
  if (!panel) return;
  const current = activity || {{}};
  const state = safeClass(current.state || '');
  panel.classList.remove(...ACTIVITY_TOPOLOGY_CLASSES);
  if (state) panel.classList.add('activity-' + state);
  updateTopologyTraffic(current);
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
function parseRequestTimestamp(value) {{
  const timestamp = Date.parse(value || '');
  return Number.isFinite(timestamp) ? timestamp : null;
}}
function requestCountLabel(count) {{
  return count === 1 ? '1 request' : count + ' requests';
}}
function renderRequestTraffic(requests) {{
  const svg = byId('requestTrafficSvg');
  if (!svg) return;
  const bucketCount = REQUEST_TRAFFIC_BUCKETS;
  const width = 240;
  const baselineY = 42;
  const topPadding = 6;
  const availableHeight = baselineY - topPadding;
  const bucketMs = REQUEST_TRAFFIC_WINDOW_MS / bucketCount;
  const now = Date.now();
  const buckets = Array(bucketCount).fill(0);
  let validHistoryCount = 0;
  (requests || []).forEach(item => {{
    const timestamp = parseRequestTimestamp(item?.timestamp);
    if (timestamp === null) return;
    validHistoryCount += 1;
    const age = now - timestamp;
    if (age < 0 || age > REQUEST_TRAFFIC_WINDOW_MS) return;
    const index = Math.max(0, Math.min(bucketCount - 1, bucketCount - 1 - Math.floor(age / bucketMs)));
    buckets[index] += 1;
  }});
  const recentCount = buckets.reduce((total, count) => total + count, 0);
  const maxBucket = Math.max(...buckets, 1);
  const barGap = 2;
  const bucketWidth = width / bucketCount;
  const barWidth = Math.max(2, bucketWidth - barGap);
  const grid = [14, 26].map(y => `<line class="request-traffic-grid" x1="0" y1="${{y}}" x2="${{width}}" y2="${{y}}"></line>`).join('');
  const bars = buckets.map((count, index) => {{
    const x = index * bucketWidth + (barGap / 2);
    const barHeight = count > 0 ? Math.max(4, (count / maxBucket) * availableHeight) : 2;
    const y = baselineY - barHeight;
    const className = count === 0 ? 'idle' : count >= 3 || (maxBucket > 1 && count === maxBucket) ? 'burst' : 'active';
    return `<rect class="request-traffic-bar ${{className}}" x="${{x.toFixed(1)}}" y="${{y.toFixed(1)}}" width="${{barWidth.toFixed(1)}}" height="${{barHeight.toFixed(1)}}" rx="1.7"><title>${{requestCountLabel(count)}} in bucket ${{index + 1}}</title></rect>`;
  }}).join('');
  svg.innerHTML = `${{grid}}<line class="request-traffic-baseline" x1="0" y1="${{baselineY}}" x2="${{width}}" y2="${{baselineY}}"></line>${{bars}}<line class="request-traffic-now" x1="${{width - 1}}" y1="${{topPadding}}" x2="${{width - 1}}" y2="${{baselineY}}"></line>`;
  if (recentCount === 0) {{
    const label = validHistoryCount === 0 ? 'No request history yet' : 'No requests in the last minute';
    setText('requestTrafficStatus', 'Idle', false);
    setText('requestTrafficCaption', label, false);
    svg.setAttribute('aria-label', label);
    return;
  }}
  const status = maxBucket >= 3 ? 'Burst' : 'Active';
  const peakText = maxBucket > 1 ? ' · peak ' + maxBucket : '';
  setText('requestTrafficStatus', status, false);
  setText('requestTrafficCaption', requestCountLabel(recentCount) + ' / 60 sec' + peakText, false);
  svg.setAttribute('aria-label', requestCountLabel(recentCount) + ' over the last minute; peak bucket ' + maxBucket);
}}
function numberOrNull(value) {{
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}}
function formatMetricNumber(value, digits) {{
  const numeric = numberOrNull(value);
  if (numeric === null) return 'N/A';
  const precision = digits ?? (Math.abs(numeric) >= 10 || Number.isInteger(numeric) ? 0 : 1);
  return numeric.toFixed(precision).replace(/\\.0$/, '');
}}
function formatPercentValue(value) {{
  const numeric = numberOrNull(value);
  return numeric === null ? 'N/A' : formatMetricNumber(numeric) + '%';
}}
function formatTokenValue(value) {{
  const numeric = numberOrNull(value);
  return numeric === null ? 'N/A' : Math.round(numeric).toLocaleString();
}}
function formatGbPair(used, total) {{
  const usedValue = numberOrNull(used);
  const totalValue = numberOrNull(total);
  if (usedValue === null || totalValue === null) return 'Memory capacity unavailable';
  return formatMetricNumber(usedValue, 1) + ' / ' + formatMetricNumber(totalValue, 1) + ' GB';
}}
function setInstrumentCardState(cardId, state) {{
  const card = byId(cardId);
  if (!card) return;
  const trendClass = card.classList.contains('instrument-trend-card') ? ' instrument-trend-card' : '';
  card.className = 'card instrument-card' + trendClass + ' ' + safeClass(state || 'unavailable');
}}
function svgElement(tag, attrs) {{
  const el = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs || {{}}).forEach(([key, value]) => el.setAttribute(key, value));
  return el;
}}
function gaugePoint(percent, radius) {{
  const clamped = Math.max(0, Math.min(100, Number(percent) || 0));
  const angle = (180 - (clamped * 1.8)) * Math.PI / 180;
  const r = radius ?? 48;
  return {{
    x: 60 + Math.cos(angle) * r,
    y: 60 - Math.sin(angle) * r
  }};
}}
function gaugePath(startPercent, endPercent) {{
  const start = gaugePoint(startPercent);
  const end = gaugePoint(endPercent);
  return `M ${{start.x.toFixed(2)}} ${{start.y.toFixed(2)}} A 48 48 0 0 1 ${{end.x.toFixed(2)}} ${{end.y.toFixed(2)}}`;
}}
function initializeInstrumentGauges() {{
  document.querySelectorAll('.instrument-gauge-shell').forEach(shell => {{
    if (shell.dataset.initialized === 'true') return;
    shell.dataset.initialized = 'true';
    shell.setAttribute('role', 'img');
    shell.setAttribute('aria-label', (shell.dataset.gaugeLabel || 'Gauge') + ': loading');
    const svg = svgElement('svg', {{
      class:'instrument-gauge-svg',
      viewBox:'0 0 120 76',
      preserveAspectRatio:'xMidYMid meet',
      'aria-hidden':'true'
    }});
    svg.appendChild(svgElement('path', {{ class:'instrument-gauge-baseline', d:gaugePath(0, 100) }}));
    INSTRUMENT_GAUGE_SEGMENTS.forEach(segment => {{
      svg.appendChild(svgElement('path', {{
        class:'instrument-gauge-segment ' + segment.className,
        d:gaugePath(segment.start, segment.end)
      }}));
    }});
    [0, 25, 50, 75, 100].forEach(tick => {{
      const inner = gaugePoint(tick, 40);
      const outer = gaugePoint(tick, 48);
      svg.appendChild(svgElement('line', {{
        class:'instrument-gauge-tick',
        x1:inner.x.toFixed(2),
        y1:inner.y.toFixed(2),
        x2:outer.x.toFixed(2),
        y2:outer.y.toFixed(2)
      }}));
    }});
    svg.appendChild(svgElement('line', {{ class:'instrument-gauge-needle', x1:'60', y1:'60', x2:'60', y2:'18' }}));
    svg.appendChild(svgElement('circle', {{ class:'instrument-gauge-pivot', cx:'60', cy:'60', r:'4.8' }}));
    const center = svgElement('text', {{ class:'instrument-gauge-center', x:'60', y:'42' }});
    center.textContent = '--';
    svg.appendChild(center);
    shell.replaceChildren(svg);
  }});
}}
function updateInstrumentGauge(id, value, centerText, statusLabel) {{
  const shell = byId(id);
  if (!shell) return;
  const numeric = numberOrNull(value);
  const available = numeric !== null;
  const clamped = available ? Math.max(0, Math.min(100, numeric)) : 0;
  const needle = shell.querySelector('.instrument-gauge-needle');
  const center = shell.querySelector('.instrument-gauge-center');
  if (needle) needle.style.transform = `rotate(${{(-90 + (clamped * 1.8)).toFixed(2)}}deg)`;
  if (center) center.textContent = centerText || (available ? formatPercentValue(clamped) : 'N/A');
  shell.classList.toggle('is-unavailable', !available);
  const label = shell.dataset.gaugeLabel || 'Gauge';
  const stateText = statusLabel ? ', ' + statusLabel : '';
  shell.setAttribute('aria-label', label + ': ' + (centerText || (available ? formatPercentValue(clamped) : 'unavailable')) + stateText);
}}
function normalizeInstrumentDetailLine(line, fallback) {{
  if (line && typeof line === 'object') {{
    const text = line.text === null || line.text === undefined ? '' : String(line.text).trim();
    const title = line.title === null || line.title === undefined ? text : String(line.title).trim();
    const kind = line.kind === null || line.kind === undefined ? '' : String(line.kind).trim();
    const modelName = line.model_name === null || line.model_name === undefined ? '' : String(line.model_name).trim();
    const sourceLabel = line.source_label === null || line.source_label === undefined ? '' : String(line.source_label).trim();
    return {{
      text:text || fallback,
      title:title || text || fallback,
      kind,
      model_name:modelName,
      source_label:sourceLabel
    }};
  }}
  const text = line === null || line === undefined ? '' : String(line).trim();
  return {{ text:text || fallback, title:text || fallback, kind:'', model_name:'', source_label:'' }};
}}
function renderInstrumentSupport(id, detailLines, fallbackLines) {{
  const support = byId(id);
  if (!support) return;
  const source = Array.isArray(detailLines) ? detailLines : [];
  const fallbacks = Array.isArray(fallbackLines) && fallbackLines.length ? fallbackLines : ['Detail unavailable', 'Detail unavailable', 'Detail unavailable'];
  support.querySelectorAll('[data-support-slot]').forEach((row, index) => {{
    const fallback = fallbacks[index] || 'Detail unavailable';
    const line = normalizeInstrumentDetailLine(source[index], fallback);
    row.classList.toggle('model-source', line.kind === 'model_source' && Boolean(line.model_name) && Boolean(line.source_label));
    row.replaceChildren();
    if (line.kind === 'model_source' && line.model_name && line.source_label) {{
      const modelSpan = document.createElement('span');
      modelSpan.className = 'instrument-support-model';
      modelSpan.textContent = line.model_name;
      modelSpan.setAttribute('title', line.model_name);
      const separator = document.createElement('span');
      separator.className = 'instrument-support-separator';
      separator.textContent = '•';
      const sourceSpan = document.createElement('span');
      sourceSpan.className = 'instrument-support-source';
      sourceSpan.textContent = line.source_label;
      row.append(modelSpan, separator, sourceSpan);
    }} else {{
      row.textContent = line.text;
    }}
    if (line.title) row.setAttribute('title', line.title);
    else row.removeAttribute('title');
  }});
}}
function updateUtilizationInstrument(config, data) {{
  const current = data || {{}};
  const status = current.status || 'unavailable';
  const label = current.status_label || titleCase(status);
  const value = numberOrNull(current.usage_percent);
  const valueText = value === null ? 'N/A' : formatPercentValue(value);
  setInstrumentCardState(config.cardId, status);
  setText(config.valueId, valueText);
  setStatusBadge(config.statusId, status, label);
  renderInstrumentSupport(config.supportId, current.detail_lines, config.supportFallbacks || [
    current.message || config.emptyText || 'Telemetry unavailable.',
    'Detail unavailable',
    'Detail unavailable'
  ]);
  updateInstrumentGauge(config.gaugeId, value, valueText, label);
}}
function updateContextUsageInstrument(context) {{
  const current = context || {{}};
  const status = current.status || current.state || 'unavailable';
  const label = current.status_label || titleCase(status);
  const usage = numberOrNull(current.usage_percent);
  const disabled = current.state === 'disabled';
  const gaugeValue = disabled ? 0 : usage;
  const valueText = disabled ? '' : (usage === null ? 'N/A' : formatPercentValue(usage));
  const centerText = disabled ? '0%' : valueText;
  setInstrumentCardState('contextInstrumentCard', status);
  updateContextHeaderBadge(current);
  setInstrumentReadingNeutral('contextInstrumentValue', disabled);
  setText('contextInstrumentValue', valueText);
  setStatusBadge('contextInstrumentStatus', status, label);
  renderInstrumentSupport('contextInstrumentSupport', current.detail_lines, [
    current.message || 'Active context telemetry unavailable.',
    (current.active_model ? current.active_model + ' • ' : '') + (current.context_window_source_label || 'Default'),
    'Warn ' + (current.warning_threshold_percent ?? '--') + '% • Compress ' + (current.compression_threshold_percent ?? '--') + '%'
  ]);
  updateInstrumentGauge('contextInstrumentGauge', gaugeValue, centerText, label);
}}
function updateCompressionInstrument(compression) {{
  const current = compression || {{}};
  const state = current.state || current.status || 'unavailable';
  const label = current.status_label || titleCase(state);
  const proximity = numberOrNull(current.proximity_percent);
  const disabled = state === 'disabled';
  const valueText = disabled ? '' : label;
  const centerText = disabled ? '—' : label;
  setInstrumentCardState('compressionInstrumentCard', state);
  setInstrumentReadingNeutral('compressionInstrumentValue', disabled);
  setText('compressionInstrumentValue', valueText);
  setStatusBadge('compressionInstrumentStatus', state, label);
  renderInstrumentSupport('compressionInstrumentSupport', current.detail_lines, [
    'Threshold ' + (current.threshold_percent ?? '--') + '%',
    'Events ' + (current.event_count ?? 0),
    current.message || 'Compression status unavailable.'
  ]);
  updateInstrumentGauge('compressionInstrumentGauge', disabled ? null : proximity, centerText, 'Threshold proximity ' + (disabled || proximity === null ? 'unavailable' : formatPercentValue(proximity)));
}}
function renderContextTrend(trend) {{
  const current = trend || {{}};
  const state = current.state || 'empty';
  const displayState = state === 'empty' ? 'waiting' : (current.status || state);
  const displayLabel = state === 'empty' ? 'Waiting' : (current.status_label || (state === 'ready' ? 'Ready' : titleCase(displayState)));
  const samples = Array.isArray(current.samples) ? current.samples : [];
  const currentUsage = numberOrNull(current.current_usage_percent);
  setInstrumentCardState('contextTrendCard', displayState);
  setText('contextTrendValue', currentUsage === null && state === 'empty' ? '0%' : (currentUsage === null ? '--' : formatPercentValue(currentUsage)));
  setStatusBadge('contextTrendStatus', displayState, displayLabel);
  setText('contextTrendDetail', current.estimate_label || current.message || 'Estimate unavailable');
  setText('contextTrendThresholds', 'Warn ' + (current.warning_threshold_percent ?? '--') + '% • Compress ' + (current.compression_threshold_percent ?? '--') + '%');

  const line = byId('contextTrendLine');
  const area = byId('contextTrendArea');
  const empty = byId('contextTrendEmpty');
  const warning = byId('contextTrendWarning');
  const compression = byId('contextTrendCompression');
  const title = byId('contextTrendA11y');
  if (!line || !area || !empty || !warning || !compression) return;

  const width = 260;
  const height = 72;
  const pad = 8;
  const yForPercent = percent => {{
    const value = Math.max(0, Math.min(100, Number(percent) || 0));
    return height - pad - ((value / 100) * (height - (pad * 2)));
  }};
  const warningY = yForPercent(current.warning_threshold_percent);
  const compressionY = yForPercent(current.compression_threshold_percent);
  warning.setAttribute('y1', warningY.toFixed(2));
  warning.setAttribute('y2', warningY.toFixed(2));
  compression.setAttribute('y1', compressionY.toFixed(2));
  compression.setAttribute('y2', compressionY.toFixed(2));

  const values = samples.map(sample => numberOrNull(sample.usage_percent)).filter(value => value !== null);
  if (values.length < 2) {{
    line.setAttribute('points', '');
    area.setAttribute('points', '');
    empty.style.display = 'grid';
    empty.textContent = current.message || 'Awaiting context history.';
    if (title) title.textContent = current.message || 'Awaiting context history.';
    return;
  }}

  const points = values.map((value, index) => {{
    const x = values.length === 1 ? width - pad : pad + ((index / (values.length - 1)) * (width - (pad * 2)));
    const y = yForPercent(value);
    return `${{x.toFixed(2)}},${{y.toFixed(2)}}`;
  }}).join(' ');
  line.setAttribute('points', points);
  area.setAttribute('points', `${{pad}},${{height - pad}} ${{points}} ${{width - pad}},${{height - pad}}`);
  empty.style.display = 'none';
  if (title) title.textContent = 'Context trend with ' + values.length + ' sample(s). Current usage ' + (currentUsage === null ? 'unavailable' : formatPercentValue(currentUsage)) + '.';
}}
function updateInstrumentPanel(instrumentPanel) {{
  const panel = instrumentPanel || {{}};
  updateUtilizationInstrument({{
    cardId:'cpuInstrumentCard',
    gaugeId:'cpuInstrumentGauge',
    valueId:'cpuInstrumentValue',
    statusId:'cpuInstrumentStatus',
    supportId:'cpuInstrumentSupport',
    emptyText:'CPU telemetry unavailable.',
    supportFallbacks:['CPU identity unavailable', 'Thread count unavailable', 'Temperature unavailable']
  }}, panel.cpu);
  updateUtilizationInstrument({{
    cardId:'gpuInstrumentCard',
    gaugeId:'gpuInstrumentGauge',
    valueId:'gpuInstrumentValue',
    statusId:'gpuInstrumentStatus',
    supportId:'gpuInstrumentSupport',
    emptyText:'GPU telemetry unavailable.',
    supportFallbacks:['GPU unavailable', 'VRAM unavailable', 'Temperature unavailable']
  }}, panel.gpu);
  updateUtilizationInstrument({{
    cardId:'memoryInstrumentCard',
    gaugeId:'memoryInstrumentGauge',
    valueId:'memoryInstrumentValue',
    statusId:'memoryInstrumentStatus',
    supportId:'memoryInstrumentSupport',
    emptyText:'Memory telemetry unavailable.',
    supportFallbacks:['Used memory unavailable', 'Total memory unavailable', 'Memory status unavailable']
  }}, panel.memory);
  updateContextUsageInstrument(panel.context_usage);
  renderContextTrend(panel.context_trend);
  updateCompressionInstrument(panel.compression_status);
}}
function cloneSettingsSnapshot(snapshot) {{
  return JSON.parse(JSON.stringify(snapshot));
}}
function freezeSettingsSnapshot(value) {{
  if (!value || typeof value !== 'object' || Object.isFrozen(value)) return value;
  Object.getOwnPropertyNames(value).forEach(key => freezeSettingsSnapshot(value[key]));
  return Object.freeze(value);
}}
function settingValueMatchesDataType(dataType, value) {{
  if (dataType === 'boolean') return typeof value === 'boolean';
  if (dataType === 'integer') return Number.isSafeInteger(value);
  if (dataType === 'string') return typeof value === 'string';
  return false;
}}
function validateSettingsSnapshot(snapshot) {{
  const invalid = () => {{ throw new Error('The settings response format is not supported.'); }};
  if (!snapshot || typeof snapshot !== 'object' || snapshot.schema_version !== 2 || !Array.isArray(snapshot.categories)) invalid();
  const categoryIds = new Set();
  const settingIds = new Set();
  snapshot.categories.forEach(category => {{
    if (!category || typeof category !== 'object' || typeof category.id !== 'string' || !category.id ||
        typeof category.display_name !== 'string' || typeof category.description !== 'string' || !Array.isArray(category.settings) ||
        categoryIds.has(category.id)) invalid();
    categoryIds.add(category.id);
    category.settings.forEach(setting => {{
      if (!setting || typeof setting !== 'object' || typeof setting.id !== 'string' || typeof setting.category !== 'string' ||
          typeof setting.display_name !== 'string' || typeof setting.description !== 'string' ||
          typeof setting.runtime_editable !== 'boolean' || typeof setting.restart_required !== 'boolean' ||
          typeof setting.persistable !== 'boolean' || typeof setting.reset_eligible !== 'boolean' ||
          typeof setting.differs_from_persisted !== 'boolean' ||
          !['boolean','integer','string'].includes(setting.data_type) || setting.category !== category.id || settingIds.has(setting.id) ||
          !settingValueMatchesDataType(setting.data_type, setting.value) ||
          !settingValueMatchesDataType(setting.data_type, setting.persisted_value) ||
          !settingValueMatchesDataType(setting.data_type, setting.default_value)) invalid();
      const prefix = category.id + '.';
      const fieldName = setting.id.startsWith(prefix) ? setting.id.slice(prefix.length) : '';
      if (!fieldName || fieldName.includes('.')) invalid();
      if (setting.minimum !== null && !Number.isSafeInteger(setting.minimum)) invalid();
      if (setting.maximum !== null && !Number.isSafeInteger(setting.maximum)) invalid();
      if (setting.data_type !== 'integer' && (setting.minimum !== null || setting.maximum !== null)) invalid();
      if (setting.minimum !== null && setting.maximum !== null && setting.minimum > setting.maximum) invalid();
      if (setting.data_type === 'integer' && setting.minimum !== null &&
          (setting.value < setting.minimum || setting.persisted_value < setting.minimum || setting.default_value < setting.minimum)) invalid();
      if (setting.data_type === 'integer' && setting.maximum !== null &&
          (setting.value > setting.maximum || setting.persisted_value > setting.maximum || setting.default_value > setting.maximum)) invalid();
      if (setting.reset_eligible && !setting.runtime_editable && !setting.persistable) invalid();
      if (setting.differs_from_persisted !== !settingsValuesEqual(setting.value, setting.persisted_value)) invalid();
      settingIds.add(setting.id);
    }});
  }});
  return snapshot;
}}
function settingsIndex(snapshot) {{
  const index = new Map();
  if (!snapshot) return index;
  snapshot.categories.forEach(category => category.settings.forEach(setting => index.set(setting.id, setting)));
  return index;
}}
function setSettingsStatus(message, tone) {{
  const status = byId('settingsStatus');
  if (!status) return;
  status.className = 'settings-status' + (tone ? ' ' + safeClass(tone) : '');
  status.textContent = message;
}}
function focusSettingsStatus() {{
  const status = byId('settingsStatus');
  if (status && settingsPageIsActive()) status.focus();
}}
function clearSettingsPageError() {{
  const summary = byId('settingsErrorSummary');
  if (!summary) return;
  summary.textContent = '';
  summary.hidden = true;
}}
function settingsPageIsActive() {{
  const page = byId('settings');
  return Boolean(page && page.classList.contains('active'));
}}
function showSettingsPageError(message, focusSummary) {{
  const summary = byId('settingsErrorSummary');
  if (!summary) return;
  summary.textContent = message;
  summary.hidden = false;
  if (focusSummary && settingsPageIsActive()) summary.focus();
}}
function showSettingsLoadState(title, detail, retryable) {{
  const state = byId('settingsLoadState');
  if (!state) return;
  setText('settingsLoadStateTitle', title, false);
  setText('settingsLoadStateDetail', detail, false);
  const retry = byId('settingsRetryButton');
  if (retry) retry.hidden = !retryable;
  state.hidden = false;
}}
function hideSettingsLoadState() {{
  const state = byId('settingsLoadState');
  if (state) state.hidden = true;
}}
function createSettingsElement(tagName, className, textValue) {{
  const element = document.createElement(tagName);
  if (className) element.className = className;
  if (textValue !== undefined) element.textContent = String(textValue);
  return element;
}}
function formatSettingValue(value, dataType) {{
  if (dataType === 'boolean') return value ? 'Enabled' : 'Disabled';
  return String(value);
}}
function settingsDescriptionIds(controlId, setting) {{
  const ids = [controlId + '-description', controlId + '-metadata', controlId + '-difference', controlId + '-error'];
  if (!setting.runtime_editable || !setting.persistable) ids.push(controlId + '-availability');
  if (setting.restart_required) ids.push(controlId + '-restart');
  return ids.join(' ');
}}
function createSettingsBadge(label, state) {{
  return createSettingsElement('span', 'badge ' + state, label);
}}
function createSettingsControl(setting, controlId) {{
  let control;
  if (setting.data_type === 'boolean') {{
    const row = createSettingsElement('div', 'settings-checkbox-row');
    control = createSettingsElement('input', 'settings-checkbox');
    control.type = 'checkbox';
    control.checked = setting.value;
    const state = createSettingsElement('span', 'settings-checkbox-state', setting.value ? 'Enabled' : 'Disabled');
    state.id = controlId + '-boolean-state';
    row.append(control, state);
    row.settingsControl = control;
    return row;
  }}
  control = createSettingsElement('input', 'settings-input');
  if (setting.data_type === 'integer') {{
    control.type = 'number';
    control.step = '1';
    control.required = true;
    control.inputMode = 'numeric';
    if (setting.minimum !== null) control.min = String(setting.minimum);
    if (setting.maximum !== null) control.max = String(setting.maximum);
  }} else {{
    control.type = setting.id === CONNECTION_ENDPOINT_SETTING_ID ? 'url' : 'text';
    if (setting.id === CONNECTION_ENDPOINT_SETTING_ID) {{
      control.required = true;
      control.inputMode = 'url';
      control.spellcheck = false;
    }}
    control.autocomplete = 'off';
    control.autocapitalize = 'none';
  }}
  control.value = String(setting.value);
  control.settingsControl = control;
  return control;
}}
function configureSettingsControl(controlRoot, setting, controlId) {{
  const control = controlRoot.settingsControl || controlRoot;
  control.id = controlId;
  control.name = setting.id;
  control.dataset.settingId = setting.id;
  control.dataset.settingType = setting.data_type;
  control.setAttribute('aria-describedby', settingsDescriptionIds(controlId, setting));
  control.disabled = (!setting.runtime_editable && !setting.persistable) || settingsPageState.loading || settingsPageState.saving ||
    settingsPageState.persisting || settingsPageState.resetting || settingsPageState.discarding ||
    settingsPageState.testingConnection;
  if (control.disabled) control.setAttribute('aria-disabled', 'true');
  else control.removeAttribute('aria-disabled');
  settingsPageState.controlsById.set(setting.id, control);
  return control;
}}
function createSettingsItem(setting, itemNumber) {{
  const controlId = 'settings-control-' + itemNumber;
  const confirmedSetting = settingsPageState.confirmedSettingsById.get(setting.id) || setting;
  const item = createSettingsElement('article', 'settings-item');
  const metadata = createSettingsElement('div', 'settings-item-meta');
  const labelRow = createSettingsElement('div', 'settings-label-row');
  const label = createSettingsElement('label', 'settings-label', setting.display_name);
  label.htmlFor = controlId;
  labelRow.append(label);
  if (!setting.runtime_editable) labelRow.append(createSettingsBadge('Runtime read-only', 'disabled'));
  if (!setting.persistable) labelRow.append(createSettingsBadge('Not persistable', 'disabled'));
  if (setting.differs_from_persisted) labelRow.append(createSettingsBadge('Runtime differs from saved', 'warning'));
  if (setting.restart_required) labelRow.append(createSettingsBadge('Restart required', 'warning'));
  const description = createSettingsElement('p', 'settings-item-description', setting.description);
  description.id = controlId + '-description';
  const metadataLine = createSettingsElement('div', 'settings-metadata');
  metadataLine.id = controlId + '-metadata';
  metadataLine.append(createSettingsElement('span', '', 'Default: ' + formatSettingValue(setting.default_value, setting.data_type)));
  metadataLine.append(createSettingsElement('span', '', 'Current runtime: ' + formatSettingValue(confirmedSetting.value, setting.data_type)));
  metadataLine.append(createSettingsElement('span', '', 'Saved configuration: ' + formatSettingValue(setting.persisted_value, setting.data_type)));
  if (setting.minimum !== null || setting.maximum !== null) {{
    const minimum = setting.minimum === null ? 'no minimum' : String(setting.minimum);
    const maximum = setting.maximum === null ? 'no maximum' : String(setting.maximum);
    metadataLine.append(createSettingsElement('span', '', 'Allowed range: ' + minimum + ' to ' + maximum));
  }}
  metadata.append(labelRow, description, metadataLine);

  const controlPanel = createSettingsElement('div', 'settings-control-panel');
  const controlRoot = createSettingsControl(setting, controlId);
  const control = configureSettingsControl(controlRoot, setting, controlId);
  controlPanel.append(controlRoot);
  if (setting.reset_eligible) {{
    const resetButton = createSettingsElement('button', 'settings-button recovery settings-reset-setting', 'Reset to default');
    resetButton.type = 'button';
    resetButton.dataset.settingsResetSetting = setting.id;
    resetButton.setAttribute('aria-label', 'Reset ' + setting.display_name + ' to built-in default');
    resetButton.addEventListener('click', () => void resetSettingsToDefaults({{ settingId:setting.id, label:setting.display_name }}));
    controlPanel.append(resetButton);
    settingsPageState.resetButtonsById.set(setting.id, resetButton);
  }}
  if (!setting.runtime_editable || !setting.persistable) {{
    let availabilityMessage = '';
    if (!setting.runtime_editable && setting.persistable) availabilityMessage = 'This draft can be saved to configuration, but it cannot be applied to the current runtime.';
    else if (setting.runtime_editable && !setting.persistable) availabilityMessage = 'This setting can be changed for the current runtime, but it cannot be saved to configuration.';
    else availabilityMessage = 'This setting cannot be changed during the current runtime or saved to configuration.';
    const availability = createSettingsElement('div', 'settings-field-note', availabilityMessage);
    availability.id = controlId + '-availability';
    controlPanel.append(availability);
  }}
  if (setting.restart_required) {{
    const restart = createSettingsElement('div', 'settings-field-note', 'Saved changes are read at startup and require a manual ContextKeeper restart. ContextKeeper is not restarted automatically. Higher-priority environment or command-line overrides may still take precedence.');
    restart.id = controlId + '-restart';
    controlPanel.append(restart);
  }}
  const difference = createSettingsElement('div', 'settings-difference');
  difference.id = controlId + '-difference';
  controlPanel.append(difference);
  settingsPageState.differenceElementsById.set(setting.id, difference);
  const error = createSettingsElement('div', 'settings-field-error');
  error.id = controlId + '-error';
  error.hidden = true;
  controlPanel.append(error);
  settingsPageState.errorElementsById.set(setting.id, error);
  item.append(metadata, controlPanel);
  return item;
}}
function createConnectionTestPanel() {{
  const panel = createSettingsElement('section', 'settings-connection-test');
  panel.setAttribute('aria-labelledby', 'settingsConnectionTestTitle');
  const header = createSettingsElement('div', 'settings-connection-test-header');
  const headingGroup = createSettingsElement('div', 'settings-connection-test-heading');
  const heading = createSettingsElement('h4', 'settings-connection-test-title', 'Test draft connection');
  heading.id = 'settingsConnectionTestTitle';
  const copy = createSettingsElement(
    'p',
    'settings-connection-test-copy',
    'Probe the endpoint and timeout currently entered above once. The temporary test does not save configuration, replace the active Ollama client, or update active health state.'
  );
  copy.id = 'settingsConnectionTestDescription';
  headingGroup.append(heading, copy);
  const button = createSettingsElement('button', 'settings-button', 'Test connection');
  button.id = 'settingsConnectionTestButton';
  button.type = 'button';
  button.setAttribute('aria-controls', 'settingsConnectionTestResult');
  button.setAttribute('aria-describedby', 'settingsConnectionTestDescription');
  button.addEventListener('click', () => void testDraftConnection());
  header.append(headingGroup, button);
  const result = createSettingsElement('div', 'settings-connection-result');
  result.id = 'settingsConnectionTestResult';
  result.setAttribute('role', 'status');
  result.setAttribute('aria-live', 'polite');
  result.setAttribute('aria-atomic', 'true');
  result.hidden = true;
  panel.append(header, result);
  return panel;
}}
function renderSettingsCategories() {{
  const container = byId('settingsCategories');
  if (!container || !settingsPageState.draftSnapshot) return false;
  settingsPageState.controlsById = new Map();
  settingsPageState.resetButtonsById = new Map();
  settingsPageState.categoryResetButtonsById = new Map();
  settingsPageState.errorElementsById = new Map();
  settingsPageState.differenceElementsById = new Map();
  const fragment = document.createDocumentFragment();
  let itemNumber = 0;
  settingsPageState.draftSnapshot.categories.forEach((category, categoryIndex) => {{
    const section = createSettingsElement('section', 'card settings-category');
    const headingId = 'settings-category-' + (categoryIndex + 1);
    section.setAttribute('aria-labelledby', headingId);
    const header = createSettingsElement('header', 'settings-category-header');
    const headingGroup = createSettingsElement('div', 'settings-category-heading');
    const heading = createSettingsElement('h3', 'settings-category-title', category.display_name);
    heading.id = headingId;
    const description = createSettingsElement('p', 'settings-category-description', category.description);
    headingGroup.append(heading, description);
    const resetCategory = createSettingsElement('button', 'settings-button recovery compact', 'Reset category to defaults');
    resetCategory.type = 'button';
    resetCategory.dataset.settingsResetCategory = category.id;
    resetCategory.setAttribute('aria-label', 'Reset ' + category.display_name + ' settings to built-in defaults');
    resetCategory.addEventListener('click', () => void resetSettingsToDefaults({{ categoryId:category.id, label:category.display_name, confirmation:true }}));
    settingsPageState.categoryResetButtonsById.set(category.id, resetCategory);
    header.append(headingGroup, resetCategory);
    const list = createSettingsElement('div', 'settings-list');
    if (category.id === CONNECTION_SETTINGS_CATEGORY_ID) list.classList.add('settings-list-connection');
    if (category.settings.length) {{
      category.settings.forEach(setting => {{
        itemNumber += 1;
        list.append(createSettingsItem(setting, itemNumber));
      }});
    }} else {{
      list.append(createSettingsElement('div', 'settings-field-note', 'No settings are exposed in this category.'));
    }}
    section.append(header, list);
    if (category.id === CONNECTION_SETTINGS_CATEGORY_ID) section.append(createConnectionTestPanel());
    fragment.append(section);
  }});
  container.replaceChildren(fragment);
  settingsPageState.differenceElementsById.forEach((element, settingId) => refreshSettingsDifference(settingId));
  settingsPageState.errorElementsById.forEach((element, settingId) => refreshSettingsFieldError(settingId));
  renderConnectionTestResult();
  return itemNumber > 0;
}}
function settingsValuesEqual(confirmedValue, draftValue) {{
  return typeof confirmedValue === typeof draftValue && confirmedValue === draftValue;
}}
function settingsDraftBaselineValue(setting) {{
  return !setting.runtime_editable && setting.persistable ? setting.persisted_value : setting.value;
}}
function createSettingsDraftSnapshot(confirmedSnapshot) {{
  const draft = cloneSettingsSnapshot(confirmedSnapshot);
  draft.categories.forEach(category => category.settings.forEach(setting => {{
    setting.value = settingsDraftBaselineValue(setting);
  }}));
  return draft;
}}
function isConnectionSettingId(settingId) {{
  return CONNECTION_SETTING_IDS.includes(settingId);
}}
function settingCanReset(setting) {{
  return Boolean(setting && setting.reset_eligible && (setting.runtime_editable || setting.persistable) &&
    settingValueMatchesDataType(setting.data_type, setting.default_value));
}}
function resettableSettings(options) {{
  if (!settingsPageState.confirmedSnapshot) return [];
  const selection = options || {{}};
  const changes = [];
  settingsPageState.confirmedSnapshot.categories.forEach(category => {{
    if (selection.categoryId && category.id !== selection.categoryId) return;
    category.settings.forEach(setting => {{
      if (selection.settingId && setting.id !== selection.settingId) return;
      if (!settingCanReset(setting)) return;
      const draftSetting = settingsPageState.draftSettingsById.get(setting.id);
      if (!draftSetting) return;
      if (!selection.includeAlreadyDefault && settingsValuesEqual(draftSetting.value, setting.default_value)) return;
      changes.push({{ setting:setting, value:setting.default_value }});
    }});
  }});
  return changes;
}}
function settingsDifferentFromPersisted() {{
  if (!settingsPageState.confirmedSnapshot) return [];
  const differences = [];
  settingsPageState.confirmedSnapshot.categories.forEach(category => category.settings.forEach(setting => {{
    if (settingsValuesEqual(setting.value, setting.persisted_value)) return;
    differences.push(setting);
  }}));
  return differences;
}}
function runtimeSettingsDifferentFromPersisted() {{
  if (!settingsPageState.confirmedSnapshot) return [];
  const changes = [];
  settingsPageState.confirmedSnapshot.categories.forEach(category => category.settings.forEach(setting => {{
    if (!setting.runtime_editable || settingsValuesEqual(setting.value, setting.persisted_value)) return;
    changes.push({{ setting:setting, value:setting.persisted_value }});
  }}));
  return changes;
}}
function changedDraftSettings() {{
  if (!settingsPageState.confirmedSnapshot || !settingsPageState.draftSnapshot) return [];
  const changes = [];
  settingsPageState.confirmedSnapshot.categories.forEach(category => category.settings.forEach(confirmedSetting => {{
    if (!confirmedSetting.runtime_editable && !confirmedSetting.persistable) return;
    const draftSetting = settingsPageState.draftSettingsById.get(confirmedSetting.id);
    const baselineValue = settingsDraftBaselineValue(confirmedSetting);
    if (draftSetting && !settingsValuesEqual(baselineValue, draftSetting.value)) {{
      changes.push({{ setting:confirmedSetting, value:draftSetting.value }});
    }}
  }}));
  return changes;
}}
function changedRuntimeSettings() {{
  return changedDraftSettings().filter(change => change.setting.runtime_editable);
}}
function changedPersistableSettings() {{
  if (!settingsPageState.confirmedSnapshot || !settingsPageState.draftSnapshot) return [];
  const changes = [];
  settingsPageState.confirmedSnapshot.categories.forEach(category => category.settings.forEach(confirmedSetting => {{
    if (!confirmedSetting.persistable) return;
    const draftSetting = settingsPageState.draftSettingsById.get(confirmedSetting.id);
    if (draftSetting && !settingsValuesEqual(confirmedSetting.persisted_value, draftSetting.value)) {{
      changes.push({{ setting:confirmedSetting, value:draftSetting.value }});
    }}
  }}));
  return changes;
}}
function settingsDifferenceMessage(settingId) {{
  const confirmed = settingsPageState.confirmedSettingsById.get(settingId);
  const draft = settingsPageState.draftSettingsById.get(settingId);
  if (!confirmed || !draft) return {{ message:'', state:'' }};
  const differsFromRuntime = !settingsValuesEqual(confirmed.value, draft.value);
  const differsFromPersisted = !settingsValuesEqual(confirmed.persisted_value, draft.value);
  if (differsFromRuntime && differsFromPersisted) return {{ message:'Draft differs from the current runtime and saved configuration.', state:'warning' }};
  if (differsFromRuntime) return {{ message:'Draft matches the saved configuration and differs from the current runtime.', state:'warning' }};
  if (differsFromPersisted) return {{ message:'Current runtime differs from the saved configuration.', state:'warning' }};
  return {{ message:'Draft matches the current runtime and saved configuration.', state:'success' }};
}}
function refreshSettingsDifference(settingId) {{
  const element = settingsPageState.differenceElementsById.get(settingId);
  if (!element) return;
  const difference = settingsDifferenceMessage(settingId);
  element.className = 'settings-difference' + (difference.state ? ' ' + difference.state : '');
  element.textContent = difference.message;
}}
function connectionDraftValues() {{
  const endpoint = settingsPageState.draftSettingsById.get(CONNECTION_ENDPOINT_SETTING_ID);
  const timeout = settingsPageState.draftSettingsById.get(CONNECTION_TIMEOUT_SETTING_ID);
  if (!endpoint || !timeout || typeof endpoint.value !== 'string' || !Number.isSafeInteger(timeout.value)) {{
    throw new Error('The draft connection settings are unavailable.');
  }}
  return {{ base_url:endpoint.value, timeout_seconds:timeout.value }};
}}
function connectionTestFailure(testedEndpoint, failureCategory, message) {{
  return {{
    connected:false,
    tested_endpoint:typeof testedEndpoint === 'string' && testedEndpoint ? testedEndpoint : null,
    latency_ms:null,
    ollama_version:null,
    failure_category:failureCategory,
    message:message
  }};
}}
function validateConnectionTestResponse(payload) {{
  const invalid = () => {{ throw new Error('The connection test response format is not supported.'); }};
  if (!payload || typeof payload !== 'object' || typeof payload.connected !== 'boolean' ||
      typeof payload.message !== 'string' || !payload.message.trim()) invalid();
  if (payload.tested_endpoint !== null && typeof payload.tested_endpoint !== 'string') invalid();
  if (payload.latency_ms !== null &&
      (typeof payload.latency_ms !== 'number' || !Number.isFinite(payload.latency_ms) || payload.latency_ms < 0)) invalid();
  if (payload.ollama_version !== null && typeof payload.ollama_version !== 'string') invalid();
  if (payload.failure_category !== null && typeof payload.failure_category !== 'string') invalid();
  if (payload.connected && (!payload.tested_endpoint || payload.latency_ms === null ||
      !payload.ollama_version || !payload.ollama_version.trim())) invalid();
  return {{
    connected:payload.connected,
    tested_endpoint:payload.tested_endpoint,
    latency_ms:payload.latency_ms,
    ollama_version:payload.ollama_version,
    failure_category:payload.failure_category,
    message:payload.message.trim()
  }};
}}
function appendConnectionResultDetail(details, label, value) {{
  if (value === null || value === undefined || value === '') return;
  details.append(
    createSettingsElement('dt', '', label),
    createSettingsElement('dd', '', value)
  );
}}
function formatConnectionLatency(latencyMs) {{
  return Number.isInteger(latencyMs) ? String(latencyMs) : String(Number(latencyMs.toFixed(1)));
}}
function formatConnectionFailureCategory(category) {{
  return typeof category === 'string' && category
    ? titleCase(category.replaceAll('_', ' ').replaceAll('-', ' '))
    : '';
}}
function renderConnectionTestResult() {{
  const region = byId('settingsConnectionTestResult');
  if (!region) return;
  region.replaceChildren();
  if (settingsPageState.testingConnection) {{
    region.hidden = false;
    region.className = 'settings-connection-result testing';
    region.append(
      createSettingsElement('div', 'settings-connection-result-title', 'Testing draft connection'),
      createSettingsElement('div', 'settings-connection-result-message', 'ContextKeeper is performing one bounded probe with the endpoint and timeout currently entered.'),
      createSettingsElement('div', 'settings-connection-result-note', 'The active runtime connection and saved configuration remain unchanged.')
    );
    return;
  }}
  const result = settingsPageState.connectionTestResult;
  if (!result) {{
    region.hidden = true;
    region.className = 'settings-connection-result';
    return;
  }}
  region.hidden = false;
  region.className = 'settings-connection-result ' + (result.connected ? 'success' : 'failure');
  const title = createSettingsElement(
    'div',
    'settings-connection-result-title',
    result.connected ? 'Connection successful' : 'Connection failed'
  );
  const message = createSettingsElement('div', 'settings-connection-result-message', result.message);
  const details = createSettingsElement('dl', 'settings-connection-result-details');
  appendConnectionResultDetail(details, 'Tested endpoint', result.tested_endpoint);
  if (result.latency_ms !== null) appendConnectionResultDetail(details, 'Round-trip latency', formatConnectionLatency(result.latency_ms) + ' ms');
  appendConnectionResultDetail(details, 'Ollama version', result.ollama_version);
  appendConnectionResultDetail(details, 'Failure category', formatConnectionFailureCategory(result.failure_category));
  const note = createSettingsElement(
    'div',
    'settings-connection-result-note',
    result.connected
      ? 'This tested the draft candidate only; it was not saved or activated. Save to configuration and restart ContextKeeper to make the saved endpoint eligible to become active. Higher-priority overrides may still take precedence.'
      : 'Runtime and saved configuration were not changed.'
  );
  region.append(title, message);
  if (details.childNodes.length) region.append(details);
  region.append(note);
}}
function clearConnectionTestResult() {{
  settingsPageState.connectionTestResult = null;
  renderConnectionTestResult();
}}
function settingsDraftValueIsValid(setting, value) {{
  if (!settingValueMatchesDataType(setting.data_type, value)) return false;
  if (setting.id === CONNECTION_ENDPOINT_SETTING_ID) return !settingsValidationMessage(setting, value);
  if (setting.data_type !== 'integer') return true;
  if (setting.minimum !== null && value < setting.minimum) return false;
  if (setting.maximum !== null && value > setting.maximum) return false;
  return true;
}}
function settingsDraftIsValid() {{
  if (!settingsPageState.draftSnapshot) return false;
  for (const setting of settingsPageState.draftSettingsById.values()) {{
    if ((setting.runtime_editable || setting.persistable) && !settingsDraftValueIsValid(setting, setting.value)) return false;
  }}
  for (const control of settingsPageState.controlsById.values()) {{
    if (!control.disabled && typeof control.checkValidity === 'function' && !control.checkValidity()) return false;
  }}
  return true;
}}
function settingsValidationMessage(setting, value) {{
  if (setting.id === CONNECTION_ENDPOINT_SETTING_ID) {{
    if (typeof value !== 'string' || !value.trim()) return 'Enter a complete AI Server Endpoint URL.';
    let endpoint;
    try {{
      endpoint = new URL(value);
    }} catch (error) {{
      return 'Enter a valid absolute AI Server Endpoint URL.';
    }}
    if (!['http:','https:'].includes(endpoint.protocol)) return 'Use an http:// or https:// AI Server Endpoint URL.';
    if (!endpoint.hostname) return 'Enter an AI Server Endpoint URL with a valid hostname or IP address.';
    if (endpoint.username || endpoint.password) return 'AI Server Endpoint credentials are not supported.';
    if (endpoint.search) return 'AI Server Endpoint query strings are not supported.';
    if (endpoint.hash) return 'AI Server Endpoint fragments are not supported.';
  }}
  if (setting.data_type === 'integer') {{
    if (value === null || value === undefined || Number.isNaN(value)) return 'Enter a whole number.';
    if (!Number.isSafeInteger(value)) return 'Enter a whole number within the supported safe range.';
    if (setting.minimum !== null && value < setting.minimum) return 'Enter a value of at least ' + setting.minimum + '.';
    if (setting.maximum !== null && value > setting.maximum) return 'Enter a value no greater than ' + setting.maximum + '.';
  }}
  return '';
}}
function refreshSettingsFieldError(settingId) {{
  const error = settingsPageState.errorElementsById.get(settingId);
  const control = settingsPageState.controlsById.get(settingId);
  if (!error || !control) return;
  const message = settingsPageState.fieldErrors.get(settingId) || '';
  error.textContent = message;
  error.hidden = !message;
  if (message) control.setAttribute('aria-invalid', 'true');
  else control.removeAttribute('aria-invalid');
}}
function clearSettingsFieldErrors() {{
  settingsPageState.fieldErrors = new Map();
  settingsPageState.errorElementsById.forEach((error, settingId) => refreshSettingsFieldError(settingId));
}}
function refreshSettingsPageErrorFromFields() {{
  const messages = Array.from(new Set(settingsPageState.fieldErrors.values()));
  if (!messages.length) {{
    clearSettingsPageError();
    return;
  }}
  showSettingsPageError('Some settings still need attention. ' + messages.join(' '), false);
}}
function setSettingsButtonDisabled(button, disabled) {{
  if (!button) return;
  button.disabled = disabled;
  if (disabled) button.setAttribute('aria-disabled', 'true');
  else button.removeAttribute('aria-disabled');
}}
function updateSettingsActions() {{
  const draftChanges = changedDraftSettings();
  const runtimeChanges = changedRuntimeSettings();
  const runtimeRecoveryChanges = runtimeSettingsDifferentFromPersisted();
  const confirmedDifferences = settingsDifferentFromPersisted();
  const persistenceChanges = changedPersistableSettings();
  const draftValid = settingsDraftIsValid();
  const busy = settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting ||
    settingsPageState.resetting || settingsPageState.discarding || settingsPageState.testingConnection;
  const locked = busy || settingsPageState.confirmationRequired;
  const save = byId('settingsSaveButton');
  const persist = byId('settingsPersistButton');
  const discard = byId('settingsDiscardButton');
  const resetAll = byId('settingsResetAllButton');
  const connectionTest = byId('settingsConnectionTestButton');
  if (save) save.disabled = locked || !settingsPageState.loaded || !runtimeChanges.length || !draftValid;
  if (persist) {{
    persist.disabled = locked || !settingsPageState.loaded || !persistenceChanges.length || !draftValid;
    persist.textContent = settingsPageState.persisting ? 'Saving to configuration...' : 'Save to configuration';
  }}
  if (discard) {{
    setSettingsButtonDisabled(discard, locked || !settingsPageState.loaded || (!draftChanges.length && !runtimeRecoveryChanges.length));
    discard.textContent = settingsPageState.discarding ? 'Discarding changes...' : 'Discard changes';
  }}
  if (connectionTest) {{
    const connectionSettingsAvailable = CONNECTION_SETTING_IDS.every(settingId =>
      settingsPageState.draftSettingsById.has(settingId));
    setSettingsButtonDisabled(connectionTest, locked || !settingsPageState.loaded || !connectionSettingsAvailable);
    connectionTest.textContent = settingsPageState.testingConnection ? 'Testing connection...' : 'Test connection';
  }}
  settingsPageState.resetButtonsById.forEach((button, settingId) => {{
    setSettingsButtonDisabled(button, locked || !settingsPageState.loaded || !resettableSettings({{ settingId:settingId }}).length);
  }});
  settingsPageState.categoryResetButtonsById.forEach((button, categoryId) => {{
    setSettingsButtonDisabled(button, locked || !settingsPageState.loaded || !resettableSettings({{ categoryId:categoryId }}).length);
  }});
  setSettingsButtonDisabled(resetAll, locked || !settingsPageState.loaded || !resettableSettings().length);
  settingsPageState.controlsById.forEach((control, settingId) => {{
    const setting = settingsPageState.draftSettingsById.get(settingId);
    control.disabled = locked || !setting || (!setting.runtime_editable && !setting.persistable);
    if (control.disabled) control.setAttribute('aria-disabled', 'true');
    else control.removeAttribute('aria-disabled');
  }});
  const form = byId('settingsForm');
  if (form) {{
    form.setAttribute('aria-busy', busy ? 'true' : 'false');
    form.setAttribute('aria-disabled', settingsPageState.confirmationRequired ? 'true' : 'false');
  }}
  const summary = byId('settingsDirtySummary');
  if (summary) {{
    if (settingsPageState.confirmationRequired) summary.textContent = 'Confirm the current server values before making another change.';
    else if (!draftChanges.length && !persistenceChanges.length && !runtimeRecoveryChanges.length) {{
      summary.textContent = confirmedDifferences.length
        ? 'No unsaved draft changes. ' + confirmedDifferences.length + ' active runtime value' + (confirmedDifferences.length === 1 ? '' : 's') + ' differs from saved configuration; a pending restart or higher-priority override may explain the difference.'
        : 'Runtime and saved configuration values are aligned. No unsaved changes.';
    }}
    else if (!draftValid) summary.textContent = 'Correct invalid draft values before saving.';
    else {{
      const pendingRuntimeIds = new Set(runtimeRecoveryChanges.map(change => change.setting.id));
      runtimeChanges.forEach(change => pendingRuntimeIds.add(change.setting.id));
      const runtimeCount = pendingRuntimeIds.size;
      const runtimeLabel = runtimeCount + ' runtime change' + (runtimeCount === 1 ? '' : 's');
      const configurationLabel = persistenceChanges.length + ' configuration change' + (persistenceChanges.length === 1 ? '' : 's');
      const restartOnlyDifferenceCount = confirmedDifferences.filter(setting => !setting.runtime_editable).length;
      const activeDifferenceLabel = restartOnlyDifferenceCount
        ? '; ' + restartOnlyDifferenceCount + ' restart-only active value' + (restartOnlyDifferenceCount === 1 ? '' : 's') + ' differs from saved configuration'
        : '';
      summary.textContent = runtimeLabel + '; ' + configurationLabel + ' eligible to save' + activeDifferenceLabel + '.';
    }}
  }}
}}
function captureSettingsDraftValues() {{
  const values = new Map();
  settingsPageState.draftSettingsById.forEach((setting, settingId) => values.set(settingId, setting.value));
  return values;
}}
function captureSettingsDraftValuesExcept(settingIds) {{
  const values = new Map();
  settingsPageState.draftSettingsById.forEach((setting, settingId) => {{
    if (!settingIds.has(settingId)) values.set(settingId, setting.value);
  }});
  return values;
}}
function firstInvalidSettingsControlOutside(settingIds) {{
  for (const [settingId, setting] of settingsPageState.draftSettingsById.entries()) {{
    if (settingIds.has(settingId) || (!setting.runtime_editable && !setting.persistable)) continue;
    const control = settingsPageState.controlsById.get(settingId);
    if (!settingsDraftValueIsValid(setting, setting.value)) return control || null;
    if (control && !control.disabled && typeof control.checkValidity === 'function' && !control.checkValidity()) return control;
  }}
  return null;
}}
function capturePersistenceOnlyDraftValues() {{
  const values = new Map();
  settingsPageState.draftSettingsById.forEach((setting, settingId) => {{
    const confirmed = settingsPageState.confirmedSettingsById.get(settingId);
    if (confirmed && !confirmed.runtime_editable && confirmed.persistable) values.set(settingId, setting.value);
  }});
  return values;
}}
function acceptSettingsSnapshot(snapshot, preservedDraftValues) {{
  validateSettingsSnapshot(snapshot);
  const confirmed = freezeSettingsSnapshot(cloneSettingsSnapshot(snapshot));
  const draft = createSettingsDraftSnapshot(confirmed);
  const confirmedIndex = settingsIndex(confirmed);
  const draftIndex = settingsIndex(draft);
  if (preservedDraftValues instanceof Map) {{
    preservedDraftValues.forEach((value, settingId) => {{
      const draftSetting = draftIndex.get(settingId);
      if (draftSetting && settingValueMatchesDataType(draftSetting.data_type, value)) draftSetting.value = value;
    }});
  }}
  settingsPageState.confirmedSnapshot = confirmed;
  settingsPageState.draftSnapshot = draft;
  settingsPageState.confirmedSettingsById = confirmedIndex;
  settingsPageState.draftSettingsById = draftIndex;
  settingsPageState.fieldErrors = new Map();
  settingsPageState.loaded = true;
  settingsPageState.confirmationRequired = false;
  settingsPageState.confirmationAction = null;
  settingsPageState.confirmationPreservedDraftValues = null;
  const hasSettings = renderSettingsCategories();
  const form = byId('settingsForm');
  if (form) form.hidden = !hasSettings;
  hideSettingsLoadState();
  if (!hasSettings) {{
    showSettingsLoadState('No settings available', 'ContextKeeper did not expose any settings for this runtime.', false);
  }}
  clearSettingsPageError();
  updateSettingsActions();
  return hasSettings;
}}
function valueFromSettingsControl(control, setting) {{
  if (setting.data_type === 'boolean') return control.checked;
  if (setting.data_type === 'integer') {{
    const rawValue = control.value.trim();
    return rawValue === '' ? null : Number(rawValue);
  }}
  return control.value;
}}
function handleSettingsInput(event) {{
  const control = event.target.closest ? event.target.closest('.settings-input,.settings-checkbox') : null;
  if (!control || settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting ||
      settingsPageState.resetting || settingsPageState.discarding || settingsPageState.testingConnection ||
      settingsPageState.confirmationRequired) return;
  const settingId = control.dataset.settingId;
  const setting = settingsPageState.draftSettingsById.get(settingId);
  if (!setting || (!setting.runtime_editable && !setting.persistable)) return;
  setting.value = valueFromSettingsControl(control, setting);
  if (isConnectionSettingId(settingId)) clearConnectionTestResult();
  if (setting.data_type === 'boolean') {{
    const state = byId(control.id + '-boolean-state');
    if (state) state.textContent = setting.value ? 'Enabled' : 'Disabled';
  }}
  settingsPageState.fieldErrors.delete(settingId);
  const validationMessage = settingsValidationMessage(setting, setting.value);
  if (validationMessage) settingsPageState.fieldErrors.set(settingId, validationMessage);
  refreshSettingsFieldError(settingId);
  refreshSettingsDifference(settingId);
  refreshSettingsPageErrorFromFields();
  updateSettingsActions();
  const runtimeChanges = changedRuntimeSettings();
  const persistenceChanges = changedPersistableSettings();
  if (!runtimeChanges.length && !persistenceChanges.length) setSettingsStatus('No unsaved changes.', '');
  else if (!settingsDraftIsValid()) setSettingsStatus('Review the invalid setting values before saving.', 'warning');
  else setSettingsStatus(runtimeChanges.length + ' runtime and ' + persistenceChanges.length + ' configuration change' + (persistenceChanges.length === 1 ? '' : 's') + ' available.', 'warning');
}}
function buildSettingsPayload(changes) {{
  const payload = Object.create(null);
  changes.forEach(change => {{
    const category = change.setting.category;
    const prefix = category + '.';
    const fieldName = change.setting.id.startsWith(prefix) ? change.setting.id.slice(prefix.length) : '';
    if (!fieldName || fieldName.includes('.')) throw new Error('A setting could not be mapped to the update request.');
    if (!Object.prototype.hasOwnProperty.call(payload, category)) payload[category] = Object.create(null);
    payload[category][fieldName] = change.value;
  }});
  return payload;
}}
function buildSettingsPatchPayload() {{
  return buildSettingsPayload(changedRuntimeSettings());
}}
function buildSettingsConfigPayload() {{
  return buildSettingsPayload(changedPersistableSettings());
}}
async function readSettingsResponse(response) {{
  try {{
    return await response.json();
  }} catch (error) {{
    return null;
  }}
}}
function validateSettingsPersistenceResponse(payload) {{
  if (!payload || typeof payload !== 'object' || payload.status !== 'saved' ||
      !Array.isArray(payload.persisted_setting_ids) || typeof payload.configuration_created !== 'boolean') {{
    throw new Error('The configuration persistence response format is not supported.');
  }}
  const persistedSettingIds = new Set();
  payload.persisted_setting_ids.forEach(settingId => {{
    if (typeof settingId !== 'string' || !settingId || persistedSettingIds.has(settingId)) {{
      throw new Error('The configuration persistence response format is not supported.');
    }}
    persistedSettingIds.add(settingId);
  }});
  validateSettingsSnapshot(payload.settings);
  return payload;
}}
function settingsErrorMessages(payload) {{
  if (!payload || typeof payload !== 'object') return [];
  if (typeof payload.detail === 'string' && payload.detail.trim()) return [payload.detail.trim()];
  if (!Array.isArray(payload.detail)) return [];
  return payload.detail
    .filter(detail => detail && typeof detail === 'object' && typeof detail.msg === 'string' && detail.msg.trim())
    .map(detail => detail.msg.trim());
}}
function settingsErrorMessage(payload, statusCode, action) {{
  const messages = settingsErrorMessages(payload);
  if (messages.length) return Array.from(new Set(messages)).join(' ');
  return 'ContextKeeper could not ' + action + ' settings (HTTP ' + statusCode + ').';
}}
function settingIdFromErrorLocation(location) {{
  if (!Array.isArray(location)) return null;
  const parts = location[0] === 'body' ? location.slice(1) : location.slice();
  if (parts.some(part => typeof part !== 'string')) return null;
  let settingId = parts.length === 2 ? parts.join('.') : null;
  if (parts.length === 1 && ['base_url','timeout_seconds'].includes(parts[0])) settingId = 'ollama.' + parts[0];
  if (!settingId) return null;
  return settingsPageState.draftSettingsById.has(settingId) ? settingId : null;
}}
function clearSettingsFieldErrorsFor(settingIds) {{
  settingIds.forEach(settingId => {{
    settingsPageState.fieldErrors.delete(settingId);
    refreshSettingsFieldError(settingId);
  }});
}}
function applySettingsValidationErrors(payload, allowedSettingIds) {{
  const allowed = Array.isArray(allowedSettingIds) ? new Set(allowedSettingIds) : null;
  if (allowed) clearSettingsFieldErrorsFor(allowedSettingIds);
  else clearSettingsFieldErrors();
  if (!payload || !Array.isArray(payload.detail)) return null;
  let firstInvalidControl = null;
  payload.detail.forEach(detail => {{
    if (!detail || typeof detail !== 'object' || typeof detail.msg !== 'string') return;
    const settingId = settingIdFromErrorLocation(detail.loc);
    if (!settingId || (allowed && !allowed.has(settingId))) return;
    settingsPageState.fieldErrors.set(settingId, detail.msg);
    refreshSettingsFieldError(settingId);
    if (!firstInvalidControl) firstInvalidControl = settingsPageState.controlsById.get(settingId) || null;
  }});
  return firstInvalidControl;
}}
function validateConnectionDraft() {{
  clearSettingsFieldErrorsFor(CONNECTION_SETTING_IDS);
  let firstInvalidControl = null;
  CONNECTION_SETTING_IDS.forEach(settingId => {{
    const setting = settingsPageState.draftSettingsById.get(settingId);
    const control = settingsPageState.controlsById.get(settingId);
    let message = setting ? settingsValidationMessage(setting, setting.value) : 'This connection setting is unavailable.';
    if (!message && control && typeof control.checkValidity === 'function' && !control.checkValidity()) {{
      message = settingId === CONNECTION_ENDPOINT_SETTING_ID
        ? 'Enter a valid absolute AI Server Endpoint URL.'
        : 'Enter a valid Request Timeout.';
    }}
    if (!message) return;
    settingsPageState.fieldErrors.set(settingId, message);
    refreshSettingsFieldError(settingId);
    if (!firstInvalidControl) firstInvalidControl = control || null;
  }});
  refreshSettingsPageErrorFromFields();
  return firstInvalidControl;
}}
async function testDraftConnection() {{
  if (settingsPageState.testingConnection || settingsPageState.loading || settingsPageState.saving ||
      settingsPageState.persisting || settingsPageState.resetting || settingsPageState.discarding ||
      settingsPageState.confirmationRequired || !settingsPageState.loaded) return;
  const invalidControl = validateConnectionDraft();
  if (invalidControl) {{
    settingsPageState.connectionTestResult = connectionTestFailure(
      null,
      'invalid_request',
      'Connection test could not start because the draft connection values are invalid.'
    );
    renderConnectionTestResult();
    setSettingsStatus('Correct the invalid connection values before testing. No settings were changed.', 'warning');
    if (settingsPageIsActive()) invalidControl.focus();
    return;
  }}
  let payload;
  try {{
    payload = connectionDraftValues();
  }} catch (error) {{
    settingsPageState.connectionTestResult = connectionTestFailure(
      null,
      'invalid_request',
      'Connection test could not start because the draft connection values are unavailable.'
    );
    renderConnectionTestResult();
    setSettingsStatus('Connection test could not start. Runtime and saved configuration were not changed.', 'warning');
    return;
  }}

  settingsPageState.testingConnection = true;
  settingsPageState.connectionTestResult = null;
  clearSettingsPageError();
  setSettingsStatus('Testing the draft connection once...', '');
  updateSettingsActions();
  renderConnectionTestResult();
  let focusAfterTest = null;
  try {{
    const response = await fetch(SETTINGS_CONNECTION_TEST_ENDPOINT, {{
      method:'POST',
      headers:{{'Accept':'application/json','Content-Type':'application/json'}},
      body:JSON.stringify({{
        base_url:payload.base_url,
        timeout_seconds:payload.timeout_seconds
      }})
    }});
    const responsePayload = await readSettingsResponse(response);
    if (!response.ok) {{
      focusAfterTest = applySettingsValidationErrors(responsePayload, CONNECTION_SETTING_IDS);
      refreshSettingsPageErrorFromFields();
    }}
    try {{
      settingsPageState.connectionTestResult = validateConnectionTestResponse(responsePayload);
    }} catch (error) {{
      settingsPageState.connectionTestResult = connectionTestFailure(
        payload.base_url,
        'invalid_response',
        response.ok
          ? 'ContextKeeper returned an unsupported connection test response.'
          : settingsErrorMessage(responsePayload, response.status, 'test the connection')
      );
    }}
    if (!response.ok) {{
      showSettingsPageError(settingsPageState.connectionTestResult.message, !focusAfterTest);
      setSettingsStatus('Connection validation failed. Runtime and saved configuration were not changed.', 'warning');
    }} else if (settingsPageState.connectionTestResult.connected) {{
      setSettingsStatus('Draft connection test succeeded. No settings were saved or activated.', 'success');
    }} else {{
      setSettingsStatus('Draft connection test failed. Runtime and saved configuration were not changed.', 'warning');
    }}
  }} catch (error) {{
    settingsPageState.connectionTestResult = connectionTestFailure(
      payload.base_url,
      'dashboard_unreachable',
      'ContextKeeper could not complete the connection test request. Check the dashboard connection and try again.'
    );
    setSettingsStatus('Connection test could not be completed. Runtime and saved configuration were not changed.', 'warning');
  }} finally {{
    settingsPageState.testingConnection = false;
    updateSettingsActions();
    renderConnectionTestResult();
    if (focusAfterTest && settingsPageIsActive()) focusAfterTest.focus();
  }}
}}
async function requestSettingsSnapshot() {{
  let response;
  try {{
    response = await fetch(SETTINGS_ENDPOINT, {{
      method:'GET',
      headers:{{'Accept':'application/json'}}
    }});
  }} catch (error) {{
    throw new Error('ContextKeeper could not be reached. Check the connection and try again.');
  }}
  const payload = await readSettingsResponse(response);
  if (!response.ok) throw new Error(settingsErrorMessage(payload, response.status, 'load'));
  return validateSettingsSnapshot(payload);
}}
async function loadSettings() {{
  if (settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting ||
      settingsPageState.resetting || settingsPageState.discarding || settingsPageState.testingConnection) return;
  settingsPageState.loading = true;
  clearSettingsPageError();
  const form = byId('settingsForm');
  if (form) form.hidden = true;
  showSettingsLoadState('Loading settings', 'Requesting current runtime and persisted settings from ContextKeeper.', false);
  setSettingsStatus('Loading settings...', '');
  updateSettingsActions();
  try {{
    const snapshot = await requestSettingsSnapshot();
    const hasSettings = acceptSettingsSnapshot(snapshot);
    const persistedDifferences = settingsDifferentFromPersisted().length;
    if (!hasSettings) setSettingsStatus('No settings are currently available.', 'warning');
    else if (persistedDifferences) setSettingsStatus('Settings loaded. ' + persistedDifferences + ' active runtime value' + (persistedDifferences === 1 ? '' : 's') + ' differs from saved configuration; a pending restart or higher-priority override may explain the difference.', 'warning');
    else setSettingsStatus('Settings loaded. Runtime and saved configuration values are aligned.', 'success');
  }} catch (error) {{
    settingsPageState.loaded = false;
    settingsPageState.confirmedSnapshot = null;
    settingsPageState.draftSnapshot = null;
    settingsPageState.confirmedSettingsById = new Map();
    settingsPageState.draftSettingsById = new Map();
    settingsPageState.controlsById = new Map();
    settingsPageState.resetButtonsById = new Map();
    settingsPageState.categoryResetButtonsById = new Map();
    settingsPageState.errorElementsById = new Map();
    settingsPageState.differenceElementsById = new Map();
    settingsPageState.fieldErrors = new Map();
    const message = error instanceof Error && error.message
      ? error.message
      : 'ContextKeeper could not load settings. Check the connection and try again.';
    showSettingsLoadState('Settings could not be loaded', message, true);
    showSettingsPageError(message, false);
    setSettingsStatus('Settings load failed. Retry is available.', 'warning');
  }} finally {{
    settingsPageState.loading = false;
    updateSettingsActions();
  }}
}}
function ensureSettingsLoaded() {{
  if (!settingsPageState.loaded && !settingsPageState.loading) void loadSettings();
}}
async function confirmSettingsAfterAcceptedUpdate() {{
  if (!settingsPageState.confirmationRequired || settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting ||
      settingsPageState.resetting || settingsPageState.discarding || settingsPageState.testingConnection) return;
  const confirmationAction = settingsPageState.confirmationAction;
  const preservedDraftValues = confirmationAction === 'configuration'
    ? captureSettingsDraftValues()
    : confirmationAction === 'reset' && settingsPageState.confirmationPreservedDraftValues instanceof Map
      ? settingsPageState.confirmationPreservedDraftValues
      : confirmationAction === 'discard'
        ? new Map()
        : capturePersistenceOnlyDraftValues();
  settingsPageState.loading = true;
  clearSettingsPageError();
  if (confirmationAction === 'configuration') {{
    showSettingsLoadState('Confirming saved configuration', 'Requesting authoritative runtime and persisted values after the accepted configuration write.', false);
    setSettingsStatus('Confirming saved configuration...', '');
  }} else {{
    showSettingsLoadState('Confirming current settings', 'Requesting the authoritative values after the accepted update.', false);
    setSettingsStatus('Confirming current settings...', '');
  }}
  updateSettingsActions();
  try {{
    const snapshot = await requestSettingsSnapshot();
    if (confirmationAction === 'discard') settingsPageState.connectionTestResult = null;
    acceptSettingsSnapshot(snapshot, preservedDraftValues);
    setSettingsStatus(confirmationAction === 'configuration' ? 'Saved configuration confirmed. Your draft is still available.' : 'Current runtime settings confirmed.', 'success');
  }} catch (error) {{
    const message = error instanceof Error && error.message
      ? error.message
      : confirmationAction === 'configuration'
        ? 'ContextKeeper could not confirm the saved configuration. Check the connection and try again.'
        : 'ContextKeeper could not confirm the current settings. Check the connection and try again.';
    showSettingsLoadState(confirmationAction === 'configuration' ? 'Saved configuration still needs confirmation' : 'Current settings still need confirmation', message, true);
    showSettingsPageError(message, false);
    setSettingsStatus(confirmationAction === 'configuration' ? 'Saved configuration could not be confirmed. Retry is available.' : 'Current settings could not be confirmed. Retry is available.', 'warning');
  }} finally {{
    settingsPageState.loading = false;
    updateSettingsActions();
  }}
}}
function stageSettingsDraftChanges(changes) {{
  changes.forEach(change => {{
    const draftSetting = settingsPageState.draftSettingsById.get(change.setting.id);
    if (draftSetting) draftSetting.value = change.value;
  }});
  settingsPageState.fieldErrors = new Map();
  if (changes.some(change => isConnectionSettingId(change.setting.id))) settingsPageState.connectionTestResult = null;
  renderSettingsCategories();
  clearSettingsPageError();
  updateSettingsActions();
}}
function announceSettingsReset(changes, runtimeResetChanges, selection) {{
  const scopeLabel = selection.settingId
    ? selection.label + ' default'
    : selection.categoryId
      ? selection.label + ' defaults'
      : 'Managed settings defaults';
  const unsavedResetCount = changes.filter(change => {{
    const confirmed = settingsPageState.confirmedSettingsById.get(change.setting.id);
    const draft = settingsPageState.draftSettingsById.get(change.setting.id);
    return confirmed && draft && confirmed.persistable &&
      !settingsValuesEqual(draft.value, confirmed.persisted_value);
  }}).length;
  const configurationOnlyCount = changes.filter(change => !change.setting.runtime_editable).length;
  const runtimeMessage = runtimeResetChanges.length
    ? ' ' + runtimeResetChanges.length + ' runtime setting' + (runtimeResetChanges.length === 1 ? '' : 's') + ' applied to the current process.'
    : ' Runtime was not changed.';
  const draftOnlyMessage = configurationOnlyCount
    ? ' ' + configurationOnlyCount + ' restart-only setting' + (configurationOnlyCount === 1 ? '' : 's') + ' staged as a browser draft.'
    : '';
  const configurationMessage = unsavedResetCount
    ? ' Configuration has not been saved. Use Save to configuration for restart persistence.'
    : ' Configuration was not changed by this reset; persisted values already match. No configuration save is needed.';
  const restartCount = changes.filter(change => {{
    const confirmed = settingsPageState.confirmedSettingsById.get(change.setting.id);
    const draft = settingsPageState.draftSettingsById.get(change.setting.id);
    return change.setting.restart_required && confirmed && draft &&
      !settingsValuesEqual(draft.value, confirmed.persisted_value);
  }}).length;
  const restartMessage = restartCount
    ? ' ' + restartCount + ' saved setting' + (restartCount === 1 ? '' : 's') + ' will require a manual restart after saving; higher-priority overrides may still take precedence.'
    : '';
  setSettingsStatus(
    scopeLabel + ' staged for ' + changes.length + ' managed setting' + (changes.length === 1 ? '' : 's') + '.' +
      runtimeMessage + draftOnlyMessage + configurationMessage + restartMessage,
    'success'
  );
  focusSettingsStatus();
}}
async function resetSettingsToDefaults(options) {{
  if (settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting || settingsPageState.resetting ||
      settingsPageState.discarding || settingsPageState.testingConnection ||
      settingsPageState.confirmationRequired || !settingsPageState.loaded) return;
  const selection = options || {{}};
  const resetSelection = {{ ...selection, includeAlreadyDefault:Boolean(selection.confirmation) }};
  const changes = resettableSettings(resetSelection);
  if (!changes.length) {{
    setSettingsStatus('The selected managed settings already use their built-in defaults.', 'success');
    return;
  }}
  const runtimePayloadChanges = changes.filter(change => change.setting.runtime_editable);
  const runtimeResetChanges = runtimePayloadChanges.filter(change =>
    !settingsValuesEqual(change.setting.value, change.value));
  const resetSettingIds = new Set(changes.map(change => change.setting.id));
  const firstUnrelatedInvalid = firstInvalidSettingsControlOutside(resetSettingIds);
  if (firstUnrelatedInvalid) {{
    showSettingsPageError('Correct invalid draft values outside this reset before continuing.', false);
    setSettingsStatus('Defaults were not staged. No settings were changed.', 'warning');
    if (settingsPageIsActive()) firstUnrelatedInvalid.focus();
    return;
  }}
  if (selection.confirmation) {{
    const confirmationMessage = selection.categoryId
      ? 'Reset the ' + selection.label + ' category to built-in defaults? ' + changes.length + ' managed setting' + (changes.length === 1 ? '' : 's') + ' will be staged. Only runtime-editable settings will be applied now. Configuration will not be saved.'
      : 'Reset all dashboard-managed settings to built-in defaults? ' + changes.length + ' managed setting' + (changes.length === 1 ? '' : 's') + ' will be staged. Only runtime-editable settings will be applied now. Configuration will not be saved.';
    if (!window.confirm(confirmationMessage)) {{
      setSettingsStatus('Reset was cancelled. No settings were changed.', '');
      return;
    }}
  }}
  if (!runtimePayloadChanges.length) {{
    stageSettingsDraftChanges(changes);
    announceSettingsReset(changes, runtimeResetChanges, selection);
    return;
  }}
  let payload;
  try {{
    payload = buildSettingsPayload(runtimePayloadChanges);
  }} catch (error) {{
    showSettingsPageError('The reset could not be prepared safely. Reload the page and try again.', true);
    setSettingsStatus('Defaults were not staged. No settings were changed.', 'warning');
    return;
  }}

  const preservedDraftValues = captureSettingsDraftValuesExcept(resetSettingIds);
  changes.forEach(change => preservedDraftValues.set(change.setting.id, change.value));
  settingsPageState.resetting = true;
  clearSettingsPageError();
  clearSettingsFieldErrors();
  setSettingsStatus('Applying runtime-editable defaults and staging restart-only drafts...', '');
  updateSettingsActions();
  let patchAccepted = false;
  let focusAfterReset = null;
  try {{
    const response = await fetch(SETTINGS_ENDPOINT, {{
      method:'PATCH',
      headers:{{'Accept':'application/json','Content-Type':'application/json'}},
      body:JSON.stringify(payload)
    }});
    const responsePayload = await readSettingsResponse(response);
    if (!response.ok) {{
      const firstInvalid = applySettingsValidationErrors(responsePayload);
      const message = settingsErrorMessage(responsePayload, response.status, 'reset');
      showSettingsPageError(message, !firstInvalid);
      setSettingsStatus(response.status === 400 || response.status === 422
        ? 'Reset validation failed. No settings were changed.'
        : 'Defaults were not staged. No settings were changed.', 'warning');
      focusAfterReset = firstInvalid;
      return;
    }}
    patchAccepted = true;
    if (changes.some(change => isConnectionSettingId(change.setting.id))) settingsPageState.connectionTestResult = null;
    const snapshot = await authoritativeSettingsSnapshot(responsePayload);
    acceptSettingsSnapshot(snapshot, preservedDraftValues);
    announceSettingsReset(changes, runtimeResetChanges, selection);
    requestDashboardRefresh();
  }} catch (error) {{
    if (patchAccepted) {{
      settingsPageState.confirmationRequired = true;
      settingsPageState.confirmationAction = 'reset';
      settingsPageState.confirmationPreservedDraftValues = preservedDraftValues;
      showSettingsLoadState('Confirm staged defaults', 'ContextKeeper accepted the runtime reset, but the current runtime values could not be confirmed. Retry before making another change.', true);
      showSettingsPageError('ContextKeeper accepted the runtime reset, but the current values could not be confirmed. Editing and Save actions are paused.', false);
      setSettingsStatus('The accepted runtime reset requires confirmation.', 'warning');
    }} else {{
      showSettingsPageError('ContextKeeper could not confirm whether defaults were staged. No configuration was saved; check the connection and retry.', false);
      setSettingsStatus('Reset could not be confirmed. Configuration was not saved.', 'warning');
    }}
  }} finally {{
    settingsPageState.resetting = false;
    updateSettingsActions();
    if (focusAfterReset && settingsPageIsActive()) focusAfterReset.focus();
  }}
}}
function restoreSettingsDraft() {{
  if (!settingsPageState.confirmedSnapshot) return;
  settingsPageState.draftSnapshot = createSettingsDraftSnapshot(settingsPageState.confirmedSnapshot);
  settingsPageState.draftSettingsById = settingsIndex(settingsPageState.draftSnapshot);
  settingsPageState.fieldErrors = new Map();
  settingsPageState.connectionTestResult = null;
  renderSettingsCategories();
  clearSettingsPageError();
  updateSettingsActions();
}}
async function discardSettingsDraft() {{
  if (settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting || settingsPageState.resetting ||
      settingsPageState.discarding || settingsPageState.testingConnection ||
      settingsPageState.confirmationRequired || !settingsPageState.confirmedSnapshot) return;
  const draftChanges = changedDraftSettings();
  const runtimeChanges = runtimeSettingsDifferentFromPersisted();
  if (!draftChanges.length && !runtimeChanges.length) {{
    setSettingsStatus('No draft or runtime changes to discard.', '');
    return;
  }}
  if (!runtimeChanges.length) {{
    restoreSettingsDraft();
    setSettingsStatus('Unsaved draft changes discarded. Runtime and configuration were not changed.', 'success');
    return;
  }}
  let payload;
  try {{
    payload = buildSettingsPayload(runtimeChanges);
  }} catch (error) {{
    showSettingsPageError('The runtime recovery could not be prepared safely. Reload the page and try again.', true);
    setSettingsStatus('Runtime changes were not discarded.', 'warning');
    return;
  }}

  settingsPageState.discarding = true;
  clearSettingsPageError();
  clearSettingsFieldErrors();
  setSettingsStatus('Restoring persisted values to the current runtime...', '');
  updateSettingsActions();
  let patchAccepted = false;
  let focusAfterDiscard = null;
  try {{
    const response = await fetch(SETTINGS_ENDPOINT, {{
      method:'PATCH',
      headers:{{'Accept':'application/json','Content-Type':'application/json'}},
      body:JSON.stringify(payload)
    }});
    const responsePayload = await readSettingsResponse(response);
    if (!response.ok) {{
      const firstInvalid = applySettingsValidationErrors(responsePayload);
      const message = settingsErrorMessage(responsePayload, response.status, 'discard runtime');
      showSettingsPageError(message, !firstInvalid);
      setSettingsStatus(response.status === 400 || response.status === 422
        ? 'Runtime recovery validation failed. No runtime settings were changed.'
        : 'Runtime changes were not discarded. Your draft is still available.', 'warning');
      focusAfterDiscard = firstInvalid;
      return;
    }}
    patchAccepted = true;
    const snapshot = await authoritativeSettingsSnapshot(responsePayload);
    settingsPageState.connectionTestResult = null;
    acceptSettingsSnapshot(snapshot);
    const remainingRuntimeDifferences = runtimeSettingsDifferentFromPersisted();
    requestDashboardRefresh();
    if (remainingRuntimeDifferences.length) {{
      showSettingsPageError('Persisted configuration changed during runtime recovery. Review the refreshed values and retry Discard.', false);
      setSettingsStatus(remainingRuntimeDifferences.length + ' runtime setting' + (remainingRuntimeDifferences.length === 1 ? '' : 's') + ' still differs from persisted configuration. YAML was not changed.', 'warning');
      focusSettingsStatus();
      return;
    }}
    setSettingsStatus(runtimeChanges.length + ' runtime setting' + (runtimeChanges.length === 1 ? '' : 's') + ' restored from persisted configuration. YAML was not changed.', 'success');
    focusSettingsStatus();
  }} catch (error) {{
    if (patchAccepted) {{
      settingsPageState.confirmationRequired = true;
      settingsPageState.confirmationAction = 'discard';
      settingsPageState.confirmationPreservedDraftValues = null;
      showSettingsLoadState('Confirm restored runtime', 'ContextKeeper accepted the recovery update, but the current runtime values could not be confirmed. Retry before making another change.', true);
      showSettingsPageError('ContextKeeper accepted the recovery update, but the current runtime values could not be confirmed. Editing and Save actions are paused.', false);
      setSettingsStatus('The accepted runtime recovery requires confirmation.', 'warning');
    }} else {{
      showSettingsPageError('ContextKeeper could not confirm whether runtime values were restored. YAML was not changed; check the connection and retry.', false);
      setSettingsStatus('Runtime recovery could not be confirmed. Your draft is still available.', 'warning');
    }}
  }} finally {{
    settingsPageState.discarding = false;
    updateSettingsActions();
    if (focusAfterDiscard && settingsPageIsActive()) focusAfterDiscard.focus();
  }}
}}
async function authoritativeSettingsSnapshot(patchPayload) {{
  try {{
    return validateSettingsSnapshot(patchPayload);
  }} catch (error) {{
    return await requestSettingsSnapshot();
  }}
}}
async function authoritativePersistenceResult(responsePayload) {{
  try {{
    return validateSettingsPersistenceResponse(responsePayload);
  }} catch (error) {{
    return {{
      status:'saved',
      persisted_setting_ids:[],
      configuration_created:false,
      settings:await requestSettingsSnapshot()
    }};
  }}
}}
async function saveSettings() {{
  if (settingsPageState.saving || settingsPageState.persisting || settingsPageState.loading || settingsPageState.resetting ||
      settingsPageState.discarding || settingsPageState.testingConnection ||
      settingsPageState.confirmationRequired || !settingsPageState.loaded) return;
  const changes = changedRuntimeSettings();
  if (!changes.length) {{
    setSettingsStatus('No changes to save.', '');
    return;
  }}
  if (!settingsDraftIsValid()) {{
    const firstInvalid = firstInvalidSettingsControlOutside(new Set());
    showSettingsPageError('Correct the invalid setting values before saving.', false);
    setSettingsStatus('Settings were not saved.', 'warning');
    if (firstInvalid) firstInvalid.focus();
    return;
  }}
  let payload;
  try {{
    payload = buildSettingsPatchPayload();
  }} catch (error) {{
    showSettingsPageError('The changed settings could not be prepared safely. Reload the page and try again.', true);
    setSettingsStatus('Settings were not saved.', 'warning');
    return;
  }}

  const preservedPersistenceOnlyDraftValues = capturePersistenceOnlyDraftValues();
  settingsPageState.saving = true;
  clearSettingsPageError();
  clearSettingsFieldErrors();
  setSettingsStatus('Saving settings...', '');
  updateSettingsActions();
  let patchAccepted = false;
  let focusAfterSave = null;
  try {{
    const response = await fetch(SETTINGS_ENDPOINT, {{
      method:'PATCH',
      headers:{{'Accept':'application/json','Content-Type':'application/json'}},
      body:JSON.stringify(payload)
    }});
    const responsePayload = await readSettingsResponse(response);
    if (!response.ok) {{
      const firstInvalid = applySettingsValidationErrors(responsePayload);
      const message = settingsErrorMessage(responsePayload, response.status, 'save');
      showSettingsPageError(message, !firstInvalid);
      setSettingsStatus(response.status === 400 || response.status === 422 ? 'Validation failed. Your changes are still available to correct.' : 'Settings were not saved. Your changes are still available.', 'warning');
      focusAfterSave = firstInvalid;
      return;
    }}
    patchAccepted = true;
    const snapshot = await authoritativeSettingsSnapshot(responsePayload);
    acceptSettingsSnapshot(snapshot, preservedPersistenceOnlyDraftValues);
    setSettingsStatus('Settings saved for the current runtime.', 'success');
    requestDashboardRefresh();
  }} catch (error) {{
    if (patchAccepted) {{
      settingsPageState.confirmationRequired = true;
      settingsPageState.confirmationAction = 'runtime';
      showSettingsLoadState('Confirm current settings', 'ContextKeeper accepted the update, but the current values could not be confirmed. Retry the authoritative settings load before making another change.', true);
      showSettingsPageError('ContextKeeper accepted the update, but the current values could not be confirmed. Your draft remains visible while editing and Save are paused.', false);
      setSettingsStatus('The accepted settings update requires confirmation.', 'warning');
    }} else {{
      showSettingsPageError('ContextKeeper could not confirm whether settings were saved. Your changes were not discarded; check the connection and retry Save.', false);
      setSettingsStatus('Save could not be confirmed. Your changes are still available.', 'warning');
    }}
  }} finally {{
    settingsPageState.saving = false;
    updateSettingsActions();
    if (focusAfterSave && settingsPageIsActive()) focusAfterSave.focus();
  }}
}}
async function persistSettings() {{
  if (settingsPageState.persisting || settingsPageState.saving || settingsPageState.loading || settingsPageState.resetting ||
      settingsPageState.discarding || settingsPageState.testingConnection ||
      settingsPageState.confirmationRequired || !settingsPageState.loaded) return;
  const changes = changedPersistableSettings();
  if (!changes.length) {{
    setSettingsStatus('No configuration changes to save.', '');
    return;
  }}
  if (!settingsDraftIsValid()) {{
    const firstInvalid = firstInvalidSettingsControlOutside(new Set());
    showSettingsPageError('Correct the invalid setting values before saving to configuration.', false);
    setSettingsStatus('Configuration was not saved.', 'warning');
    if (firstInvalid) firstInvalid.focus();
    return;
  }}
  let payload;
  try {{
    payload = buildSettingsConfigPayload();
  }} catch (error) {{
    showSettingsPageError('The configuration changes could not be prepared safely. Reload the page and try again.', true);
    setSettingsStatus('Configuration was not saved.', 'warning');
    return;
  }}

  const preservedDraftValues = captureSettingsDraftValues();
  settingsPageState.persisting = true;
  clearSettingsPageError();
  clearSettingsFieldErrors();
  setSettingsStatus('Saving draft values to configuration...', '');
  updateSettingsActions();
  let persistenceAccepted = false;
  let focusAfterPersistence = null;
  try {{
    const response = await fetch(SETTINGS_CONFIG_ENDPOINT, {{
      method:'PUT',
      headers:{{'Accept':'application/json','Content-Type':'application/json'}},
      body:JSON.stringify(payload)
    }});
    const responsePayload = await readSettingsResponse(response);
    if (!response.ok) {{
      const firstInvalid = applySettingsValidationErrors(responsePayload);
      const message = settingsErrorMessage(responsePayload, response.status, 'save configuration');
      showSettingsPageError(message, !firstInvalid);
      setSettingsStatus(response.status === 400 || response.status === 422 ? 'Configuration validation failed. Your draft is still available to correct.' : 'Configuration was not saved. Your draft is still available.', 'warning');
      focusAfterPersistence = firstInvalid;
      return;
    }}
    persistenceAccepted = true;
    const result = await authoritativePersistenceResult(responsePayload);
    const authoritativeSettings = settingsIndex(result.settings);
    changes.forEach(change => {{
      const authoritative = authoritativeSettings.get(change.setting.id);
      if (authoritative) preservedDraftValues.set(change.setting.id, authoritative.persisted_value);
    }});
    if (changes.some(change => isConnectionSettingId(change.setting.id))) settingsPageState.connectionTestResult = null;
    acceptSettingsSnapshot(result.settings, preservedDraftValues);
    const savedCount = result.persisted_setting_ids.length || changes.length;
    const createdMessage = result.configuration_created ? ' A new configuration file was created.' : '';
    const savedDefaults = changes.length > 0 && changes.every(change =>
      change.setting.reset_eligible && settingsValuesEqual(change.value, change.setting.default_value));
    const savedMessage = savedDefaults
      ? savedCount + ' managed setting' + (savedCount === 1 ? '' : 's') + ' restored to built-in defaults and saved.'
      : savedCount + ' setting' + (savedCount === 1 ? '' : 's') + ' saved to configuration.';
    const restartCount = changes.filter(change => change.setting.restart_required).length;
    const restartMessage = restartCount
      ? ' ' + restartCount + ' saved setting' + (restartCount === 1 ? '' : 's') + ' requires a manual ContextKeeper restart before the saved value can become active; higher-priority overrides may still take precedence.'
      : '';
    setSettingsStatus(savedMessage + ' Runtime values were not changed.' + restartMessage + createdMessage, 'success');
  }} catch (error) {{
    if (persistenceAccepted) {{
      settingsPageState.confirmationRequired = true;
      settingsPageState.confirmationAction = 'configuration';
      showSettingsLoadState('Confirm saved configuration', 'ContextKeeper accepted the configuration write, but the refreshed persisted values could not be confirmed. Retry before making another change.', true);
      showSettingsPageError('ContextKeeper accepted the configuration write, but the persisted values could not be confirmed. Your draft remains visible while editing and Save actions are paused.', false);
      setSettingsStatus('The accepted configuration write requires confirmation.', 'warning');
    }} else {{
      showSettingsPageError('ContextKeeper could not confirm whether configuration was saved. Your draft was not discarded; check the connection and retry.', false);
      setSettingsStatus('Configuration save could not be confirmed. Your draft is still available.', 'warning');
    }}
  }} finally {{
    settingsPageState.persisting = false;
    updateSettingsActions();
    if (focusAfterPersistence && settingsPageIsActive()) focusAfterPersistence.focus();
  }}
}}
function initializeSettingsPage() {{
  const form = byId('settingsForm');
  if (form) {{
    form.addEventListener('input', handleSettingsInput);
    form.addEventListener('submit', event => {{
      event.preventDefault();
      void saveSettings();
    }});
  }}
  const discard = byId('settingsDiscardButton');
  if (discard) discard.addEventListener('click', () => void discardSettingsDraft());
  const resetAll = byId('settingsResetAllButton');
  if (resetAll) resetAll.addEventListener('click', () => void resetSettingsToDefaults({{ confirmation:true }}));
  const persist = byId('settingsPersistButton');
  if (persist) persist.addEventListener('click', () => void persistSettings());
  const retry = byId('settingsRetryButton');
  if (retry) retry.addEventListener('click', () => {{
    if (settingsPageState.confirmationRequired) void confirmSettingsAfterAcceptedUpdate();
    else void loadSettings();
  }});
  updateSettingsActions();
}}
function showPage(pageName) {{
  const target = pageName || 'operations';
  document.querySelectorAll('[data-page]').forEach(page => page.classList.toggle('active', page.dataset.page === target));
  document.querySelectorAll('[data-page-link]').forEach(link => {{
    const active = link.dataset.pageLink === target;
    link.classList.toggle('active', active);
    if (link.closest('.nav')) {{
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    }}
  }});
  if (location.hash !== '#' + target) history.replaceState(null, '', '#' + target);
  if (target === 'settings') ensureSettingsLoaded();
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
function initializeConversationInspector() {{
  const list = byId('liveConversationTimelineList');
  if (list) list.addEventListener('click', handleTimelineInspectorSelection);
  const closeButton = byId('conversationInspectorClose');
  if (closeButton) closeButton.addEventListener('click', () => closeConversationInspector());
  const backdrop = byId('conversationInspectorBackdrop');
  if (backdrop) {{
    backdrop.addEventListener('click', () => {{
      if (window.matchMedia('(max-width: 1000px)').matches) closeConversationInspector();
    }});
  }}
  document.addEventListener('keydown', event => {{
    if (event.key === 'Escape' && conversationInspectorState.inspectorOpen) {{
      event.preventDefault();
      closeConversationInspector();
    }}
  }});
}}
async function refreshHealth() {{
  const res = await fetch('/health');
  const h = await res.json();
  const c = h.connections;
  setDot('clientDot', c.client.status);
  setStatusBadge('clientStatusBadge', c.client.status || 'waiting');
  setText('clientText', c.client.count > 0 ? 'Connected' : 'Waiting');
  setText('clientSub', c.client.count + ' client(s) seen recently');
  setDot('proxyDot', c.proxy.status);
  setStatusBadge('proxyStatusBadge', c.proxy.status || 'online');
  setText('proxySub', 'Listening at ' + c.proxy.listen);
  setStatusBadge('opsContextKeeperStatus', c.proxy.status || h.status || 'running');
  setText('opsContextKeeperDetail', 'Listening at ' + c.proxy.listen);
  setDot('ollamaDot', c.ollama.status);
  setStatusBadge('ollamaStatusBadge', c.ollama.status || 'waiting');
  setText('ollamaText', c.ollama.status === 'online' ? 'Online' : c.ollama.status);
  setText('ollamaSub', h.ollama_base_url + (c.ollama.version ? ' - v' + c.ollama.version : '') + ' - ' + c.ollama.latency_ms + ' ms');
  setStatusBadge('opsOllamaStatus', c.ollama.status || 'waiting');
  setText('opsOllamaDetail', h.ollama_base_url + (c.ollama.version ? ' - v' + c.ollama.version : '') + ' - ' + c.ollama.latency_ms + ' ms');
  setDot('modelDot', c.model.status);
  setStatusBadge('modelStatusBadge', c.model.status || 'waiting');
  const modelLabel = c.model.label || c.model.name || 'No model observed yet';
  setText('modelText', c.model.status === 'unknown' ? 'Unknown' : c.model.name ? 'Active' : 'Waiting');
  setText('modelSub', modelLabel);
  setStatusBadge('opsModelStatus', c.model.status || 'waiting');
  setText('opsModelDetail', modelLabel);
  setText('opsLastRefreshDetail', 'Every ' + dashboardRefreshIntervalMs + ' ms');
  setStatusBadge('opsLastRefreshStatus', 'running', new Date().toLocaleTimeString());
  refreshOperationalActivity(h.activity);
  updateTopologyState(c, h.activity);
}}
async function refreshMetrics() {{
  const res = await fetch('/metrics');
  const data = await res.json();
  const r = data.requests;
  setText('req', r.total_requests);
  setText('err', r.total_errors);
  renderSparkline(r.recent_requests);
  renderRequestTraffic(r.recent_requests);
  setHtml('recent', r.recent_requests.map(x => `<tr><td>${{escapeHtml(new Date(x.timestamp).toLocaleTimeString())}}</td><td>${{escapeHtml(x.client_host||'')}}</td><td>${{escapeHtml(x.endpoint)}}</td><td>${{escapeHtml(x.model||'')}}</td><td>${{escapeHtml(x.status_code)}}</td><td>${{escapeHtml(x.latency_ms)}} ms</td></tr>`).join(''));
}}
async function refreshDashboardData() {{
  const res = await fetch('/dashboard/data');
  const data = await res.json();
  scheduleDashboardRefresh(data.refresh_interval_ms);
  const context = data.context;
  const compression = data.compression;
  const intelligence = data.intelligence || {{}};
  const activity = data.activity || {{}};
  setText('contextUsage', context.usage_percent + '%');
  setText('contextUsageText', context.estimated_tokens + ' estimated tokens across ' + context.conversation_count + ' conversation(s)');
  setText('activeConversationCount', context.conversation_count);
  setWidth('contextUsageBar', Math.min(context.usage_percent, 100) + '%');
  setGauge('contextGaugeArc', context.usage_percent);
  setText('compressionCount', compression.count);
  setText('compressionText', compression.history.length + ' recent compression event(s)');
  updateInstrumentPanel(data.instrument_panel || {{}});
  refreshOperationalActivity(activity);
  refreshIntelligence(intelligence);
  refreshActiveConversation(data.active_conversation, intelligence.conversation_risk);
  renderLiveConversationTimeline(data.conversation_timeline);
  updateConversationInspectorFromDashboardData(data);
}}
function refreshOperationalActivity(activity) {{
  const current = activity || {{}};
  const state = safeClass(current.state || 'starting') || 'starting';
  const label = current.label || titleCase(state);
  const details = current.details || 'Activity state is not available yet.';
  const activeCount = Number(current.active_request_count || 0);
  const summary = byId('currentActivitySummary');
  if (summary) summary.className = 'ops-state-column ops-activity-summary ' + state;
  setText('currentActivityStatus', label);
  setText('currentActivityDetails', details);
  setText('opsActivityDetail', details);
  setStatusBadge('opsActivityBadge', state, activeCount > 0 ? activeCount + ' active' : label);
  updateActivityTopology(current);
}}
function refreshIntelligence(intelligence) {{
  const health = intelligence.health || {{}};
  const status = health.status || 'unknown';
  const healthCard = byId('systemHealthCard');
  if (healthCard) healthCard.className = 'card health-card signal-card compact-card ops-health-panel ' + safeClass(status);
  const hero = byId('opsHeroStatus');
  if (hero) hero.className = 'card hero-status ' + safeClass(status);
  const heroState = heroStateForHealth(health);
  setText('opsHeroIcon', heroState.icon);
  setText('opsHeroText', heroState.title);
  setText('opsHeroMessage', health.message || 'Dashboard health evaluated.');
  setStatusBadge('systemHealthBadge', status);
  setText('systemHealthStatus', health.label || titleCase(status));
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
function timelineEmptyHtml() {{
  return '<div class="live-timeline-empty"><div class="live-timeline-empty-title">Waiting for conversation activity</div><div class="live-timeline-empty-detail">Request, context, and compression events will appear here without prompt or response content.</div></div>';
}}
function timelineTimeLabel(event) {{
  if (event && event.time_label) return String(event.time_label);
  const date = new Date(event?.timestamp || '');
  return Number.isFinite(date.getTime()) ? date.toLocaleTimeString() : '--';
}}
function timelineDetailHtml(event) {{
  const detail = event?.detail === null || event?.detail === undefined ? '' : String(event.detail).trim();
  return detail ? `<div class="live-timeline-detail">${{escapeHtml(detail)}}</div>` : '';
}}
function inspectorSafeText(value) {{
  const text = value === null || value === undefined ? '' : String(value).trim();
  return text || 'Not available';
}}
function inspectorShortId(value) {{
  const text = value === null || value === undefined ? '' : String(value).trim();
  if (!text) return 'Not available';
  return text.length > 12 ? text.slice(0, 4) + '…' + text.slice(-4) : text;
}}
function inspectorDateLabel(value) {{
  const date = new Date(value || '');
  return Number.isFinite(date.getTime()) ? date.toLocaleTimeString() : 'Not available';
}}
function inspectorDurationLabel(value) {{
  const ms = Number(value);
  if (!Number.isFinite(ms) || ms < 0) return 'Not available';
  if (ms < 1000) return Math.round(ms) + ' ms';
  return (ms / 1000).toFixed(ms < 10000 ? 1 : 0).replace(/\\.0$/, '') + ' s';
}}
function selectedConversationAvailable(data) {{
  const conversationId = conversationInspectorState.selectedConversationId;
  if (!conversationId || !data) return false;
  const activeId = data.active_conversation?.conversation_id || null;
  const timelineId = data.conversation_timeline?.conversation_id || null;
  const inspectorId = data.conversation_inspector?.conversation_id || null;
  return activeId === conversationId || timelineId === conversationId || inspectorId === conversationId;
}}
function buildConversationInspectorMetadata(data) {{
  const conversationId = conversationInspectorState.selectedConversationId;
  const inspector = data?.conversation_inspector || {{}};
  const overview = inspector.conversation_id === conversationId ? (inspector.overview || {{}}) : {{}};
  const intelligence = inspector.conversation_id === conversationId ? (inspector.intelligence || {{}}) : {{}};
  const statusLabel = overview.state_label || 'Unavailable';
  const statusClass = overview.state === 'failed' ? 'error' : overview.state === 'completed' ? 'success' : overview.state === 'active' ? 'info' : 'unavailable';
  return {{
    statusLabel,
    statusClass,
    shortId: inspectorShortId(conversationId),
    fullId: inspectorSafeText(conversationId),
    model: inspectorSafeText(overview.model),
    source: inspectorSafeText(overview.client_source),
    started: inspectorDateLabel(overview.started_at),
    fields: [
      {{ key:'conversation-id', id:'conversationInspectorOverviewConversationId', label:'Conversation identifier', value:conversationId, display:inspectorShortId(conversationId), title:conversationId || '' }},
      {{ key:'conversation-state', id:'conversationInspectorOverviewConversationState', label:'Conversation state', value:statusLabel }},
      {{ key:'model', id:'conversationInspectorOverviewModel', label:'Model', value:overview.model }},
      {{ key:'client-source', id:'conversationInspectorOverviewClientSource', label:'Client / Source', value:overview.client_source }},
      {{ key:'endpoint', id:'conversationInspectorOverviewEndpoint', label:'Endpoint', value:overview.endpoint }},
      {{ key:'request-type', id:'conversationInspectorOverviewRequestType', label:'Request type', value:overview.request_type }},
      {{ key:'message-count', id:'conversationInspectorOverviewMessageCount', label:'Message count', value:overview.message_count }},
      {{ key:'request-count', id:'conversationInspectorOverviewRequestCount', label:'Request count', value:overview.request_count }},
      {{ key:'estimated-tokens', id:'conversationInspectorOverviewEstimatedTokens', label:'Estimated token count', value:overview.estimated_tokens, formatter:formatTokenValue }},
      {{ key:'context-window-capacity', id:'conversationInspectorOverviewContextCapacity', label:'Context-window capacity', value:overview.context_window_tokens, formatter:value => formatTokenValue(value) + ' tokens' }},
      {{ key:'context-usage', id:'conversationInspectorOverviewContextUsage', label:'Context usage', value:overview.context_usage_percent, formatter:formatPercentValue }},
      {{ key:'compression-count', id:'conversationInspectorOverviewCompressionCount', label:'Compression count', value:overview.compression_count }},
      {{ key:'last-activity', id:'conversationInspectorOverviewLastActivity', label:'Last activity', value:overview.last_activity_at, formatter:inspectorDateLabel }},
      {{ key:'duration', id:'conversationInspectorOverviewDuration', label:'Duration', value:overview.duration_ms, formatter:inspectorDurationLabel }}
    ],
    intelligence
  }};
}}
function inspectorFieldValue(field) {{
  const value = field?.value;
  if (value === null || value === undefined || value === '') return '—';
  if (typeof field.formatter === 'function') return field.formatter(value);
  return String(value);
}}
function renderConversationInspectorOverview(metadata) {{
  const gridHtml = metadata.fields.map(field => {{
    const value = inspectorFieldValue(field);
    const title = field.title || value;
    const valueId = field.id || ('conversationInspectorOverview' + String(field.key).replace(/(^|-)([a-z])/g, (_, __, char) => char.toUpperCase()));
    return `<div class="conversation-inspector-field" data-inspector-field="${{escapeHtml(field.key)}}"><div class="conversation-inspector-label">${{escapeHtml(field.label)}}</div><div id="${{escapeHtml(valueId)}}" class="conversation-inspector-value" title="${{escapeHtml(title)}}">${{escapeHtml(value)}}</div></div>`;
  }}).join('');
  setHtml('conversationInspectorOverviewGrid', gridHtml);
}}
function renderConversationInspectorIntelligence(intelligence) {{
  const current = intelligence || {{}};
  const severity = safeClass(current.severity || 'unavailable') || 'unavailable';
  const statusLabel = inspectorSafeText(current.status_label || 'Insufficient data');
  const explanation = inspectorSafeText(current.explanation || 'Conversation intelligence will appear when sufficient conversation data exists.');
  const card = byId('conversationInspectorIntelligenceCard');
  if (card) card.className = 'conversation-inspector-intelligence-card ' + severity;
  setText('conversationInspectorIntelligenceStatus', statusLabel, false);
  setStatusBadge('conversationInspectorIntelligenceBadge', severity, statusLabel);
  setText('conversationInspectorIntelligenceExplanation', explanation, false);
  const signals = Array.isArray(current.signals) ? current.signals : [];
  setHtml('conversationInspectorIntelligenceSignals', signals.length
    ? signals.map(signal => `<span class="conversation-inspector-signal"><strong>${{escapeHtml(signal.label || 'Signal')}}</strong>${{escapeHtml(signal.value || '—')}}</span>`).join('')
    : '<span class="conversation-inspector-signal"><strong>Status</strong>—</span>');
  const recommendation = current.recommendation === null || current.recommendation === undefined ? '' : String(current.recommendation).trim();
  const recommendationEl = byId('conversationInspectorRecommendation');
  if (recommendationEl) {{
    recommendationEl.hidden = !recommendation;
    recommendationEl.textContent = recommendation;
  }}
}}
function setInspectorVisibility(id, visible) {{
  const el = byId(id);
  if (el) el.hidden = !visible;
}}
function showConversationInspectorPanel(panelName) {{
  setInspectorVisibility('conversationInspectorLoading', panelName === 'loading');
  setInspectorVisibility('conversationInspectorUnavailable', panelName === 'unavailable');
  setInspectorVisibility('conversationInspectorDetails', panelName === 'metadata');
}}
function renderConversationInspector() {{
  const drawer = byId('conversationInspectorDrawer');
  const backdrop = byId('conversationInspectorBackdrop');
  if (!drawer) return;
  const isOpen = Boolean(conversationInspectorState.inspectorOpen);
  document.body.classList.toggle('conversation-inspector-open', isOpen);
  drawer.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
  if (backdrop) backdrop.hidden = !isOpen;
  if (!isOpen) {{
    setText('conversationInspectorConversationId', 'No conversation selected', false);
    setStatusBadge('conversationInspectorStatusBadge', 'waiting', 'Closed');
    setText('conversationInspectorModelLine', 'Model not available', false);
    setText('conversationInspectorStartedLine', 'Start time not available', false);
    showConversationInspectorPanel(null);
    return;
  }}
  const data = conversationInspectorState.lastDashboardData;
  const unavailable = conversationInspectorState.inspectorError === 'unavailable' || !selectedConversationAvailable(data);
  if (conversationInspectorState.inspectorLoading && !data) {{
    setText('conversationInspectorConversationId', inspectorShortId(conversationInspectorState.selectedConversationId), false);
    setStatusBadge('conversationInspectorStatusBadge', 'waiting', 'Loading');
    setText('conversationInspectorModelLine', 'Loading conversation details…', false);
    setText('conversationInspectorStartedLine', 'Start time not available', false);
    showConversationInspectorPanel('loading');
    setText('conversationInspectorLiveRegion', 'Loading conversation details…', false);
    return;
  }}
  if (unavailable) {{
    setText('conversationInspectorConversationId', inspectorShortId(conversationInspectorState.selectedConversationId), false);
    setStatusBadge('conversationInspectorStatusBadge', 'warning', 'Unavailable');
    setText('conversationInspectorModelLine', 'Model not available', false);
    setText('conversationInspectorStartedLine', 'Start time not available', false);
    showConversationInspectorPanel('unavailable');
    setText('conversationInspectorLiveRegion', 'Conversation details unavailable', false);
    return;
  }}
  const metadata = buildConversationInspectorMetadata(data);
  setText('conversationInspectorConversationId', metadata.shortId, false);
  const idHeader = byId('conversationInspectorConversationId');
  if (idHeader) idHeader.setAttribute('title', metadata.fullId);
  setStatusBadge('conversationInspectorStatusBadge', metadata.statusClass, metadata.statusLabel);
  setText('conversationInspectorModelLine', metadata.model + ' · ' + metadata.source, false);
  setText('conversationInspectorStartedLine', 'Started ' + metadata.started, false);
  renderConversationInspectorOverview(metadata);
  renderConversationInspectorIntelligence(metadata.intelligence);
  showConversationInspectorPanel('metadata');
  setText('conversationInspectorLiveRegion', 'Conversation Inspector opened for ' + metadata.shortId, false);
}}
function syncTimelineSelectionState() {{
  document.querySelectorAll('#liveConversationTimelineList [data-inspector-conversation-id]').forEach(entry => {{
    const selected = Boolean(
      conversationInspectorState.inspectorOpen
      && conversationInspectorState.selectedConversationId
      && entry.dataset.inspectorConversationId === conversationInspectorState.selectedConversationId
    );
    entry.classList.toggle('is-selected', selected);
    entry.setAttribute('aria-pressed', selected ? 'true' : 'false');
  }});
}}
function updateConversationInspectorFromDashboardData(data) {{
  conversationInspectorState.lastDashboardData = data;
  if (!conversationInspectorState.inspectorOpen) return;
  conversationInspectorState.inspectorLoading = false;
  conversationInspectorState.inspectorError = selectedConversationAvailable(data) ? null : 'unavailable';
  renderConversationInspector();
  syncTimelineSelectionState();
}}
function openConversationInspector(conversationId, eventId) {{
  if (!conversationId) return;
  conversationInspectorState.selectedConversationId = conversationId;
  conversationInspectorState.selectedTimelineEventId = eventId || null;
  conversationInspectorState.inspectorOpen = true;
  conversationInspectorState.inspectorLoading = !conversationInspectorState.lastDashboardData;
  conversationInspectorState.inspectorError = conversationInspectorState.lastDashboardData && !selectedConversationAvailable(conversationInspectorState.lastDashboardData)
    ? 'unavailable'
    : null;
  renderConversationInspector();
  syncTimelineSelectionState();
  const closeButton = byId('conversationInspectorClose');
  if (closeButton) closeButton.focus({{ preventScroll:true }});
}}
function closeConversationInspector(options) {{
  const eventId = conversationInspectorState.selectedTimelineEventId;
  conversationInspectorState.selectedConversationId = null;
  conversationInspectorState.selectedTimelineEventId = null;
  conversationInspectorState.inspectorOpen = false;
  conversationInspectorState.inspectorLoading = false;
  conversationInspectorState.inspectorError = null;
  renderConversationInspector();
  syncTimelineSelectionState();
  const shouldReturnFocus = !options || options.returnFocus !== false;
  if (!shouldReturnFocus || !eventId) return;
  const trigger = Array.from(document.querySelectorAll('#liveConversationTimelineList [data-event-id]'))
    .find(entry => entry.dataset.eventId === eventId);
  if (trigger && typeof trigger.focus === 'function') trigger.focus({{ preventScroll:true }});
}}
function handleTimelineInspectorSelection(event) {{
  const list = byId('liveConversationTimelineList');
  const trigger = event.target.closest ? event.target.closest('[data-inspector-conversation-id]') : null;
  if (!list || !trigger || !list.contains(trigger)) return;
  const nestedInteractive = event.target.closest('a,input,select,textarea,summary,[data-page-link]');
  if (nestedInteractive && nestedInteractive !== trigger) return;
  openConversationInspector(trigger.dataset.inspectorConversationId, trigger.dataset.eventId);
}}
function renderLiveConversationTimeline(timeline) {{
  const list = byId('liveConversationTimelineList');
  if (!list) return;
  const events = Array.isArray(timeline?.events) ? timeline.events : (Array.isArray(timeline) ? timeline : []);
  const conversationId = !Array.isArray(timeline) && timeline?.conversation_id ? String(timeline.conversation_id) : '';
  const signature = conversationId + '|' + events.map(event => String(event?.id || '')).join('|');
  const status = byId('liveConversationTimelineStatus');
  const countLabel = events.length === 1 ? '1 event' : events.length + ' events';
  if (status) setStatusBadge('liveConversationTimelineStatus', events.length ? 'info' : 'waiting', events.length ? countLabel : 'Waiting');
  if (list.dataset.renderedSignature === signature) {{
    syncTimelineSelectionState();
    return;
  }}
  const wasPinned = list.scrollHeight - list.scrollTop - list.clientHeight < 24;
  if (!events.length) {{
    list.innerHTML = timelineEmptyHtml();
    list.dataset.renderedSignature = signature;
    syncTimelineSelectionState();
    return;
  }}
  const html = events.map(event => {{
    const severity = safeClass(event?.severity || 'info') || 'info';
    const eventType = safeClass(event?.type || 'event') || 'event';
    const eventId = event?.id ? String(event.id) : '';
    const title = event?.title || 'Timeline event';
    const selected = Boolean(conversationInspectorState.inspectorOpen && conversationId && conversationInspectorState.selectedConversationId === conversationId);
    const className = 'live-timeline-event ' + severity + (selected ? ' is-selected' : '');
    const content = `<div class="live-timeline-marker" aria-hidden="true"></div><div class="live-timeline-time">${{escapeHtml(timelineTimeLabel(event))}}</div><div class="live-timeline-copy"><div class="live-timeline-title">${{escapeHtml(title)}}</div>${{timelineDetailHtml(event)}}</div>`;
    const commonAttrs = `class="${{className}}" data-event-id="${{escapeHtml(eventId)}}" data-event-type="${{eventType}}"`;
    if (!conversationId) return `<div ${{commonAttrs}}>${{content}}</div>`;
    const label = 'Open Conversation Inspector for ' + inspectorShortId(conversationId) + ': ' + title;
    return `<button type="button" ${{commonAttrs}} data-inspector-conversation-id="${{escapeHtml(conversationId)}}" aria-pressed="${{selected ? 'true' : 'false'}}" aria-label="${{escapeHtml(label)}}">${{content}}</button>`;
  }}).join('');
  list.innerHTML = html;
  list.dataset.renderedSignature = signature;
  syncTimelineSelectionState();
  if (wasPinned) list.scrollTop = list.scrollHeight;
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
function setRefreshBusy(isBusy) {{
  document.body.classList.toggle('is-refreshing', isBusy);
  document.body.setAttribute('aria-busy', isBusy ? 'true' : 'false');
}}
function scheduleDashboardRefresh(intervalMs) {{
  if (!Number.isInteger(intervalMs) || intervalMs < 1) return;
  if (dashboardRefreshTimer !== null && dashboardRefreshIntervalMs === intervalMs) return;
  if (dashboardRefreshTimer !== null) clearInterval(dashboardRefreshTimer);
  dashboardRefreshIntervalMs = intervalMs;
  dashboardRefreshTimer = setInterval(refresh, dashboardRefreshIntervalMs);
  setText('opsLastRefreshDetail', 'Every ' + dashboardRefreshIntervalMs + ' ms', false);
}}
function requestDashboardRefresh() {{
  if (refreshInFlight) {{
    refreshAfterCurrent = true;
    return;
  }}
  void refresh();
}}
async function refresh() {{
  if (refreshInFlight) return;
  refreshInFlight = true;
  setRefreshBusy(true);
  try {{
    await Promise.all([refreshHealth(), refreshMetrics(), refreshDashboardData()]);
    document.body.classList.remove('refresh-error');
  }} catch (error) {{
    document.body.classList.add('refresh-error');
  }} finally {{
    refreshInFlight = false;
    setRefreshBusy(false);
    if (refreshAfterCurrent) {{
      refreshAfterCurrent = false;
      void refresh();
    }}
  }}
}}
initializeSettingsPage();
initializePages();
initializeConversationInspector();
initializeInstrumentGauges();
scheduleDashboardRefresh(DASHBOARD_REFRESH_INTERVAL_MS);
refresh();
</script>
</body>
</html>
"""
