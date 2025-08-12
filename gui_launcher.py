import customtkinter as ctk
import tkinter as tk
import subprocess
import threading
import webbrowser
import os
import sys
import time
from pathlib import Path
from PIL import Image, ImageTk

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MinecraftServerLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Manager Launcher")
        self.root.geometry("600x550")
        self.root.minsize(600, 550)
        
        # Initialize variables
        self.php_server_process = None
        self.python_server_process = None
        self.gui_process = None
        
        # Try to load icon
        try:
            icon_path = resource_path(os.path.join("icons", "launcher.svg"))
            if os.path.exists(icon_path):
                # For Windows, use PhotoImage
                if sys.platform == "win32":
                    self.root.iconbitmap(default=icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Minecraft Server Manager", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Choose an interface to launch:", 
                                 font=ctk.CTkFont(size=16))
        desc_label.pack(pady=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill='x', padx=20, pady=20)
        
        # Desktop GUI button
        gui_button = ctk.CTkButton(buttons_frame, text="Desktop GUI", 
                                  font=ctk.CTkFont(size=14),
                                  command=self.launch_gui,
                                  height=40)
        gui_button.pack(fill='x', pady=10)
        
        # Python Web Interface button
        python_web_button = ctk.CTkButton(buttons_frame, text="Python Web Interface", 
                                        font=ctk.CTkFont(size=14),
                                        command=self.launch_python_web,
                                        height=40)
        python_web_button.pack(fill='x', pady=10)
        
        # PHP Web Interface button
        php_web_button = ctk.CTkButton(buttons_frame, text="PHP Web Interface", 
                                     font=ctk.CTkFont(size=14),
                                     command=self.launch_php_web,
                                     height=40)
        php_web_button.pack(fill='x', pady=10)
        
        # Status frame
        self.status_frame = ctk.CTkFrame(main_frame)
        self.status_frame.pack(fill='x', padx=20, pady=10)
        
        # Status labels
        self.gui_status = ctk.CTkLabel(self.status_frame, text="GUI: Not running", 
                                     font=ctk.CTkFont(size=12))
        self.gui_status.pack(anchor='w', pady=2)
        
        self.python_web_status = ctk.CTkLabel(self.status_frame, text="Python Web: Not running", 
                                            font=ctk.CTkFont(size=12))
        self.python_web_status.pack(anchor='w', pady=2)
        
        self.php_web_status = ctk.CTkLabel(self.status_frame, text="PHP Web: Not running", 
                                         font=ctk.CTkFont(size=12))
        self.php_web_status.pack(anchor='w', pady=2)
        
        # Exit button
        exit_button = ctk.CTkButton(main_frame, text="Exit", 
                                   font=ctk.CTkFont(size=14),
                                   command=self.exit_application,
                                   fg_color="#E74C3C",
                                   hover_color="#C0392B",
                                   height=30)
        exit_button.pack(pady=10)
    
    def launch_gui(self):
        if self.gui_process is None or self.gui_process.poll() is not None:
            try:
                self.gui_process = subprocess.Popen([sys.executable, "mc_server_manager_gui.py"])
                self.gui_status.configure(text="GUI: Running")
                threading.Thread(target=self.monitor_process, args=(self.gui_process, self.gui_status, "GUI")).start()
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to launch GUI: {str(e)}")
        else:
            tk.messagebox.showinfo("Info", "GUI is already running")
    
    def launch_python_web(self):
        if self.python_server_process is None or self.python_server_process.poll() is not None:
            try:
                self.python_server_process = subprocess.Popen([sys.executable, "web_gui.py"])
                self.python_web_status.configure(text="Python Web: Running (http://localhost:5000)")
                threading.Thread(target=self.monitor_process, 
                               args=(self.python_server_process, self.python_web_status, "Python Web")).start()
                # Open web browser after a short delay using the main thread
                self.root.after(2000, lambda: webbrowser.open("http://localhost:5000"))
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to launch Python web interface: {str(e)}")
        else:
            tk.messagebox.showinfo("Info", "Python web interface is already running")
            webbrowser.open("http://localhost:5000")
    
    def launch_php_web(self):
        if self.php_server_process is None or self.php_server_process.poll() is not None:
            try:
                # Check if PHP is installed
                try:
                    subprocess.run(["php", "-v"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                except:
                    tk.messagebox.showerror("Error", "PHP is not installed or not in PATH")
                    return
                
                # Start PHP server
                self.php_server_process = subprocess.Popen(["php", "-S", "localhost:8000"], 
                                                        cwd=os.path.dirname(os.path.abspath(__file__)))
                self.php_web_status.configure(text="PHP Web: Running (http://localhost:8000)")
                threading.Thread(target=self.monitor_process, 
                               args=(self.php_server_process, self.php_web_status, "PHP Web")).start()
                # Open web browser after a short delay using the main thread
                self.root.after(2000, lambda: webbrowser.open("http://localhost:8000/index.php"))
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to launch PHP web interface: {str(e)}")
        else:
            tk.messagebox.showinfo("Info", "PHP web interface is already running")
            webbrowser.open("http://localhost:8000/index.php")
    
    def monitor_process(self, process, status_label, name):
        while process.poll() is None:
            time.sleep(1)
        # Use after method to update UI from a thread
        self.root.after(0, lambda: self.update_status(status_label, name))
    
    def update_status(self, status_label, name):
        status_label.configure(text=f"{name}: Not running")
        if name == "GUI":
            self.gui_process = None
        elif name == "Python Web":
            self.python_server_process = None
        elif name == "PHP Web":
            self.php_server_process = None
    
    def exit_application(self):
        # Terminate all running processes
        processes = [
            (self.gui_process, "GUI"),
            (self.python_server_process, "Python Web Server"),
            (self.php_server_process, "PHP Web Server")
        ]
        
        for process, name in processes:
            if process is not None and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=3)
                except:
                    try:
                        process.kill()
                    except:
                        print(f"Could not terminate {name} process")
        
        self.root.quit()
        self.root.destroy()


def main():
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
    
    root = ctk.CTk()
    app = MinecraftServerLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_application)
    root.mainloop()

if __name__ == "__main__":
    main()