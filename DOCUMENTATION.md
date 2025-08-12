# Minecraft Server Manager - Documentation

This document provides detailed information about the Minecraft Server Manager tool, its components, and how to use them effectively.

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Installation](#installation)
4. [GUI Interface](#gui-interface)
5. [Web Interface](#web-interface)
6. [Command Line Interface](#command-line-interface)
7. [Server Configuration](#server-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)

## Overview

The Minecraft Server Manager is a comprehensive tool designed to simplify the process of creating, configuring, and managing multiple Minecraft Java Edition servers. It provides three interfaces:

- A GUI application built with customtkinter
- A web interface built with Flask
- A command-line interface for scripting and automation

## Components

### Core Components

- **mc_server_setup.py**: Contains the core functionality for server setup, including:
  - Fetching version information from Mojang API
  - Downloading server files
  - Verifying file integrity
  - Creating startup scripts
  - Checking Java version compatibility
  - Starting and stopping servers

- **mc_server_manager_gui.py**: Provides a graphical user interface with:
  - Server list management
  - Server creation wizard
  - Server control panel
  - Server properties editor
  - Console output viewer
  - Settings and appearance customization

- **web_gui.py**: Offers a Python-based web interface with:
  - Server management via browser
  - Version selection
  - Server status monitoring
  - Configuration options

- **index.php** and **api.php**: Provide a PHP-based web interface with:
  - Server setup and management
  - Version selection
  - Server properties configuration
  - Server status monitoring

- **gui_launcher.py**: A unified launcher that allows users to choose between:
  - Desktop GUI application
  - Python web interface
  - PHP web interface

### Supporting Files

- **templates/index.html**: HTML template for the web interface
- **icons/**: Contains status icons for the GUI
- **config.php**: PHP implementation for web-based server management

## Installation

### Prerequisites

- Python 3.6 or newer (not needed if using the executable version)
- Java 17 or newer (required for Minecraft 1.18+)
- Internet connection for downloading server files
- PHP (optional, only needed for PHP web interface)

### Setup

1. Clone the repository or download the files to your computer
2. Install required Python packages:
   ```
   pip install customtkinter Pillow flask requests
   ```
   Or use the requirements file:
   ```
   pip install -r requirements.txt
   ```
3. Verify Java installation:
   ```
   java -version
   ```
   Ensure the version is 17 or higher
4. For the PHP web interface, ensure PHP is installed and available in your PATH
5. On Windows, you can use the quick installation batch file:
   ```
   install.bat
   ```

### Setup

1. Clone the repository or download the files to your computer
2. Install required Python packages:
   ```
   pip install customtkinter flask
   ```
3. Verify Java installation:
   ```
   java -version
   ```
   Ensure the version is 17 or higher
4. For the PHP web interface, ensure PHP is installed and available in your PATH

## Unified Launcher

The unified launcher provides a simple way to access all interfaces of the Minecraft Server Manager.

### Starting the Launcher

#### Windows Batch File
```
launch.bat
```

#### Python Script (Any Platform)
```
python gui_launcher.py
```

### Using the Launcher

The launcher presents three options:

1. **Desktop GUI**: Launches the full-featured desktop application
2. **Python Web Interface**: Starts the Flask web server and opens the interface in your default browser
3. **PHP Web Interface**: Starts the PHP built-in web server and opens the interface in your default browser

The launcher also displays the status of each interface and provides an easy way to exit all running components.

## GUI Interface

### Starting the GUI

Run the following command from the project directory:

```
python mc_server_manager_gui.py
```

### Interface Tabs

1. **Server List**: Displays all configured servers with their status
2. **Server Setup**: Form for creating new servers
3. **Server Control**: Interface for starting, stopping, and monitoring servers
4. **Server Properties**: Editor for server.properties configuration
5. **Console**: Real-time server console output
6. **Settings**: Application settings and appearance options

### Creating a New Server

1. Navigate to the "Server Setup" tab
2. Fill in the required fields:
   - Server Name: A friendly name for the server
   - Server Directory: Where server files will be stored
   - Minecraft Version: Select from available versions
   - Memory Allocation: Set minimum and maximum memory
3. Optional settings:
   - No GUI: Run server without GUI (recommended)
   - Accept EULA: Automatically accept Minecraft EULA
4. Click "Create Server" to set up the server

### Managing Servers

1. Select a server from the list
2. Use the control buttons to:
   - Start the server
   - Stop the server
   - Edit server configuration
   - Delete the server

## Web Interface

### Starting the Web Server

Run the following command from the project directory:

```
python web_gui.py
```

Then open your browser and navigate to http://localhost:5000

### Web Interface Features

- Server creation and management
- Real-time server status monitoring
- Version selection from available releases and snapshots
- Server configuration options

## Command Line Interface

The Minecraft Server Manager provides a command-line interface through the `launch.bat` script, which supports several launch options:

- `launch.bat`: Launches the GUI launcher, allowing you to choose between Desktop GUI, Python Web Interface, or PHP Web Interface
- `launch.bat --gui`: Directly launches the Desktop GUI application
- `launch.bat --python`: Directly launches the Python Web Interface (Flask) on http://localhost:5000
- `launch.bat --php`: Directly launches the PHP Web Interface on http://localhost:8000

The command line interface is provided through mc_server_setup.py and supports various options:

```
python mc_server_setup.py [options]
```

### Available Options

- `--version`: Server version to install (e.g., 1.20.4, 'latest', or 'snapshot')
- `--dir`: Directory to install/setup the server
- `--min-memory`: Initial heap size for JVM (e.g., 1G)
- `--max-memory`: Maximum heap size for JVM (e.g., 2G)
- `--nogui`: Run server without GUI (recommended)
- `--accept-eula`: Automatically accept the Minecraft EULA
- `--start`: Start the server after setup completes
- `--force`: Re-download server.jar even if it exists

### Example Usage

```
python mc_server_setup.py --version 1.20.4 --dir ./survival_server --min-memory 2G --max-memory 4G --nogui --accept-eula --start
```

## Server Configuration

### server.properties

The Server Properties tab in the GUI allows editing common server settings:

- Server MOTD (message of the day)
- PvP settings
- Online mode (authentication)
- Difficulty level
- Game mode
- Maximum players
- View distance
- Flight settings
- Whitelist enforcement
- Spawn protection
- Server port
- Command block enablement

### Advanced Configuration

For advanced configuration options not available in the GUI:

1. Stop the server
2. Edit the server.properties file directly in the server directory
3. Restart the server to apply changes

## Troubleshooting

### Java Issues

- **Error**: Java not found or incorrect version
- **Solution**: Install Java 17+ and ensure it's in your PATH

### Server Won't Start

- **Error**: Server fails to start
- **Solutions**:
  - Check Java version compatibility
  - Verify server.jar exists and is not corrupted
  - Ensure sufficient memory is allocated
  - Check for port conflicts

### GUI Issues

- **Error**: GUI fails to launch
- **Solution**: Verify customtkinter is installed correctly

### Web Interface Issues

- **Error**: Web interface not accessible
- **Solutions**:
  - Verify Flask is installed
  - Check if another service is using port 5000
  - Ensure firewall is not blocking the connection

## Development

### Project Structure

```
MCserverPy/
├── mc_server_manager_gui.py  # Main GUI application
├── mc_server_setup.py        # Core functionality
├── web_gui.py               # Web interface
├── config.php               # PHP implementation
├── templates/               # Web templates
│   └── index.html           # Main web interface
├── icons/                   # GUI icons
│   ├── running.svg          # Server running icon
│   └── stopped.svg          # Server stopped icon
├── python_to_java_converter.py  # Python to Java (Minecraft) converter
└── README.md                # Project documentation
```

### Adding Features

To extend the functionality:

1. For core features, modify mc_server_setup.py
2. For GUI enhancements, modify mc_server_manager_gui.py
3. For web interface changes, modify web_gui.py and templates/index.html

### Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

---

*This documentation is provided for users and developers of the Minecraft Server Manager. For official Minecraft server documentation, please refer to the [Minecraft Wiki](https://minecraft.fandom.com/wiki/Server).*