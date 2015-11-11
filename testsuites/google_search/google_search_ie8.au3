;~ The contents of this file are subject to the Mozilla Public License
;~ Version 2.0 (the "License"); you may not use this file except in
;~ compliance with the License. You may obtain a copy of the License at
;~    http://www.mozilla.org/MPL/
;~
;~ Software distributed under the License is distributed on an "AS IS" basis,
;~ WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
;~ for the specific language governing rights and limitations under the
;~ License.
;~
;~ Copyright 2015 Magenta Aps
;~
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

AppmonitorWaitForId($oIE, "footer")
AppmonitorCheckCurrentMeasure(@error)
AppmonitorCompleteMeasure()


AppmonitorCreateMeasure("Input søgeudtryk")
Local $oForm =  _IEFormGetObjByName($oIE, "f")
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

AppmonitorCreateMeasure("Klik på link")
_IELinkClickByText($oIE, "Aalborg Kommune: Borger");
AppmonitorCheckError(@error)
AppmonitorWaitForId($oIE, "main-search")
AppmonitorCheckError(@error)

AppmonitorCompleteMeasure()
