<img width="1024" height="280" alt="MCSpy" src="https://github.com/user-attachments/assets/35bf8ca2-b5d2-4201-b4f8-b92e2ef28963" />

# Minecraft Server Manager

A comprehensive tool for managing multiple Minecraft Java Edition servers with both GUI and web interfaces, plus advanced development tools for converting Python code to Java for Minecraft plugin development.

![Minecraft Server Manager](https://img.shields.io/badge/Minecraft-Server%20Manager-brightgreen)
![Python to Java](https://img.shields.io/badge/Python%20to%20Java-Converter-blue)


## Features

### Server Management
- **Multiple Server Management**: Create, configure, and manage multiple Minecraft servers from a single interface
- **Server Control**: Start, stop, and restart servers with ease
- **Server Properties Editor**: Edit server.properties files through a user-friendly interface
- **Version Selection**: Choose from the latest releases or snapshots
- **Memory Management**: Configure JVM memory allocation for optimal performance
- **Dual Interface**: Use either the GUI application or web interface
- **Auto-Configuration**: Automatically download server files and configure startup scripts
- **WebSocket Integration**: Real-time server monitoring and log streaming

### Development Tools
- **Python to Java Converter**: Convert Python code to Java for Minecraft plugin development (Bukkit/Spigot/Paper, Forge, Fabric)
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

## Requirements

- Python 3.6+
- Java 17+ (required for Minecraft 1.18 and newer)
- Required Python packages:
  - customtkinter
  - Flask (for web interface)
  - PyInstaller (for creating executables)
  - websockets (for real-time communication)

## Installation

### Quick Installation (Windows)

1. Clone this repository or download the files
2. Run the installation script:
```
   install.bat
```
3. Launch the application using one of the following methods:
   - Run `launch.bat` for the unified launcher
   - Run `launch.bat --gui` to launch the desktop GUI directly
   - Run `launch.bat --python` to launch the Python web interface directly
   - Run `launch.bat --php` to launch the PHP web interface directly

### Manual Installation

1. Clone this repository or download the files
2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
   Or install packages individually:
   ```
   pip install customtkinter flask requests pillow
   ```
3. Ensure Java 17+ is installed and available in your PATH

## Usage

### Unified Launcher (Recommended)

The easiest way to use the Minecraft Server Manager is through the unified launcher:

1. On Windows, double-click `launch.bat`
2. On other platforms, run `python gui_launcher.py`

This will open the launcher interface with three options:
- Desktop GUI
- Python Web Interface
- PHP Web Interface


### Desktop GUI

Run the desktop application:
```
python mc_server_manager_gui.py
```

Menu Bar Overview:
- File: New Server, Import/Export configs and server lists, Open Project/Configs directories, Exit
- Server: Server Management (New/Edit/Delete/Clone) and Server Control (Start/Stop/Restart selected, Start/Stop all)
- Tools: Development Tools (Python to Java Converter), Server Tools (Java check, Download JAR, Backup/Restore), Web Interfaces (Python/PHP Web GUI, WebSocket Server)
- View: Interface (switch tabs) and Theme (Dark/Light/System), Refresh All
- Help: Documentation (User/Quick Start/WebSocket/Installation) and Support (Report Issue, Check Updates, System Info), About

### Web Interface

#### Python Web Server
Start the Python web server:
```
python web_gui.py
```
Then open a browser and navigate to `http://localhost:5000`

#### PHP Web Server
Start the PHP web server:
```
php -S localhost:8000
```
Then open a browser and navigate to `http://localhost:8000/index.php`

### Command Line Setup

For basic server setup via command line:

```
python mc_server_setup.py --version latest --dir ./my_server --min-memory 1G --max-memory 2G --nogui --accept-eula --start
```

## Server Management

1. **Create a New Server**:
   - Specify a name, directory, and Minecraft version
   - Set memory allocation and other options
   - Click "Create Server"

2. **Start/Stop Servers**:
   - Select a server from the list
   - Use the control buttons to manage the server state

3. **Edit Server Properties**:
   - Select a server in the Server Control tab
   - Navigate to the Server Properties tab
   - Modify settings and save changes

## Project Structure

- `mc_server_manager_gui.py`: Main GUI application
- `mc_server_setup.py`: Core functionality for server setup and management
- `web_gui.py`: Web interface using Flask
- `templates/`: HTML templates for web interface
- `icons/`: Status icons for the GUI
- `python_to_java_converter.py`: Convert Python code to Java for Minecraft plugin development
- `create_exe.py`: Build standalone executables (.exe) for Windows

## Python to Java Converter

Convert Python code to Java for Bukkit/Spigot/Paper, Forge, or Fabric:

- Basic usage (Bukkit by default):
  ```
  python python_to_java_converter.py path\to\your_input.py
  ```
- Specify platform and package:
  ```
  python python_to_java_converter.py your.py -o MyPlugin.java -p bukkit --package com.example.myplugin
  ```
- Platforms: `-p bukkit|forge|fabric`

Notes:
- Maps common Python features to Java equivalents and adds platform imports
- Infers simple types by parameter names (player, event, world, etc.)
- A starting point; complex Python features may need manual adjustment

## License

This project is open source and available for personal and educational use.

## Credits

Developed by AsanCraft DEv

---

*Note: This tool is not affiliated with Mojang or Microsoft. Minecraft is a trademark of Mojang Synergies AB.*