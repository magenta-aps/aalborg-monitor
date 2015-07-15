#include-once

#include <MsgBoxConstants.au3>
#include <IE.au3>
#include <File.au3>
#include <Crypt.au3>
#include <String.au3>
#include <Array.au3>
#include <SQLite.au3>
#include <SQLite.dll.au3>

Func AppmonitorConnectDb()
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

    Local $hAppmonitorDb = _SQLite_Open($sDbFile) ; Open a permanent disk database
    If @error Then
        ConsoleWriteError("SQLite Error: Can't open " & $sDbFile & @CRLF)
        Exit -1
    EndIf

    Return $hAppmonitorDb
EndFunc

Func AppmonitorGetRun($hAppmonitorDb)
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
        $sDbError = "Sanity check query failed"
    EndIf

    If $sDbError <> "" Then
        ConsoleWriteError("SQLite Error: " & $sDbError & @CRLF)
        Exit -1
    EndIf

    Return $iAppmonitorRun
EndFunc

Func AppmonitorGetDbConfigValue($hAppmonitorDb, $sConfigName)
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

Func CreateMeasure($hAppmonitorDb, $iAppmonitorRun, $sName)
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
        Return $iId
    Else
        MsgBox($MB_SYSTEMMODAL, "SQLite Error", _
               "Failed to create measure query")
        Exit -1
    EndIf
    Return 0
EndFunc

Func CompleteMeasure($hAppmonitorDb, $iMeasureId)
    ConsoleWrite("Completing measure [" & $iMeasureId & "]" & @CRLF)

    Local $sSQL = "" & _
        "UPDATE appmonitor_testmeasure " & _
        "SET " & _
            "ended = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'), " & _
            "success = 1 " & _
        "WHERE id = " & $iMeasureId

    Return _SQLite_Exec($hAppmonitorDb, $sSQL)
EndFunc

Func WaitForId(ByRef $oIE, $sID, $iTimeout = 30000)
    Local $oFoundObject
    Local $iLookupError = 0

    ; Initialize timer
    Local $hStartTime = TimerInit()

    ; Make sure page is loaded
    _IELoadWait($oIE, 0, $iTimeout)
    If @error <> 0 Then
        Local $iError = @error, $iExtended = @extended
        ConsoleWriteError("_IELoadWait timeout while trying to get object with id " & $sID & ": " & @error & @CRLF)
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
            ConsoleWriteError("Could not find object with ID " & $sID & " withing the specified time" & @CRLF)
            $iLookupError = $_IEStatus_LoadWaitTimeout
        Else
            ConsoleWriteError("Object with id " & $sID & " not found" & @CRLF)
            $iLookupError = $_IEStatus_NoMatch
        EndIf
    EndIf

    Return SetError($iLookupError, 0, $oFoundObject)
EndFunc

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

Local $__IEObjectToShutdown
Func AppmonitorRegisterIEShutdown(ByRef $oIE)
    $__IEObjectToShutdown = $oIE
EndFunc

Func __AppmonitorShutdownIE()
    If IsObj($__IEObjectToShutdown) Then
        _IEQuit($__IEObjectToShutdown)
    EndIf
EndFunc
OnAutoItExitRegister("__AppmonitorShutdownIE")

Func AppmonitorExitWithError($iError)
    ConsoleWriteError("Exiting with error: " & $iError & @CRLF)
    Exit($iError)
EndFunc

Func AppmonitorCheckError($iError)
    If $iError <> 0 Then
        AppmonitorExitWithError($iError)
    EndIf
EndFunc