import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter as tk
import threading
import subprocess
import os
import json
import time
from pathlib import Path
import sys


# Import functions from the existing setup script
try:
    from mc_server_setup import (
        get_version_info, check_java_version, ensure_dir, download_file,
        write_eula, write_start_script, sha1_file
    )
except ImportError:
    messagebox.showerror("Import Error", "Could not import mc_server_setup.py functions")
    sys.exit(1)


class ServerConfig:
    def __init__(self, name="", directory="", version="latest", min_memory="1G", 
                 max_memory="2G", nogui=True, eula_accepted=False):
        self.name = name
        self.directory = directory
        self.version = version
        self.min_memory = min_memory
        self.max_memory = max_memory
        self.nogui = nogui
        self.eula_accepted = eula_accepted
        self.process = None
    
    def to_dict(self):
        return {
            'name': self.name,
            'directory': self.directory,
            'version': self.version,
            'min_memory': self.min_memory,
            'max_memory': self.max_memory,
            'nogui': self.nogui,
            'eula_accepted': self.eula_accepted
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class MinecraftServerManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Server Manager")
        self.root.geometry("1000x700")
        
        # Initialize variables
        self.servers = []
        self.server_items = []
        self.selected_server = None
        self.current_server = None
        self.config_file = "servers_config.json"
        
        # Initialize settings
        self.auto_create_dirs = tk.BooleanVar(value=True)
        
        # Load status icons
        self.load_status_icons()
        
        self.setup_ui()
        self.load_servers()
    
    def load_status_icons(self):
        """Load status icons for server status display"""
        # Use Unicode symbols as fallback since CustomTkinter doesn't natively support SVG
        # These can be replaced with proper icon loading if needed
        self.running_icon = "🟢"  # Green circle for running
        self.stopped_icon = "🔴"  # Red circle for stopped
        
    def setup_ui(self):
        # Create main tabview for tabs
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.setup_server_list_tab()
        self.setup_server_setup_tab()
        self.setup_server_control_tab()
        self.setup_server_properties_tab()
        self.setup_settings_tab()
    
    def setup_server_list_tab(self):
        self.list_frame = self.notebook.add("Server List")
        
        list_label = ctk.CTkLabel(self.list_frame, text="Minecraft Servers", font=ctk.CTkFont(size=16, weight="bold"))
        list_label.pack(pady=10)
        
        self.server_list_frame = ctk.CTkScrollableFrame(self.list_frame, height=300)
        self.server_list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.server_items = []
        
        buttons_frame = ctk.CTkFrame(self.list_frame)
        buttons_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkButton(buttons_frame, text="New Server", command=self.new_server).pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Edit Server", command=self.edit_server).pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Delete Server", command=self.delete_server).pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Start Server", command=self.start_selected_server).pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Stop Server", command=self.stop_selected_server).pack(side='left', padx=5)
        ctk.CTkButton(buttons_frame, text="Refresh", command=self.refresh_server_list).pack(side='right', padx=5)
    
    def setup_server_setup_tab(self):
        self.setup_frame = self.notebook.add("Server Setup")
        
        scrollable_frame = ctk.CTkScrollableFrame(self.setup_frame)
        scrollable_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        setup_label = ctk.CTkLabel(scrollable_frame, text="Create New Minecraft Server", font=ctk.CTkFont(size=16, weight="bold"))
        setup_label.pack(pady=10)
        
        form_frame = ctk.CTkFrame(scrollable_frame)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Name
        ctk.CTkLabel(form_frame, text="Server Name:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.name_var = tk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.name_var, width=300).grid(row=0, column=1, padx=10, pady=5)
        
        # Directory
        ctk.CTkLabel(form_frame, text="Server Directory:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        dir_frame = ctk.CTkFrame(form_frame)
        dir_frame.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
        self.dir_var = tk.StringVar()
        ctk.CTkEntry(dir_frame, textvariable=self.dir_var, width=250).pack(side='left', padx=5)
        ctk.CTkButton(dir_frame, text="Browse", command=self.browse_directory, width=60).pack(side='right', padx=5)
        
        # Version
        ctk.CTkLabel(form_frame, text="Minecraft Version:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.version_var = tk.StringVar(value="latest")
        ctk.CTkComboBox(form_frame, values=["latest", "1.20", "1.19", "1.18", "custom"], variable=self.version_var, width=300).grid(row=2, column=1, padx=10, pady=5)
        
        # Custom version
        ctk.CTkLabel(form_frame, text="Custom Version:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.custom_version_var = tk.StringVar()
        ctk.CTkEntry(form_frame, textvariable=self.custom_version_var, width=300).grid(row=3, column=1, padx=10, pady=5)
        
        # Memory
        mem_frame = ctk.CTkFrame(form_frame)
        mem_frame.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
        ctk.CTkLabel(form_frame, text="Memory:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        ctk.CTkLabel(mem_frame, text="Min:").pack(side='left', padx=5)
        self.min_mem_var = tk.StringVar(value="1G")
        ctk.CTkEntry(mem_frame, textvariable=self.min_mem_var, width=60).pack(side='left', padx=5)
        ctk.CTkLabel(mem_frame, text="Max:").pack(side='left', padx=5)
        self.max_mem_var = tk.StringVar(value="2G")
        ctk.CTkEntry(mem_frame, textvariable=self.max_mem_var, width=60).pack(side='left', padx=5)
        
        # Options
        options_frame = ctk.CTkFrame(scrollable_frame)
        options_frame.pack(fill='x', padx=10, pady=10)
        
        self.nogui_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="No GUI", variable=self.nogui_var).pack(anchor='w', padx=10, pady=5)
        
        self.eula_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="Accept EULA", variable=self.eula_var).pack(anchor='w', padx=10, pady=5)
        
        self.force_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="Force overwrite existing files", variable=self.force_var).pack(anchor='w', padx=10, pady=5)
        
        # Progress and status
        progress_frame = ctk.CTkFrame(scrollable_frame)
        progress_frame.pack(fill='x', padx=10, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill='x', padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(progress_frame, text="Ready")
        self.status_label.pack(padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(scrollable_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.setup_button = ctk.CTkButton(button_frame, text="Setup Server", command=self.setup_server)
        self.setup_button.pack(side='left', padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Clear Log", command=self.clear_setup_log).pack(side='right', padx=10, pady=10)
        
        self.java_status = ctk.CTkLabel(button_frame, text="Checking Java...")
        self.java_status.pack(padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="Check Java", command=self.check_java).pack(padx=10, pady=10)
        
        # Log
        log_frame = ctk.CTkFrame(scrollable_frame)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(log_frame, text="Setup Log", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.setup_log = ctk.CTkTextbox(log_frame, height=200)
        self.setup_log.pack(fill='both', expand=True, padx=10, pady=10)
    
    def setup_server_control_tab(self):
        self.control_frame = self.notebook.add("Server Control")
        
        control_label = ctk.CTkLabel(self.control_frame, text="Server Control", font=ctk.CTkFont(size=16, weight="bold"))
        control_label.pack(pady=10)
        
        # Server selection
        select_frame = ctk.CTkFrame(self.control_frame)
        select_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(select_frame, text="Select Server:").pack(side='left', padx=10)
        self.control_server_var = tk.StringVar()
        self.control_server_combo = ctk.CTkComboBox(select_frame, variable=self.control_server_var, command=self.on_control_server_selected)
        self.control_server_combo.pack(side='left', padx=10, fill='x', expand=True)
        
        # Control buttons
        control_buttons = ctk.CTkFrame(self.control_frame)
        control_buttons.pack(fill='x', padx=10, pady=5)
        
        self.start_btn = ctk.CTkButton(control_buttons, text="Start Server", command=self.start_server_control)
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ctk.CTkButton(control_buttons, text="Stop Server", command=self.stop_server_control)
        self.stop_btn.pack(side='left', padx=5)
        
        self.restart_btn = ctk.CTkButton(control_buttons, text="Restart Server", command=self.restart_server_control)
        self.restart_btn.pack(side='left', padx=5)
        
        ctk.CTkButton(control_buttons, text="Open Directory", command=self.open_server_directory).pack(side='right', padx=5)
        
        # Status
        self.server_status_label = ctk.CTkLabel(self.control_frame, text="No server selected")
        self.server_status_label.pack(pady=5)
        
        # Console
        console_frame = ctk.CTkFrame(self.control_frame)
        console_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        console_label = ctk.CTkLabel(console_frame, text="Server Console", font=ctk.CTkFont(weight="bold"))
        console_label.pack(pady=5)
        
        # Console controls
        console_controls = ctk.CTkFrame(console_frame)
        console_controls.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkButton(console_controls, text="Clear Console", command=self.clear_console).pack(side='left', padx=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(console_controls, text="Auto-scroll", variable=self.auto_scroll_var).pack(side='left', padx=5)
        
        # Console textbox
        self.console_output = ctk.CTkTextbox(console_frame, height=300, font=ctk.CTkFont(family="Consolas", size=10))
        self.console_output.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Command input
        cmd_frame = ctk.CTkFrame(console_frame)
        cmd_frame.pack(fill='x', padx=10, pady=5)
        
        ctk.CTkLabel(cmd_frame, text="Command:").pack(side='left')
        self.command_var = tk.StringVar()
        self.command_entry = ctk.CTkEntry(cmd_frame, textvariable=self.command_var, state='disabled')
        self.command_entry.pack(side='left', fill='x', expand=True, padx=5)
        self.command_entry.bind('<Return>', self.send_command)
        
        self.send_btn = ctk.CTkButton(cmd_frame, text="Send", command=self.send_command, state='disabled')
        self.send_btn.pack(side='right')
    
    def setup_server_properties_tab(self):
        """Setup the Server Properties tab for editing server.properties files"""
        self.properties_frame = self.notebook.add("Server Properties")
        frame = ctk.CTkScrollableFrame(self.properties_frame)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        ctk.CTkLabel(frame, text="Edit server.properties for the selected server", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
    
        form = ctk.CTkFrame(frame)
        form.pack(fill='x', padx=10, pady=5)
    
        # Variables for server properties
        self.prop_motd = tk.StringVar(value="A Minecraft Server")
        self.prop_pvp = tk.BooleanVar(value=True)
        self.prop_online_mode = tk.BooleanVar(value=True)
        self.prop_difficulty = tk.StringVar(value="easy")
        self.prop_gamemode = tk.StringVar(value="survival")
        self.prop_max_players = tk.IntVar(value=20)
        self.prop_view_distance = tk.IntVar(value=10)
        self.prop_allow_flight = tk.BooleanVar(value=False)
        self.prop_white_list = tk.BooleanVar(value=False)
        self.prop_spawn_protection = tk.IntVar(value=16)
        self.prop_server_port = tk.IntVar(value=25565)
        self.prop_enable_command_block = tk.BooleanVar(value=False)
    
        # Helper function to add form rows
        def add_row(label, widget):
            row = ctk.CTkFrame(form)
            row.pack(fill='x', padx=5, pady=4)
            ctk.CTkLabel(row, text=label, width=180, anchor='w').pack(side='left')
            widget.pack(side='left', fill='x', expand=True, padx=5)
    
        # Add form fields
        add_row("MOTD:", ctk.CTkEntry(form, textvariable=self.prop_motd, width=400))
        add_row("PVP Enabled:", ctk.CTkSwitch(form, text="", variable=self.prop_pvp))
        add_row("Online Mode:", ctk.CTkSwitch(form, text="", variable=self.prop_online_mode))
        add_row("Difficulty:", ctk.CTkOptionMenu(form, values=["peaceful","easy","normal","hard"], variable=self.prop_difficulty))
        add_row("Game Mode:", ctk.CTkOptionMenu(form, values=["survival","creative","adventure","spectator"], variable=self.prop_gamemode))
        add_row("Max Players:", ctk.CTkEntry(form, textvariable=self.prop_max_players, width=120))
        add_row("View Distance:", ctk.CTkEntry(form, textvariable=self.prop_view_distance, width=120))
        add_row("Allow Flight:", ctk.CTkSwitch(form, text="", variable=self.prop_allow_flight))
        add_row("Whitelist:", ctk.CTkSwitch(form, text="", variable=self.prop_white_list))
        add_row("Spawn Protection:", ctk.CTkEntry(form, textvariable=self.prop_spawn_protection, width=120))
        add_row("Server Port:", ctk.CTkEntry(form, textvariable=self.prop_server_port, width=120))
        add_row("Enable Command Block:", ctk.CTkSwitch(form, text="", variable=self.prop_enable_command_block))
    
        # Buttons
        btns = ctk.CTkFrame(frame)
        btns.pack(fill='x', padx=10, pady=10)
        ctk.CTkButton(btns, text="Load from File", command=self.load_server_properties).pack(side='left', padx=5)
        ctk.CTkButton(btns, text="Save to File", command=self.save_server_properties).pack(side='left', padx=5)
    
    def setup_settings_tab(self):
        self.settings_frame = self.notebook.add("Settings")
        
        settings_label = ctk.CTkLabel(self.settings_frame, text="Application Settings", font=ctk.CTkFont(size=16, weight="bold"))
        settings_label.pack(pady=10)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(self.settings_frame)
        theme_frame.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(theme_frame, text="Appearance", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=10, pady=(10,5))
        
        # Appearance mode selection
        appearance_frame = ctk.CTkFrame(theme_frame)
        appearance_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(appearance_frame, text="Mode:").pack(side='left', padx=5)
        
        self.appearance_var = ctk.StringVar(value="dark")
        appearance_combo = ctk.CTkComboBox(appearance_frame, 
                                         variable=self.appearance_var,
                                         values=["light", "dark", "system"],
                                         command=self.change_appearance_mode)
        appearance_combo.pack(side='left', padx=5)
        
        # Color theme selection
        color_frame = ctk.CTkFrame(theme_frame)
        color_frame.pack(fill='x', padx=10, pady=5)
        ctk.CTkLabel(color_frame, text="Theme:").pack(side='left', padx=5)
        
        self.color_theme_var = ctk.StringVar(value="blue")
        color_combo = ctk.CTkComboBox(color_frame,
                                    variable=self.color_theme_var,
                                    values=["blue", "green", "dark-blue"],
                                    command=self.change_color_theme)
        color_combo.pack(side='left', padx=5)
        
        # Directory Settings
        dir_frame = ctk.CTkFrame(self.settings_frame)
        dir_frame.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(dir_frame, text="Directory Settings", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=10, pady=(10,5))
        
        ctk.CTkCheckBox(dir_frame, text="Auto-create directories when opening", variable=self.auto_create_dirs).pack(anchor='w', padx=10, pady=5)
        
        # Java check
        java_frame = ctk.CTkFrame(self.settings_frame)
        java_frame.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(java_frame, text="Java Installation", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=10, pady=(10,5))
        
        self.java_status = ctk.CTkLabel(java_frame, text="Checking Java...")
        self.java_status.pack(padx=10, pady=10)
        
        ctk.CTkButton(java_frame, text="Check Java", command=self.check_java).pack(padx=10, pady=5)
        
        # About
        about_frame = ctk.CTkFrame(self.settings_frame)
        about_frame.pack(fill='x', padx=20, pady=10)
        ctk.CTkLabel(about_frame, text="About", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor='w', padx=10, pady=(10,5))
        
        about_text = "Minecraft Server Manager GUI\nBased on mc_server_setup.py\nManage multiple Minecraft servers easily\nAsanCraft DEv\n ;)"
        ctk.CTkLabel(about_frame, text=about_text, justify='center').pack(padx=10, pady=10)
        
        # Initial Java check
        self.root.after(1000, self.check_java)

    def change_appearance_mode(self, choice):
        """Change the appearance mode (light/dark/system)"""
        ctk.set_appearance_mode(choice)

    def change_color_theme(self, choice):
        """Change the color theme (blue/green/dark-blue)"""
        ctk.set_default_color_theme(choice)
        messagebox.showinfo("Theme Change", 
                          "Color theme will be fully applied on next app restart.\n"
                          "Some elements may update immediately.")

    def _get_properties_path(self):
        """Get the path to server.properties for the currently selected server"""
        if not self.current_server:
            return None
        return os.path.join(self.current_server.directory, "server.properties")

    def load_server_properties(self):
        """Load server.properties file into the form fields"""
        path = self._get_properties_path()
        if not path:
            messagebox.showwarning("No Selection", "Please select a server in Server Control tab")
            return
        if not os.path.exists(path):
            messagebox.showwarning("Missing File", "server.properties not found. Start the server once to generate it, or Save to create a new one.")
            return
        try:
            props = {}
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        k, v = line.split('=', 1)
                        props[k.strip()] = v.strip()
            
            # Populate fields with loaded values
            self.prop_motd.set(props.get('motd', 'A Minecraft Server'))
            self.prop_pvp.set(props.get('pvp', 'true').lower() == 'true')
            self.prop_online_mode.set(props.get('online-mode', 'true').lower() == 'true')
            
            # Handle difficulty (may be numeric or string)
            difficulty = props.get('difficulty', '1')
            if difficulty.isdigit():
                difficulty_map = {"0":"peaceful","1":"easy","2":"normal","3":"hard"}
                self.prop_difficulty.set(difficulty_map.get(difficulty, 'easy'))
            else:
                self.prop_difficulty.set(difficulty if difficulty in ['peaceful','easy','normal','hard'] else 'easy')
            
            # Handle gamemode (may be numeric or string)
            gamemode = props.get('gamemode', '0')
            if gamemode.isdigit():
                gamemode_map = {"0":"survival","1":"creative","2":"adventure","3":"spectator"}
                self.prop_gamemode.set(gamemode_map.get(gamemode, 'survival'))
            else:
                self.prop_gamemode.set(gamemode if gamemode in ['survival','creative','adventure','spectator'] else 'survival')
            
            self.prop_max_players.set(int(props.get('max-players', '20')))
            self.prop_view_distance.set(int(props.get('view-distance', '10')))
            self.prop_allow_flight.set(props.get('allow-flight', 'false').lower() == 'true')
            self.prop_white_list.set(props.get('white-list', props.get('enforce-whitelist','false')).lower() == 'true')
            self.prop_spawn_protection.set(int(props.get('spawn-protection', '16')))
            self.prop_server_port.set(int(props.get('server-port', '25565')))
            self.prop_enable_command_block.set(props.get('enable-command-block', 'false').lower() == 'true')
            
            messagebox.showinfo("Loaded", "server.properties loaded successfully")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load server.properties: {e}")

    def save_server_properties(self):
        """Save the form fields to server.properties file"""
        path = self._get_properties_path()
        if not path:
            messagebox.showwarning("No Selection", "Please select a server in Server Control tab")
            return
        try:
            # Auto-create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            # Build properties mapping
            mapping = {
                'motd': self.prop_motd.get(),
                'pvp': str(self.prop_pvp.get()).lower(),
                'online-mode': str(self.prop_online_mode.get()).lower(),
                'difficulty': self.prop_difficulty.get(),
                'gamemode': self.prop_gamemode.get(),
                'max-players': str(self.prop_max_players.get()),
                'view-distance': str(self.prop_view_distance.get()),
                'allow-flight': str(self.prop_allow_flight.get()).lower(),
                'white-list': str(self.prop_white_list.get()).lower(),
                'spawn-protection': str(self.prop_spawn_protection.get()),
                'server-port': str(self.prop_server_port.get()),
                'enable-command-block': str(self.prop_enable_command_block.get()).lower(),
            }
            
            # Write properties file
            lines = [f"{k}={v}\n" for k, v in mapping.items()]
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            messagebox.showinfo("Saved", f"server.properties saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save server.properties: {e}")

    def log_setup(self, message):
        self.setup_log.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.setup_log.see(tk.END)
        self.root.update()

    def clear_setup_log(self):
        self.setup_log.delete("1.0", tk.END)

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)
            if not self.name_var.get().strip():
                folder_name = os.path.basename(os.path.normpath(directory))
                if folder_name:
                    self.name_var.set(self.generate_unique_name(folder_name))

    def check_java(self):
        def check():
            try:
                ok, output = check_java_version()
                if ok:
                    self.java_status.configure(text="✓ Java 17+ detected")
                else:
                    self.java_status.configure(text="⚠ Java 17+ required")
            except Exception as e:
                self.java_status.configure(text=f"✗ Java check failed: {e}")
        
        threading.Thread(target=check, daemon=True).start()

    def setup_server(self):
        def setup():
            try:
                self.setup_button.configure(state='disabled')
                self.progress_bar.set(0)
                
                name = self.name_var.get().strip()
                directory = self.dir_var.get().strip()
                version = self.version_var.get()
                if version == "custom":
                    version = self.custom_version_var.get().strip()
                min_mem = self.min_mem_var.get().strip()
                max_mem = self.max_mem_var.get().strip()
                nogui = self.nogui_var.get()
                accept_eula = self.eula_var.get()
                force = self.force_var.get()
                
                if not name and directory:
                    base_name = os.path.basename(os.path.normpath(directory))
                    if base_name:
                        name = self.generate_unique_name(base_name)
                        self.name_var.set(name)
                if not directory:
                    messagebox.showerror("Error", "Please provide server directory")
                    return
                if not name:
                    name = self.generate_unique_name("server")
                    self.name_var.set(name)

                self.log_setup(f"Setting up server '{name}'")
                self.status_label.configure(text="Creating directory...")
                self.progress_bar.set(0.1)
                
                try:
                    ensure_dir(directory)
                    test_file = os.path.join(directory, ".test_write")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    self.log_setup(f"Directory created/verified: {directory}")
                except PermissionError:
                    raise RuntimeError(f"Permission denied: Cannot write to directory '{directory}'. Check folder permissions.")
                except OSError as e:
                    raise RuntimeError(f"Cannot create/access directory '{directory}': {e}")
                
                self.status_label.configure(text="Resolving version...")
                self.progress_bar.set(0.2)
                
                try:
                    version_id, server_download = get_version_info(version)
                    url = server_download.get("url")
                    expected_sha1 = server_download.get("sha1")
                    self.log_setup(f"Resolved version: {version_id}")
                except Exception as e:
                    raise RuntimeError(f"Failed to resolve version '{version}': {e}")
                
                self.progress_bar.set(0.3)
                
                jar_path = os.path.join(directory, "server.jar")
                if os.path.exists(jar_path) and not force:
                    self.log_setup("server.jar already exists, skipping download")
                else:
                    self.status_label.configure(text="Downloading server.jar...")
                    self.log_setup("Downloading server.jar...")
                    try:
                        download_file(url, jar_path)
                        self.log_setup("Download complete")
                    except Exception as e:
                        raise RuntimeError(f"Failed to download server.jar: {e}")
                
                self.progress_bar.set(0.7)
                
                if expected_sha1 and os.path.exists(jar_path):
                    self.status_label.configure(text="Verifying SHA1...")
                    actual_sha1 = sha1_file(jar_path)
                    if actual_sha1.lower() != expected_sha1.lower():
                        raise RuntimeError(f"SHA1 mismatch for server.jar")
                    self.log_setup("SHA1 verified")
                
                self.progress_bar.set(0.8)
                
                self.status_label.configure(text="Writing configuration...")
                try:
                    write_eula(directory, accept_eula)
                    write_start_script(directory, min_mem, max_mem, nogui)
                    self.log_setup("Configuration files written")
                except Exception as e:
                    raise RuntimeError(f"Failed to write configuration files: {e}")
                
                self.progress_bar.set(0.9)
                
                server_config = ServerConfig(
                    name=name,
                    directory=directory,
                    version=version_id,
                    min_memory=min_mem,
                    max_memory=max_mem,
                    nogui=nogui,
                    eula_accepted=accept_eula
                )
                
                existing = next((s for s in self.servers if s.name == name), None)
                if existing:
                    idx = self.servers.index(existing)
                    self.servers[idx] = server_config
                else:
                    self.servers.append(server_config)
                
                self.save_servers()
                self.refresh_server_list()
                self.update_control_server_list()
                
                self.progress_bar.set(1.0)
                self.status_label.configure(text="Setup complete!")
                self.log_setup("Setup complete!")
                
            except Exception as e:
                self.log_setup(f"Error: {e}")
                messagebox.showerror("Setup Error", str(e))
            finally:
                self.setup_button.configure(state='normal')
        
        threading.Thread(target=setup, daemon=True).start()

    def generate_unique_name(self, base_name):
        existing = {s.name for s in self.servers}
        name = base_name or "server"
        idx = 2
        while name in existing:
            name = f"{base_name}_{idx}"
            idx += 1
        return name

    def load_servers(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.servers = [ServerConfig.from_dict(s) for s in data]
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not load servers: {e}")
        
        self.refresh_server_list()
        self.update_control_server_list()

    def save_servers(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump([s.to_dict() for s in self.servers], f, indent=2)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save servers: {e}")

    def refresh_server_list(self):
        for item in self.server_items:
            item.destroy()
        self.server_items.clear()
        
        for i, server in enumerate(self.servers):
            status = "Stopped"
            color = "red"
            icon = self.stopped_icon
            if server.process and server.process.poll() is None:
                status = "Running"
                color = "green"
                icon = self.running_icon
            
            item_frame = ctk.CTkFrame(self.server_list_frame)
            item_frame.pack(fill='x', padx=5, pady=2)
            
            name_label = ctk.CTkLabel(item_frame, text=f"Name: {server.name}", font=ctk.CTkFont(weight="bold"))
            name_label.pack(anchor='w', padx=10, pady=2)
            
            version_label = ctk.CTkLabel(item_frame, text=f"Version: {server.version}")
            version_label.pack(anchor='w', padx=10)
            
            dir_label = ctk.CTkLabel(item_frame, text=f"Directory: {server.directory}")
            dir_label.pack(anchor='w', padx=10)
            
            # Status with icon
            status_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            status_frame.pack(anchor='w', padx=10, pady=2, fill='x')
            
            status_icon_label = ctk.CTkLabel(status_frame, text=icon, text_color=color, font=ctk.CTkFont(size=14))
            status_icon_label.pack(side='left')
            
            status_label = ctk.CTkLabel(status_frame, text=f"Status: {status}", text_color=color)
            status_label.pack(side='left', padx=(5, 0))
            
            item_frame.server_index = i
            self.server_items.append(item_frame)
            
            def on_click(event, index=i):
                self.selected_server = self.servers[index]
                
            item_frame.bind("<Button-1>", on_click)

    def update_control_server_list(self):
        server_names = [s.name for s in self.servers]
        self.control_server_combo.configure(values=server_names)
        if server_names and not self.control_server_var.get():
            self.control_server_combo.set(server_names[0])

    def get_selected_server(self):
        return self.selected_server

    def new_server(self):
        self.name_var.set("")
        self.dir_var.set("")
        self.version_var.set("latest")
        self.custom_version_var.set("")
        self.min_mem_var.set("1G")
        self.max_mem_var.set("2G")
        self.nogui_var.set(True)
        self.eula_var.set(False)
        self.force_var.set(False)
        self.notebook.set("Server Setup")

    def edit_server(self):
        server = self.get_selected_server()
        if not server:
            messagebox.showwarning("No Selection", "Please select a server to edit")
            return
        
        self.name_var.set(server.name)
        self.dir_var.set(server.directory)
        self.version_var.set("custom")
        self.custom_version_var.set(server.version)
        self.min_mem_var.set(server.min_memory)
        self.max_mem_var.set(server.max_memory)
        self.nogui_var.set(server.nogui)
        self.eula_var.set(server.eula_accepted)
        self.force_var.set(False)
        self.notebook.set("Server Setup")

    def delete_server(self):
        server = self.get_selected_server()
        if not server:
            messagebox.showwarning("No Selection", "Please select a server to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete server '{server.name}'?\n\nThis will only remove it from the list, not delete files."):
            if server.process and server.process.poll() is None:
                server.process.terminate()
            
            self.servers.remove(server)
            self.save_servers()
            self.refresh_server_list()
            self.update_control_server_list()

    def start_selected_server(self):
        server = self.get_selected_server()
        if not server:
            messagebox.showwarning("No Selection", "Please select a server to start")
            return
        
        self.start_server(server)

    def stop_selected_server(self):
        server = self.get_selected_server()
        if not server:
            messagebox.showwarning("No Selection", "Please select a server to stop")
            return
        
        self.stop_server(server)

    def start_server(self, server):
        if server.process and server.process.poll() is None:
            messagebox.showinfo("Already Running", f"Server '{server.name}' is already running")
            return
        
        try:
            java_ok, java_output = check_java_version()
            if not java_ok:
                error_msg = f"Java 17+ is required to run Minecraft servers.\n\nJava check result: {java_output}\n\nPlease install Java 17 or newer and ensure it's in your PATH."
                messagebox.showerror("Java Error", error_msg)
                return
            
            jar_path = os.path.join(server.directory, "server.jar")
            if not os.path.isfile(jar_path):
                messagebox.showerror("Error", f"server.jar not found in {server.directory}\n\nRun server setup first.")
                return
            
            if not os.access(server.directory, os.W_OK):
                messagebox.showerror("Permission Error", f"No write access to server directory: {server.directory}")
                return
            
            cmd = [
                "java",
                f"-Xms{server.min_memory}",
                f"-Xmx{server.max_memory}",
                "-jar",
                jar_path,
            ]
            if server.nogui:
                cmd.append("nogui")
            
            try:
                server.process = subprocess.Popen(
                    cmd,
                    cwd=server.directory,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                
                threading.Thread(target=self._stream_server_output, args=(server,), daemon=True).start()
                self.append_console(f"Starting server '{server.name}'...\n")
                self.update_server_status()
                self.refresh_server_list()  # Refresh list to update status icons
                
            except FileNotFoundError:
                messagebox.showerror("Java Error", "Java not found. Please ensure Java 17+ is installed and in your PATH.")
            except Exception as e:
                messagebox.showerror("Start Error", f"Failed to start server: {e}")
                
        except Exception as e:
            messagebox.showerror("Start Error", str(e))

    def stop_server(self, server):
        if not server.process or server.process.poll() is not None:
            messagebox.showinfo("Not Running", f"Server '{server.name}' is not running")
            return
        
        try:
            if server.process.stdin and not server.process.stdin.closed:
                server.process.stdin.write("stop\n")
                server.process.stdin.flush()
            
            # Wait for graceful shutdown
            try:
                server.process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(server.process.pid)], check=False)
                else:
                    server.process.kill()
                self.append_console(f"[Force killed server '{server.name}']\n")
            
            server.process = None
            self.append_console(f"[Server '{server.name}' stopped]\n")
            self.update_server_status()
            self.refresh_server_list()  # Refresh list to update status icons
            
        except Exception as e:
            messagebox.showerror("Stop Error", f"Failed to stop server: {e}")

    def on_control_server_selected(self, selection=None):
        if not selection:
            selection = self.control_server_var.get()
        
        self.current_server = None
        for server in self.servers:
            if server.name == selection:
                self.current_server = server
                break
        
        self.update_server_status()

    def update_server_status(self):
        if not self.current_server:
            self.server_status_label.configure(text="No server selected")
            self.command_entry.configure(state='disabled')
            self.send_btn.configure(state='disabled')
            return
        
        if self.current_server.process and self.current_server.process.poll() is None:
            status_text = f"{self.running_icon} Server '{self.current_server.name}' is RUNNING"
            self.server_status_label.configure(text=status_text, text_color="green")
            self.command_entry.configure(state='normal')
            self.send_btn.configure(state='normal')
        else:
            status_text = f"{self.stopped_icon} Server '{self.current_server.name}' is STOPPED"
            self.server_status_label.configure(text=status_text, text_color="red")
            self.command_entry.configure(state='disabled')
            self.send_btn.configure(state='disabled')

    def start_server_control(self):
        if self.current_server:
            self.start_server(self.current_server)

    def stop_server_control(self):
        if self.current_server:
            self.stop_server(self.current_server)

    def restart_server_control(self):
        if self.current_server:
            self.stop_server(self.current_server)
            # Wait for stop, then start
            self.root.after(3000, lambda: self.start_server(self.current_server))

    def append_console(self, text, tag=None):
        if hasattr(self, 'console_output'):
            try:
                self.console_output.insert(tk.END, text)
                
                # Auto-scroll if enabled
                if self.auto_scroll_var.get():
                    self.console_output.see(tk.END)
                
                # Limit console buffer to prevent memory issues
                lines = self.console_output.get("1.0", tk.END).split('\n')
                if len(lines) > 1000:
                    lines = lines[-800:]
                    self.console_output.delete("1.0", tk.END)
                    self.console_output.insert("1.0", '\n'.join(lines))
                    
            except Exception as e:
                print(f"Console append error: {e}")

    def clear_console(self):
        if hasattr(self, 'console_output'):
            self.console_output.delete("1.0", tk.END)

    def send_command(self, event=None):
        if not self.current_server or not self.current_server.process:
            return
        
        command = self.command_var.get().strip()
        if not command:
            return
        
        try:
            if self.current_server.process.stdin and not self.current_server.process.stdin.closed:
                self.current_server.process.stdin.write(f"{command}\n")
                self.current_server.process.stdin.flush()
                self.append_console(f"> {command}\n")
                self.command_var.set("")
        except Exception as e:
            messagebox.showerror("Send Command Error", str(e))

    def open_server_directory(self):
        if not self.current_server:
            messagebox.showwarning("No Selection", "Please select a server first")
            return
        
        try:
            # Auto-create directory if setting is enabled and it doesn't exist
            if self.auto_create_dirs.get() and not os.path.exists(self.current_server.directory):
                os.makedirs(self.current_server.directory, exist_ok=True)
                self.append_console(f"Created directory: {self.current_server.directory}\n")
            
            if os.name == 'nt':  # Windows
                os.startfile(self.current_server.directory)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.run(['open' if sys.platform == 'darwin' else 'xdg-open', self.current_server.directory])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    def _stream_server_output(self, server):
        try:
            while True:
                if server.process is None:
                    break
                line = server.process.stdout.readline()
                if not line:
                    if server.process.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue
                self.append_console(line)
        except Exception as e:
            self.append_console(f"[Console reader error: {e}]\n")
        finally:
            self.append_console("[Process ended]\n")
            self.update_server_status()


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = MinecraftServerManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()