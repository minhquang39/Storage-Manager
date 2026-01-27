; Storage Manager Installer Script
; For Inno Setup (https://jrsoftware.org/isinfo.php)
;
; This creates a professional Windows installer with:
; - Start Menu shortcut
; - Desktop shortcut (optional)
; - Uninstaller
; - Version information
;
; Usage:
; 1. Build executable first: python build_exe.py
; 2. Open this file in Inno Setup
; 3. Build → Compile
; 4. Installer will be in Output/ folder

[Setup]
; App information
AppName=Storage Manager
AppVersion=2.0
AppPublisher=Your Name
AppPublisherURL=https://github.com/YOUR_USERNAME/storage-manager
AppSupportURL=https://github.com/YOUR_USERNAME/storage-manager/issues
AppUpdatesURL=https://github.com/YOUR_USERNAME/storage-manager/releases

; Default installation directory
DefaultDirName={autopf}\StorageManager
DefaultGroupName=Storage Manager

; Output settings
OutputDir=Output
OutputBaseFilename=StorageManager-Setup-v2.0
SetupIconFile=icon.ico
; Uncomment above if you have icon.ico

; Compression
Compression=lzma2/max
SolidCompression=yes

; Privileges
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; UI
WizardStyle=modern
DisableWelcomePage=no

; Uninstaller
UninstallDisplayIcon={app}\StorageManager.exe
UninstallDisplayName=Storage Manager

; License (optional)
; LicenseFile=LICENSE
; InfoBeforeFile=README.md

; System requirements
MinVersion=10.0.17763

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
; Main executable
Source: "dist\StorageManager.exe"; DestDir: "{app}"; Flags: ignoreversion

; Additional files
Source: "dist\README.txt"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README.txt"
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "README-Dev.md"
; Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu shortcut
Name: "{group}\Storage Manager"; Filename: "{app}\StorageManager.exe"
Name: "{group}\Readme"; Filename: "{app}\README.txt"
Name: "{group}\Uninstall Storage Manager"; Filename: "{uninstallexe}"

; Desktop shortcut (optional)
Name: "{autodesktop}\Storage Manager"; Filename: "{app}\StorageManager.exe"; Tasks: desktopicon

[Run]
; Option to run after installation
Filename: "{app}\StorageManager.exe"; Description: "Launch Storage Manager"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Custom welcome message
function InitializeSetup(): Boolean;
begin
  Result := True;
  MsgBox('Storage Manager v2.0' + #13#10 + 
         #13#10 +
         'This will install a system-wide file scanner that helps you find and remove large files.' + #13#10 +
         #13#10 +
         'System folders (Windows, Program Files, AppData) are automatically protected.' + #13#10 +
         #13#10 +
         'All deletions go to Recycle Bin (safe and reversible).',
         mbInformation, MB_OK);
end;

// Custom finish message
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Installation complete
  end;
end;
