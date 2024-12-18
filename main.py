import subprocess as sp
import os
import tkinter as tk
import threading
import speech_recognition as sr
import jellyfish

class AppLauncher:
    def __init__(self):
        self.desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.shortcuts_folder = os.path.join(self.desktop, 'shortcuts')
        if not os.path.exists(self.shortcuts_folder):
            os.makedirs(self.shortcuts_folder)

    def list_available_shortcuts(self):
        try:
            shortcuts = [f.replace('.lnk', '').replace('.exe', '').lower()
                         for f in os.listdir(self.shortcuts_folder) 
                         if f.endswith(('.lnk', '.exe'))]
            return shortcuts
        except Exception as e:
            print(f"Error listing shortcuts: {e}")
            return []
    def launch_app(self, app_name):
        extensions = ['.lnk', '.exe', '.url']
        for ext in extensions:
            shortcut_path = os.path.join(self.shortcuts_folder, app_name + ext)
            if os.path.exists(shortcut_path):
                try:
                    sp.Popen(f'"{shortcut_path}"', shell=True)
                    print(f"Launched: {app_name}")
                    txt_label.configure(text=f"Launched: {app_name}")
                    return True
                except Exception as e:
                    print(f"Error launching {app_name}: {e}")
                    txt_label.configure(text=f"Error launching: {app_name}")
                    return False

            for i in self.list_available_shortcuts():
                levenshtein_distance = jellyfish.levenshtein_distance(app_name, i)
                levenshtein_similarity = 100 - (levenshtein_distance / max(len(app_name), len(i))) * 100
                if levenshtein_similarity > 60:
                    app_name = i

            for ext in extensions:
                shortcut_path = os.path.join(self.shortcuts_folder, app_name + ext)
                if os.path.exists(shortcut_path):
                    try:
                        sp.Popen(f'"{shortcut_path}"', shell=True)
                        print(f"Launched: {app_name}")
                        txt_label.configure(text=f"Launched: {app_name}")
                        return True
                    except Exception as e:
                        print(f"Error launching {app_name}: {e}")
                        txt_label.configure(text=f"Error launching: {app_name}")
                        return False

        print(f"No shortcut found for: {app_name}")
        txt_label.configure(text=f"No shortcut found for: {app_name}")
        return False
def recognize():
    global text
    global muted
    with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            while True:
                if muted == False:
                    audio = recognizer.listen(source)
                    try:
                        text = recognizer.recognize_google(audio, language='en-US')
                        if text.find(KEYWORD) != -1:
                            app.launch_app(text.replace(KEYWORD,"").lower().replace(" ","",1))
                    except:
                        pass

def start():
    thread = threading.Thread(target=recognize)
    thread.daemon = True
    thread.start()
    window.mainloop()
    
app = AppLauncher()
text = ""
window = tk.Tk()
window.title("MicroLaunch")
window.geometry("400x200")
window.configure(bg="#000000")
window.resizable(False,False)
icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
window.iconbitmap(icon_path)
muted = False
KEYWORD = "launch"
recognizer = sr.Recognizer()
txt_label = tk.Label(window,text="",width=400)
txt_label.pack()
mute_button = tk.Button(window,command=lambda: toggle_mute(),text="Mute",height=150, width=400)
mute_button.pack()

def toggle_mute():
    global muted
    global text
    muted = not muted
    window.title("MicroLaunch - Not Listening" if muted else "MicroLaunch - Listening")
    mute_button.config(text="Unmute" if muted else "Mute")
    text = ""

start()
