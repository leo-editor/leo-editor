
!addincludedir c:\leo.repo\trunk\leo\dist

!include MUI2.nsh
!include nsDialogs.nsh
!include LogicLib.nsh

;##version
!define version         "4.10-final"

; These are *not* Python strings--backslashes are fine.

!define app_icon        "leo\Icons\LeoApp.ico"
!define doc_icon        "leo\Icons\LeoDoc.ico"
!define ext             ".leo"
;!define install_icon    "c:\leo.repo\trunk\leo\Icons\leo_inst.ico" ; Doesn't work
!define leo_hklm        "SOFTWARE\EKR\Leo"
!define license         "License.txt"
!define name            "Leo"
!define publisher       "Edward K. Ream"
!define site            "http://webpages.charter.net/edreamleo/front.html"
!define target_file     "LeoSetup-${version}.exe"
!define uninst_key      "Software\Microsoft\Windows\CurrentVersion\Uninstall\leo"

!include nsi-boilerplate.txt
