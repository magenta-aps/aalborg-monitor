#include <IE.au3>
#include <Array.au3>
#include "..\..\lib\autoit\appmonitor.au3"

Local $hDbConnection = AppmonitorConnectDb()
Local $sEncryptedPassword = AppmonitorGetDbConfigValue( _
    $hDbConnection, _
    "krypteret_digital_signatur_login" _
)
If Not $sEncryptedPassword Then
    ConsoleWriteError("Could not read encrypted password value" & @CRLF)
    Exit -1
EndIf
Local $sPassword = AppmonitorDecrypt($sEncryptedPassword)

; Utility methods
Func MouseMoveAppletControl($hWnd, $sText, $hButton)
    Local $winPosData = WinGetPos($hWnd)
    Local $posData = ControlGetPos($hWnd, $sText, $hButton)
    MouseMove($winPosData[0] + $posData[0] + $posData[2] / 2, $winPosData[1] + $posData[1] + $posData[3] / 2, 0)
EndFunc

Func ControlWait($hWnd, $sText, $hButton, $iTimeout = 30)
   Local $hWaitStart = TimerInit()
   Local $fTimeout = $iTimeout * 1000
   Local $iErrorValue = 0
   Local $hResult

   While TimerDiff($hWaitStart) < $fTimeout
	  $hResult = ControlGetHandle($hWnd, "", $hButton)
	  If $hResult Then
		 ExitLoop
	  EndIf
	  Sleep(200)
   WEnd
   If TimerDiff($hWaitStart) >= $fTimeout Then
	  $iErrorValue = $_IEStatus_LoadWaitTimeout
   EndIf

   Return SetError($iErrorValue, @extended, $hResult)
EndFunc

; Actual script
ConsoleWriteError("Locating IE with login page" & @CRLF)
Local $oIEWin = WinWaitActive("[TITLE:DUBU Logon - Internet Explorer; CLASS:IEFrame]", "", 5)
If @error Then Exit(@error)

ConsoleWriteError("Locate applet OK button" & @CRLF)
Local $hControlButton = ControlWait($oIEWin, "", "[CLASS:Button; INSTANCE:2]")
If @error Then Exit(@error)

ConsoleWriteError("Activating window" & @CRLF)
WinActivate($oIEWin)

ConsoleWriteError("Move mouse to OK button" & @CRLF)
MouseMoveAppletControl($oIEWin, "", $hControlButton)
If @error Then Exit(@error)

ConsoleWriteError("Click OK button" & @CRLF)
ControlClick($oIEWin, "", $hControlButton, "primary")
If @error Then Exit(@error)

ConsoleWriteError("Locate password dialog" & @CRLF)
Local $hWndDialog = WinWait("[TITLE:Adgang til signaturcentralen]", "", 10)
If @error Then Exit(@error)

ConsoleWriteError("Activate password dialog window" & @CRLF)
WinActivate($hWndDialog)
If @error Then Exit(@error)

ConsoleWriteError("Locate text input in password dialog" & @CRLF)
Local $hTextInput = ControlWait($hWndDialog, "", "[CLASS:Edit; INSTANCE:1]")
If @error Then Exit(@error)

ConsoleWriteError("Input password" & @CRLF)
ControlSend($hWndDialog, "", $hTextInput, $sPassword)
If @error Then Exit(@error)

ConsoleWriteError("Locate password OK button" & @CRLF)
Local $hDlgOKButton = ControlGetHandle($hWndDialog, "", "[CLASS:Button; INSTANCE:1]")
If @error Then Exit(@error)

ConsoleWriteError("Move mouse to password OK button" & @CRLF)
MouseMoveAppletControl($hWndDialog, "", $hDlgOKButton)
If @error Then Exit(@error)

ConsoleWriteError("Click password OK button" & @CRLF)
ControlClick($hWndDialog, "", $hDlgOKButton, "primary")
If @error Then Exit(@error)

Exit(0)
