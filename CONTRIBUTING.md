# Contributing to Minecraft Server Manager

Thank you for your interest in contributing to the Minecraft Server Manager project! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Environment](#development-environment)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Pull Request Process](#pull-request-process)

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful and considerate of others when participating in this project.

## Getting Started

### Prerequisites

- Python 3.6+
- Java 17+ (for testing Minecraft server functionality)
- Git

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```
   git clone https://github.com/YOUR-USERNAME/MCserverPy.git
   cd MCserverPy
   ```
3. Install development dependencies:
   ```
   pip install customtkinter flask pytest
   ```

## How to Contribute

There are many ways to contribute to the project:

1. **Report bugs**: If you find a bug, please create an issue with detailed information about how to reproduce it.
2. **Suggest features**: If you have an idea for a new feature, create an issue to discuss it.
3. **Improve documentation**: Help improve the documentation by fixing errors or adding missing information.
4. **Submit code changes**: Fix bugs or implement new features through pull requests.

## Development Environment

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
└── README.md                # Project documentation
```

### Components

- **Core Functionality**: `mc_server_setup.py` contains the core server management functions.
- **GUI Interface**: `mc_server_manager_gui.py` provides the desktop application interface.
- **Web Interface**: `web_gui.py` and templates provide the browser-based interface.

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines.
- Use 4 spaces for indentation (not tabs).
- Keep line length to a maximum of 100 characters.
- Use meaningful variable and function names.
- Add docstrings to all functions and classes.

### Commit Messages

- Use clear and descriptive commit messages.
- Start with a short summary line (50 characters or less).
- Optionally, follow with a blank line and a more detailed explanation.
- Reference issue numbers when applicable (e.g., "Fixes #123").

## Testing

- Write tests for new features and bug fixes.
- Ensure all tests pass before submitting a pull request.
- Test your changes on different platforms if possible (Windows, macOS, Linux).

## Pull Request Process

1. Create a new branch for your changes:
   ```
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with descriptive messages.

3. Push your branch to your fork:
   ```
   git push origin feature/your-feature-name
   ```

4. Submit a pull request to the main repository.

5. In your pull request description:
   - Clearly describe the changes you've made.
   - Reference any related issues.
   - Mention any breaking changes.

6. Be responsive to feedback and be prepared to make additional changes if requested.

## Feature Development Guidelines

### Adding a New Feature

1. **Discuss first**: For significant features, open an issue to discuss the proposal before implementing.

2. **Maintain compatibility**: Ensure new features don't break existing functionality.

3. **Document changes**: Update documentation to reflect new features or changes.

4. **User experience**: Consider the user experience when designing new features.

### GUI Development

- Maintain consistency with the existing UI design.
- Use customtkinter components for a consistent look and feel.
- Consider accessibility in your design.

### Web Interface Development

- Follow responsive design principles.
- Maintain compatibility with major browsers.
- Consider security implications of any changes.

---

Thank you for contributing to the Minecraft Server Manager project! Your efforts help make this tool better for everyone.