# ContextKeeper

ContextKeeper is a transparent, Ollama-compatible middleware layer that sits between AI clients and Ollama.

Clients connect to ContextKeeper instead of Ollama. ContextKeeper proxies requests, preserves streaming, logs diagnostics, exposes system metrics, and provides a dashboard foundation for future context management.

## Current Status

Phase 1 clean repository starter.

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
- Pytest smoke tests

## Quick Start

```powershell
python -m pip install -r requirements.txt
python -m pip install -e .
python -m ctxkeeper.main
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

## Important

The product is called **ContextKeeper**, but the Python package is named `ctxkeeper` to avoid conflict with an unrelated PyPI package named `contextkeeper`.
