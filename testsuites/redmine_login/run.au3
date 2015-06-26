#include <IE.au3>

Local $oIE = _IECreate("https://redmine.magenta-aps.dk/")
If @error Then
    Exit @error
EndIf

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

_IEAction($oLinkElem, "click")
_FailIfError()

_IELoadWait ($oIE)
_FailIfError()

MsgBox(0, "Notice", "Success")
_IEQuit($oIE)
