#include <GUIConstantsEx.au3>
#include <EditConstants.au3>
#include "appmonitor.au3"

Opt("GUIOnEventMode", 1) ; Change to OnEvent mode

Local $hMainGUI = GUICreate("Crypt Tool", 300, 150)
GUISetOnEvent($GUI_EVENT_CLOSE, "CLOSEButton")
GUICtrlCreateLabel("Input pharse to be encrypted", 0, 0)
Local $iEncryptButton = GUICtrlCreateButton("Encrypt", 120, 120, 60)
GUICtrlSetOnEvent($iEncryptButton, "EncryptButton")
Local $g_idInputEdit = GUICtrlCreateEdit("", 0, 20, 300, 20, $ES_WANTRETURN)
Local $g_idOutputEdit = GUICtrlCreateEdit("", 0, 45, 300, 70, $ES_READONLY)

GUISetState(@SW_SHOW, $hMainGUI)

While 1
    Sleep(100) ; Sleep to reduce CPU usage
WEnd

Func EncryptButton()
    Local $sRead = GUICtrlRead($g_idInputEdit)
    If $sRead <> "" Then
        Local $sHexEncrypted = AppmonitorEncrypt($sRead)
        GUICtrlSetData($g_idOutputEdit, $sHexEncrypted)
    EndIf
EndFunc   ;==>OKButton

Func CLOSEButton()
    Exit
EndFunc   ;==>CLOSEButton
