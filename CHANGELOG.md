# Changelog

All notable changes to this project will be documented in this file.

## [1.2.1] - 2024-12-18

### Added
- Comprehensive menubar with File, Server, Tools, View, and Help menus
- Import/Export functionality for server configurations and server lists
- Batch operations for starting/stopping multiple servers
- Server cloning functionality
- Quick access to project and config directories
- Enhanced navigation with tab switching from View menu
- Python to Java converter integration in Tools menu
- Backup and restore server functionality
- Web GUI launchers (Python and PHP versions)
- WebSocket server integration
- System information display
- About dialog with version information

### Fixed
- Fixed TclError in file dialogs by replacing `initialvalue` with `initialfile`
- Corrected tab reference from "Properties" to "Server Properties" in View menu
- Improved error handling for server operations

### Removed
- Removed "Create Executable" option from Tools menu
- Cleaned up unused `launch_exe_builder` function

### Changed
- Enhanced GUI with modern menubar interface
- Improved user experience with organized menu structure
- Updated version numbering to 1.2.1

## [1.2.1] - Initial Release

### Added
- Basic Minecraft server management functionality
- GUI interface for server setup and control
- Web interface for remote management
- Command-line interface for server setup
- Support for multiple server configurations
- Java version checking
- Automatic server JAR downloading
- EULA acceptance handling
- Server properties configuration
- Real-time server console integration