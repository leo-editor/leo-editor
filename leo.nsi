;@+leo-ver=5-thin
;@+node:ekr.20101027054254.1590: * @file ../../leo.nsi
;@@language nsi

;@+<< defines >>
;@+node:ekr.20161017094430.1: ** << defines >>
;;; This doesn't work.
;;; !addincludedir C:\leo.repo\leo-editor\leo\dist

!include MUI2.nsh
!include nsDialogs.nsh
!include LogicLib.nsh

;##version
!define version         "5.7.1"

; These are *not* Python strings--backslashes are fine.

!define app_icon        "leo\Icons\LeoApp.ico"
!define doc_icon        "leo\Icons\LeoDoc.ico"
; This works, but the icon is too small.
;!define icon            "C:\leo.repo\trunk\leo\Icons\SplashScreen.ico"
!define ext             ".leo"
!define leo_hklm        "SOFTWARE\EKR\Leo"
!define license         "LICENSE"
!define name            "Leo"
!define publisher       "Edward K. Ream"
!define site            "http://leoeditor.com/"
!define target_file     "LeoSetup-${version}.exe"
!define uninst_key      "Software\Microsoft\Windows\CurrentVersion\Uninstall\leo"
;@-<< defines >>

;;; !include nsi-boilerplate.txt

; RequestExecutionLevel highest
; RequestExecutionLevel admin

;@+<< prolog >>
;@+node:ekr.20161017094235.2: ** << prolog >>
; Globals.
Var PythonDirectory
    ; Directory containing Pythonw.exe
    ; Set by onInit.  May be set in Python Directory page.

!define PythonExecutable "$PythonDirectory\pythonw.exe"
    ;;; Always use pythonw.exe here.
    ;;; To debug, set the target to python.exe in the desktop icon properties.

!addincludedir C:\leo.repo\leo-editor\leo\dist

; Boilerplate
SetCompressor bzip2
Caption "${name}-${version} Installer"
AutoCloseWindow false 
SilentInstall normal
CRCCheck on
SetCompress auto
SetDatablockOptimize on
WindowIcon on
ShowInstDetails show
ShowUnInstDetails show

; Locations
Name "${name}"
OutFile "${target_file}"
InstallDir "$PROGRAMFILES\${name}-${version}"

; Icons
!define MUI_ICON "${app_icon}"
;@-<< prolog >>
;@+<< pages >>
;@+node:ekr.20161017094235.3: ** << pages >>
;@@language nsi

Var StartMenuFolder

; Define the TEXT_TOP for both the MUI_PAGE_DIRECTORY pages.
; "${s1a} ${s2} ${s3}" is the TEXT_TOP for the Install Location page.
; "${s2b} ${s2} ${s3}" is the TEXT_TOP for the Choose Python Folder page.
!define s1a "Setup will install ${name} in the following folder."
!define s1b "Setup will use the following folder as the Python location."
!define s2 "To install in a different folder, click Browse and select another folder."
!define s3 "Click next to continue."

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE       ${license}
!insertmacro MUI_PAGE_COMPONENTS

; These are the defaults, but defined them here so the back button works.
!define MUI_PAGE_HEADER_TEXT "Choose Install Location"
!define MUI_PAGE_HEADER_SUBTEXT "Choose the folder in which to install ${name}"
!define MUI_DIRECTORYPAGE_TEXT_TOP "${s1a} ${s2} ${s3}"
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Destination Folder"
!insertmacro MUI_PAGE_DIRECTORY

; It's so easy: just set these *before* creating another directory page!
!define MUI_PAGE_HEADER_TEXT "Choose Python Location"
!define MUI_PAGE_HEADER_SUBTEXT "Select the top-level Python directory"
!define MUI_DIRECTORYPAGE_TEXT_TOP "${s1b} ${s2} ${s3}"
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Python Folder"
!define MUI_DIRECTORYPAGE_VARIABLE $PythonDirectory
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_STARTMENU     "Application" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; ----- uninstaller pages -----

!insertmacro MUI_UNPAGE_WELCOME
; !insertmacro MUI_UNPAGE_LICENSE   ${license}
; !insertmacro MUI_UNPAGE_CONFIRM
; !insertmacro MUI_UNPAGE_COMPONENTS ; doesn't actually list components.
!insertmacro MUI_UNPAGE_DIRECTORY
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
;@-<< pages >>

; Language should follow pages.
!insertmacro MUI_LANGUAGE "English"

; The order of sections *does* matter slightly.
; It determines the order of items in the components dialog.
; It may also have some other very subtle effects.

;@+others
;@+node:ekr.20161017094235.4: ** onInit

; Set PythonDirectory to the top-level Python path.
; For now, prefer Python 2.x to Python 3.x.
Function .onInit
    ;try27:
        SetRegView 64
        ReadRegStr $9 HKLM Software\Python\PythonCore\2.7\InstallPath ""
        StrCmp $9 "" try26 ok
    try26:
        ReadRegStr $9 HKLM SOFTWARE\Python\PythonCore\2.6\InstallPath ""
        StrCmp $9 "" try35 ok
    try35:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.5\InstallPath ""
        StrCmp $9 "" try34 ok
    try34:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.4\InstallPath ""
        StrCmp $9 "" try33 ok
    try33:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.3\InstallPath ""
        StrCmp $9 "" try32 ok
    try32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.2\InstallPath ""
        StrCmp $9 "" try31 ok
    try31:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.1\InstallPath ""
        StrCmp $9 "" try30 ok
    try30:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.0\InstallPath ""
        StrCmp $9 "" tryReg32 ok
    ; Entries not found in 64-bit registry: try 32-bit registry...
    tryReg32:
        SetRegView 32
        ReadRegStr $9 HKLM Software\Python\PythonCore\2.7\InstallPath ""
        StrCmp $9 "" try26_32 ok
    try26_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\2.6\InstallPath ""
        StrCmp $9 "" try35_32 ok
    try35_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.5\InstallPath ""
        StrCmp $9 "" try34_32 ok
    try34_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.4\InstallPath ""
        StrCmp $9 "" try33_32 ok
    try33_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.3\InstallPath ""
        StrCmp $9 "" try32_32 ok
    try32_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.2\InstallPath ""
        StrCmp $9 "" try31_32 ok
    try31_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.1\InstallPath ""
        StrCmp $9 "" try30_32 ok
    try30_32:
        ReadRegStr $9 HKLM Software\Python\PythonCore\3.0\InstallPath ""
        StrCmp $9 "" oops ok
    oops:
        MessageBox MB_OK "Python not found"
        StrCpy $PythonDirectory ""
        Goto done
    ok:
        StrCpy $PythonDirectory $9
    done:
FunctionEnd ; End .onInit
;@+node:ekr.20161017094235.5: ** Section Leo

; The name of this section must be "Leo".
Section "Leo" SEC01
    ; Add all files and directories.
    ; The make-leo button creates nsi-install-files.txt.
    !include nsi-install-files.txt
SectionEnd
;@+node:ekr.20161017094235.6: ** Section File Association

Section "${ext} File Association" SEC02
    SectionIn 1 2 3 4
    WriteRegStr HKCR "${ext}" "" "${name}File"
    WriteRegStr HKCR "${name}File" "" "${name} File"
    WriteRegStr HKCR "${name}File\shell" "" "open"
    ; The single quotes below appear to be required.
    WriteRegStr HKCR "${name}File\DefaultIcon" "" '"$INSTDIR\${app_icon}"'
    ; https://github.com/leo-editor/leo-editor/issues/24
    WriteRegStr HKCR "${name}File\shell\open\command" "" '"${PythonExecutable}" "$INSTDIR\launchLeo.py %*"'
SectionEnd
;@+node:ekr.20161017094235.7: ** Section Desktop Shortcut

Section "${name} Desktop Shortcut" SEC03
  ; This sets the "Start in folder" box!!!"
  SetOutPath "$INSTDIR\leo"
  ;;; This is **tricky**.  We need single quotes to handle paths containing spaces.
  ;;; Add single quotes around PythonExecutable and launchLeo.py args, but *not* the app_icon arg.
  CreateShortCut "$DESKTOP\${name}.lnk" '"${PythonExecutable}"' '"$INSTDIR\launchLeo.py"' "$INSTDIR\${app_icon}"
SectionEnd
;@+node:ekr.20161017094235.8: ** Section Start Menu

Section "${name} Start Menu" SEC04
  CreateDirectory "$SMPROGRAMS\${name}"
  ;;; This is **tricky**.  We need single quotes to handle paths containing spaces.
  ;;; Add single quotes around PythonExecutable and launchLeo.py args, but *not* the app_icon arg.
  CreateShortCut "$SMPROGRAMS\${name}\${name}.lnk" '"${PythonExecutable}"' '"$INSTDIR\launchLeo.py"' "$INSTDIR\${app_icon}"
  CreateShortCut "$SMPROGRAMS\${name}\Uninstall.lnk" '"$INSTDIR\uninst.exe"'
SectionEnd
;@+node:ekr.20161017094235.9: ** Section -Post

Section -Post
  WriteRegStr HKLM ${leo_hklm} "" "$INSTDIR"
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${uninst_key}" "DisplayName" "${name}-${version} (remove only)"
  WriteRegStr HKLM "${uninst_key}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${uninst_key}" "DisplayVersion" "${version}"
  WriteRegStr HKLM "${uninst_key}" "URLInfoAbout" "${site}"
  WriteRegStr HKLM "${uninst_key}" "Publisher" "${publisher}"
SectionEnd
;@+node:ekr.20161017094235.10: ** Section Uninstall

Section Uninstall

    DeleteRegKey HKLM "${leo_hklm}"
    DeleteRegKey HKCR "${ext}"
    DeleteRegKey HKCR "${name}File"
    ; Safely removes all files and directories, including $INSTDIR.
    ; The make-leo button creates nsi-uninstall-files.txt.
    !include nsi-uninstall-files.txt
    ; Remove links.
    Delete "$SMPROGRAMS\${name}\Uninstall.lnk"
    Delete "$SMPROGRAMS\${name}.lnk"
    ; RMDir  "$SMPROGRAMS\${name}-${version}"
    RMDir  "$SMPROGRAMS\${name}"
    Delete "$DESKTOP\${name}.lnk"
    DeleteRegKey HKLM "${uninst_key}" 
    SetAutoClose false

SectionEnd ; end Uninstall section
;@-others
;@-leo
