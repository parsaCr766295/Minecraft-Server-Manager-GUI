# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2024-12-18

### Added
- Native tkinter menu bar integration replacing popup menu system
- Comprehensive menu structure with File, Server, Tools, View, and Help menus
- Organized submenus for better navigation and functionality grouping
- Menu keyboard shortcuts and accelerators
- Professional menu bar appearance consistent with modern desktop applications

### Fixed
- Improved menu accessibility and usability over previous popup system
- Menu items now follow standard desktop application conventions
- Better integration with operating system menu styling

### Changed
- **BREAKING**: Replaced button-based popup menus with native menu bar
- Menu structure reorganized into logical categories:
  - File: Server management, import/export, directory access
  - Server: Server management and control operations
  - Tools: Development tools, server utilities, web interfaces
  - View: Interface navigation and theme selection
  - Help: Documentation, support, and system information
- Removed obsolete popup menu methods and UI elements
- Cleaner interface with more space for content

### Removed
- Old popup menu system (show_file_menu, show_server_menu, etc.)
- Menu button widgets from top toolbar
- Popup window menu implementations

## [1.2.2-pre] - 2024-12-18 (Pre-release)

### Added
- Window icons throughout the application using `icons/launcher.ico`
- Icon support for main GUI window and all popup dialogs/menus
- Resource path handling for both development and PyInstaller builds

### Fixed
- Fixed GUI launcher reliability when launching Desktop GUI from different working directories
- Improved absolute path handling in launcher for all script executions
- Enhanced process monitoring with daemon threads for cleaner app exit
- Added existence checks for script files before launching

### Changed
- GUI launcher now uses absolute paths and proper working directories
- All Toplevel windows (menus, dialogs) now display the application icon
- Improved error messages showing full paths when scripts are not found

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