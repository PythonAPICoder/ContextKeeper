from __future__ import annotations

from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings


class DashboardSettingsMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.attributes_by_id: dict[str, dict[str, str | None]] = {}
        self.page_links: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            self.attributes_by_id[element_id] = {"tag": tag, **attributes}
        if attributes.get("data-page-link"):
            self.page_links.append({"tag": tag, **attributes})


@pytest.fixture(scope="module")
def dashboard_html() -> str:
    response = TestClient(create_app(Settings())).get("/dashboard")
    assert response.status_code == 200
    return response.text


def _source_between(html: str, start: str, end: str) -> str:
    start_index = html.index(start)
    return html[start_index : html.index(end, start_index)]


def test_settings_navigation_uses_existing_client_side_page_switching(dashboard_html: str) -> None:
    parser = DashboardSettingsMarkupParser()
    parser.feed(dashboard_html)

    settings_links = [link for link in parser.page_links if link["data-page-link"] == "settings"]
    assert len(settings_links) == 1
    assert settings_links[0]["tag"] == "a"
    assert settings_links[0]["href"] == "#settings"
    assert parser.attributes_by_id["settings"]["data-page"] == "settings"
    assert parser.attributes_by_id["settings"]["aria-labelledby"] == "settingsPageTitle"
    assert parser.attributes_by_id["operations"]["data-page"] == "operations"
    assert "function showPage(pageName)" in dashboard_html
    assert "link.classList.toggle('active', active)" in dashboard_html
    assert "link.setAttribute('aria-current', 'page')" in dashboard_html
    assert "if (target === 'settings') ensureSettingsLoaded();" in dashboard_html


def test_settings_page_has_form_states_actions_and_accessible_feedback(dashboard_html: str) -> None:
    parser = DashboardSettingsMarkupParser()
    parser.feed(dashboard_html)

    assert parser.attributes_by_id["settingsForm"]["tag"] == "form"
    assert parser.attributes_by_id["settingsForm"]["novalidate"] is None
    assert parser.attributes_by_id["settingsCategories"]["aria-label"] == "ContextKeeper settings categories"
    assert parser.attributes_by_id["settingsStatus"]["role"] == "status"
    assert parser.attributes_by_id["settingsStatus"]["aria-live"] == "polite"
    assert parser.attributes_by_id["settingsErrorSummary"]["role"] == "alert"
    assert parser.attributes_by_id["settingsErrorSummary"]["aria-live"] == "assertive"
    assert parser.attributes_by_id["settingsRetryButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsDiscardButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsPersistButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsSaveButton"]["type"] == "submit"
    assert "Save to configuration" in dashboard_html
    assert "Save runtime changes" in dashboard_html
    assert "label.htmlFor = controlId" in dashboard_html
    assert "control.setAttribute('aria-describedby'" in dashboard_html
    assert "control.setAttribute('aria-invalid', 'true')" in dashboard_html


def test_settings_runtime_and_configuration_notice_is_unambiguous(dashboard_html: str) -> None:
    assert 'class="settings-runtime-notice" role="note"' in dashboard_html
    assert "Runtime and saved configuration are separate" in dashboard_html
    assert "The Save runtime changes action applies eligible values to the current ContextKeeper process only" in dashboard_html
    assert "Save to configuration explicitly writes eligible draft values to contextkeeper.yaml" in dashboard_html
    assert "without changing the current runtime or restarting ContextKeeper" in dashboard_html


def test_settings_uses_distinct_runtime_and_configuration_endpoints(dashboard_html: str) -> None:
    assert dashboard_html.count("'/api/dashboard/settings'") == 1
    assert dashboard_html.count("'/api/dashboard/settings/config'") == 1
    assert "const SETTINGS_ENDPOINT = '/api/dashboard/settings';" in dashboard_html
    assert "const SETTINGS_CONFIG_ENDPOINT = '/api/dashboard/settings/config';" in dashboard_html
    assert "method:'GET'" in dashboard_html
    assert "method:'PATCH'" in dashboard_html
    assert "method:'PUT'" in dashboard_html
    assert dashboard_html.count("fetch(SETTINGS_ENDPOINT") == 2
    assert dashboard_html.count("fetch(SETTINGS_CONFIG_ENDPOINT") == 1


def test_settings_controls_are_metadata_driven_and_safely_rendered(dashboard_html: str) -> None:
    settings_renderer = _source_between(dashboard_html, "function cloneSettingsSnapshot", "function settingsValuesEqual")

    assert "category.settings.forEach(setting" in settings_renderer
    assert "snapshot.schema_version !== 2" in settings_renderer
    assert "['boolean','integer','string'].includes(setting.data_type)" in settings_renderer
    assert "Number.isSafeInteger(value)" in settings_renderer
    assert "categoryIds.has(category.id)" in settings_renderer
    assert "setting.minimum > setting.maximum" in settings_renderer
    assert "if (setting.data_type === 'boolean')" in settings_renderer
    assert "if (setting.data_type === 'integer')" in settings_renderer
    assert "control.type = 'text'" in settings_renderer
    assert "control.min = String(setting.minimum)" in settings_renderer
    assert "control.max = String(setting.maximum)" in settings_renderer
    assert "typeof setting.persistable !== 'boolean'" in settings_renderer
    assert "typeof setting.differs_from_persisted !== 'boolean'" in settings_renderer
    assert "settingValueMatchesDataType(setting.data_type, setting.persisted_value)" in settings_renderer
    assert "control.disabled = (!setting.runtime_editable && !setting.persistable)" in settings_renderer
    assert "if (setting.restart_required)" in settings_renderer
    assert "Runtime read-only" in settings_renderer
    assert "Not persistable" in settings_renderer
    assert "Runtime differs from saved" in settings_renderer
    assert "Restart required" in settings_renderer
    assert "Saved configuration: " in settings_renderer
    assert "Saved changes require a ContextKeeper restart before they become active." in settings_renderer
    assert "ContextKeeper is not restarted automatically." in settings_renderer
    assert "document.createElement(tagName)" in settings_renderer
    assert "element.textContent = String(textValue)" in settings_renderer
    assert "container.replaceChildren(fragment)" in settings_renderer
    assert ".innerHTML" not in settings_renderer
    for setting_id in (
        "context.enabled",
        "context.warning_threshold_percent",
        "context.compression_threshold_percent",
        "context.keep_recent_messages",
        "compression.enabled",
        "compression.summarizer_model",
        "compression.max_summary_tokens",
        "dashboard.refresh_interval_ms",
    ):
        assert setting_id not in settings_renderer


def test_confirmed_and_draft_snapshots_are_separate_and_type_safe(dashboard_html: str) -> None:
    state_logic = _source_between(dashboard_html, "function settingsValuesEqual", "function buildSettingsPatchPayload")

    assert "confirmedSnapshot:null" in dashboard_html
    assert "draftSnapshot:null" in dashboard_html
    assert "const confirmed = freezeSettingsSnapshot(cloneSettingsSnapshot(snapshot))" in state_logic
    assert "const draft = cloneSettingsSnapshot(confirmed)" in state_logic
    assert "settingsPageState.confirmedSnapshot = confirmed" in state_logic
    assert "settingsPageState.draftSnapshot = draft" in state_logic
    assert "typeof confirmedValue === typeof draftValue && confirmedValue === draftValue" in state_logic
    assert "if (!confirmedSetting.runtime_editable && !confirmedSetting.persistable) return" in state_logic
    assert "return changedDraftSettings().filter(change => change.setting.runtime_editable)" in state_logic
    assert "if (!confirmedSetting.persistable) return" in state_logic
    assert "!settingsValuesEqual(confirmedSetting.persisted_value, draftSetting.value)" in state_logic
    assert "setting.value = valueFromSettingsControl(control, setting)" in state_logic
    assert "return control.checked" in state_logic
    assert "return rawValue === '' ? null : Number(rawValue)" in state_logic
    assert "!settingsValuesEqual(confirmedSetting.value, draftSetting.value)" in state_logic


def test_dirty_actions_follow_changed_and_valid_draft_state(dashboard_html: str) -> None:
    actions = _source_between(dashboard_html, "function updateSettingsActions", "function acceptSettingsSnapshot")

    assert "const draftChanges = changedDraftSettings()" in actions
    assert "const runtimeChanges = changedRuntimeSettings()" in actions
    assert "const persistenceChanges = changedPersistableSettings()" in actions
    assert "const draftValid = settingsDraftIsValid()" in actions
    assert "const locked = busy || settingsPageState.confirmationRequired" in actions
    assert "!runtimeChanges.length || !draftValid" in actions
    assert "!persistenceChanges.length || !draftValid" in actions
    assert "!draftChanges.length" in actions
    assert "Runtime and saved configuration values are aligned. No unsaved changes." in actions
    assert "Correct invalid draft values before saving." in actions
    assert "settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting" in actions


def test_save_builds_one_nested_changed_fields_only_request(dashboard_html: str) -> None:
    payload_builder = _source_between(dashboard_html, "function buildSettingsPayload", "async function readSettingsResponse")
    save_logic = _source_between(dashboard_html, "async function saveSettings", "async function persistSettings")

    assert "changes.forEach(change" in payload_builder
    assert "const category = change.setting.category" in payload_builder
    assert "payload[category] = Object.create(null)" in payload_builder
    assert "payload[category][fieldName] = change.value" in payload_builder
    assert "return buildSettingsPayload(changedRuntimeSettings())" in payload_builder
    assert save_logic.count("fetch(SETTINGS_ENDPOINT") == 1
    assert "method:'PATCH'" in save_logic
    assert "method:'PUT'" not in save_logic
    assert "body:JSON.stringify(payload)" in save_logic
    assert "if (settingsPageState.saving" in save_logic
    assert "settingsPageState.persisting" in save_logic
    assert "settingsPageState.saving = true" in save_logic
    assert "settingsPageState.saving = false" in save_logic


def test_success_uses_authoritative_snapshot_and_clears_dirty_state(dashboard_html: str) -> None:
    success_logic = _source_between(dashboard_html, "async function authoritativeSettingsSnapshot", "async function persistSettings")

    assert "return validateSettingsSnapshot(patchPayload)" in success_logic
    assert "return await requestSettingsSnapshot()" in success_logic
    assert "const snapshot = await authoritativeSettingsSnapshot(responsePayload)" in success_logic
    assert "const preservedPersistenceOnlyDraftValues = capturePersistenceOnlyDraftValues()" in success_logic
    assert "acceptSettingsSnapshot(snapshot, preservedPersistenceOnlyDraftValues)" in success_logic
    assert "!confirmed.runtime_editable && confirmed.persistable" in dashboard_html
    assert "Settings saved for the current runtime." in success_logic
    assert "requestDashboardRefresh()" in success_logic
    assert "settingsPageState.confirmationRequired = true" in success_logic
    assert "showSettingsLoadState('Confirm current settings'" in success_logic


def test_save_failures_preserve_draft_and_surface_safe_retryable_errors(dashboard_html: str) -> None:
    save_logic = _source_between(dashboard_html, "async function saveSettings", "async function persistSettings")
    error_logic = _source_between(dashboard_html, "function settingsErrorMessages", "async function requestSettingsSnapshot")

    assert "if (!response.ok)" in save_logic
    assert "applySettingsValidationErrors(responsePayload)" in save_logic
    assert "Your changes are still available to correct." in save_logic
    assert "Your changes were not discarded" in save_logic
    assert "focusAfterSave = firstInvalid" in save_logic
    assert "if (focusAfterSave && settingsPageIsActive()) focusAfterSave.focus()" in save_logic
    assert "settingsPageState.draftSnapshot =" not in save_logic
    assert "restoreSettingsDraft()" not in save_logic
    assert "detail.msg" in error_logic
    assert "summary.textContent = message" in dashboard_html
    assert "summary.innerHTML" not in dashboard_html


def test_persistence_payload_uses_only_persistable_values_that_differ_from_saved(dashboard_html: str) -> None:
    change_logic = _source_between(dashboard_html, "function changedPersistableSettings", "function settingsDifferenceMessage")
    payload_logic = _source_between(dashboard_html, "function buildSettingsPayload", "async function readSettingsResponse")

    assert "if (!confirmedSetting.persistable) return" in change_logic
    assert "!settingsValuesEqual(confirmedSetting.persisted_value, draftSetting.value)" in change_logic
    assert "changes.push({ setting:confirmedSetting, value:draftSetting.value })" in change_logic
    assert "return buildSettingsPayload(changedPersistableSettings())" in payload_logic
    assert "const prefix = category + '.'" in payload_logic
    assert "payload[category][fieldName] = change.value" in payload_logic


def test_persistence_is_explicit_put_only_and_never_triggered_by_editing(dashboard_html: str) -> None:
    input_logic = _source_between(dashboard_html, "function handleSettingsInput", "function buildSettingsPayload")
    persist_logic = _source_between(dashboard_html, "async function persistSettings", "function initializeSettingsPage")
    initialization = _source_between(dashboard_html, "function initializeSettingsPage", "function showPage")

    assert "fetch(" not in input_logic
    assert "persistSettings(" not in input_logic
    assert persist_logic.count("fetch(SETTINGS_CONFIG_ENDPOINT") == 1
    assert "method:'PUT'" in persist_logic
    assert "body:JSON.stringify(payload)" in persist_logic
    assert "const persist = byId('settingsPersistButton')" in initialization
    assert "persist.addEventListener('click', () => void persistSettings())" in initialization
    assert dashboard_html.count("void persistSettings()") == 1
    assert "form.addEventListener('submit'" in initialization
    assert "void saveSettings()" in initialization


def test_persistence_busy_state_disables_duplicate_actions_and_reports_progress(dashboard_html: str) -> None:
    actions = _source_between(dashboard_html, "function updateSettingsActions", "function captureSettingsDraftValues")
    persist_logic = _source_between(dashboard_html, "async function persistSettings", "function initializeSettingsPage")

    assert "persisting:false" in dashboard_html
    assert "const busy = settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting" in actions
    assert "persist.disabled = locked || !settingsPageState.loaded || !persistenceChanges.length || !draftValid" in actions
    assert "settingsPageState.persisting ? 'Saving to configuration...' : 'Save to configuration'" in actions
    assert "if (settingsPageState.persisting || settingsPageState.saving || settingsPageState.loading" in persist_logic
    assert "settingsPageState.persisting = true" in persist_logic
    assert "settingsPageState.persisting = false" in persist_logic


def test_persistence_success_validates_response_refreshes_metadata_and_preserves_draft(dashboard_html: str) -> None:
    response_logic = _source_between(dashboard_html, "function validateSettingsPersistenceResponse", "function settingsErrorMessages")
    snapshot_logic = _source_between(dashboard_html, "function captureSettingsDraftValues", "function valueFromSettingsControl")
    persist_logic = _source_between(dashboard_html, "async function persistSettings", "function initializeSettingsPage")

    assert "payload.status !== 'saved'" in response_logic
    assert "Array.isArray(payload.persisted_setting_ids)" in response_logic
    assert "typeof payload.configuration_created !== 'boolean'" in response_logic
    assert "validateSettingsSnapshot(payload.settings)" in response_logic
    assert "const preservedDraftValues = captureSettingsDraftValues()" in persist_logic
    assert "const result = await authoritativePersistenceResult(responsePayload)" in persist_logic
    assert "acceptSettingsSnapshot(result.settings, preservedDraftValues)" in persist_logic
    assert "Runtime values were not changed." in persist_logic
    assert "preservedDraftValues.forEach((value, settingId)" in snapshot_logic
    assert "draftSetting.value = value" in snapshot_logic


def test_persistence_failure_retains_draft_and_uses_inline_feedback(dashboard_html: str) -> None:
    persist_logic = _source_between(dashboard_html, "async function persistSettings", "function initializeSettingsPage")

    assert "if (!response.ok)" in persist_logic
    assert "applySettingsValidationErrors(responsePayload)" in persist_logic
    assert "Your draft is still available to correct." in persist_logic
    assert "Your draft is still available." in persist_logic
    assert "Your draft was not discarded" in persist_logic
    assert "settingsPageState.draftSnapshot =" not in persist_logic
    assert "restoreSettingsDraft()" not in persist_logic
    assert "showSettingsPageError(" in persist_logic
    assert "alert(" not in persist_logic


def test_runtime_and_persisted_differences_are_explicit_and_restart_safe(dashboard_html: str) -> None:
    difference_logic = _source_between(dashboard_html, "function settingsDifferenceMessage", "function settingsDraftValueIsValid")
    renderer = _source_between(dashboard_html, "function createSettingsItem", "function renderSettingsCategories")

    assert "Draft differs from the current runtime and saved configuration." in difference_logic
    assert "Draft matches the saved configuration and differs from the current runtime." in difference_logic
    assert "Current runtime differs from the saved configuration." in difference_logic
    assert "Draft matches the current runtime and saved configuration." in difference_logic
    assert "Saved configuration: " in renderer
    assert "Runtime differs from saved" in renderer
    assert "Saved changes require a ContextKeeper restart before they become active." in renderer
    assert "ContextKeeper is not restarted automatically." in renderer
    assert "This draft can be saved to configuration, but it cannot be applied to the current runtime." in renderer


def test_discard_restores_latest_confirmed_snapshot_without_network_request(dashboard_html: str) -> None:
    restore_logic = _source_between(dashboard_html, "function restoreSettingsDraft", "async function authoritativeSettingsSnapshot")
    discard_logic = _source_between(dashboard_html, "function discardSettingsDraft", "async function authoritativeSettingsSnapshot")

    assert "cloneSettingsSnapshot(settingsPageState.confirmedSnapshot)" in restore_logic
    assert "settingsPageState.fieldErrors = new Map()" in restore_logic
    assert "restoreSettingsDraft()" in discard_logic
    assert "Unsaved changes discarded." in discard_logic
    assert "fetch(" not in discard_logic
    assert "PATCH" not in discard_logic


def test_load_failure_retry_and_malformed_data_paths_fail_safely(dashboard_html: str) -> None:
    load_logic = _source_between(dashboard_html, "async function requestSettingsSnapshot", "function restoreSettingsDraft")

    assert "return validateSettingsSnapshot(payload)" in load_logic
    assert "showSettingsLoadState('Settings could not be loaded'" in load_logic
    assert "showSettingsPageError(message, false)" in load_logic
    assert "settingsPageState.loaded = false" in load_logic
    assert "Retry loading settings" in dashboard_html
    assert "if (settingsPageState.confirmationRequired) void confirmSettingsAfterAcceptedUpdate()" in dashboard_html
    assert "else void loadSettings()" in dashboard_html
    assert "The settings response format is not supported." in dashboard_html


def test_settings_responsive_accessibility_and_dashboard_lifecycle_guards(dashboard_html: str) -> None:
    assert ".settings-input:focus-visible,.settings-checkbox:focus-visible" in dashboard_html
    assert ".settings-button:disabled { cursor:not-allowed; opacity:.5" in dashboard_html
    assert "@media (max-width: 700px)" in dashboard_html
    assert ".settings-item { grid-template-columns:1fr" in dashboard_html
    assert ".settings-action-bar { align-items:stretch; flex-direction:column" in dashboard_html
    assert "@media (prefers-reduced-motion: reduce)" in dashboard_html
    assert ".settings-button,.settings-input { transition:none; }" in dashboard_html
    assert dashboard_html.count("setInterval(") == 1
    assert "clearInterval(dashboardRefreshTimer)" in dashboard_html
    assert "scheduleDashboardRefresh(data.refresh_interval_ms)" in dashboard_html
    assert "setText('opsLastRefreshDetail', 'Every ' + dashboardRefreshIntervalMs + ' ms')" in dashboard_html
    assert "if (refreshInFlight)" in dashboard_html
    assert "refreshAfterCurrent = true" in dashboard_html
    assert dashboard_html.count("initializeSettingsPage();") == 1
    assert "form.addEventListener('input', handleSettingsInput)" in dashboard_html
    assert "if (focusSummary && settingsPageIsActive()) summary.focus()" in dashboard_html
