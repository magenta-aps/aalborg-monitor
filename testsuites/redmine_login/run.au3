#include "..\..\lib\autoit\appmonitor.au3"

; Utility methods

; Actual test-case
AppmonitorCreateMeasure("Start IE")
$oIE = _IECreate("https://redmine.magenta-aps.dk/")
If @error Then
    Exit @error
EndIf

; Shut down IE when program exits
AppmonitorRegisterIEShutdown($oIE)

Local $oAccountDiv = AppmonitorWaitForId($oIE, "account")
AppmonitorCheckCurrentMeasure(@error)
Local $oLinkElem = _IETagNameGetCollection($oAccountDiv, "a").Item(0)
AppmonitorCheckCurrentMeasure(@error)
AppmonitorCompleteMeasure()

AppmonitorCreateMeasure("Navigate to login page")
_IEAction($oLinkElem, "click")
AppmonitorCheckCurrentMeasure(@error)

_IELoadWait ($oIE)
AppmonitorCheckCurrentMeasure(@error)

Local $oUsernameField = _IEGetObjById($oIE, "username")
AppmonitorCheckCurrentMeasure(@error)
AppmonitorCompleteMeasure()

ConsoleWrite("Success!" & @CRLF)
_IEQuit($oIE)
