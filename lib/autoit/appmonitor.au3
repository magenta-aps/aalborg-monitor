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
#include-once

#include <MsgBoxConstants.au3>
#include <IE.au3>
#include <File.au3>
#include <Crypt.au3>
#include <String.au3>
#include <Array.au3>
#include <SQLite.au3>
#include <SQLite.dll.au3>

Local $__AppmonitorDbHandle
Local $__AppminotorRun
Local $__AppmonitorLastMeasure = -1
Local $__AppmonitorLastMeasureName = ""
Local $__AppmonitorMeasureError = ""
Local $__IEObjectToShutdown

Func AppmonitorConnectDb()
    If $__AppmonitorDbHandle Then
        Return
    EndIf

    Local $sDbFile = EnvGet("APPMONITOR_SQLITE_FILE")

    If Not $sDbFile Then
        ConsoleWriteError("SQLite Error: No SQLite file specified" & @CRLF)
        Exit -1
    EndIf

    _SQLite_Startup()
    If @error Then
        ConsoleWriteError("SQLite Error: Can't load SQLite!" & @CRLF)
        Exit -1
    EndIf

    $__AppmonitorDbHandle = _SQLite_Open($sDbFile) ; Open a permanent disk database
    If @error Then
        ConsoleWriteError("SQLite Error: Can't open " & $sDbFile & @CRLF)
        Exit -1
    EndIf

    Return $__AppmonitorDbHandle
EndFunc

Func AppmonitorGetDbHandle()
    AppmonitorConnectDb()
    return $__AppmonitorDbHandle
EndFunc

Func AppmonitorGetRun()
    If $__AppminotorRun Then
        return $__AppminotorRun
    EndIf

    $hAppmonitorDb = AppmonitorGetDbHandle()

    Local $iAppmonitorRun = EnvGet("APPMONITOR_RUN_ID")

    If Not $iAppmonitorRun Then
        ConsoleWriteError("SQLite Error: No AppMonitor run id specified" & @CRLF)
        Exit -1
    EndIf

    Local $hQuery, $aRow, $iSuccess, $sDbError = ""
    $iSuccess = _SQLite_Query($hAppmonitorDb, _
        "SELECT run.id id " & _
        "FROM appmonitor_testrun run " & _
        "WHERE run.id = '" & $iAppmonitorRun & "' " & _
        "LIMIT 1", _
        $hQuery _
    )

    If _SQLite_FetchData($hQuery, $aRow) == $SQLITE_OK Then
        If $aRow[0] <> $iAppmonitorRun Then
            $sDbError = "Sanity check failed"
        EndIf
    Else
        $sDbError = "Sanity check query failed: " & _SQLite_ErrMsg($hAppmonitorDb)
    EndIf

    If $sDbError <> "" Then
        ConsoleWriteError("SQLite Error: " & $sDbError & @CRLF)
        Exit -1
    EndIf

    Return $iAppmonitorRun
EndFunc

Func AppmonitorGetDbConfigValue($sConfigName)
    $hAppmonitorDb = AppmonitorGetDbHandle()

    Local $hQuery, $aRow, $iSuccess
    $iSuccess = _SQLite_Query($hAppmonitorDb, _
        "SELECT confval.value " & _
        "FROM appmonitor_configurationvalue confval " & _
        "WHERE confval.name = " & _SQLite_Escape($sConfigName) & " " & _
        "LIMIT 1", _
        $hQuery _
    )
    If @error Then
        ConsoleWriteError("Error while querying configuration value: " & @error & @CRLF)
        Exit @error
    EndIf

    If _SQLite_FetchData($hQuery, $aRow) == $SQLITE_OK Then
        Return $aRow[0]
    Else
        Return ""
    EndIf
EndFunc

Func AppmonitorReadConfigValueFromFile($sFileName, $sConfigName)
    Local $sValue

    Local $hFileHandle = FileOpen($sFileName)
    If @error Then
        ConsoleWriteError(_
            "Could not open file '" & $sFileName & "': " & @error & @CRLF _
        )
        Exit(@error)
    EndIf

    While Not @error
        $sLine = FileReadLine($hFileHandle)
        If StringInStr($sLine, $sConfigName) <> 0 Then
            $sValue = StringMid($sLine, StringInStr($sLine, "=") + 1)
            $sValue = StringStripWS($sValue, $STR_STRIPLEADING)
            $sValue = StringMid($sValue, 2, StringLen($sValue) - 2)
            ExitLoop
        EndIf
    WEnd

    Return $sValue
EndFunc

Func AppmonitorReadConfigValue($sConfigName)
    Local $sRootDir = EnvGet("APPMONITOR_ROOT_DIR")
    If Not $sRootDir Then
        ConsoleWriteError("Could not get APPMONITOR_ROOT_DIR")
        Exit -1
    EndIf

    ; Normalize the retrieved path
    Local $sDrive = "", $sDir = "", $sFileName, $sExtension
    Local $aPathSplit = _PathSplit($sRootDir, $sDrive, $sDir, $sFileName, $sExtension)
    $sRootDir = _PathMake($sDrive, $sDir, "", "")

    ; Make config file path
    Local $sConfigDir = _PathFull("aalborgmonitor", $sRootDir)

    Local $sResult
    ; Check for value in local settings file
    If FileExists(_PathFull("settings_local.py", $sConfigDir)) Then
        $sResult = AppmonitorReadConfigValueFromFile( _
            _PathFull("settings_local.py", $sConfigDir), _
            $sConfigName _
        )
    EndIf
    ; If not previously found, look in standard settings file
    If Not $sResult Then
        $sResult = AppmonitorReadConfigValueFromFile( _
            _PathFull("settings.py", $sConfigDir), _
            $sConfigName _
        )
    EndIf

    return $sResult
EndFunc

Func AppmonitorDecrypt($sHexCryptedValue)
    ; Convert incoming data from hex to string
    Local $sCryptedValue = _HexToString($sHexCryptedValue)
    If @error Then
        ConsoleWriteError(_
            "Could not convert encrypted string '" & _
            $sHexCryptedValue & "' from hex to string" _
        )
        Exit -1
    EndIf

    Local $sSecret = AppmonitorReadConfigValue("SECRET_KEY")
    If Not $sSecret Then
        ConsoleWriteError("Could not retrieve SECRET_KEY from Django config")
        Exit -1
    EndIf

    _Crypt_Startup()
    Local $bEncryptedData = StringToBinary($sCryptedValue)
    Return BinaryToString(_Crypt_DecryptData($bEncryptedData, $sSecret, $CALG_3DES))
EndFunc

Func AppmonitorEncrypt($sStringToEncrypt)
    Local $sSecret = AppmonitorReadConfigValue("SECRET_KEY")
    If Not $sSecret Then
        ConsoleWriteError("Could not retrieve SECRET_KEY from Django config")
        Exit -1
    EndIf

    _Crypt_Startup()
    Local $bEncrypted = _Crypt_EncryptData($sStringToEncrypt, $sSecret, $CALG_3DES)
    Local $sEncrypted = BinaryToString($bEncrypted)
    Return _StringToHex($sEncrypted)
EndFunc

Func AppmonitorSetMeasureData($iMeasureId, $sMeasureName)
    $__AppmonitorLastMeasure = $iMeasureId
    $__AppmonitorLastMeasureName = $sMeasureName
EndFunc

Func AppmonitorResetMeasureData($iError, $iExtended, $mReturnValue)
    AppmonitorSetMeasureData(-1, "")
    $__AppmonitorMeasureError = ""
    Return SetError($iError, $iExtended, $mReturnValue)
EndFunc

Func AppmonitorGetMeasure($iMeasureId = -1)
    If $iMeasureId <> -1 Then
        return $iMeasureId
    Else
        Return $__AppmonitorLastMeasure
    EndIf
EndFunc

Func AppmonitorGetMeasureName($iMeasureId = -1, $sMeasureName = "")
    If $sMeasureName == "" Then
        $sMeasureName = $__AppmonitorLastMeasureName
    EndIf

    If $sMeasureName <> "" Then
        return $sMeasureName
    EndIf

    Return "Measure with id " & AppmonitorGetMeasure($iMeasureId)
EndFunc

Func AppmonitorSetMeasureError($sMessage, $iMeasureId = -1)
    $iMeasureId = AppmonitorGetMeasure($iMeasureId)

    If $iMeasureId == -1 Then
        Return
    EndIf

    $__AppmonitorMeasureError = $sMessage
EndFunc

Func AppmonitorGetMeasureError($iMeasureId = -1)
    If AppmonitorGetMeasure($iMeasureId) == -1 Then
        Return ""
    EndIf

    Return $__AppmonitorMeasureError
EndFunc

Func AppmonitorCreateMeasure($sName, $iAppmonitorRun = -1)
    $hAppmonitorDb = AppmonitorGetDbHandle()
    If $iAppmonitorRun == -1 Then
        $iAppmonitorRun = AppmonitorGetRun()
    EndIf

    Local $sSQL = "" & _
        "INSERT INTO appmonitor_testmeasure " & _
        "(test_run_id, name, started) " & _
        "VALUES (" & _
            $iAppmonitorRun & ", " & _
            _SQLite_FastEscape($sName) & ", " & _
            "STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')" & _
        ")"
    Local $iResult = _SQLite_Exec($hAppmonitorDb, $sSQL)
    If $iResult == $SQLITE_OK Then
        Local $iId = _SQLite_LastInsertRowID($hAppmonitorDb)
        ConsoleWrite("Started measure '" & $sName & "' [" & $iId & "]" & @CRLF)
        AppmonitorSetMeasureData($iId, $sName)
        $__AppmonitorMeasureError = ""
        Return $iId
    Else
        ConsoleWriteError("SQLite Error: Failed create measure query")
        Exit -1
    EndIf
    Return 0
EndFunc

Func AppmonitorCompleteMeasure($iMeasureId = -1)
    $iMeasureid = AppmonitorGetMeasure($iMeasureId)

    If $iMeasureid == -1 Then
        ConsoleWriteError( _
            "Trying to complete unspecifed measure, but there is no " & _
            "measure currently registered" & @CRLF _
        )
        Exit -1
    EndIf

    ConsoleWrite("Completing measure [" & AppmonitorGetMeasureName($iMeasureId) & "]" & @CRLF)

    Local $hAppmonitorDb = AppmonitorGetDbHandle()

    Local $sSQL = "" & _
        "UPDATE appmonitor_testmeasure " & _
        "SET " & _
            "ended = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'), " & _
            "success = 1 " & _
        "WHERE id = " & $iMeasureId

    Local $iResult = _SQLite_Exec($hAppmonitorDb, $sSQL)

    Return AppmonitorResetMeasureData(@error, @extended, $iResult)
EndFunc

Func AppmonitorCheckCurrentMeasure($iError, $sMessage = "", $bFatal = True)
    ; Do not do anything if there was no error
    If $iError = 0 Then
        Return
    EndIf

    ; Do not do anything if we are not currently measuring
    Local $iMeasureId = AppmonitorGetMeasure()
    If $iMeasureId == -1 Then
        Return
    EndIf

    ; Check for a stored error
    If $sMessage == "" Then
        $sMessage = AppmonitorGetMeasureError($iMeasureId)
    EndIf

    ; Default message is reporting the error code
    If $sMessage == "" Then
        $sMessage = "Failed with error code " & $iError
    EndIf

    AppmonitorFailMeasure($sMessage, $iMeasureId, $bFatal)

    If $bFatal Then
        Exit $iError
    EndIf
EndFunc

Func AppmonitorFailMeasure($sMessage, $iMeasureId = -1, $bFatal = True)
    $iMeasureId = AppmonitorGetMeasure($iMeasureId)

    If $iMeasureId == -1 Then
        ConsoleWriteError( _
            "Trying to fail unspecifed measure, but there is no " & _
            "measure currently registered" & @CRLF _
        )
        Exit -1
    EndIf

    ConsoleWrite( _
        "Failing measure [" & AppmonitorGetMeasureName($iMeasureId) & "] " & _
        "with message '" & $sMessage & "'" & @CRLF _
    )

    Local $hAppmonitorDb = AppmonitorGetDbHandle()

    Local $sSQL = "" & _
        "UPDATE appmonitor_testmeasure " & _
        "SET " & _
            "ended = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'), " & _
            "success = 0, " & _
            "failure_reason = " & _SQLite_FastEscape($sMessage) & " " & _
        "WHERE id = " & $iMeasureId

    Local $iResult = _SQLite_Exec($hAppmonitorDb, $sSQL)

    Return AppmonitorResetMeasureData(@error, @extended, $iResult)
EndFunc

Func AppmonitorWaitForId(ByRef $oIE, $sID, $iTimeout = 30000)
    Local $oFoundObject
    Local $iLookupError = 0
    Local $sMessage = ""

    ; Initialize timer
    Local $hStartTime = TimerInit()

    ; Make sure page is loaded
    _IELoadWait($oIE, 0, $iTimeout)
    If @error <> 0 Then
        Local $iError = @error, $iExtended = @extended
        $sMessage = "_IELoadWait error while trying to get object with id " & $sID & ": " & @error
        ConsoleWriteError($sMessage & @CRLF)
        AppmonitorSetMeasureError($sMessage)
        return SetError($iError, $iExtended, $oFoundObject)
    EndIf

    ; Try finding the object until we time out
    While TimerDiff($hStartTime) < $iTimeout
        $oFoundObject = _IEGetObjById($oIE, $sID)
        If IsObj($oFoundObject) Then
            ExitLoop
        ElseIf @error == $_IEStatus_NoMatch Then
            ; Sleep for .2 seconds and try again
            Sleep(200)
        ElseIf @error <> 0 Then
            $iLookupError = @error
            ExitLoop
        EndIf
    WEnd

    ; Set specific errors if we did not find anything
    If (Not IsObj($oFoundObject)) And ($iLookupError == 0) Then
        If TimerDiff($hStartTime) >= $iTimeout Then
            $sMessage = "Could not find object with ID " & $sID & " within the specified time"
            $iLookupError = $_IEStatus_LoadWaitTimeout
        Else
            $sMessage = "Object with id " & $sID & " not found"
            $iLookupError = $_IEStatus_NoMatch
        EndIf
    EndIf

    If $iLookupError <> 0 Then
        If $sMessage <> "" Then ConsoleWriteError($sMessage & @CRLF)
        AppmonitorSetMeasureError($sMessage)
    EndIf

    Return SetError($iLookupError, 0, $oFoundObject)
EndFunc

Func AppmonitorExitWithError($iError)
    ConsoleWriteError("Exiting with error: " & $iError & @CRLF)
    Exit($iError)
EndFunc

Func AppmonitorCheckError($iError)
    If $iError <> 0 Then
        AppmonitorExitWithError($iError)
    EndIf
EndFunc

Func AppmonitorMouseMoveAppletControl($hWnd, $sText, $hButton)
    Local $winPosData = WinGetPos($hWnd)
    Local $posData = ControlGetPos($hWnd, $sText, $hButton)
    MouseMove($winPosData[0] + $posData[0] + $posData[2] / 2, $winPosData[1] + $posData[1] + $posData[3] / 2, 0)
EndFunc

Func AppmonitorControlWait($hWnd, $sText, $hButton, $iTimeout = 30000)
    Local $hWaitStart = TimerInit()
    Local $hResult

    While TimerDiff($hWaitStart) < $iTimeout
        $hResult = ControlGetHandle($hWnd, $sText, $hButton)
        If $hResult Then
			Return SetError(0, 0, $hResult)
        EndIf
        Sleep(200)
    WEnd

	ConsoleWriteError("Failed to locate button " & $hButton & @CRLF)
    Return SetError($_IEStatus_LoadWaitTimeout, 0, $hResult)
EndFunc

Func AppmonitorDigitalSignaturLogin($sWindowTitle = "DUBU Logon - Internet Explorer")
    Local $sEncryptedPassword = AppmonitorGetDbConfigValue( _
        "krypteret_digital_signatur_login" _
    )
    If Not $sEncryptedPassword Then
        ConsoleWriteError("Could not read encrypted password value" & @CRLF)
        Exit -1
    EndIf
    Local $sPassword = AppmonitorDecrypt($sEncryptedPassword)

    ConsoleWriteError("Locating IE with login page" & @CRLF)
    Local $oIEWin = WinWait("[TITLE:" & $sWindowTitle & "; CLASS:IEFrame]", "", 5)
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to locate IE login page")
        Return SetError($iError, @extended)
    EndIf

    ConsoleWriteError("Locate applet OK button" & @CRLF)
    Local $hControlButton = AppmonitorControlWait($oIEWin, "", "[CLASS:Button; INSTANCE:2]")
    If @error Then
		Local $iError = @error
		ConsoleWriteError("Button not found " & $iError & @CRLF)
        AppmonitorSetMeasureError("Failed to locate applet OK button")
        Return SetError($iError, @extended)
    EndIf

	ConsoleWriteError("Locate IE window control" & @CRLF)
	Local $hIEWindowControl = ControlGetHandle($oIEWin, "", "[CLASS:SunAwtCanvas; INSTANCE:2]")
	ConsoleWriteError("Located IE window control: " & $hIEWindowControl & @CRLF)

	Sleep(1000)

    ConsoleWriteError("Click OK button" & @CRLF)
    ControlSend($oIEWin, "", $hIEWindowControl, "{TAB}")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to send first tab to applet")
        Return SetError($iError, @extended)
    EndIf
	Sleep(100)
    ControlSend($oIEWin, "", $hIEWindowControl, "{TAB}")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to send second tab to applet")
        Return SetError($iError, @extended)
    EndIf
	Sleep(100)
    ControlSend($oIEWin, "", $hIEWindowControl, "{ENTER}")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to send enter to applet")
        Return SetError($iError, @extended)
    EndIf

    ConsoleWriteError("Locate password dialog" & @CRLF)
    Local $hWndDialog = WinWait("[TITLE:Adgang til signaturcentralen]", "", 10)
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to find dialog with password input")
        Return SetError($iError, @extended)
	EndIf

    ConsoleWriteError("Locate text input in password dialog" & @CRLF)
    Local $hTextInput = AppmonitorControlWait($hWndDialog, "", "[CLASS:Edit; INSTANCE:1]")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to find password input field")
        Return SetError($iError, @extended)
    EndIf

    ConsoleWriteError("Input password" & @CRLF)
    ControlSend($hWndDialog, "", $hTextInput, $sPassword)
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to input the password")
        Return SetError($iError, @extended)
    EndIf

    ConsoleWriteError("Locate password OK button" & @CRLF)
    Local $hDlgOKButton = ControlGetHandle($hWndDialog, "", "[CLASS:Button; INSTANCE:1]")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to locate the OK button")
        Return SetError($iError, @extended)
    EndIf

    ConsoleWriteError("Click password OK button" & @CRLF)
    ControlClick($hWndDialog, "", $hDlgOKButton, "primary")
    If @error Then
		Local $iError = @error
        AppmonitorSetMeasureError("Failed to click on the password OK button")
        Return SetError($iError, @extended)
    EndIf

    Return True
EndFunc

Func AppmonitorIEMoveMouseToObj(ByRef $oObject)
   Local $iWidth = _IEPropertyGet($oObject, "width")
   If Not IsInt($iWidth) Or $iWidth == 0 Then
	  $iWidth = 2
   EndIf
   Local $iHeight = _IEPropertyGet($oObject, "height")
   If Not IsInt($iHeight) Or $iHeight == 0 Then
	  $iHeight = 2
   EndIf
   Local $iX = _IEPropertyGet($oObject, "screenx")
   ConsoleWrite("X: " & $iX & @CRLF)
   $iX += Int($iWidth / 2)
   ConsoleWrite("X: " & $iX & @CRLF)
   Local $iY = _IEPropertyGet($oObject, "screeny")
   ConsoleWrite("Y: " & $iY & @CRLF)
   $iY += Int($iHeight / 2)
   ConsoleWrite("Y: " & $iY & @CRLF)

   MouseMove($iX, $iY)
EndFunc

; Methods for handling proper shutdown of IE
Func AppmonitorIEReattach($sString, $sMode = "title", $iInstance = 1)
    Local $hIEAttachStart = TimerInit()

    While True
        $oIE = _IEAttach($sString, $sMode, $iInstance)
        If @error == 0 Then
            ExitLoop
        EndIf
        If TimerDiff($hIEAttachStart) > 30000 Then
            ConsoleWriteError("Timeout while trying to reattach to IE session" & @CRLF)
            return SetError($_IEStatus_LoadWaitTimeout, 0, $oIE)
        EndIf
        Sleep(100)
    WEnd

    AppmonitorRegisterIEShutdown($oIE)
    Return SetError(0, 0, $oIE)
 EndFunc

Func AppmonitorRegisterIEShutdown(ByRef $oIE)
    $__IEObjectToShutdown = $oIE
EndFunc

Func __AppmonitorShutdownIE()
    If IsObj($__IEObjectToShutdown) Then
        _IEQuit($__IEObjectToShutdown)
    EndIf
EndFunc
OnAutoItExitRegister("__AppmonitorShutdownIE")

; If we die unexpectedly register it on the current measure
Func __AppminotorShutdownMeasure()
    Local $iMeasureId = AppmonitorGetMeasure()
    If $iMeasureId <> -1 Then
        Local $sErrorMsg = "AutoIt script closed while measure was still active."
        Local $sMeasureError = AppmonitorGetMeasureError()
        If $sMeasureError <> "" Then
            $sErrorMsg = $sErrorMsg & " Last error: " & $sMeasureError & "."
        EndIf
        AppmonitorFailMeasure($sErrorMsg, $iMeasureId)
    EndIf
EndFunc
OnAutoItExitRegister("__AppminotorShutdownMeasure")
