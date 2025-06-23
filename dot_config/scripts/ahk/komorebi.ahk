; komorebi


#Requires AutoHotkey v2.0.2
#SingleInstance Force

Komorebic(cmd) {
    RunWait(format("komorebic.exe {}", cmd), , "Hide")
}

; !q::Komorebic("close")
; !m::Komorebic("minimize")

; Focus windows
; !n::Komorebic("focus left")
!SC024::Komorebic("focus left")
!SC025::Komorebic("focus down")
!SC026::Komorebic("focus up")
!SC027::Komorebic("focus right")

; !+[::Komorebic("cycle-focus previous")
; !+]::Komorebic("cycle-focus next")

; Move windows
!+SC024::Komorebic("move left")
!+SC025::Komorebic("move down")
!+SC026::Komorebic("move up")
!+SC027::Komorebic("move right")

; Stack windows
; !Left::Komorebic("stack left")
; !Down::Komorebic("stack down")
; !Up::Komorebic("stack up")
; !Right::Komorebic("stack right")
; !;::Komorebic("unstack")
; ![::Komorebic("cycle-stack previous")
; !]::Komorebic("cycle-stack next")
; !Left::Komorebic("cycle-stack previous")
!Left::Komorebic("change-layout")

!Right::Komorebic("cycle-stack next")
; Resize
!=::Komorebic("resize-axis horizontal increase")
!-::Komorebic("resize-axis horizontal decrease")
!+=::Komorebic("resize-axis vertical increase")
!+_::Komorebic("resize-axis vertical decrease")

; Manipulate windows
!.::Komorebic("toggle-float")
!/::Komorebic("toggle-monocle")

; Window manager options
!+r::Komorebic("retile")
; !p::Komorebic("toggle-pause")

; Layouts
; !x::Komorebic("flip-layout horizontal")
; !y::Komorebic("flip-layout vertical")

; send to workspace A-Z
!q::Komorebic("focus-workspace 0")
!w::Komorebic("focus-workspace 1")
!SC012::Komorebic("focus-workspace 2")
!SC013::Komorebic("focus-workspace 3")

; arst
!a::Komorebic("focus-workspace 4")
!SC01F::Komorebic("focus-workspace 5")
!SC020::Komorebic("focus-workspace 6")
!SC021::Komorebic("focus-workspace 7")

; zxcdv
!z::Komorebic("focus-workspace 8")
!x::Komorebic("focus-workspace 9")
!c::Komorebic("focus-workspace 10")
!SC02f::Komorebic("focus-workspace 11")
!SC030::Komorebic("focus-workspace 12")

; send to workspace with shift
!+q::Komorebic("send-to-workspace 0")
!+w::Komorebic("send-to-workspace 1")
!+SC012::Komorebic("send-to-workspace 2")
!+SC013::Komorebic("send-to-workspace 3")

; arst
!+a::Komorebic("send-to-workspace 4")
!+SC01F::Komorebic("send-to-workspace 5")
!+SC020::Komorebic("send-to-workspace 6")
!+SC021::Komorebic("send-to-workspace 7")


; zxcdv
!+z::Komorebic("send-to-workspace 8")
!+x::Komorebic("send-to-workspace 9")
!+c::Komorebic("send-to-workspace 10")
!+SC02f::Komorebic("send-to-workspace 11")
!+SC030::Komorebic("send-to-workspace 12")





