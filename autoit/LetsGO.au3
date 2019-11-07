#NoTrayIcon
#include <Misc.au3>
#include <MsgBoxConstants.au3>

If _Singleton("letsgo", 1) = 0 Then
    MsgBox($MB_SYSTEMMODAL, "Warning", "An instance of program is already running.")
    Exit
EndIf

Local $iReturn = RunWait(@ScriptDir & "\LetsGO.bat", "", @SW_HIDE)
If $iReturn <> 0 Then
   MsgBox($MB_SYSTEMMODAL, "Error", "Unable to run program, error code: " & $iReturn)
EndIf
