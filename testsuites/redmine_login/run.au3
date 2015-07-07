#include <IE.au3>
#include "..\autoit_include\appmonitor.au3"

local $iMeasureID = CreateMeasure("Start IE")
Local $oIE = _IECreate("https://redmine.magenta-aps.dk/")
If @error Then
    Exit @error
EndIf
CompleteMeasure($iMeasureID)

Func _ExitWithError()
    _IEQuit($oIE)
    MsgBox(0, "Notice", "Exiting with status: " & @error)
    Exit @error
EndFunc

Func _FailIfError()
    If @error Then
        _ExitWithError(@error)
    EndIf
EndFunc

Local $oAccountDiv = _IEGetObjById($oIE, "account")
_FailIfError()

Local $oLinkElem = _IETagNameGetCollection($oAccountDiv, "a").Item(0)
_FailIfError()

$iMeasureID = CreateMeasure("Navigate to login page")
_IEAction($oLinkElem, "click")
_FailIfError()

_IELoadWait ($oIE)
_FailIfError()

Local $oUsernameField = _IEGetObjById($oIE, "username")
_FailIfError()
CompleteMeasure($iMeasureID)

MsgBox(0, "Notice", "Success")
_IEQuit($oIE)
