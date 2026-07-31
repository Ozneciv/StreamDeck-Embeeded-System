; ==============================================================================
; STREAM DECK STM32 BLUEPILL - WINDOWS AUTOHOTKEY v2 SCRIPT
; ==============================================================================
; Este script captura os atalhos F13 a F21 enviados pelo Stream Deck USB (STM32)
; e os converte em ações nativas do Windows e OBS Studio.
; ==============================================================================

#Requires AutoHotkey v2.0
#SingleInstance Force

TrayTip "Stream Deck STM32", "Script ativo! Pressione botões F13-F21", 1

; ------------------------------------------------------------------------------
; F13 (Botão 1 - 0x68): Tocar/Pausar Mídia do Windows (Spotify / YouTube / Media Player)
; ------------------------------------------------------------------------------
F13:: {
    Send "{Media_Play_Pause}"
    SoundBeep 750, 100
}

; ------------------------------------------------------------------------------
; F14 (Botão 2 - 0x69): Mudar Mudo do Áudio Geral / Microfone do Windows
; ------------------------------------------------------------------------------
F14:: {
    SoundSetMute -1 ; Alterna estado do som principal
    isMuted := SoundGetMute()
    if (isMuted) {
        ToolTip "🔊 Áudio Mutado"
    } else {
        ToolTip "🎙️ Áudio Desmutado"
    }
    SetTimer () => ToolTip(), -1500
}

; ------------------------------------------------------------------------------
; F15 (Botão 3 - 0x6A): Alternar Janelas (Alt+Tab rápido)
; ------------------------------------------------------------------------------
F15:: {
    Send "!{Tab}"
}

; ------------------------------------------------------------------------------
; F16 (Botão 4 - 0x6B): Abrir Bloco de Notas / Anotações Rápidas
; ------------------------------------------------------------------------------
F16:: {
    Run "notepad.exe"
}

; ------------------------------------------------------------------------------
; F17 (Botão 5 - 0x6C): Captura de Tela (PrintScreen / Snipping Tool)
; ------------------------------------------------------------------------------
F17:: {
    Send "#+{s}" ; Tecla Windows + Shift + S
}

; ------------------------------------------------------------------------------
; F18 (Botão 6 - 0x6D): Aumentar Volume do Sistema
; ------------------------------------------------------------------------------
F18:: {
    SoundSetVolume "+5"
    vol := SoundGetVolume()
    ToolTip "🔊 Volume: " . Round(vol) . "%"
    SetTimer () => ToolTip(), -1000
}

; ------------------------------------------------------------------------------
; F19 (Botão 7 - 0x6E): Diminuir Volume do Sistema
; ------------------------------------------------------------------------------
F19:: {
    SoundSetVolume "-5"
    vol := SoundGetVolume()
    ToolTip "🔉 Volume: " . Round(vol) . "%"
    SetTimer () => ToolTip(), -1000
}

; ------------------------------------------------------------------------------
; F20 (Botão 8 - 0x6F): Abrir Calculadora
; ------------------------------------------------------------------------------
F20:: {
    Run "calc.exe"
}

; ------------------------------------------------------------------------------
; F21 (Botão 9 - 0x70): Minimizar Tudo / Mostrar Área de Trabalho (Win + D)
; ------------------------------------------------------------------------------
F21:: {
    Send "#d"
}
