from __future__ import annotations

from ctxkeeper.config import Settings
from ctxkeeper.dashboard.settings_snapshot import build_dashboard_settings_snapshot
from ctxkeeper.dashboard.template import render_dashboard_html


def test_release_gate_escapes_configured_dashboard_title() -> None:
    unsafe_title = "</title><script id='audit-marker'>alert(1)</script><title>"

    html = render_dashboard_html(Settings(dashboard={"title": unsafe_title}))

    assert unsafe_title not in html
    assert "<script id='audit-marker'>" not in html
    assert (
        "<title>&lt;/title&gt;&lt;script id=&#x27;audit-marker&#x27;&gt;"
        "alert(1)&lt;/script&gt;&lt;title&gt;</title>"
    ) in html


def test_release_gate_settings_catalog_matches_rendered_metadata_contract() -> None:
    snapshot = build_dashboard_settings_snapshot(Settings()).to_dict()
    expected_categories = [
        ("ollama", "Connection"),
        ("context", "Context"),
        ("compression", "Compression"),
        ("dashboard", "Dashboard"),
    ]
    expected_settings = {
        "ollama.base_url": (
            "AI Server Endpoint",
            "string",
            None,
            None,
            False,
            True,
            True,
            True,
        ),
        "ollama.timeout_seconds": (
            "Request Timeout",
            "integer",
            1,
            None,
            False,
            True,
            True,
            True,
        ),
        "context.enabled": (
            "Context tracking",
            "boolean",
            None,
            None,
            True,
            True,
            False,
            True,
        ),
        "context.warning_threshold_percent": (
            "Warning threshold",
            "integer",
            0,
            100,
            True,
            True,
            False,
            True,
        ),
        "context.compression_threshold_percent": (
            "Compression threshold",
            "integer",
            0,
            100,
            True,
            True,
            False,
            True,
        ),
        "context.keep_recent_messages": (
            "Recent messages retained",
            "integer",
            1,
            None,
            True,
            True,
            False,
            True,
        ),
        "compression.enabled": (
            "Compression",
            "boolean",
            None,
            None,
            True,
            True,
            False,
            True,
        ),
        "compression.summarizer_model": (
            "Summarizer model",
            "string",
            None,
            None,
            True,
            True,
            False,
            True,
        ),
        "compression.max_summary_tokens": (
            "Maximum summary tokens",
            "integer",
            1,
            None,
            True,
            True,
            False,
            True,
        ),
        "dashboard.refresh_interval_ms": (
            "Refresh interval",
            "integer",
            1,
            None,
            True,
            True,
            False,
            True,
        ),
    }

    assert [
        (category["id"], category["display_name"])
        for category in snapshot["categories"]
    ] == expected_categories
    actual_settings = {
        setting["id"]: (
            setting["display_name"],
            setting["data_type"],
            setting["minimum"],
            setting["maximum"],
            setting["runtime_editable"],
            setting["persistable"],
            setting["restart_required"],
            setting["reset_eligible"],
        )
        for category in snapshot["categories"]
        for setting in category["settings"]
    }
    assert actual_settings == expected_settings
    assert {
        "server.host",
        "server.port",
        "ollama.retry_count",
        "ollama.retry_delay_seconds",
        "ollama.backoff_seconds",
    }.isdisjoint(actual_settings)

    html = render_dashboard_html(Settings())
    assert "settingsPageState.draftSnapshot.categories.forEach" in html
    assert "category.settings.forEach(setting =>" in html
    assert "const CONNECTION_SETTINGS_CATEGORY_ID = 'ollama';" in html
    assert "const CONNECTION_ENDPOINT_SETTING_ID = 'ollama.base_url';" in html
    assert "const CONNECTION_TIMEOUT_SETTING_ID = 'ollama.timeout_seconds';" in html


def test_release_gate_preserves_unavailable_numeric_telemetry() -> None:
    html = render_dashboard_html(Settings())

    assert "function numberOrNull(value)" in html
    assert (
        "return typeof value === 'number' && Number.isFinite(value) ? value : null;"
        in html
    )
    assert "const numeric = Number(value);\n  return Number.isFinite(numeric)" not in html
    assert "const valueText = value === null ? 'N/A' : formatPercentValue(value);" in html


def test_release_gate_protects_inspector_keyboard_contract() -> None:
    html = render_dashboard_html(Settings())

    assert (
        'id="conversationInspectorDrawer" class="conversation-inspector-drawer" '
        'role="complementary" aria-labelledby="conversationInspectorTitle" '
        'aria-hidden="true" inert'
    ) in html
    assert "drawer.inert = !isOpen;" in html
    assert "if (closeButton) closeButton.focus({ preventScroll:true });" in html
    assert "event.key === 'Escape' && conversationInspectorState.inspectorOpen" in html
    assert "if (trigger && typeof trigger.focus === 'function')" in html
    assert "trigger.focus({ preventScroll:true });" in html


def test_release_gate_announces_dashboard_refresh_failure_and_recovery() -> None:
    html = render_dashboard_html(Settings())

    assert (
        'id="dashboardRefreshStatus" class="topbar-status" role="status" '
        'aria-live="polite" aria-atomic="true" '
        'aria-label="Dashboard refresh operating normally."'
    ) in html
    assert "body.refresh-error .topbar-status" in html
    assert "setText('dashboardRefreshStatusText', 'Refresh failed', false);" in html
    assert (
        "Dashboard refresh failed. Displayed data may be stale; retrying automatically."
        in html
    )
    assert "const recovered = document.body.classList.contains('refresh-error');" in html
    assert "setText('dashboardRefreshStatusText', 'Operations', false);" in html
    assert (
        "refreshStatus.setAttribute('aria-label', 'Dashboard refresh operating normally.');"
        in html
    )


def test_release_gate_protects_unsaved_settings_drafts_on_navigation() -> None:
    html = render_dashboard_html(Settings())

    assert "window.addEventListener('beforeunload', event =>" in html
    assert (
        "if (!settingsPageState.loaded || !changedDraftSettings().length) return;"
        in html
    )
    assert "event.preventDefault();" in html
    assert "event.returnValue = '';" in html


def test_release_gate_protects_responsive_and_reduced_motion_contracts() -> None:
    long_endpoint = "http://ollama.internal/" + ("long-endpoint-segment-" * 30)
    html = render_dashboard_html(Settings(ollama={"base_url": long_endpoint}))

    for breakpoint in (1900, 1500, 1350, 1000):
        assert f"@media (max-width: {breakpoint}px)" in html
    assert "@media (prefers-reduced-motion: reduce)" in html
    assert (
        "const REDUCED_MOTION_QUERY = "
        "window.matchMedia('(prefers-reduced-motion: reduce)');"
    ) in html
    assert "function motionAllowed()" in html
    assert "return !REDUCED_MOTION_QUERY.matches;" in html
    assert (
        ".topbar-actions { flex:1 1 auto; min-width:0; max-width:100%;"
        in html
    )
    assert "grid-template-columns:minmax(0,1fr); grid-template-rows:auto" in html
    assert (
        ".topbar-endpoint { flex:0 1 auto; overflow:hidden; "
        "text-overflow:ellipsis; white-space:nowrap; }"
        in html
    )
    assert f'<span class="topbar-pill topbar-endpoint">{long_endpoint}</span>' in html


def test_release_gate_active_conversation_open_button_contract() -> None:
    html = render_dashboard_html(Settings())

    assert (
        '<button type="button" id="opsActiveConversationInspectBtn" '
        'class="badge info" data-inspect-active-conversation="true" '
        'aria-label="Inspect active conversation details" disabled aria-disabled="true">Open</button>'
    ) in html
    assert "returnFocusId:null" in html
    assert "const inspectBtn = byId('opsActiveConversationInspectBtn');" in html
    assert (
        "openConversationInspector(activeId, null, { returnFocusId: "
        "'opsActiveConversationInspectBtn' });"
    ) in html
    assert "const hasActiveId = Boolean(current.conversation_id);" in html
    assert "inspectBtn.disabled = !hasActiveId;" in html
    assert "if (hasActiveId) inspectBtn.removeAttribute('aria-disabled');" in html
    assert "else inspectBtn.setAttribute('aria-disabled', 'true');" in html


def test_release_gate_inspector_focus_restoration_and_timeline_integrity() -> None:
    html = render_dashboard_html(Settings())

    assert (
        "function openConversationInspector(conversationId, eventId, options) {"
        in html
    )
    assert (
        "conversationInspectorState.returnFocusId = options?.returnFocusId || "
        "null;"
    ) in html
    assert "const returnFocusId = conversationInspectorState.returnFocusId;" in html
    assert "if (eventId) {" in html
    assert (
        "const trigger = "
        "Array.from(document.querySelectorAll('#liveConversationTimelineList "
        "[data-event-id]'))"
    ) in html
    assert "if (returnFocusId) {" in html
    assert "const trigger = byId(returnFocusId);" in html
    assert (
        "if (trigger && typeof trigger.focus === 'function') trigger.focus({ "
        "preventScroll:true });"
    ) in html
    assert "a.badge:hover,button.badge:hover:not(:disabled)" in html
