# SatelliteSimulator
A simple python desktop satellite orbit simulator


# Satellite Simulator

A 3D satellite orbital simulation and visualization tool built with Python and PyQt5.

![Satellite Simulator Screenshot](screenshots/simulator.png)

## Overview

Satellite Simulator is an educational tool that allows users to create, visualize, and analyze satellite orbits around planets. The application provides a realistic 3D visualization of orbital mechanics and satellite movement, making it useful for students, educators, and space enthusiasts.

## Features

- **3D Visualization**: Real-time rendering of planets and satellites in 3D space
- **Interactive Camera**: Trackball camera controls for intuitive navigation
- **Multiple Satellites**: Create and manage multiple satellites with different orbital parameters
- **Configurable Planets**: Customize planet properties (radius, gravitational parameter, day length)
- **Orbit Customization**: Set orbital elements (semi-major axis, eccentricity, inclination, etc.)
- **Time Controls**: Adjust simulation speed and precision
- **Save/Load**: Save and load simulation configurations

## Requirements

- Python 3.6+
- PyQt5
- PyOpenGL
- NumPy (optional for additional calculations)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/logangutknecht/SatelliteSimulator.git
cd SatelliteSimulator
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the simulator:
```bash
python main.py
```

## Usage

### Basic Controls

- **Left-click and drag**: Rotate the view
- **Mouse wheel**: Zoom in/out
- **Space**: Play/pause simulation
- **F**: Increase simulation speed
- **S**: Decrease simulation speed

### Creating a New Simulation

1. Click on **File → New simulation**
2. Configure the planet parameters
3. Click "Start simulation"

### Adding a Satellite

1. Click on **Satellites → Add new satellite**
2. Configure the orbital parameters
3. Click "Add satellite"

### Configuring the Simulation

1. Click on **Simulation → Configure**
2. Adjust the time step and speed settings
3. Click "Apply and reset simulation"

## File Structure

- `main.py` - Main entry point for the application
- `simulation.py` - Core simulation logic
- `orbit.py` - Orbital calculations and mechanics
- `planet.py` - Planet representation and properties
- `satellite.py` - Satellite representation and state
- `point.py` - Base class for points in 3D space
- `point_pol.py` - Polar coordinate representation
- `point_cart.py` - Cartesian coordinate representation
- `propulsion.py` - Satellite propulsion (placeholder for future expansion)

UI Components:
- `main_window.py` - Main application window
- `simulation_display.py` - OpenGL display for 3D visualization
- `simulation_gl.py` - Base OpenGL widget
- `configure_window.py` - Dialog for simulation configuration
- `satellite_window.py` - Dialog for satellite configuration
- `monitor.py` - Information display widget
- `track_ball_camera.py` - Camera control system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This simulator was ported from a C++/Qt implementation to Python/PyQt5 to enhance accessibility and extensibility.

## Future Improvements

- Integration with real-world satellite data
- Visualization of ground tracks
- Effects of orbital perturbations
- Advanced propulsion modeling
- Multiple planet simulations