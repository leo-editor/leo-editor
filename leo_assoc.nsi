;@+leo-ver=5-thin
;@+node:ekr.20160510090441.1: * @file ../../leo_assoc.nsi
;@@language nsi

;##version
!define version         "5.7.1"

!include MUI2.nsh
!include nsDialogs.nsh
!include LogicLib.nsh

; Globals.
Var PythonDirectory
    ; Directory containing Python.exe
Var PythonExe
    ; "python.exe" or "pythonw.exe"
Var PythonExecutable
    ; $PythonDirectory/$PythonExe

!define app_icon        "leo\Icons\LeoApp.ico"
!define doc_icon        "leo\Icons\LeoDoc.ico"
!define ext             ".leo"
!define leo_hklm        "SOFTWARE\EKR\Leo"
!define license         "LICENSE"
!define name            "Leo"
!define publisher       "Edward K. Ream"
!define site            "http://leoeditor.com/"
!define target_file     "LeoAssoc.exe"
!define uninst_key      "Software\Microsoft\Windows\CurrentVersion\Uninstall\leo"

; Locations
Name "Leo Associations"
OutFile "LeoAssoc.exe"
InstallDir "$PROGRAMFILES\Leo-${version}"

; Icons
!define MUI_ICON "${app_icon}"

;@+<< assoc prolog >>
;@+node:ekr.20160510090943.1: ** << assoc prolog >>


!addincludedir C:\leo.repo\leo-editor\leo\dist

; Boilerplate
SetCompressor bzip2
Caption "Leo File Associations Installer"
AutoCloseWindow false 
SilentInstall normal
CRCCheck on
SetCompress auto
SetDatablockOptimize on
WindowIcon on
ShowInstDetails show
ShowUnInstDetails show
;@-<< assoc prolog >>
;@+<< assoc pages >>
;@+node:ekr.20160510091130.1: ** << assoc pages >>
;@@language nsi

Var StartMenuFolder

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE       ${license}
!insertmacro MUI_PAGE_COMPONENTS

; Define these here so the back button works.
!define MUI_PAGE_HEADER_TEXT "Choose Installed Location"
!define MUI_PAGE_HEADER_SUBTEXT "Choose the folder in which Leo has been installed."
!define MUI_DIRECTORYPAGE_TEXT_TOP "Setup installs file associations for Leo in the Windows registry."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Select the top-level leo-editor Folder"
!insertmacro MUI_PAGE_DIRECTORY

; It's so easy: just set these *before* creating another directory page!
!define MUI_PAGE_HEADER_TEXT "Choose Python Location"
!define MUI_PAGE_HEADER_SUBTEXT "Select the top-level Python directory"
!define MUI_DIRECTORYPAGE_TEXT_TOP "Choose the top-level Python folder."
!define MUI_DIRECTORYPAGE_TEXT_DESTINATION "Python Folder"
!define MUI_DIRECTORYPAGE_VARIABLE $PythonDirectory
!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_STARTMENU "Application" $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; ----- uninstaller pages -----

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_DIRECTORY
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH
;@-<< assoc pages >>
;@+others
;@+node:ekr.20160510093344.1: ** LeoAssoc
; The name of this section must be "Leo".
Section "LeoAssoc" SEC01
    ; This section is required, but does not need any contents.
    ; It must have the name of the .exe file.
SectionEnd
;@+node:ekr.20160510093411.1: ** Section FileAssociation
Section "${ext} File Association" SEC02
    MessageBox MB_YESNO "Launch Leo in Python console? (recommended for Python 3)" IDYES true IDNO false
    true:
        StrCpy $PythonExe "python.exe"
        goto next
    false:
        StrCpy $PythonExe "pythonw.exe"
    next:
    StrCpy $PythonExecutable "$PythonDirectory\$PythonExe"
        ; Set for all other sections.
    SectionIn 1 2 3 4
    WriteRegStr HKCR "${ext}" "" "Leo File"
    WriteRegStr HKCR "LeoFile" "" "Leo File"
    WriteRegStr HKCR "LeoFile\shell" "" "open"
    ; The single quotes below appear to be required.
    WriteRegStr HKCR "LeoFile\DefaultIcon" "" '"$INSTDIR\${app_icon}"'
        ; https://github.com/leo-editor/leo-editor/issues/24
    WriteRegStr HKCR "LeoFile\shell\open\command" "" '"$PythonExecutable" "$INSTDIR\launchLeo.py %*"'
SectionEnd
;@+node:ekr.20160510093822.1: ** Section Desktop Shortcut

Section "Leo Desktop Shortcut" SEC03
  ; This sets the "Start in folder" box!!!"
  SetOutPath "$INSTDIR\leo"
  ;This is **tricky**.  We need single quotes to handle paths containing spaces.
  ;Add single quotes around PythonExecutable and launchLeo.py args, but *not* the app_icon arg.
  CreateShortCut "$DESKTOP\Leo.lnk" '"$PythonExecutable"' '"$INSTDIR\launchLeo.py"' "$INSTDIR\${app_icon}"
SectionEnd
;@+node:ekr.20160510093859.1: ** Section Start Menu

Section "Leo Start Menu" SEC04
  ; This is **tricky**.
  ; We need single quotes to handle paths containing spaces.
  ; Add single quotes around PythonExecutable and launchLeo.py args,
  ; but *not* the app_icon arg.
  CreateShortCut "$SMPROGRAMS\Leo\Leo.lnk" '"$PythonExecutable"' '"$INSTDIR\launchLeo.py"' "$INSTDIR\${app_icon}"
  CreateShortCut "$SMPROGRAMS\Leo\Uninstall.lnk" '"$INSTDIR\uninst.exe"'
SectionEnd
;@+node:ekr.20160510095724.1: ** Section Uninstall

Section Uninstall
    DeleteRegKey HKLM "${leo_hklm}"
    DeleteRegKey HKCR "${ext}"
    DeleteRegKey HKCR "LeoFile"
    ; Remove links.
    Delete "$SMPROGRAMS\Leo\Uninstall.lnk"
    Delete "$SMPROGRAMS\Leo.lnk"
    Delete "$DESKTOP\Leo.lnk"
    DeleteRegKey HKLM "${uninst_key}" 
    SetAutoClose false

SectionEnd ; end Uninstall section
;@+node:ekr.20160510095711.1: ** Section -Post

Section -Post
  WriteRegStr HKLM ${leo_hklm} "" "$INSTDIR"
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${uninst_key}" "DisplayName" "Leo File Associations (remove only)"
  WriteRegStr HKLM "${uninst_key}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${uninst_key}" "DisplayVersion" "Leo File Associations"
  WriteRegStr HKLM "${uninst_key}" "URLInfoAbout" "${site}"
  WriteRegStr HKLM "${uninst_key}" "Publisher" "${publisher}"
SectionEnd
;@-others
; Language should follow pages.
!insertmacro MUI_LANGUAGE "English"
;@-leo
