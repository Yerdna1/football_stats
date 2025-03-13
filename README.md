# Football Stats

A desktop application for analyzing football statistics, tracking team performance, and making predictions based on form analysis.

## Features

- View league standings and statistics
- Analyze team form and performance
- Track upcoming fixtures with date-based grouping
- Make predictions based on team performance
- Filter out past matches
- Sort fixtures by various criteria
- Customizable interface

## Installation

### Option 1: Using the Installer

1. Download the latest installer (`FootballStats_Setup.exe`) from the [Releases](https://github.com/Yerdna1/FootballStatsWindows/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch the application from the desktop shortcut or start menu

### Option 2: Portable Version

1. Download the latest portable version (`Football_Stats_Portable.zip`) from the [Releases](https://github.com/Yerdna1/FootballStatsWindows/releases) page
2. Extract the ZIP file to a location of your choice
3. Run `Football Stats.exe` to start the application

## Building from Source

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- PyInstaller
- Inno Setup (optional, for creating installers)

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/Yerdna1/FootballStatsWindows.git
   cd FootballStatsWindows
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Build the executable:
   ```
   pyinstaller app.spec
   ```

5. (Optional) Create an installer:
   ```
   iscc FootballStats.iss
   ```

## Usage

1. Launch the application
2. Select a league from the dropdown menu
3. Use the tabs to navigate between different views:
   - League Stats: View league standings and statistics
   - Team Analysis: Analyze individual team performance
   - Form Analysis: View team form and performance changes
   - Upcoming Fixtures: See upcoming matches grouped by date

## Recent Changes

- Changed date format to DD.MM.YYYY
- Added filtering to hide past matches
- Implemented date separators for better organization
- Added sorting functionality within date groups
- Removed Firebase dependencies to improve stability
- Created proper installer with Inno Setup

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Football data provided by various APIs
- Built with Python and CustomTkinter
