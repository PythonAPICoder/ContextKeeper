# ContextKeeper Installer

This folder contains the first-stage Inno Setup installer foundation.

## Prerequisites

- Build `dist/ContextKeeper.exe` with PyInstaller first.
- Install Inno Setup on the build machine.

## Build

The recommended way to build a release is to run:

```powershell
.\scripts\build_release.ps1
```

The script runs preflight checks for `contextkeeper.spec`,
`installer/ContextKeeper.iss`, and `ISCC.exe`; cleans prior generated
artifacts; runs PyInstaller; verifies `dist/ContextKeeper.exe`; and builds the
Inno Setup installer.

For manual installer-only builds, open `ContextKeeper.iss` in Inno Setup
Compiler and build the script, or run:

```powershell
ISCC.exe installer\ContextKeeper.iss
```

## Output

The release script writes:

```text
dist/ContextKeeper.exe
dist/installer/ContextKeeperSetup.exe
```

## Notes

Service installation and uninstall cleanup are placeholders for a later phase.
