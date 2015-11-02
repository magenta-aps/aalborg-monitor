#include "..\..\lib\autoit\appmonitor.au3"

; Utility methods

; Actual test-case
AppmonitorCreateMeasure("Naviger til google.dk")
$oIE = _IECreate("https://google.dk/")
If @error Then
    Exit @error
EndIf

; Shut down IE when program exits
AppmonitorRegisterIEShutdown($oIE)

AppmonitorWaitForId($oIE, "tsf")
AppmonitorCheckCurrentMeasure(@error)
AppmonitorCompleteMeasure()


AppmonitorCreateMeasure("Input s�geudtryk")
Local $oForm =  _IEFormGetObjByName($oIE, "tsf")
AppmonitorCheckError(@error)

$oSearchInput = _IEFormElementGetObjByName($oForm, "q")
AppmonitorCheckError(@error)

_IEFormElementSetValue($oSearchInput, "aalborg kommune")
AppmonitorCheckError(@error)
Send("{ENTER}")
AppmonitorCheckError(@error)
AppmonitorWaitForId($oIE, "ires")
AppmonitorCheckError(@error)
AppmonitorCompleteMeasure()

AppmonitorCreateMeasure("Klik p� link")
_IELinkClickByText($oIE, "Aalborg Kommune: Borger");
AppmonitorCheckError(@error)
AppmonitorWaitForId($oIE, "main-search")
AppmonitorCheckError(@error)

AppmonitorCompleteMeasure()
