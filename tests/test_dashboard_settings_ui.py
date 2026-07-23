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


def test_active_ollama_endpoint_is_escaped_in_static_dashboard_markup() -> None:
    endpoint = "http://example.com/</span><img/src=x/onerror=alert(1)>"
    response = TestClient(
        create_app(Settings(ollama={"base_url": endpoint}))
    ).get("/dashboard")

    assert response.status_code == 200
    assert endpoint not in response.text
    assert (
        response.text.count(
            "http://example.com/&lt;/span&gt;&lt;img/src=x/onerror=alert(1)&gt;"
        )
        == 3
    )
    assert "<img/src=x/onerror=alert(1)>" not in response.text


def test_settings_page_has_form_states_actions_and_accessible_feedback(dashboard_html: str) -> None:
    parser = DashboardSettingsMarkupParser()
    parser.feed(dashboard_html)

    assert parser.attributes_by_id["settingsForm"]["tag"] == "form"
    assert parser.attributes_by_id["settingsForm"]["novalidate"] is None
    assert parser.attributes_by_id["settingsCategories"]["aria-label"] == "ContextKeeper settings categories"
    assert parser.attributes_by_id["settingsStatus"]["role"] == "status"
    assert parser.attributes_by_id["settingsStatus"]["aria-live"] == "polite"
    assert parser.attributes_by_id["settingsStatus"]["tabindex"] == "-1"
    assert parser.attributes_by_id["settingsErrorSummary"]["role"] == "alert"
    assert parser.attributes_by_id["settingsErrorSummary"]["aria-live"] == "assertive"
    assert parser.attributes_by_id["settingsRetryButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsResetAllButton"]["tag"] == "button"
    assert parser.attributes_by_id["settingsResetAllButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsResetAllButton"]["disabled"] is None
    assert parser.attributes_by_id["settingsDiscardButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsPersistButton"]["type"] == "button"
    assert parser.attributes_by_id["settingsSaveButton"]["type"] == "submit"
    assert (
        '<button id="settingsResetAllButton" class="settings-button recovery" type="button" disabled>'
        "Reset managed settings to defaults</button>"
    ) in dashboard_html
    assert "Reset managed settings to defaults" in dashboard_html
    assert "Discard changes" in dashboard_html
    assert "Save to configuration" in dashboard_html
    assert "Save runtime changes" in dashboard_html
    assert "label.htmlFor = controlId" in dashboard_html
    assert "control.setAttribute('aria-describedby'" in dashboard_html
    assert "control.setAttribute('aria-invalid', 'true')" in dashboard_html


def test_settings_runtime_and_configuration_notice_is_unambiguous(dashboard_html: str) -> None:
    assert 'class="settings-runtime-notice" role="note"' in dashboard_html
    assert "Runtime and saved configuration are separate" in dashboard_html
    assert "Save runtime changes applies only runtime-editable drafts" in dashboard_html
    assert "runtime-editable defaults are applied to the current process" in dashboard_html
    assert "restart-required defaults remain browser drafts until saved" in dashboard_html
    assert "Save to configuration writes eligible drafts to contextkeeper.yaml" in dashboard_html
    assert "without changing runtime or restarting ContextKeeper" in dashboard_html
    assert "Higher-priority environment or command-line overrides may still take precedence after restart" in dashboard_html


def test_settings_uses_distinct_runtime_and_configuration_endpoints(dashboard_html: str) -> None:
    assert dashboard_html.count("'/api/dashboard/settings'") == 1
    assert dashboard_html.count("'/api/dashboard/settings/config'") == 1
    assert "const SETTINGS_ENDPOINT = '/api/dashboard/settings';" in dashboard_html
    assert "const SETTINGS_CONFIG_ENDPOINT = '/api/dashboard/settings/config';" in dashboard_html
    assert (
        "const SETTINGS_CONNECTION_TEST_ENDPOINT = "
        "'/api/dashboard/settings/connection/test';"
    ) in dashboard_html
    assert "method:'GET'" in dashboard_html
    assert "method:'PATCH'" in dashboard_html
    assert "method:'PUT'" in dashboard_html
    assert dashboard_html.count("fetch(SETTINGS_ENDPOINT") == 4
    assert dashboard_html.count("fetch(SETTINGS_CONFIG_ENDPOINT") == 1
    assert dashboard_html.count("fetch(SETTINGS_CONNECTION_TEST_ENDPOINT") == 1


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
    assert "control.type = setting.id === CONNECTION_ENDPOINT_SETTING_ID ? 'url' : 'text'" in settings_renderer
    assert "control.required = true" in settings_renderer
    assert "control.inputMode = 'url'" in settings_renderer
    assert "control.min = String(setting.minimum)" in settings_renderer
    assert "control.max = String(setting.maximum)" in settings_renderer
    assert "typeof setting.persistable !== 'boolean'" in settings_renderer
    assert "typeof setting.reset_eligible !== 'boolean'" in settings_renderer
    assert "typeof setting.differs_from_persisted !== 'boolean'" in settings_renderer
    assert "settingValueMatchesDataType(setting.data_type, setting.persisted_value)" in settings_renderer
    assert "settingValueMatchesDataType(setting.data_type, setting.default_value)" in settings_renderer
    assert (
        "if (setting.reset_eligible && !setting.runtime_editable && !setting.persistable) invalid()"
        in settings_renderer
    )
    assert "control.disabled = (!setting.runtime_editable && !setting.persistable)" in settings_renderer
    assert "if (setting.restart_required)" in settings_renderer
    assert "Runtime read-only" in settings_renderer
    assert "Not persistable" in settings_renderer
    assert "Runtime differs from saved" in settings_renderer
    assert "Restart required" in settings_renderer
    assert "Current runtime: " in settings_renderer
    assert "Default: " in settings_renderer
    assert "Saved configuration: " in settings_renderer
    assert "Saved changes are read at startup and require a manual ContextKeeper restart." in settings_renderer
    assert "ContextKeeper is not restarted automatically." in settings_renderer
    assert "Higher-priority environment or command-line overrides may still take precedence" in settings_renderer
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


def test_connection_action_panel_is_scoped_accessible_and_transient(dashboard_html: str) -> None:
    renderer = _source_between(
        dashboard_html,
        "function createConnectionTestPanel",
        "function settingsValuesEqual",
    )

    assert "if (category.id === CONNECTION_SETTINGS_CATEGORY_ID)" in renderer
    assert "createConnectionTestPanel()" in renderer
    assert "Test draft connection" in renderer
    assert "button.type = 'button'" in renderer
    assert "button.setAttribute('aria-controls', 'settingsConnectionTestResult')" in renderer
    assert "button.setAttribute('aria-describedby', 'settingsConnectionTestDescription')" in renderer
    assert "button.addEventListener('click', () => void testDraftConnection())" in renderer
    assert "result.setAttribute('role', 'status')" in renderer
    assert "result.setAttribute('aria-live', 'polite')" in renderer
    assert "result.setAttribute('aria-atomic', 'true')" in renderer
    assert "does not save configuration, replace the active Ollama client, or update active health state" in renderer
    assert ".innerHTML" not in renderer


def test_reset_controls_are_native_accessible_and_metadata_driven(dashboard_html: str) -> None:
    renderer = _source_between(dashboard_html, "function createSettingsItem", "function settingsValuesEqual")
    initialization = _source_between(dashboard_html, "function initializeSettingsPage", "function showPage")

    assert "if (setting.reset_eligible)" in renderer
    assert "resetButton.type = 'button'" in renderer
    assert "resetButton.dataset.settingsResetSetting = setting.id" in renderer
    assert "resetButton.setAttribute('aria-label', 'Reset ' + setting.display_name + ' to built-in default')" in renderer
    assert "resetSettingsToDefaults({ settingId:setting.id, label:setting.display_name })" in renderer
    assert "resetCategory.type = 'button'" in renderer
    assert "resetCategory.dataset.settingsResetCategory = category.id" in renderer
    assert "resetCategory.setAttribute('aria-label', 'Reset ' + category.display_name + ' settings to built-in defaults')" in renderer
    assert "resetSettingsToDefaults({ categoryId:category.id, label:category.display_name, confirmation:true })" in renderer
    assert "const resetAll = byId('settingsResetAllButton')" in initialization
    assert "resetAll.addEventListener('click', () => void resetSettingsToDefaults({ confirmation:true }))" in initialization
    assert ".innerHTML" not in renderer


def test_reset_eligibility_scope_and_noop_state_are_authoritative(dashboard_html: str) -> None:
    reset_helpers = _source_between(dashboard_html, "function settingCanReset", "function changedDraftSettings")
    actions = _source_between(dashboard_html, "function updateSettingsActions", "function captureSettingsDraftValues")

    assert "setting.reset_eligible && (setting.runtime_editable || setting.persistable)" in reset_helpers
    assert "settingValueMatchesDataType(setting.data_type, setting.default_value)" in reset_helpers
    assert "settingsPageState.confirmedSnapshot.categories.forEach(category" in reset_helpers
    assert "if (selection.categoryId && category.id !== selection.categoryId) return" in reset_helpers
    assert "if (selection.settingId && setting.id !== selection.settingId) return" in reset_helpers
    assert "const draftSetting = settingsPageState.draftSettingsById.get(setting.id)" in reset_helpers
    assert "settingsValuesEqual(draftSetting.value, setting.default_value)" in reset_helpers
    assert "changes.push({ setting:setting, value:setting.default_value })" in reset_helpers
    assert "resettableSettings({ settingId:settingId }).length" in actions
    assert "resettableSettings({ categoryId:categoryId }).length" in actions
    assert "setSettingsButtonDisabled(resetAll, locked || !settingsPageState.loaded || !resettableSettings().length)" in actions

    reset_source = reset_helpers + _source_between(
        dashboard_html,
        "async function resetSettingsToDefaults",
        "function restoreSettingsDraft",
    )
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
        assert setting_id not in reset_source
    for hard_coded_default in ("gpt-oss:20b", "value:75", "value:85", "value:8", "value:1200", "value:1000"):
        assert hard_coded_default not in reset_source


def test_confirmed_and_draft_snapshots_are_separate_and_type_safe(dashboard_html: str) -> None:
    state_logic = _source_between(dashboard_html, "function settingsValuesEqual", "function buildSettingsPatchPayload")

    assert "confirmedSnapshot:null" in dashboard_html
    assert "draftSnapshot:null" in dashboard_html
    assert "const confirmed = freezeSettingsSnapshot(cloneSettingsSnapshot(snapshot))" in state_logic
    assert "const draft = createSettingsDraftSnapshot(confirmed)" in state_logic
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
    assert "!settingsValuesEqual(baselineValue, draftSetting.value)" in state_logic


def test_restart_only_drafts_start_and_restore_from_saved_configuration(
    dashboard_html: str,
) -> None:
    state_logic = _source_between(
        dashboard_html,
        "function settingsDraftBaselineValue",
        "function settingsDifferenceMessage",
    )
    restore_logic = _source_between(
        dashboard_html,
        "function restoreSettingsDraft",
        "async function discardSettingsDraft",
    )

    assert (
        "return !setting.runtime_editable && setting.persistable ? "
        "setting.persisted_value : setting.value"
    ) in state_logic
    assert "setting.value = settingsDraftBaselineValue(setting)" in state_logic
    assert "const baselineValue = settingsDraftBaselineValue(confirmedSetting)" in state_logic
    assert "!settingsValuesEqual(baselineValue, draftSetting.value)" in state_logic
    assert (
        "createSettingsDraftSnapshot(settingsPageState.confirmedSnapshot)"
        in restore_logic
    )
    assert "settingsPageState.connectionTestResult = null" in restore_logic


def test_dirty_actions_follow_changed_and_valid_draft_state(dashboard_html: str) -> None:
    actions = _source_between(dashboard_html, "function updateSettingsActions", "function acceptSettingsSnapshot")

    assert "const draftChanges = changedDraftSettings()" in actions
    assert "const runtimeChanges = changedRuntimeSettings()" in actions
    assert "const runtimeRecoveryChanges = runtimeSettingsDifferentFromPersisted()" in actions
    assert "const confirmedDifferences = settingsDifferentFromPersisted()" in actions
    assert "const persistenceChanges = changedPersistableSettings()" in actions
    assert "const draftValid = settingsDraftIsValid()" in actions
    assert "const locked = busy || settingsPageState.confirmationRequired" in actions
    assert "!runtimeChanges.length || !draftValid" in actions
    assert "!persistenceChanges.length || !draftValid" in actions
    assert "!draftChanges.length" in actions
    assert "Runtime and saved configuration values are aligned. No unsaved changes." in actions
    assert "No unsaved draft changes." in actions
    assert "a pending restart or higher-priority override may explain the difference." in actions
    assert "restart-only active value" in actions
    assert "Correct invalid draft values before saving." in actions
    assert "settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting" in actions
    assert "settingsPageState.resetting || settingsPageState.discarding" in actions
    assert "settingsPageState.testingConnection" in actions
    assert "(!draftChanges.length && !runtimeRecoveryChanges.length)" in actions
    assert "settingsPageState.discarding ? 'Discarding changes...' : 'Discard changes'" in actions
    assert "settingsPageState.testingConnection ? 'Testing connection...' : 'Test connection'" in actions
    assert "form.setAttribute('aria-busy', busy ? 'true' : 'false')" in actions


def test_connection_draft_validation_uses_standard_url_and_authoritative_timeout_metadata(
    dashboard_html: str,
) -> None:
    validation = _source_between(
        dashboard_html,
        "function settingsDraftValueIsValid",
        "function refreshSettingsFieldError",
    )

    assert "endpoint = new URL(value)" in validation
    assert "['http:','https:'].includes(endpoint.protocol)" in validation
    assert "endpoint.username || endpoint.password" in validation
    assert "endpoint.search" in validation
    assert "endpoint.hash" in validation
    assert "setting.minimum !== null && value < setting.minimum" in validation
    assert "setting.maximum !== null && value > setting.maximum" in validation
    assert "CONNECTION_ENDPOINT_SETTING_ID" in validation
    assert "self" not in validation.lower()


def test_connection_test_request_uses_current_draft_once_and_blocks_reentry(
    dashboard_html: str,
) -> None:
    request_logic = _source_between(
        dashboard_html,
        "async function testDraftConnection",
        "async function requestSettingsSnapshot",
    )

    assert "if (settingsPageState.testingConnection ||" in request_logic
    assert (
        request_logic.index("const invalidControl = validateConnectionDraft()")
        < request_logic.index("payload = connectionDraftValues()")
    )
    assert "payload = connectionDraftValues()" in request_logic
    assert "settingsPageState.testingConnection = true" in request_logic
    assert (
        request_logic.index("settingsPageState.testingConnection = true")
        < request_logic.index("fetch(SETTINGS_CONNECTION_TEST_ENDPOINT")
    )
    assert request_logic.count("fetch(SETTINGS_CONNECTION_TEST_ENDPOINT") == 1
    assert "method:'POST'" in request_logic
    assert "base_url:payload.base_url" in request_logic
    assert "timeout_seconds:payload.timeout_seconds" in request_logic
    assert "settingsPageState.testingConnection = false" in request_logic
    assert "finally" in request_logic
    assert "requestDashboardRefresh()" not in request_logic
    assert "opsOllama" not in request_logic
    assert "ollamaSub" not in request_logic
    assert "while (" not in request_logic


def test_connection_test_result_handles_success_failure_and_safe_malformed_responses(
    dashboard_html: str,
) -> None:
    result_logic = _source_between(
        dashboard_html,
        "function connectionDraftValues",
        "function settingsDraftValueIsValid",
    )
    request_logic = _source_between(
        dashboard_html,
        "async function testDraftConnection",
        "async function requestSettingsSnapshot",
    )

    assert "typeof payload.connected !== 'boolean'" in result_logic
    assert "Number.isFinite(payload.latency_ms)" in result_logic
    assert "payload.latency_ms < 0" in result_logic
    assert "!payload.ollama_version || !payload.ollama_version.trim()" in result_logic
    assert "Connection successful" in result_logic
    assert "Connection failed" in result_logic
    assert "Tested endpoint" in result_logic
    assert "Round-trip latency" in result_logic
    assert "Ollama version" in result_logic
    assert "Failure category" in result_logic
    assert "it was not saved or activated" in result_logic
    assert "Runtime and saved configuration were not changed." in result_logic
    assert "Higher-priority overrides may still take precedence." in result_logic
    assert "element.textContent = String(textValue)" in dashboard_html
    assert "validateConnectionTestResponse(responsePayload)" in request_logic
    assert "connectionTestFailure(" in request_logic
    assert "invalid_response" in request_logic
    assert "dashboard_unreachable" in request_logic


def test_connection_test_validation_errors_map_to_fields_and_receive_focus(
    dashboard_html: str,
) -> None:
    error_logic = _source_between(
        dashboard_html,
        "function settingIdFromErrorLocation",
        "async function requestSettingsSnapshot",
    )

    assert "['base_url','timeout_seconds'].includes(parts[0])" in error_logic
    assert "settingId = 'ollama.' + parts[0]" in error_logic
    assert "applySettingsValidationErrors(responsePayload, CONNECTION_SETTING_IDS)" in error_logic
    assert "clearSettingsFieldErrorsFor(CONNECTION_SETTING_IDS)" in error_logic
    assert "settingsPageState.fieldErrors.set(settingId, message)" in error_logic
    assert "if (settingsPageIsActive()) invalidControl.focus()" in error_logic
    assert "if (focusAfterTest && settingsPageIsActive()) focusAfterTest.focus()" in error_logic


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


def test_reset_splits_local_restart_only_staging_from_one_runtime_patch(
    dashboard_html: str,
) -> None:
    reset_logic = _source_between(
        dashboard_html,
        "async function resetSettingsToDefaults",
        "function restoreSettingsDraft",
    )

    assert "const resetSelection = { ...selection, includeAlreadyDefault:Boolean(selection.confirmation) }" in reset_logic
    assert "const changes = resettableSettings(resetSelection)" in reset_logic
    assert "const runtimePayloadChanges = changes.filter(change => change.setting.runtime_editable)" in reset_logic
    assert "const resetSettingIds = new Set(changes.map(change => change.setting.id))" in reset_logic
    assert "firstInvalidSettingsControlOutside(resetSettingIds)" in reset_logic
    assert "if (!runtimePayloadChanges.length)" in reset_logic
    local_branch = _source_between(
        reset_logic,
        "if (!runtimePayloadChanges.length)",
        "let payload",
    )
    assert "stageSettingsDraftChanges(changes)" in local_branch
    assert "announceSettingsReset(changes, runtimeResetChanges, selection)" in local_branch
    assert "return;" in local_branch
    assert "fetch(" not in local_branch
    assert "PATCH" not in local_branch
    assert "payload = buildSettingsPayload(runtimePayloadChanges)" in reset_logic
    assert "captureSettingsDraftValuesExcept(resetSettingIds)" in reset_logic
    assert "changes.forEach(change => preservedDraftValues.set(change.setting.id, change.value))" in reset_logic
    assert reset_logic.count("fetch(SETTINGS_ENDPOINT") == 1
    assert reset_logic.count("method:'PATCH'") == 1
    assert "body:JSON.stringify(payload)" in reset_logic
    assert "SETTINGS_CONFIG_ENDPOINT" not in reset_logic
    assert "method:'PUT'" not in reset_logic
    assert "persistSettings(" not in reset_logic
    assert reset_logic.index("payload = buildSettingsPayload(runtimePayloadChanges)") < reset_logic.index(
        "fetch(SETTINGS_ENDPOINT"
    )
    assert "const snapshot = await authoritativeSettingsSnapshot(responsePayload)" in reset_logic
    assert "acceptSettingsSnapshot(snapshot, preservedDraftValues)" in reset_logic
    assert "requestDashboardRefresh()" in reset_logic
    assert "settingsPageState.connectionTestResult = null" in reset_logic


def test_category_and_global_reset_require_keyboard_operable_confirmation(dashboard_html: str) -> None:
    reset_logic = _source_between(
        dashboard_html,
        "async function resetSettingsToDefaults",
        "function restoreSettingsDraft",
    )
    renderer = _source_between(dashboard_html, "function createSettingsItem", "function settingsValuesEqual")

    assert "confirmation:true" in renderer
    assert "if (selection.confirmation)" in reset_logic
    assert "Reset the ' + selection.label + ' category to built-in defaults?" in reset_logic
    assert "Reset all dashboard-managed settings to built-in defaults?" in reset_logic
    assert "Only runtime-editable settings will be applied now." in reset_logic
    assert "Configuration will not be saved." in reset_logic
    assert "if (!window.confirm(confirmationMessage))" in reset_logic
    assert "Reset was cancelled. No settings were changed." in reset_logic
    cancel_branch = _source_between(
        reset_logic,
        "if (!window.confirm(confirmationMessage))",
        "let payload",
    )
    assert "return;" in cancel_branch
    assert "fetch(" not in cancel_branch
    assert reset_logic.index("window.confirm(confirmationMessage)") < reset_logic.index("fetch(SETTINGS_ENDPOINT")
    assert "factory reset" not in dashboard_html.lower()


def test_reset_feedback_validation_and_restart_state_are_explicit(dashboard_html: str) -> None:
    reset_logic = _source_between(
        dashboard_html,
        "function stageSettingsDraftChanges",
        "function restoreSettingsDraft",
    )

    assert "The selected managed settings already use their built-in defaults." in reset_logic
    assert "settingsPageState.resetting ||" in reset_logic
    assert "settingsPageState.discarding || settingsPageState.testingConnection" in reset_logic
    assert "Correct invalid draft values outside this reset before continuing." in reset_logic
    assert "Defaults were not staged. No settings were changed." in reset_logic
    assert "applySettingsValidationErrors(responsePayload)" in reset_logic
    assert "Reset validation failed. No settings were changed." in reset_logic
    assert "const runtimeResetChanges = runtimePayloadChanges.filter" in reset_logic
    assert "const unsavedResetCount = changes.filter" in reset_logic
    assert "const configurationOnlyCount = changes.filter(change => !change.setting.runtime_editable).length" in reset_logic
    assert "Runtime was not changed." in reset_logic
    assert "staged as a browser draft." in reset_logic
    assert "Configuration has not been saved. Use Save to configuration for restart persistence." in reset_logic
    assert "persisted values already match. No configuration save is needed." in reset_logic
    assert "const restartCount = changes.filter" in reset_logic
    assert "will require a manual restart after saving; higher-priority overrides may still take precedence." in reset_logic
    assert "focusSettingsStatus()" in reset_logic
    assert "settingsPageState.confirmationAction = 'reset'" in reset_logic
    assert "settingsPageState.confirmationPreservedDraftValues = preservedDraftValues" in reset_logic
    assert "showSettingsLoadState('Confirm staged defaults'" in reset_logic
    assert "Reset could not be confirmed. Configuration was not saved." in reset_logic
    assert "settingsPageState.resetting = true" in reset_logic
    assert "settingsPageState.resetting = false" in reset_logic


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
    assert "resetting:false" in dashboard_html
    assert "discarding:false" in dashboard_html
    assert "testingConnection:false" in dashboard_html
    assert "const busy = settingsPageState.loading || settingsPageState.saving || settingsPageState.persisting" in actions
    assert "settingsPageState.resetting || settingsPageState.discarding" in actions
    assert "settingsPageState.testingConnection" in actions
    assert "persist.disabled = locked || !settingsPageState.loaded || !persistenceChanges.length || !draftValid" in actions
    assert "settingsPageState.persisting ? 'Saving to configuration...' : 'Save to configuration'" in actions
    assert "if (settingsPageState.persisting || settingsPageState.saving || settingsPageState.loading" in persist_logic
    assert "settingsPageState.resetting" in persist_logic
    assert "settingsPageState.discarding" in persist_logic
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
    assert "const authoritativeSettings = settingsIndex(result.settings)" in persist_logic
    assert "preservedDraftValues.set(change.setting.id, authoritative.persisted_value)" in persist_logic
    assert "settingsPageState.connectionTestResult = null" in persist_logic
    assert "acceptSettingsSnapshot(result.settings, preservedDraftValues)" in persist_logic
    assert "Runtime values were not changed." in persist_logic
    assert "higher-priority overrides may still take precedence" in persist_logic
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
    assert "Default: " in renderer
    assert "Current runtime: " in renderer
    assert "Saved configuration: " in renderer
    assert "Runtime differs from saved" in renderer
    assert "Saved changes are read at startup and require a manual ContextKeeper restart." in renderer
    assert "ContextKeeper is not restarted automatically." in renderer
    assert "Higher-priority environment or command-line overrides may still take precedence" in renderer
    assert "This draft can be saved to configuration, but it cannot be applied to the current runtime." in renderer


def test_discard_keeps_local_draft_recovery_network_free(dashboard_html: str) -> None:
    restore_logic = _source_between(dashboard_html, "function restoreSettingsDraft", "async function discardSettingsDraft")
    discard_logic = _source_between(dashboard_html, "async function discardSettingsDraft", "async function authoritativeSettingsSnapshot")
    local_branch = _source_between(discard_logic, "if (!runtimeChanges.length)", "let payload")

    assert "createSettingsDraftSnapshot(settingsPageState.confirmedSnapshot)" in restore_logic
    assert "settingsPageState.fieldErrors = new Map()" in restore_logic
    assert "settingsPageState.connectionTestResult = null" in restore_logic
    assert "restoreSettingsDraft()" in local_branch
    assert "Unsaved draft changes discarded. Runtime and configuration were not changed." in local_branch
    assert "return;" in local_branch
    assert "fetch(" not in local_branch
    assert "PATCH" not in local_branch


def test_discard_restores_confirmed_runtime_divergence_with_one_atomic_patch(dashboard_html: str) -> None:
    recovery_changes = _source_between(
        dashboard_html,
        "function runtimeSettingsDifferentFromPersisted",
        "function changedDraftSettings",
    )
    discard_logic = _source_between(dashboard_html, "async function discardSettingsDraft", "async function authoritativeSettingsSnapshot")

    assert "if (!setting.runtime_editable || settingsValuesEqual(setting.value, setting.persisted_value)) return" in recovery_changes
    assert "changes.push({ setting:setting, value:setting.persisted_value })" in recovery_changes
    assert "const draftChanges = changedDraftSettings()" in discard_logic
    assert "const runtimeChanges = runtimeSettingsDifferentFromPersisted()" in discard_logic
    assert "settingsPageState.resetting ||" in discard_logic
    assert "settingsPageState.discarding || settingsPageState.testingConnection" in discard_logic
    assert "payload = buildSettingsPayload(runtimeChanges)" in discard_logic
    assert discard_logic.count("fetch(SETTINGS_ENDPOINT") == 1
    assert discard_logic.count("method:'PATCH'") == 1
    assert "body:JSON.stringify(payload)" in discard_logic
    assert "SETTINGS_CONFIG_ENDPOINT" not in discard_logic
    assert "method:'PUT'" not in discard_logic
    assert "const snapshot = await authoritativeSettingsSnapshot(responsePayload)" in discard_logic
    assert "settingsPageState.connectionTestResult = null" in discard_logic
    assert "acceptSettingsSnapshot(snapshot)" in discard_logic
    assert "const remainingRuntimeDifferences = runtimeSettingsDifferentFromPersisted()" in discard_logic
    assert "Persisted configuration changed during runtime recovery." in discard_logic
    assert "still differs from persisted configuration. YAML was not changed." in discard_logic
    assert "restored from persisted configuration. YAML was not changed." in discard_logic
    assert "Runtime recovery validation failed. No runtime settings were changed." in discard_logic
    assert "Your draft is still available." in discard_logic
    assert "settingsPageState.confirmationAction = 'discard'" in discard_logic
    assert "showSettingsLoadState('Confirm restored runtime'" in discard_logic
    assert "settingsPageState.discarding = true" in discard_logic
    assert "settingsPageState.discarding = false" in discard_logic
    assert "requestDashboardRefresh()" in discard_logic


def test_candidate_result_is_cleared_when_connection_draft_state_changes(
    dashboard_html: str,
) -> None:
    input_logic = _source_between(
        dashboard_html,
        "function handleSettingsInput",
        "function buildSettingsPayload",
    )
    reset_logic = _source_between(
        dashboard_html,
        "function stageSettingsDraftChanges",
        "function restoreSettingsDraft",
    )
    restore_logic = _source_between(
        dashboard_html,
        "function restoreSettingsDraft",
        "async function discardSettingsDraft",
    )
    persist_logic = _source_between(
        dashboard_html,
        "async function persistSettings",
        "function initializeSettingsPage",
    )
    confirmation_logic = _source_between(
        dashboard_html,
        "async function confirmSettingsAfterAcceptedUpdate",
        "function stageSettingsDraftChanges",
    )

    assert "if (isConnectionSettingId(settingId)) clearConnectionTestResult()" in input_logic
    assert "changes.some(change => isConnectionSettingId(change.setting.id))" in reset_logic
    assert "settingsPageState.connectionTestResult = null" in reset_logic
    assert "settingsPageState.connectionTestResult = null" in restore_logic
    assert "changes.some(change => isConnectionSettingId(change.setting.id))" in persist_logic
    assert (
        "if (confirmationAction === 'discard') "
        "settingsPageState.connectionTestResult = null"
    ) in confirmation_logic


def test_load_failure_retry_and_malformed_data_paths_fail_safely(dashboard_html: str) -> None:
    load_logic = _source_between(dashboard_html, "async function requestSettingsSnapshot", "function restoreSettingsDraft")

    assert "return validateSettingsSnapshot(payload)" in load_logic
    assert "const persistedDifferences = settingsDifferentFromPersisted().length" in load_logic
    assert "active runtime value" in load_logic
    assert "pending restart or higher-priority override" in load_logic
    assert "showSettingsLoadState('Settings could not be loaded'" in load_logic
    assert "showSettingsPageError(message, false)" in load_logic
    assert "settingsPageState.loaded = false" in load_logic
    assert "Retry loading settings" in dashboard_html
    assert "if (settingsPageState.confirmationRequired) void confirmSettingsAfterAcceptedUpdate()" in dashboard_html
    assert "else void loadSettings()" in dashboard_html
    assert "The settings response format is not supported." in dashboard_html


def test_connection_setting_cards_stack_by_card_width_and_keep_long_content_in_flow(
    dashboard_html: str,
) -> None:
    renderer = _source_between(
        dashboard_html,
        "function createSettingsItem",
        "function settingsValuesEqual",
    )
    assert (
        "if (category.id === CONNECTION_SETTINGS_CATEGORY_ID) "
        "list.classList.add('settings-list-connection')"
    ) in renderer
    assert "category.settings.forEach(setting =>" in renderer
    assert "list.append(createSettingsItem(setting, itemNumber))" in renderer
    assert (
        ".settings-list-connection { container-name:settings-connection; "
        "container-type:inline-size; }"
    ) in dashboard_html
    assert (
        "@container settings-connection (max-width: 480px) { "
        ".settings-item { grid-template-columns:1fr; gap:9px; } }"
    ) in dashboard_html
    assert (
        ".settings-metadata > span { min-width:0; overflow-wrap:anywhere; }"
        in dashboard_html
    )
    assert ".settings-input { width:100%; min-width:0;" in dashboard_html

    difference_index = renderer.index("controlPanel.append(difference)")
    for earlier_content in (
        "controlPanel.append(controlRoot)",
        "controlPanel.append(resetButton)",
        "controlPanel.append(availability)",
        "controlPanel.append(restart)",
    ):
        assert renderer.index(earlier_content) < difference_index
    assert difference_index < renderer.index("controlPanel.append(error)")
    assert difference_index < renderer.index("item.append(metadata, controlPanel)")

    layout_rules = (
        _source_between(dashboard_html, ".settings-list-connection {", ".settings-item {"),
        _source_between(dashboard_html, ".settings-item {", ".settings-item:focus-within"),
        _source_between(
            dashboard_html,
            ".settings-item-meta,.settings-control-panel {",
            ".settings-label-row {",
        ),
        _source_between(dashboard_html, ".settings-metadata {", ".settings-metadata > span {"),
        _source_between(dashboard_html, ".settings-metadata > span {", ".settings-control-panel {"),
        _source_between(dashboard_html, ".settings-control-panel {", ".settings-reset-setting {"),
        _source_between(dashboard_html, ".settings-difference {", ".settings-difference.warning {"),
    )
    for rule in layout_rules:
        assert "position:" not in rule
        assert "height:" not in rule.replace("line-height:", "")
        for overlap_risk in ("grid-area:", "grid-row:", "grid-column:"):
            assert overlap_risk not in rule


def test_settings_responsive_accessibility_and_dashboard_lifecycle_guards(dashboard_html: str) -> None:
    mobile_css = _source_between(
        dashboard_html,
        "@media (max-width: 700px)",
        ".bar {",
    )
    assert ".settings-input:focus-visible,.settings-checkbox:focus-visible" in dashboard_html
    assert ".settings-button:focus-visible" in dashboard_html
    assert ".settings-button:disabled { cursor:not-allowed; opacity:.5" in dashboard_html
    assert ".settings-button.recovery" in dashboard_html
    assert ".settings-reset-setting" in dashboard_html
    assert ".settings-connection-result" in dashboard_html
    assert "@media (max-width: 700px)" in dashboard_html
    assert ".settings-category-header,.settings-connection-test-header { align-items:stretch; flex-direction:column; }" in mobile_css
    assert ".settings-category-header .settings-button,.settings-connection-test-header .settings-button { align-self:flex-start; }" in mobile_css
    assert ".settings-item { grid-template-columns:1fr" in mobile_css
    assert ".settings-connection-result-details { grid-template-columns:1fr" in mobile_css
    assert ".settings-action-bar { align-items:stretch; flex-direction:column" in mobile_css
    assert ".settings-reset-setting,.settings-button.compact { flex:0 0 auto; }" in mobile_css
    assert "@media (prefers-reduced-motion: reduce)" in dashboard_html
    assert ".settings-button,.settings-input { transition:none; }" in dashboard_html
    assert ".settings-button:hover:not(:disabled) { transform:none; }" in dashboard_html
    assert dashboard_html.count("setInterval(") == 1
    assert "clearInterval(dashboardRefreshTimer)" in dashboard_html
    assert "scheduleDashboardRefresh(data.refresh_interval_ms)" in dashboard_html
    assert "setText('opsLastRefreshDetail', 'Every ' + dashboardRefreshIntervalMs + ' ms')" in dashboard_html
    assert "if (refreshInFlight)" in dashboard_html
    assert "refreshAfterCurrent = true" in dashboard_html
    assert dashboard_html.count("initializeSettingsPage();") == 1
    assert "form.addEventListener('input', handleSettingsInput)" in dashboard_html
    assert "if (focusSummary && settingsPageIsActive()) summary.focus()" in dashboard_html
