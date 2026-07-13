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
.page-title {{ margin:0; font-size:22px; }}
.page-sub {{ color:var(--muted); margin-top:4px; }}
.command-meta {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:8px; }}
.page.active.operations-page {{ height:100%; min-height:0; overflow:hidden; grid-template-rows:auto auto minmax(0,1fr); align-content:stretch; }}
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
.operations-lower {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); grid-auto-rows:minmax(0,1fr); gap:10px; align-items:stretch; height:100%; min-height:0; min-width:0; overflow:hidden; }}
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
.ops-panel {{ min-height:0; overflow:hidden; }}
.operations-lower > .ops-panel {{ height:100%; overflow:auto; }}
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
.badge.positive,.badge.healthy,.badge.low,.badge.online,.badge.active,.badge.running,.badge.ready,.badge.idle {{ --badge-ring:rgba(34,197,94,.22); --badge-glow:0 0 14px rgba(34,197,94,.1); color:var(--good); background:rgba(34,197,94,.12); }} .badge.info,.badge.busy,.badge.starting,.badge.receiving,.badge.thinking,.badge.streaming,.badge.finalizing {{ --badge-ring:rgba(56,189,248,.22); --badge-glow:0 0 14px rgba(56,189,248,.1); color:var(--accent); background:rgba(56,189,248,.12); }} .badge.warning,.badge.medium,.badge.waiting,.badge.pending,.badge.connecting {{ --badge-ring:rgba(245,158,11,.24); --badge-glow:0 0 14px rgba(245,158,11,.1); color:var(--warn); background:rgba(245,158,11,.12); }} .badge.critical,.badge.high,.badge.offline,.badge.error {{ --badge-ring:rgba(239,68,68,.24); --badge-glow:0 0 14px rgba(239,68,68,.1); color:var(--bad); background:rgba(239,68,68,.12); }}
a.badge:hover {{ transform:translateY(-1px); box-shadow:inset 0 0 0 1px var(--badge-ring),var(--surface-inset-highlight),var(--badge-glow),0 0 0 3px rgba(56,189,248,.08); }}
a.badge:active {{ transform:translateY(0); opacity:.86; }}
a.badge:focus-visible {{ outline:2px solid rgba(56,189,248,.72); outline-offset:2px; box-shadow:inset 0 0 0 1px var(--badge-ring),var(--surface-inset-highlight),var(--badge-glow),0 0 0 3px rgba(56,189,248,.12); }}
.badge-update {{ animation:badgeSettle .3s ease-out 1; }}
@keyframes badgeSettle {{ 0% {{ transform:scale(.985); }} 45% {{ transform:scale(1.015); }} 100% {{ transform:scale(1); }} }}
.panel-list {{ display:grid; gap:8px; }}
.panel-item {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; background:rgba(15,23,42,.46); border:1px solid var(--border-card); border-radius:8px; padding:7px 9px; box-shadow:var(--surface-inset-highlight); transition:border-color .18s ease, background .18s ease,box-shadow .18s ease; }}
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
.bar {{ height:12px; border-radius:999px; background:#334155; overflow:hidden; margin:10px 0; }}
.fill {{ height:100%; background:var(--accent); width:0%; transition:width .25s ease; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th,td {{ text-align:left; padding:7px 8px; border-bottom:1px solid rgba(255,255,255,.08); }}
th {{ color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }}
.flow-panel {{ position:relative; display:grid; grid-template-rows:auto auto; gap:10px; min-height:0; overflow:hidden; padding:13px 14px; background:linear-gradient(145deg,rgba(15,23,42,.96),rgba(24,33,50,.86)); }}
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
.flow-svg-packet {{ fill:var(--accent); opacity:0; filter:drop-shadow(0 0 8px rgba(56,189,248,.55)); }}
.flow-svg-packet {{ offset-path:path("M 55 90 C 180 90 200 90 325 90 C 450 90 470 90 595 90 C 720 90 740 90 945 90"); offset-rotate:0deg; }}
.flow-panel.flow-active .flow-svg-packet {{ opacity:0; animation:none; }}
.flow-panel.flow-waiting .flow-svg-packet {{ fill:var(--warn); opacity:0; animation:none; }}
.flow-panel.flow-offline .flow-svg-packet {{ opacity:0; animation:none; }}
.flow-panel.activity-streaming .flow-svg-packet {{ opacity:.46; animation:flowPacket 2400ms linear infinite; }}
.flow-panel.activity-thinking .flow-svg-line.flow-line-active,.flow-panel.activity-receiving .flow-svg-line.flow-line-active {{ stroke:rgba(125,211,252,.78); filter:drop-shadow(0 0 6px rgba(56,189,248,.3)); }}
.flow-panel.activity-finalizing .pipe::after {{ background:rgba(125,211,252,.72); box-shadow:0 0 18px rgba(56,189,248,.4); }}
.flow-panel.request-pulse .flow-stage::after {{ animation:flowStagePulse 1300ms ease-out 1; }}
.flow-panel.request-pulse .flow-svg-packet {{ animation:flowPacketPulse 1300ms ease-out 1; opacity:.92; }}
.flow-panel.request-pulse .flow-svg-line.flow-line-active,.flow-panel.request-pulse .flow-svg-line.flow-line-waiting {{ stroke:rgba(125,211,252,.86); filter:drop-shadow(0 0 7px rgba(56,189,248,.36)); }}
.flow-panel.request-pulse .pipe {{ background:linear-gradient(90deg,rgba(45,58,79,.35),rgba(125,211,252,.9),rgba(45,58,79,.35)); }}
.flow-panel.request-pulse .pipe::after {{ animation:pipeRequestPulse 1300ms ease-out 1; background:rgba(125,211,252,.82); box-shadow:0 0 22px rgba(56,189,248,.54); }}
.flow-panel.request-pulse .flow-node {{ border-color:rgba(56,189,248,.36); box-shadow:var(--shadow-neutral-soft),var(--surface-inset-highlight),var(--glow-info); }}
.flow-panel.request-pulse .flow-node-icon {{ border-color:rgba(56,189,248,.34); background:rgba(56,189,248,.14); box-shadow:0 0 0 3px rgba(56,189,248,.06),var(--glow-info); }}
.flow-node.status-pulse {{ animation:nodeStatusPulse 700ms ease-out 1; }}
@keyframes flowPacket {{ 0% {{ offset-distance:0%; opacity:0; }} 10% {{ opacity:.72; }} 86% {{ opacity:.72; }} 100% {{ offset-distance:100%; opacity:0; }} }}
@keyframes flowPacketPulse {{ 0% {{ offset-distance:0%; opacity:0; }} 12% {{ opacity:1; }} 82% {{ opacity:1; }} 100% {{ offset-distance:100%; opacity:0; }} }}
@keyframes flowStagePulse {{ 0% {{ opacity:0; transform:translateX(-70%); }} 18% {{ opacity:.68; }} 72% {{ opacity:.26; }} 100% {{ opacity:0; transform:translateX(70%); }} }}
@keyframes pipeRequestPulse {{ 0% {{ transform:translate(-50%,-50%) scale(.92); opacity:.74; }} 32% {{ transform:translate(-50%,-50%) scale(1.28); opacity:1; }} 100% {{ transform:translate(-50%,-50%) scale(1); opacity:.86; }} }}
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
@media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior:auto; }} .flow-panel.flow-active .flow-svg-packet,.flow-panel.flow-waiting .flow-svg-packet,.flow-panel.activity-streaming .flow-svg-packet,.flow-panel.request-pulse .flow-svg-packet,.flow-panel.request-pulse .flow-stage::after,.flow-panel.request-pulse .pipe::after,.flow-node.status-pulse,.dot,.value-pop,.badge-update,.ops-activity-summary,.ops-activity-summary .ops-health-status,.ops-activity-summary::after {{ animation:none; }} .flow-svg-packet,.flow-stage::after {{ opacity:0; }} .nav a,.nav a::before,.topbar-status,.topbar-status-dot,.card,.node,.hero-status,.hero-status::before,.hero-status::after,.hero-stat-card,.hero-stat-icon,.hero-stat-value,.badge,.flow-svg-line,.gauge-progress,.fill,.ops-health-row,.ops-activity-summary,.panel-item,.timeline-item,.message {{ transition:none; }} .nav a:hover,.nav a:active,.card:hover,.node:hover,.hero-stat-card:hover,.hero-stat-card:focus-within,.hero-stat-card:focus-visible,.hero-stat-card:hover .hero-stat-icon,.hero-stat-card:focus-within .hero-stat-icon,.hero-stat-card:focus-visible .hero-stat-icon,a.badge:hover,a.badge:active,body.is-refreshing .topbar-status-dot {{ transform:none; }} }}
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
  .operations-lower {{ grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }}
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
  .ops-hero {{ grid-template-columns:minmax(250px,1fr) minmax(220px,.78fr); gap:7px; }}
  .hero-stats-grid {{ grid-template-columns:repeat(4,minmax(132px,1fr)); gap:7px; }}
  .hero-stat-card {{ min-height:68px; }}
  .hero-title {{ white-space:normal; }}
  .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }}
  .operations-lower {{ grid-template-columns:repeat(3,minmax(0,1fr)); gap:6px; }}
  .flow-stage {{ grid-template-columns:minmax(118px,1fr) 20px minmax(118px,1fr) 20px minmax(118px,1fr) 20px minmax(118px,1fr); gap:6px; }}
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
  .operations-lower {{ grid-template-columns:repeat(3,minmax(0,1fr)); gap:6px; }}
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
  .conversation-compact {{ grid-column:auto; gap:5px; }}
  .conversation-meta.compact {{ grid-template-columns:repeat(2,minmax(0,1fr)); gap:8px; }}
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
  .ops-health-panel {{ gap:5px; }}
  .ops-health-body {{ gap:6px; }}
  .hero-stats-grid {{ gap:5px; }}
  .flow-panel {{ padding-top:7px; padding-bottom:7px; gap:4px; }}
  .flow-panel::before {{ inset:30px 9px 7px; }}
  .flow-stage {{ gap:5px; }}
  .operations-lower {{ gap:6px; }}
  .traffic-panel,.conversation-compact {{ gap:5px; }}
  .resource-stack {{ gap:5px; }}
  .resource-error {{ margin-top:5px; padding-top:5px; }}
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
  .traffic-panel,.conversation-compact {{ gap:4px; }}
  .traffic-stats {{ gap:5px; }}
  .resource-stack {{ gap:4px; }}
  .resource-error {{ margin-top:3px; padding-top:3px; }}
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
  .traffic-panel,.conversation-compact {{ gap:3px; }}
  .traffic-stats {{ gap:4px; }}
  .resource-stack {{ gap:3px; }}
  .speedometer {{ gap:1px; }}
  .resource-error {{ margin-top:2px; padding-top:2px; }}
  .conversation-meta.compact {{ gap:4px; }}
  .risk-row {{ margin-top:4px; gap:4px; }}
  .conversation-compact .summary {{ padding:8px; }}
  .badge {{ min-height:19px; padding:1px 6px; }}
}}
@media (max-width: 1000px) {{ .app-shell {{ grid-template-columns:220px minmax(0,1fr); }} .dashboard-main {{ padding:14px 16px 18px; }} .ops-hero,.operations-lower {{ grid-template-columns:1fr; }} .hero-title {{ white-space:normal; }} .hero-title span:last-child {{ overflow:visible; text-overflow:clip; }} .ops-health-details {{ grid-template-columns:1fr; }} .ops-health-row {{ grid-template-columns:16px minmax(0,1fr) auto; }} .flow-svg-layer {{ display:none; }} .flow-stage {{ grid-template-columns:1fr; }} .pipe {{ height:20px; width:4px; justify-self:center; }} .resource-stack {{ grid-template-columns:repeat(auto-fit,minmax(120px,1fr)); }} }}
@media (max-width: 1000px) {{ .app-shell {{ height:100vh; overflow-y:auto; overflow-x:hidden; grid-template-columns:1fr; }} .workspace {{ height:auto; min-height:0; overflow:visible; }} .sidebar {{ position:relative; height:auto; gap:14px; }} .nav {{ grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); }} .sidebar-footer {{ display:none; }} .topbar {{ position:relative; align-items:flex-start; flex-direction:column; }} .dashboard-main {{ height:auto; overflow:visible; padding:18px; }} .page.active,.ops-hero,.operations-lower {{ height:auto; overflow:visible; grid-template-columns:1fr; }} .ops-hero {{ grid-template-areas:"hero" "actions" "stats"; }} .hero-stats-grid {{ grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); }} .operations-page {{ min-height:auto; grid-template-rows:none; }} .timeline-item {{ grid-template-columns:1fr; }} }}
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
      <div id="systemHealthCard" class="card health-card signal-card compact-card ops-health-panel">
        <div class="health-title">
          <h2 class="ops-health-heading"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 4 6v6c0 5 3.4 8 8 9 4.6-1 8-4 8-9V6z"></path><path d="m9 12 2 2 4-5"></path></svg>System Health</h2>
          <span id="systemHealthBadge" class="badge">Checking</span>
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
    <div class="card compact-card action-panel"><div class="health-title"><h2><span class="icon-label"><span class="icon-mark">!</span>Recommendations</span></h2><span class="badge">Action</span></div><div id="recommendationsList" class="panel-list"><div class="muted">No operator action queued.</div></div><div class="small">Open Analytics for full insight history.</div></div>
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

  <section id="connections" class="card flow-panel ops-panel">
    <div class="health-title">
      <h2 class="flow-heading"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M18 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M6 22a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"></path><path d="M8.6 6.5 15.4 10.5"></path><path d="M15.4 13.5 8.6 17.5"></path></svg>Connection Flow</h2>
      <span class="flow-note">Request pulses appear only when traffic changes.</span>
    </div>
    <div class="flow-stage">
      <svg class="flow-svg-layer" viewBox="0 0 1000 180" preserveAspectRatio="none" aria-hidden="true">
        <path id="flowLineClientProxy" class="flow-svg-line" d="M 55 90 C 180 90 200 90 325 90"></path>
        <path id="flowLineProxyOllama" class="flow-svg-line" d="M 325 90 C 450 90 470 90 595 90"></path>
        <path id="flowLineOllamaModel" class="flow-svg-line" d="M 595 90 C 720 90 740 90 945 90"></path>
        <circle id="flowPacket" class="flow-svg-packet" r="5" cx="0" cy="0"></circle>
      </svg>
      <div class="node flow-node">
        <div class="flow-node-head"><div class="flow-node-title"><span id="clientDot" class="dot waiting"></span>Client</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="12" rx="2"></rect><path d="M8 20h8"></path><path d="M12 16v4"></path></svg></div></div>
        <div class="flow-node-main"><div id="clientText" class="value">Waiting</div><div id="clientSub" class="small">No clients seen yet</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Inbound requests</span><span id="clientStatusBadge" class="badge waiting flow-status">Waiting</span></div>
      </div>
      <div class="pipe"></div>
      <div class="node flow-node">
        <div class="flow-node-head"><div class="flow-node-title"><span id="proxyDot" class="dot online"></span>ContextKeeper Status</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3 4 6v6c0 5 3.4 8 8 9 4.6-1 8-4 8-9V6z"></path><path d="m9 12 2 2 4-5"></path></svg></div></div>
        <div class="flow-node-main"><div class="value ok">Online</div><div id="proxySub" class="small">Listening on port {settings.server.port}</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Local proxy</span><span id="proxyStatusBadge" class="badge online flow-status">Online</span></div>
      </div>
      <div class="pipe"></div>
      <div class="node flow-node signal-node">
        <div class="flow-node-head"><div class="flow-node-title"><span id="ollamaDot" class="dot waiting"></span>Ollama Status</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 2v4"></path><path d="M12 18v4"></path><path d="M4.9 4.9 7.8 7.8"></path><path d="m16.2 16.2 2.9 2.9"></path><path d="M2 12h4"></path><path d="M18 12h4"></path><circle cx="12" cy="12" r="4"></circle></svg></div></div>
        <div class="flow-node-main"><div id="ollamaText" class="value">Checking</div><div id="ollamaSub" class="small">{settings.ollama.base_url}</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Upstream runtime</span><span id="ollamaStatusBadge" class="badge waiting flow-status">Checking</span></div>
      </div>
      <div class="pipe"></div>
      <div class="node flow-node">
        <div class="flow-node-head"><div class="flow-node-title"><span id="modelDot" class="dot waiting"></span>Model</div><div class="flow-node-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 7h8"></path><path d="M8 12h8"></path><path d="M8 17h5"></path><rect x="4" y="3" width="16" height="18" rx="2"></rect></svg></div></div>
        <div class="flow-node-main"><div id="modelText" class="value">Waiting</div><div id="modelSub" class="small">No model observed yet</div></div>
        <div class="flow-node-foot"><span class="flow-endpoint">Active model</span><span id="modelStatusBadge" class="badge waiting flow-status">Waiting</span></div>
      </div>
    </div>
  </section>

  <section class="operations-lower">
    <div class="card traffic-panel ops-panel">
      <h2>Traffic</h2>
      <div class="traffic-stats">
        <div><div class="small">Request Trend</div><div id="requestTrend" class="value">Flat</div><div id="requestTrendText" class="muted">Awaiting request data.</div></div>
        <div><div class="small">Rate</div><div id="requestRate" class="value">0</div><div class="muted">requests / min</div></div>
      </div>
      <div class="muted">Average response time is summarized in the hero statistics row.</div>
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
    <div class="card signal-card compact-card"><h2><span class="icon-label"><span class="icon-mark">%</span>Context Usage</span></h2><div class="signal-body"><div class="signal-stack"><div id="contextUsage" class="value">--%</div><div id="contextUsageText" class="muted">Context window usage will appear here.</div><div class="bar"><div id="contextUsageBar" class="fill"></div></div></div><svg class="gauge" viewBox="0 0 120 120" aria-hidden="true"><circle class="gauge-track" cx="60" cy="60" r="48" pathLength="100"></circle><circle id="contextGaugeArc" class="gauge-progress" cx="60" cy="60" r="48" pathLength="100"></circle></svg></div></div>
    <div class="card"><h2>Status</h2><div class="value ok">Running</div><div class="muted">Proxy -> {settings.ollama.base_url}</div></div>
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
const TOPOLOGY_PULSE_DURATION_MS = 1300;
const REDUCED_MOTION_QUERY = window.matchMedia('(prefers-reduced-motion: reduce)');
const ACTIVITY_TOPOLOGY_CLASSES = ['activity-starting','activity-connecting','activity-ready','activity-receiving','activity-thinking','activity-streaming','activity-finalizing','activity-idle'];
let lastTopologyRequestCount = null;
let lastActivityState = null;
let topologyPulseTimer = null;
let refreshInFlight = false;
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
  return el.matches('.value,.hero-stat-value,.speedometer-value,.ops-health-status') || el.dataset.liveValue === 'true';
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
  const state = safeClass(activity?.state || '');
  panel.classList.remove(...ACTIVITY_TOPOLOGY_CLASSES);
  if (state) panel.classList.add('activity-' + state);
  if (state === 'receiving' && lastActivityState !== 'receiving' && motionAllowed()) {{
    restartAnimation(panel, 'request-pulse');
    clearTimeout(topologyPulseTimer);
    topologyPulseTimer = setTimeout(() => panel.classList.remove('request-pulse'), TOPOLOGY_PULSE_DURATION_MS);
  }}
  lastActivityState = state;
}}
function triggerTopologyPulse(totalRequests) {{
  const count = Number(totalRequests);
  if (!Number.isFinite(count)) return;
  const panel = byId('connections');
  if (!panel) return;
  if (lastTopologyRequestCount !== null && count > lastTopologyRequestCount) {{
    if (motionAllowed()) {{
      restartAnimation(panel, 'request-pulse');
      clearTimeout(topologyPulseTimer);
      topologyPulseTimer = setTimeout(() => panel.classList.remove('request-pulse'), TOPOLOGY_PULSE_DURATION_MS);
    }}
  }}
  lastTopologyRequestCount = count;
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
  document.querySelectorAll('[data-page-link]').forEach(link => {{
    const active = link.dataset.pageLink === target;
    link.classList.toggle('active', active);
    if (link.closest('.nav')) {{
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    }}
  }});
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
  setText('opsLastRefreshDetail', 'Every ' + DASHBOARD_REFRESH_INTERVAL_MS + ' ms');
  setStatusBadge('opsLastRefreshStatus', 'running', new Date().toLocaleTimeString());
  refreshOperationalActivity(h.activity);
  updateTopologyState(c, h.activity);
}}
async function refreshMetrics() {{
  const res = await fetch('/metrics');
  const data = await res.json();
  const r = data.requests;
  const s = data.system;
  setText('req', r.total_requests);
  triggerTopologyPulse(r.total_requests);
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
  const activity = data.activity || {{}};
  setText('contextUsage', context.usage_percent + '%');
  setText('contextUsageText', context.estimated_tokens + ' estimated tokens across ' + context.conversation_count + ' conversation(s)');
  setText('activeConversationCount', context.conversation_count);
  setWidth('contextUsageBar', Math.min(context.usage_percent, 100) + '%');
  setGauge('contextGaugeArc', context.usage_percent);
  setText('compressionCount', compression.count);
  setText('compressionText', compression.history.length + ' recent compression event(s)');
  refreshOperationalActivity(activity);
  refreshIntelligence(intelligence);
  refreshActiveConversation(data.active_conversation, intelligence.conversation_risk);
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
  }}
}}
initializePages();
refresh(); setInterval(refresh, DASHBOARD_REFRESH_INTERVAL_MS);
</script>
</body>
</html>
"""
