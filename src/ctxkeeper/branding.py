"""Central product metadata for ContextKeeper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ProductInfo:
    """Release and branding metadata used across runtime and packaging."""

    name: str
    version: str
    description: str
    company: str
    copyright: str
    release_channel: str
    build_timestamp: str


PRODUCT_NAME = "ContextKeeper"
VERSION = "0.1.0"
DESCRIPTION = "Transparent Ollama proxy with diagnostics and dashboard."
COMPANY = "ContextKeeper Project"
COPYRIGHT = "Copyright (c) ContextKeeper Project"
RELEASE_CHANNEL = "local"
BUILD_TIMESTAMP = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

PRODUCT_INFO = ProductInfo(
    name=PRODUCT_NAME,
    version=VERSION,
    description=DESCRIPTION,
    company=COMPANY,
    copyright=COPYRIGHT,
    release_channel=RELEASE_CHANNEL,
    build_timestamp=BUILD_TIMESTAMP,
)
