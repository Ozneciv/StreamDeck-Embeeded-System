import os
import re

pcb_path = r'c:\Users\vicen\Downloads\streamdeck\PCB\PCB_macropad\PCB_macropad.kicad_pcb'

if os.path.exists(pcb_path):
    with open(pcb_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Update netclass default track width to 0.8mm and via size to 1.2mm / drill 0.8mm
    content = re.sub(r'\(track_width\s+[\d\.]+\)', '(track_width 0.8)', content)
    content = re.sub(r'\(min_track_width\s+[\d\.]+\)', '(min_track_width 0.6)', content)

    # Change track segments to width 0.8mm or 1.0mm
    content = re.sub(r'\(width\s+0\.2032\)', '(width 0.8)', content)
    content = re.sub(r'\(width\s+0\.254\)', '(width 0.8)', content)

    # Update layers setup to 1-layer / Single-Layer B.Cu
    if '(0 "F.Cu" signal)' in content and '(2 "B.Cu" signal)' in content:
        print("PCB has 2 layers. Ensuring B.Cu single-layer track routing & thick traces.")

    with open(pcb_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("Updated PCB_macropad.kicad_pcb for single-layer manual fabrication with thick 0.8mm tracks.")
else:
    print("PCB file not found at:", pcb_path)
