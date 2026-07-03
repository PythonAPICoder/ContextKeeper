from ctxkeeper.config import Settings


def test_default_settings_load() -> None:
    settings = Settings()
    assert settings.app.name == "ContextKeeper"
    assert settings.server.port == 11500
