# ContextKeeper

ContextKeeper is a transparent, Ollama-compatible middleware layer that sits between AI clients and Ollama.

Clients connect to ContextKeeper instead of Ollama. ContextKeeper proxies requests, preserves streaming, logs diagnostics, exposes system metrics, and provides a local operations dashboard.

## Current Status

Local Windows product foundation.

Implemented:

- FastAPI server
- Ollama-compatible passthrough for `/api/*` and `/v1/*`
- Streaming response preservation
- YAML configuration
- Structured logging with levels including OFF
- Request metrics
- Basic system metrics for CPU/RAM
- Optional NVIDIA GPU/VRAM metrics through `nvidia-smi`
- Basic dashboard
- Dashboard intelligence panels
- Windows executable and installer foundation
- First-run configuration wizard
- Pytest smoke tests

## Roadmap and Future Vision

The approved Version 1 direction is focused on a production-quality local release: transparent Ollama-compatible proxy behavior, automatic context management, rolling summaries, context-window discovery, retrievable historical memory after compression, dashboard visibility, validation/AutoQA, Windows service and packaging, and release-quality documentation. Some of this work remains planned; the implemented list above is the current feature summary.

The product direction is to compress active context without forgetting important information. Compression should reduce prompt size, while historical conversation details remain available for retrieval when relevant.

Long-term v2+ ideas are tracked in [docs/FUTURE_IDEAS.md](docs/FUTURE_IDEAS.md). That document is planning direction, not a feature commitment.

## Quick Start

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m ctxkeeper.main
```

On first launch, ContextKeeper creates `contextkeeper.yaml` through an
interactive configuration wizard if the file does not exist. To rerun the
wizard later:

```powershell
python -m ctxkeeper.main --configure
```

Open:

```text
http://localhost:11500/dashboard
```

Test Ollama passthrough:

```powershell
Invoke-RestMethod http://localhost:11500/api/tags
```

## Building a Windows Executable

The first-stage standalone executable build uses PyInstaller.

```powershell
python -m pip install -e ".[build]"
pyinstaller contextkeeper.spec
```

The executable is written to:

```text
dist/ContextKeeper.exe
```

`contextkeeper.yaml` is bundled as a fallback resource. For packaged runs,
place an editable `contextkeeper.yaml` beside `ContextKeeper.exe` to override
the bundled default. Source runs continue to load `contextkeeper.yaml` from the
current working directory.

## Building a Windows Installer

The installer foundation uses Inno Setup and expects the PyInstaller executable
to exist first.

```powershell
.\scripts\build_release.ps1
```

The release script runs preflight checks, builds `dist/ContextKeeper.exe`,
builds `dist/installer/ContextKeeperSetup.exe`, and copies user-facing release
files into `dist/`. Service installation hooks are placeholders and will be
implemented in a later phase.

## Important

The product is called **ContextKeeper**, but the Python package is named `ctxkeeper` to avoid conflict with an unrelated PyPI package named `contextkeeper`.
