# Satellite Simulator

A 3D satellite orbital simulation and visualization tool built with Python and PyQt5.

<img width="1512" alt="image" src="https://github.com/user-attachments/assets/548ff6d5-7bcf-41cb-a867-18931a431623" />

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
- **Multiple satellite tracking**: Import satellite data from NORAD IDs using free KeepTrack.space API
- **Earth and satellite models**: Display Earth and satellite models in the simulation
- **Time control**: Play/pause simulation, adjust speed

## Requirements

- Python 3.6+
- PyQt5
- PyOpenGL
- NumPy (optional for additional calculations)
- matplotlib (for satellite model visualization)
- skyfield (for satellite position calculations)
- requests (for API communication)

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

### NORAD ID Tracking

The simulator can import satellite data using NORAD IDs through the free KeepTrack API:

1. Import a satellite:
   - Click "Add Satellite"
   - Enter the NORAD ID
   - The simulator will fetch the latest TLE data
   - Configure additional parameters if needed


## File Structure

- `main.py` - Main entry point for the application
- `Simulation.py` - Core simulation logic
- `Oribit.py` - Orbital calculations and mechanics
- `Planet.py` - Planet representation and properties
- `Satellite.py` - Satellite representation and state
- `Point.py` - Base class for points in 3D space
- `PointPol.py` - Polar coordinate representation
- `PointCart.py` - Cartesian coordinate representation
- `Propulsion.py` - Satellite propulsion (placeholder for future expansion)

UI Components:
- `MainWindow.py` - Main application window
- `SimulationDisplay.py` - OpenGL display for 3D visualization
- `SimulationGL.py` - Base OpenGL widget
- `ConfigureWindow.py` - Dialog for simulation configuration
- `SatelliteWindow.py` - Dialog for satellite configuration
- `Monitor.py` - Information display widget
- `TrackBallCamera.py` - Camera control system

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Acknowledgements

This simulator was ported from a C++/Qt implementation to Python/PyQt5 to enhance accessibility and extensibility.
The original repository can be found here by [FlorentF9](https://github.com/FlorentF9/SatelliteSimulator/).

## Future Improvements

- Integration with real-world satellite info
- Visualization of ground tracks
- Simulate "Take Image" function for satellite
- Effects of orbital perturbations
- Advanced propulsion/GNC modeling
- Multiple planet simulations, Sun shadows
