from ctxkeeper import __app_name__, __version__
from ctxkeeper.app import create_app
from ctxkeeper.branding import DESCRIPTION, PRODUCT_INFO, PRODUCT_NAME, VERSION
from ctxkeeper.config import Settings


def test_branding_module_is_single_source_for_public_metadata() -> None:
    assert PRODUCT_INFO.name == PRODUCT_NAME == "ContextKeeper"
    assert PRODUCT_INFO.version == VERSION == "0.1.0"
    assert PRODUCT_INFO.description == DESCRIPTION
    assert PRODUCT_INFO.company
    assert PRODUCT_INFO.release_channel
    assert __app_name__ == PRODUCT_NAME
    assert __version__ == VERSION


def test_fastapi_app_uses_product_metadata() -> None:
    app = create_app(Settings())

    assert app.title == PRODUCT_NAME
    assert app.version == VERSION
    assert app.description == DESCRIPTION
