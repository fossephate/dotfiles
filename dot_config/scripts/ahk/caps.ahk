; AutoHotkey v2 script for CapsLock behavior
#Requires AutoHotkey v2.0
#SingleInstance force
InstallKeybdHook true

; Holds: Sets variable to true/false
; Tap (under 200ms): Acts as Escape key

; Global variable to track CapsLock state
CapsLockHeld := false

; Variable to track press time
CapsLockPressTime := 0

; Disable the default CapsLock behavior
SetCapsLockState("AlwaysOff")


; function which turns off all hotkeys
TurnOffHotkeys() {
    Hotkey("N", "Off")
    Hotkey("E", "Off")
    Hotkey("I", "Off")
    Hotkey("O", "Off")
    Hotkey("'", "Off")
    Hotkey("M", "Off")
    Hotkey("space", "Off")
}

TurnOnHotkeys() {
    Hotkey("N", "On")
    Hotkey("E", "On")
    Hotkey("I", "On")
    Hotkey("O", "On")
    Hotkey("'", "On")
    Hotkey("M", "On")
    Hotkey("space", "On")
}

; When CapsLock is pressed down
CapsLock::
{
    global CapsLockHeld, CapsLockPressTime
    TurnOffHotkeys()
    ; Record the time when CapsLock was pressed
    CapsLockPressTime := A_TickCount
    
    ; Set the held variable to true
    CapsLockHeld := true
    TurnOnHotkeys()
    
    ; Optional: You can add code here that runs when CapsLock starts being held
    ; For example: ToolTip("CapsLock is being held")
    ToolTip("CapsLock is being held")
    
    ; Wait for the key to be released
    KeyWait("CapsLock")
    
    ; Key has been released
    CapsLockHeld := false
    TurnOffHotkeys()

    ; Remove the tooltip
    ToolTip("")
    
    ; Calculate how long the key was held
    HoldDuration := A_TickCount - CapsLockPressTime
    
    ; If held for less than 200ms, treat it as a tap
    if (HoldDuration < 200) {
        ; This was a tap, send Escape
        Send("{Escape}")
    }
    
    ; Optional: You can add code here that runs when CapsLock is released
    ; For example: ToolTip("")
}

N::
{
    Send("{Left}")
}

E::
{
    Send("{Down}")
}

I::
{
    Send("{Up}")
}

O::
{
    Send("{Right}")
}

; apostrophe -> forward delete:
'::
{
    Send("{Del}")
}

; m -> backspace
M::
{
    Send("{Backspace}")
}

; send ctrl+shift+h:
space::
{
    Send("{Ctrl down}{Shift down}h{Ctrl up}{Shift up}")
}
