# ContextKeeper Installer

This folder contains the first-stage Inno Setup installer foundation.

## Prerequisites

- Build `dist/ContextKeeper.exe` with PyInstaller first.
- Install Inno Setup on the build machine.

## Build

Open `ContextKeeper.iss` in Inno Setup Compiler and build the script, or run:

```powershell
ISCC.exe installer\ContextKeeper.iss
```

The installer output is configured for:

```text
dist/installer/ContextKeeperSetup.exe
```

Service installation and uninstall cleanup are placeholders for a later phase.
