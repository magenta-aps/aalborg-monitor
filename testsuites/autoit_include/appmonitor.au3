#include <File.au3>
#include <MsgBoxConstants.au3>
#include <SQLite.au3>
#include <SQLite.dll.au3>
#include <Array.au3>

Local $sDbFile = EnvGet("APPMONITOR_SQLITE_FILE")

;ConsoleWriteError("FAIL FAIL FAIL" & @CRLF)
;Exit -1

If Not $sDbFile Then
    ConsoleWriteError("SQLite Error: No SQLite file specified")
    Exit -1
EndIf

Global $iAppMonitorRunPK = EnvGet("APPMONITOR_RUN_ID")

If Not $iAppMonitorRunPK Then
    ConsoleWriteError("SQLite Error: No AppMonitor run id specified")
    Exit -1
EndIf

_SQLite_Startup()
If @error Then
    ConsoleWriteError("SQLite Error: Can't load SQLite!")
    Exit -1
EndIf

Global $hAppMonitorDb = _SQLite_Open($sDbFile) ; Open a permanent disk database
If @error Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", "Can't open " & $sDbFile)
    Exit -1
EndIf


Local $hQuery, $aRow, $iSuccess, $sDbError = ""
$iSuccess = _SQLite_Query($hAppMonitorDb, _
    "SELECT run.id id " & _
    "FROM appmonitor_testrun run " & _
    "WHERE run.id = '" & $iAppMonitorRunPK & "' " & _
    "LIMIT 1", _
    $hQuery _
)

If _SQLite_FetchData($hQuery, $aRow) == $SQLITE_OK Then
   If $aRow[0] <> $iAppMonitorRunPK Then
          $sDbError = "Sanity check failed"
 EndIf
Else
    $sDbError = "Sanity check query failed"
EndIf

If $sDbError <> "" Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", $sDbError)
    Exit -1
EndIf

Func CreateMeasure($sName)
    Local $sSQL = "" & _
        "INSERT INTO appmonitor_testmeasure " & _
        "(test_run_id, name, started) " & _
        "VALUES (" & _
            $iAppMonitorRunPK & ", " & _
            _SQLite_FastEscape($sName) & ", " & _
            "STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')" & _
        ")"
    Local $iResult = _SQLite_Exec($hAppMonitorDb, $sSQL)
    If $iResult == $SQLITE_OK Then
        Return _SQLite_LastInsertRowID($hAppMonitorDb)
    Else
        MsgBox($MB_SYSTEMMODAL, "SQLite Error", _
               "Failed to create measure query")
        Exit -1
    EndIf
    Return 0
EndFunc

Func CompleteMeasure($iMeasureId)
    Local $sSQL = "" & _
        "UPDATE appmonitor_testmeasure " & _
        "SET " & _
            "ended = STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW'), " & _
            "success = 1 " & _
        "WHERE id = " & $iMeasureId

    Return _SQLite_Exec($hAppMonitorDb, $sSQL)
EndFunc

Func WaitForId($oIE, $sID, $iTimeout = 30)
    Local $oFoundObject
    Local $iLookupError = 0

    ; Initialize timer
    Local $hStartTime = TimerInit()

    ; Make sure page is loaded
    _IELoadWait($oIE, 0, $iTimeout)
    If @error <> 0 Then
        return SetError(@error, @extended, $oFoundObject)
    EndIf

    ; Try finding the object until we time out
    While TimerDiff($hStartTime) < $iTimeout
        $oFoundObject = _IEGetObjById($oIE, $sID)
        If $oFoundObject Then
            ExitLoop
        ElseIf @error == $_IEStatus_NoMatch Then
            ; Sleep for .2 seconds and try again
            Sleep(200)
        Else
            $iLookupError = @error
            ExitLoop
        EndIf
    WEnd

    ; Set specific errors if we did not find anything
    If Not $oFoundObject and $iLookupError == 0 Then
        If TimerDiff($hStartTime) >= $iTimeout Then
            $iLookupError = $_IEStatus_LoadWaitTimeout
        Else
            $iLookupError = $_IEStatus_NoMatch
        EndIf
    EndIf

    Return SetError($iLookupError, 0, $oFoundObject)
EndFunc