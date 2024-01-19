README
Overview

This tool is a Python-based map generator for creating random maps for a Tabletop Role-Playing Game (TTRPG) inspired by the Nintendo game Pokemon Mystery Dungeon. It automatically generates room layouts with varying sizes and positions, simulating dungeon floors. The program uses randomization to create unique and diverse map designs each time it is run.

Features

- **Random Map Generation**: Generates random room layouts and positions, creating unique dungeon floors.
- **Room Overlap Detection**: Identifies overlapping rooms and provides functionality for handling these overlaps.
- **Customizable Parameters**: Allows users to adjust the number of rooms, size variance, and other parameters to influence the map layout.
- **Visualization**: Offers a visual representation of the generated map layout using matplotlib.

Requirements

    Python 3.x
    matplotlib Python library (for map visualization)

Installation

    Ensure Python 3.x is installed on your system.
    Install the matplotlib library using pip:

    ```bash
    pip install matplotlib
    ```

Usage

    Edit the parameters at the beginning of the script to customize the number of rooms and their size variance.
    Run the script from the command line:

    ```bash
    python path_to_script.py
    ```

    View the generated map layout in the matplotlib window.

Code Structure

    `Floor`: Class representing the entire floor of the dungeon. Handles room addition and layout generation.
    `Room`: Represents individual rooms with properties such as size and position.
    `main`: Orchestrates the map generation process and visualizes the outcome.

Limitations and Notes

Contributing

    Contributions to the project are welcome. Please follow standard GitHub pull request procedures for contributions.

License

    Distributed under the GNU General Public License v3.0. See LICENSE for more information.

Disclaimer

This tool is not officially affiliated with Nintendo or the Pokemon franchise. It is intended for fan-made, non-commercial use only.