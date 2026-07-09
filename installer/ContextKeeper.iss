; ContextKeeper Inno Setup installer foundation.
; TODO: Keep version metadata aligned with the Python package release process.

#define MyAppName "ContextKeeper"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "ContextKeeper Project"
#define MyAppExeName "ContextKeeper.exe"

[Setup]
AppId={{1F7ED80C-5C14-4F0D-96C8-C4DE37D9A3B4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=ContextKeeper local Ollama proxy and dashboard installer
VersionInfoProductName={#MyAppName}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=..\dist\installer
OutputBaseFilename=ContextKeeperSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
Source: "..\dist\ContextKeeper.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\contextkeeper.yaml"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\scripts\install_service.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion
Source: "..\scripts\uninstall_service.ps1"; DestDir: "{app}\scripts"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; TODO: a future installer step should invoke scripts\install_service.ps1 when service installation is implemented.
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; TODO: a future installer step should invoke scripts\uninstall_service.ps1 before files are removed.

[UninstallDelete]
; TODO: a future installer step should define opt-in cleanup for generated logs/data/config if required.
