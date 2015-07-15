#include "..\..\lib\autoit\appmonitor.au3"

; Utility methods

Local $oIE
Local $hDbConnection = AppmonitorConnectDb()
Local $iRunId = AppmonitorGetRun($hDbConnection)

; Actual test-case
local $iMeasureID = CreateMeasure($hDbConnection, $iRunId, "Start IE")
$oIE = _IECreate("https://redmine.magenta-aps.dk/")
If @error Then
    Exit @error
EndIf

; Shut down IE when program exits
AppmonitorRegisterIEShutdown($oIE)

Local $oAccountDiv = WaitForId($oIE, "account")
AppmonitorCheckError(@error)
CompleteMeasure($hDbConnection, $iMeasureID)

Local $oLinkElem = _IETagNameGetCollection($oAccountDiv, "a").Item(0)
AppmonitorCheckError(@error)

$iMeasureID = CreateMeasure($hDbConnection, $iRunId, "Navigate to login page")
_IEAction($oLinkElem, "click")
AppmonitorCheckError(@error)

_IELoadWait ($oIE)
AppmonitorCheckError(@error)

Local $oUsernameField = _IEGetObjById($oIE, "username")
AppmonitorCheckError(@error)
CompleteMeasure($hDbConnection, $iMeasureID)

ConsoleWrite("Success!" & @CRLF)
_IEQuit($oIE)
