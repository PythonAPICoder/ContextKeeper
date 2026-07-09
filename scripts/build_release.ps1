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
$PyInstallerSpec = Join-Path $ProjectRoot "contextkeeper.spec"
$ReadmePath = Join-Path $ProjectRoot "README.md"
$LicensePath = Join-Path $ProjectRoot "installer\LICENSE.txt"
$DefaultConfigPath = Join-Path $ProjectRoot "contextkeeper.yaml"

function Write-Section {
    param([Parameter(Mandatory = $true)][string]$Title)

    Write-Host ""
    Write-Host "== $Title =="
}

function Test-RequiredFile {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Description
    )

    if (-not (Test-Path $Path)) {
        Write-Error "$Description was not found: $Path"
        exit 1
    }
}

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

Write-Section "Preflight"
Test-RequiredFile -Path $PyInstallerSpec -Description "PyInstaller spec file"
Test-RequiredFile -Path $InstallerScript -Description "Inno Setup installer script"
Test-RequiredFile -Path $ReadmePath -Description "Project README"
Test-RequiredFile -Path $LicensePath -Description "Installer license"
$InnoSetupCompiler = Find-InnoSetupCompiler
if (-not $InnoSetupCompiler) {
    Write-Error "Inno Setup compiler (ISCC.exe) was not found. Install Inno Setup and ensure ISCC.exe is on PATH or installed in the default location."
    exit 1
}
Write-Host "PyInstaller spec: $PyInstallerSpec"
Write-Host "Inno Setup script: $InstallerScript"
Write-Host "Inno Setup compiler: $InnoSetupCompiler"

Write-Section "Cleanup"
Remove-GeneratedArtifacts

Write-Section "Executable"
Write-Host "Building ContextKeeper executable with PyInstaller..."
pyinstaller $PyInstallerSpec

if (-not (Test-Path $ExecutablePath)) {
    Write-Error "Expected executable was not created: $ExecutablePath"
    exit 1
}

Write-Section "Installer"
Write-Host "Building ContextKeeper installer with Inno Setup..."
& $InnoSetupCompiler $InstallerScript

if (-not (Test-Path $InstallerPath)) {
    Write-Error "Expected installer was not created: $InstallerPath"
    exit 1
}

Write-Section "Release Files"
Copy-Item -LiteralPath $ReadmePath -Destination (Join-Path $DistDir "README.md") -Force
Copy-Item -LiteralPath $LicensePath -Destination (Join-Path $DistDir "LICENSE.txt") -Force
if (Test-Path $DefaultConfigPath) {
    Copy-Item -LiteralPath $DefaultConfigPath -Destination (Join-Path $DistDir "contextkeeper.yaml") -Force
}
Write-Host "Copied README, license, and default configuration when available."

Write-Section "Summary"
Write-Host "Release build complete."
Write-Host "Executable: $ExecutablePath"
Write-Host "Installer:   $InstallerPath"
Write-Host "Release dir: $DistDir"
