<#
Build the ContextKeeper executable and installer release artifacts.

Generated artifacts are removed from the top-level build and dist directories.
Source scripts live under scripts and are not part of the cleanup target.
#>

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BuildDir = Join-Path $ProjectRoot "build"
$DistDir = Join-Path $ProjectRoot "dist"
$ExecutablePath = Join-Path $DistDir "ContextKeeper.exe"
$InstallerPath = Join-Path $DistDir "installer\ContextKeeperSetup.exe"
$InstallerScript = Join-Path $ProjectRoot "installer\ContextKeeper.iss"

function Remove-GeneratedArtifacts {
    Write-Host "Cleaning previous generated build artifacts..."

    $artifactDirs = @($BuildDir, $DistDir)
    foreach ($directory in $artifactDirs) {
        if (Test-Path $directory) {
            $resolvedDirectory = (Resolve-Path $directory).Path
            $resolvedProjectRoot = (Resolve-Path $ProjectRoot).Path

            if (-not $resolvedDirectory.StartsWith($resolvedProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw "Refusing to remove path outside project root: $resolvedDirectory"
            }

            Remove-Item -LiteralPath $resolvedDirectory -Recurse -Force
        }
    }
}

function Find-InnoSetupCompiler {
    $command = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidatePaths = @(
        "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
        "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
    )

    foreach ($path in $candidatePaths) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }

    return $null
}

Set-Location $ProjectRoot

Remove-GeneratedArtifacts

Write-Host "Building ContextKeeper executable with PyInstaller..."
pyinstaller contextkeeper.spec

if (-not (Test-Path $ExecutablePath)) {
    Write-Error "Expected executable was not created: $ExecutablePath"
    exit 1
}

$InnoSetupCompiler = Find-InnoSetupCompiler
if (-not $InnoSetupCompiler) {
    Write-Error "Inno Setup compiler (ISCC.exe) was not found. Install Inno Setup and ensure ISCC.exe is on PATH or installed in the default location."
    exit 1
}

Write-Host "Building ContextKeeper installer with Inno Setup..."
& $InnoSetupCompiler $InstallerScript

if (-not (Test-Path $InstallerPath)) {
    Write-Error "Expected installer was not created: $InstallerPath"
    exit 1
}

Write-Host ""
Write-Host "Release build complete."
Write-Host "Executable: $ExecutablePath"
Write-Host "Installer:   $InstallerPath"
