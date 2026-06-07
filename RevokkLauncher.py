import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import math
from PIL import Image, ImageTk

angle_x = 0.0
angle_y = 0.0

mouse_x = 400
mouse_y = 300
current_para_x = 0.0
current_para_y = 0.0

try:
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    if getattr(sys, 'frozen', False):
        LAUNCHER_DIR = os.path.dirname(sys.executable)
    else:
        LAUNCHER_DIR = os.path.dirname(os.path.abspath(__file__))

    GAME_ROOT_DIR = os.path.abspath(os.path.join(LAUNCHER_DIR, ".."))

    vr_options = [
        os.path.join(GAME_ROOT_DIR, "Radium_VR.bat"),
        os.path.join(GAME_ROOT_DIR, "RecRoom_VR.bat")
    ]
    
    screen_options = [
        os.path.join(GAME_ROOT_DIR, "Radium_ScreenMode.bat"),
        os.path.join(GAME_ROOT_DIR, "RecRoom_ScreenMode.bat")
    ]

    VR_BATCH_FILE = next((path for path in vr_options if os.path.exists(path)), None)
    
    SCREEN_BATCH_FILE = next((path for path in screen_options if os.path.exists(path)), None)

    def get_layout_path(filename):
        return os.path.join(LAUNCHER_DIR, "Assets", filename)

    TARGET_WIDTH = 800  

    root = tk.Tk()
    root.title("Revokk Launcher")

    bg_path = get_layout_path("RVKKlauncherBG.png")
    if not os.path.exists(bg_path):
        raise FileNotFoundError(f"Missing background image asset:\n{bg_path}")

    bg_orig = Image.open(bg_path)
    orig_w, orig_h = bg_orig.size
    scale_factor = TARGET_WIDTH / orig_w
    target_height = int(orig_h * scale_factor)

    root.geometry(f"{TARGET_WIDTH}x{target_height}")
    root.resizable(False, False)

    mouse_x = TARGET_WIDTH / 2
    mouse_y = target_height / 2

    def load_scaled_image(filename):
        path = get_layout_path(filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing image asset:\n{path}")
        img = Image.open(path)
        return img.resize((TARGET_WIDTH, target_height), Image.Resampling.LANCZOS)

    bg_w_large = int(TARGET_WIDTH * 1.2)
    bg_h_large = int(target_height * 1.2)
    bg_scaled = bg_orig.resize((bg_w_large, bg_h_large), Image.Resampling.LANCZOS)
    bg_img = ImageTk.PhotoImage(bg_scaled)

    txt_scaled = load_scaled_image("RVKKlauncherTXT.png")
    txt_img = ImageTk.PhotoImage(txt_scaled)

    cool_txt_scaled = load_scaled_image("RVKKlauncherCoolTXT.png")
    cool_txt_img = ImageTk.PhotoImage(cool_txt_scaled)

    vr_scaled = load_scaled_image("RVKKlauncherVR.png")
    sm_scaled = load_scaled_image("RVKKlauncherSM.png")

    canvas = tk.Canvas(root, width=TARGET_WIDTH, height=target_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    bg_center_x = TARGET_WIDTH / 2
    bg_center_y = target_height / 2
    bg_canvas_id = canvas.create_image(bg_center_x, bg_center_y, image=bg_img, anchor="center")

    txt_base_x, txt_base_y = 0, 0
    txt_id = canvas.create_image(txt_base_x, txt_base_y, image=txt_img, anchor="nw")

    cool_base_x, cool_base_y = 0, 0
    cool_txt_id = canvas.create_image(cool_base_x, cool_base_y, image=cool_txt_img, anchor="nw")

    vr_bbox = vr_scaled.getbbox()
    if vr_bbox:
        vr_base_x, vr_base_y = vr_bbox[0], vr_bbox[1]
        vr_cropped = vr_scaled.crop(vr_bbox)
        vr_img = ImageTk.PhotoImage(vr_cropped)
    else:
        vr_base_x, vr_base_y = 0, 0
        vr_img = ImageTk.PhotoImage(vr_scaled)
    vr_button = canvas.create_image(vr_base_x, vr_base_y, image=vr_img, anchor="nw")

    sm_bbox = sm_scaled.getbbox()
    if sm_bbox:
        sm_base_x, sm_base_y = sm_bbox[0], sm_bbox[1]
        sm_cropped = sm_scaled.crop(sm_bbox)
        sm_img = ImageTk.PhotoImage(sm_cropped)
    else:
        sm_base_x, sm_base_y = 0, 0
        sm_img = ImageTk.PhotoImage(sm_scaled)
    sm_button = canvas.create_image(sm_base_x, sm_base_y, image=sm_img, anchor="nw")

    def track_mouse(event):
        global mouse_x, mouse_y
        mouse_x = event.x
        mouse_y = event.y

    root.bind("<Motion>", track_mouse)

    max_drift_x = TARGET_WIDTH * 0.05
    max_drift_y = target_height * 0.05

    def animate_all():
        global angle_x, angle_y, current_para_x, current_para_y
        
        angle_x += 0.005  
        angle_y += 0.004  
        bg_offset_x = max_drift_x * math.sin(angle_x)
        bg_offset_y = max_drift_y * math.cos(angle_y)
        canvas.coords(bg_canvas_id, (TARGET_WIDTH / 2) + bg_offset_x, (target_height / 2) + bg_offset_y)
        
        dist_from_center_x = mouse_x - (TARGET_WIDTH / 2)
        dist_from_center_y = mouse_y - (target_height / 2)
        
        target_para_x = dist_from_center_x * 0.035
        target_para_y = dist_from_center_y * 0.035
        
        current_para_x += (target_para_x - current_para_x) * 0.1
        current_para_y += (target_para_y - current_para_y) * 0.1
        
        canvas.coords(txt_id, txt_base_x + current_para_x, txt_base_y + current_para_y)
        canvas.coords(vr_button, vr_base_x + current_para_x, vr_base_y + current_para_y)
        canvas.coords(sm_button, sm_base_x + current_para_x, sm_base_y + current_para_y)
        
        cool_para_x = current_para_x * 0.57  
        cool_para_y = current_para_y * 0.57
        canvas.coords(cool_txt_id, cool_base_x + cool_para_x, cool_base_y + cool_para_y)
        
        root.after(16, animate_all)

    animate_all()

    def launch_vr(event):
        if not VR_BATCH_FILE:
            messagebox.showerror("Launch Error", "Could not find either Radium_VR.bat or RecRoom_VR.bat.")
            return
        try:
            subprocess.Popen(VR_BATCH_FILE, shell=True, cwd=GAME_ROOT_DIR)
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch VR Script:\n{e}")

    def launch_screen(event):
        if not SCREEN_BATCH_FILE:
            messagebox.showerror("Launch Error", "Could not find either Radium_ScreenMode.bat or RecRoom_ScreenMode.bat.")
            return
        try:
            subprocess.Popen(SCREEN_BATCH_FILE, shell=True, cwd=GAME_ROOT_DIR)
        except Exception as e:
            messagebox.showerror("Launch Error", f"Could not launch Screen Mode Script:\n{e}")

    canvas.tag_bind(vr_button, "<Button-1>", launch_vr)
    canvas.tag_bind(sm_button, "<Button-1>", launch_screen)

    canvas.tag_bind(vr_button, "<Enter>", lambda e: canvas.config(cursor="hand2"))
    canvas.tag_bind(vr_button, "<Leave>", lambda e: canvas.config(cursor=""))
    canvas.tag_bind(sm_button, "<Enter>", lambda e: canvas.config(cursor="hand2"))
    canvas.tag_bind(sm_button, "<Leave>", lambda e: canvas.config(cursor=""))

    root.mainloop()

except Exception as critical_error:
    import tkinter as tk
    from tkinter import messagebox
    error_root = tk.Tk()
    error_root.withdraw()
    messagebox.showerror("Launcher Startup Error", f"Application failed to start:\n\n{critical_error}")