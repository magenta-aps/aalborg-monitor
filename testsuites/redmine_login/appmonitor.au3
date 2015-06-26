#include <File.au3>
#include <MsgBoxConstants.au3>
#include <SQLite.au3>
#include <SQLite.dll.au3>
#include <Array.au3>

Local $sDbFile = EnvGet("APPMONITOR_SQLITE_FILE")

If Not $sDbFile Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", "No SQLite file specified")
    Exit -1
EndIf

Local $sAppMonitorRunPK = EnvGet("APPMONITOR_RUN_ID")

If Not $sAppMonitorRunPK Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", "No AppMonitor run id specified")
    Exit -1
EndIf

_SQLite_Startup()
If @error Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", "Can't load SQLite!")
    Exit -1
EndIf

Local $hAppMonitorDb = _SQLite_Open($sDbFile) ; Open a permanent disk database
If @error Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", "Can't open " & $sDbFile)
    Exit -1
EndIf


Local $hQuery, $aRow, $iSuccess, $sDbError = ""
$iSuccess = _SQLite_Query($hAppMonitorDb, _
    "SELECT run.id id " & _
    "FROM appmonitor_testrun run " & _
    "WHERE run.id = '" & $sAppMonitorRunPK & "' " & _
    "LIMIT 1", _
    $hQuery _
)

If _SQLite_FetchData($hQuery, $aRow) == $SQLITE_OK Then
    If $aRow[0] <> $sAppMonitorRunPK Then
        $sDbError = "Sanity check failed"
    EndIf
Else
    $sDbError = "Sanity check query failed"
EndIf

If $sDbError <> "" Then
    MsgBox($MB_SYSTEMMODAL, "SQLite Error", $sDbError)
    Exit -1
EndIf
