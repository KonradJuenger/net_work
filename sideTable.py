#!/usr/bin/python3
#build with:
#pyinstaller --noconfirm --onefile --windowed --icon "D:XXX/release/juengerkuehn.ico" --win-private-assemblies --add-data "D:xxx/release/input;input/"  "D:/xxx/release/sideTable.py"

import PySimpleGUI as sg
import re
from pathlib import Path
import ast
import sys
#import os


def main():
   
    in_files = get_input()
    out_files = get_output_path(in_files)
    defaults = get_defaults(out_files[0])
    ui = ini_ui(defaults)
    while True:
        event, cfg = ui.read()
        if event == sg.WIN_CLOSED or event == 'Quit': # if user closes window or clicks Quit
            break
        elif event == 'export Gcode': 
            if allowed_input(cfg,ui):
                gen_gcode(cfg,in_files,out_files)
        elif event == 'export test-piece': 
            if allowed_input(cfg,ui):
                gen_gcode(cfg,in_files[0:1],out_files[0:1])
    ui.close()


def get_input():    
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
        file_a = resource_path(str(Path(sys._MEIPASS) / './input/test_piece.gcode'))    
        file_b = resource_path(str(Path(sys._MEIPASS) / './input/sideTable_juengerkuehn_lower.gcode')) 
        file_c = resource_path(str(Path(sys._MEIPASS) / './input/sideTable_juengerkuehn_upper.gcode')) 
        
    else:
        file_a = resource_path(str(Path(__file__).parent / './input/test_piece.gcode')) 
        file_b = resource_path(str(Path(__file__).parent / './input/sideTable_juengerkuehn_lower.gcode')) 
        file_c = resource_path(str(Path(__file__).parent / './input/sideTable_juengerkuehn_upper.gcode'))    
        
    #print(f'infiles = {file_a},{file_b},{file_c}')
    return[file_a,file_b,file_c]

def get_output_path(in_files):
    out_files =[]
    for file in in_files:
        if getattr(sys, 'frozen', False):
            #application_path = sys._MEIPASS
            application_path = Path(sys.executable).parent
        else:
            application_path = Path(__file__).parent
        out_files.append(Path(application_path) / Path(file.name))
    print(f'outfiles = {out_files}')
    return out_files

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)/Path(relative_path)
        #return os.path.join(sys._MEIPASS, relative_path)
    #return os.path.join(os.path.abspath("."), relative_path)
    else:
        return Path(Path(".").resolve())/Path(relative_path)

def ini_ui(default):
    sg.theme('Default1')
    icon_b64 = b"""iVBORw0KGgoAAAANSUhEUgAAABkAAAAZCAYAAADE6YVjAAAACXBIWXMAAAsTAAALEwEAmpwYAAAF8WlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNi4wLWMwMDYgNzkuMTY0NzUzLCAyMDIxLzAyLzE1LTExOjUyOjEzICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjIuMyAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIxLTA1LTA5VDEzOjMxOjI1KzAyOjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMS0wNS0wOVQxMzo1MDo1MiswMjowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMS0wNS0wOVQxMzo1MDo1MiswMjowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo2MzljZjM1MC1hMmE4LWQyNDgtYWExYi02MTA5N2EyNDQ4NmUiIHhtcE1NOkRvY3VtZW50SUQ9ImFkb2JlOmRvY2lkOnBob3Rvc2hvcDpiNzc2YWRlMi03MmE3LTlmNDAtYjIyMy0xOTExZWNhYzE3N2UiIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDoyZTI5OTFlMC0yOTIzLTI0NGUtOWRhMy1iOGFiZWViZTBmMzEiPiA8eG1wTU06SGlzdG9yeT4gPHJkZjpTZXE+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJjcmVhdGVkIiBzdEV2dDppbnN0YW5jZUlEPSJ4bXAuaWlkOjJlMjk5MWUwLTI5MjMtMjQ0ZS05ZGEzLWI4YWJlZWJlMGYzMSIgc3RFdnQ6d2hlbj0iMjAyMS0wNS0wOVQxMzozMToyNSswMjowMCIgc3RFdnQ6c29mdHdhcmVBZ2VudD0iQWRvYmUgUGhvdG9zaG9wIDIyLjMgKFdpbmRvd3MpIi8+IDxyZGY6bGkgc3RFdnQ6YWN0aW9uPSJzYXZlZCIgc3RFdnQ6aW5zdGFuY2VJRD0ieG1wLmlpZDo2MzljZjM1MC1hMmE4LWQyNDgtYWExYi02MTA5N2EyNDQ4NmUiIHN0RXZ0OndoZW49IjIwMjEtMDUtMDlUMTM6NTA6NTIrMDI6MDAiIHN0RXZ0OnNvZnR3YXJlQWdlbnQ9IkFkb2JlIFBob3Rvc2hvcCAyMi4zIChXaW5kb3dzKSIgc3RFdnQ6Y2hhbmdlZD0iLyIvPiA8L3JkZjpTZXE+IDwveG1wTU06SGlzdG9yeT4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz5bS9u+AAABGUlEQVRIx+2WPQrCQBBG01gYcwQhBCKIWHsGPYA21p7ECwj2Vh7AO9jbWAjBQiEYQSLBQsUf4rcwgXXYFTZapHDgEZjMzIPNZhMrTVOLgwhALLEAZes9ypSX6wLlPI3kBFKJHagwSYXyct3JRJKw5lAjCVldYiKJwF1CLJ/NJDbl5brIROKDhoRnqcNjdb6JJHcUTuKCGi2buFY1M6uszjWRiF1zBRe6rjTvyYrVhYXbwjFr3mokW1YX/yV/STElG80pvPlGcmTNe+AwiUP53JIDa36CNpN0KJ9bsmTN2ZJ1QRP0FM/DWDJWDMh4fLhnJKmD84dhP5GI6NPxrRs4U2yQW54vYwtMwZq2tfjBmIMBKIEhmEiMVPNeISPFwVGZa4cAAAAASUVORK5CYII="""
    layout = [  [sg.Text('')],
                [sg.Text('Printer Setup')],
                [sg.Text('   '),sg.Text('bed temperature in °C',size=(35,1)), sg.InputText(default["bed"],key='bed', justification = "right")],
                [sg.Text('   '),sg.Text('hot-end temperature in °C',size=(35,1)), sg.InputText(default["nozzle"],key='nozzle', justification = "right")],
                [sg.Text('   '),sg.Text('bed size X in mm ',size=(35,1)), sg.InputText(default["printer_x"],key='printer_x', justification = "right")],
                [sg.Text('   '),sg.Text('bed size Y in mm',size=(35,1)), sg.InputText(default["printer_y"],key='printer_y', justification = "right")],
                [sg.Text('   '),sg.Text('offset Z ',size=(35,1)), sg.InputText(default["offset_z"],key='offset_z', justification = "right")],
                [sg.Text('G0 speeds (Travel Moves)')],
                [sg.Text('   '),sg.Text('speed for horizontal non-print moves in mm/s',size=(35,1)), sg.InputText(default["speed_g0_h"],key='speed_g0_h', justification = "right")],
                [sg.Text('   '),sg.Text('speed for vertical non-print moves  in mm/s',size=(35,1)), sg.InputText(default["speed_g0_v"],key='speed_g0_v', justification = "right")],
                [sg.Text('G1 speeds and Flow (Print Moves)')],
                [sg.Text('   '),sg.Text('speed for horizontal print moves in mm/s',size=(35,1)), sg.InputText(default["speed_h"],key='speed_h', justification = "right")],
                [sg.Text('   '),sg.Text('speed for vertical print moves in % (from current)',size=(35,1)), sg.InputText(default["speed_v"],key='speed_v', justification = "right")],
                [sg.Text('   '),sg.Text('flow for horizontal print moves in %',size=(35,1)), sg.InputText(default["flow_h"],key='flow_h', justification = "right")],
                [sg.Text('   '),sg.Text('flow for vertical print moves in %',size=(35,1)), sg.InputText(default["flow_v"],key='flow_v', justification = "right")],
                [sg.Text('Anti-stringing and retraction')],
                [sg.Text('   '),sg.Text('cool-off delay after vertical print move in s',size=(35,1)), sg.InputText(default["cool_off"],key='cool_off', justification = "right")],
                [sg.Text('   '),sg.Text('anti-stringing move after vertical print (true/false)',size=(35,1)), sg.InputText(default["post_move_v"],key='post_move_v', justification = "right")],
                [sg.Text('   '),sg.Text('retraction in mm',size=(35,1)), sg.InputText(default["retraction"],key='retraction', justification = "right")],
                [sg.Text('   '),sg.Text('unRetraction in mm',size=(35,1)), sg.InputText(default["unretraction"],key='unretraction', justification = "right")],
                                
                [sg.Text('export')],
                [sg.Text('   '),sg.Button('export test-piece'),sg.Button('export Gcode'), sg.Button('Quit')],
                [sg.Text('')]]

    ui = sg.Window('table gcode generator v0.1', layout,icon = icon_b64, )
    return ui
    
def generate_defaults():
    defaults = {
    'bed': '62', 
    'printer_x': '300',
    'printer_y': '300',
    'offset_z': '0',
    'nozzle': '205', 
    'speed_g0_h': '150', 
    'speed_g0_v': '10', 
    'speed_h': '15', 
    'speed_v': '100', 
    'flow_h': '100', 
    'flow_v': '100', 
    'cool_off': '7', 
    'post_move_v': 'true', 
    'retraction': '1.5', 
    'unretraction': '1.9'}
    return defaults

def gen_gcode(cfg,in_files,out_files):
    try:
        for in_file, out_file in zip(in_files, out_files):
            with open(out_file, 'w') as output:
                output.write(stringify(cfg))
                with open(in_file) as file:
                    for line in file:
                        comment = get_comment(line)
                        if comment in ("extrudeMove vertical","printMove vertical"):  
                            new_line = replace_relSpeed_relFlow(line,cfg["speed_v"],cfg["flow_v"])
                        elif comment in ("printMove"):
                            new_line = replace_absSpeed_relFlow(line,cfg["speed_h"],cfg["flow_h"])    
                        elif comment == "dwell vertical":
                            new_line = replace_dwell(line,cfg["cool_off"])
                        elif comment == "BedTemp":
                            new_line = replace_temp(line,cfg["bed"])
                        elif comment == "ExtruderTemp":
                            new_line = replace_temp(line,cfg["nozzle"])
                        elif comment in ("positionMove", "positionMove vertical","positionMove skirt","forced_G0 travelBetweenVerticals", "forced_G0"):
                            new_line = replace_speed(line,cfg["speed_g0_h"])
                        elif comment == "zHop":
                            new_line = replace_speed(line,cfg["speed_g0_v"])                   
                        elif comment == "postMove vertical":
                            new_line = post_move(line,cfg["post_move_v"])
                        elif comment == "zHop":
                            new_line = replace_speed(line,cfg["speed_g0_v"])
                        elif comment in ("retract vertical", "retract"):
                            new_line = replace_retract(line, -float(cfg["retraction"]))
                        elif comment in ("UnRetract vertical", "UnRetract"):
                            new_line = replace_retract(line, cfg["unretraction"])
                        else: 
                            new_line = line
                        
                        new_line = printer_offset(new_line,cfg["printer_x"],cfg["printer_y"],cfg["offset_z"])
                        output.write(new_line)
            output.close()
    except Exception as e:
        print(e)
    
def printer_offset(line,printer_x,printer_y,offset_z):
    old_xyz = get_XYZ(line)
    if old_xyz[0] == True:
        new_X = str(round(float(old_xyz[1]) - 150.0 + (float(printer_x)/2),5))
        new_Y = str(round(float(old_xyz[2]) - 150.0 + (float(printer_x)/2),5))
        new_Z = str(round(float(old_xyz[3]) + float(offset_z),5))
        
        new_line = line.replace("X"+old_xyz[1],"X"+new_X)
        new_line = new_line.replace("Y"+old_xyz[2],"Y"+new_X)
        new_line = new_line.replace("Z"+old_xyz[3],"Z"+new_Z)
        return new_line
    else:
        return line 

def get_XYZ(line):
    print("get xyz")
    g1_g0 = ["G1", "G0"]
    if any(g in line[0:4] for g in g1_g0):
        try: 
            pos_X = re.findall(r'(?<=\bX)-?\d+(?:\.\d+)?\b', line)[0]
            pos_Y = re.findall(r'(?<=\bY)-?\d+(?:\.\d+)?\b', line)[0]
            pos_Z = re.findall(r'(?<=\bZ)-?\d+(?:\.\d+)?\b', line)[0]
            return (True, pos_X, pos_Y, pos_Z)
        except Exception as e:
            return (False,False,False,False)
    else:
        return (False,False,False,False)



def get_defaults(last_gcode):
    if last_gcode.is_file(): return read_vals(last_gcode)
    else: return generate_defaults()

def read_vals(last_gcode):
    print("reading form last file")
    with open(last_gcode) as file:
        first_line=file.readline()
        file.close()
        stringified = first_line.split("!")[1].strip()
        print(f"stingi = {stringified}")
        return ast.literal_eval(stringified)
       
def stringify(cfg):
    return f";  config ! {cfg} \n"

def allowed_input(cfg,ui):
    check_val = True
    for key,value in cfg.items():
        if key != 'post_move_v':
            if not numeric(value):
                ui[key].Update(background_color="red")
                check_val = False
            else:
                ui[key].Update(background_color="white")
        elif value not in ("true","false"):
            ui[key].Update(background_color="red")
            check_val = False
        else:
            ui[key].Update(background_color="white")
    return check_val 
        
def post_move(line,post_move_toggle):
    if post_move_toggle == "true": return line
    else: return ""

def replace_absSpeed_relFlow(line,speed,flow_multi):
    old_speed = re.findall(r'(?<=\bF)\d+(?:\.\d+)?\b', line)[0]
    new_speed = str(round(float(speed)*60))
    
    flow = re.findall(r'(?<=\bE)\d+(?:\.\d+)?\b', line)[0]
    new_flow = str(round(float(flow)*(float(flow_multi)/100),5))
    
    new_line = line.replace("F"+old_speed,"F"+new_speed)
    new_line = new_line.replace("E"+flow,"E"+new_flow)
    return new_line

def replace_retract(line, retract):
    old_retract = re.findall(r'(?<=\bE)-?\d+(?:\.\d+)?\b', line)[0]
    new_retract = str(round(float(retract),5))
    new_line = line.replace("E"+old_retract, "E"+new_retract)
    return new_line

def replace_speed(line,speed):
    old_speed = re.findall(r'(?<=\bF)\d+(?:\.\d+)?\b', line)[0]
    new_speed = str(round(float(speed)*60))
    new_line = line.replace("F"+old_speed,"F"+new_speed)
    return new_line

def replace_temp(line,temp):
    old_temp = re.findall(r'(?<=\bS)\d+(?:\.\d+)?\b', line)[0]
    new_temp = str(round(float(temp)))
    new_line = line.replace("S"+old_temp,"S"+new_temp)
    return new_line

def replace_dwell(line,cool_off):
    dwell = re.findall(r'(?<=\bP)\d+(?:\.\d+)?\b', line)[0]
    new_dwell = str(round(float(cool_off)*1000,5))
    new_line = line.replace("P"+dwell,"P"+new_dwell)
    return new_line

def replace_relSpeed_relFlow(line,speed_multi,flow_multi):
    speed = re.findall(r'(?<=\bF)\d+(?:\.\d+)?\b', line)[0]
    flow = re.findall(r'(?<=\bE)\d+(?:\.\d+)?\b', line)[0]
    
    new_speed = str(round(float(speed)*(float(speed_multi)/100),5))
    new_flow = str(round(float(flow)*(float(flow_multi)/100),5))       
    
    new_line = line.replace("F"+speed,"F"+new_speed)
    new_line = new_line.replace("E"+flow,"E"+new_flow)

    return new_line

def get_comment(line):
    comment= line.split(";")[1]
    comment= comment.strip()
    #comments = comment.split(' ')
    return comment

def numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    main()

