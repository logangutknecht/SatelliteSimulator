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
- **Multiple satellite tracking**: Import satellite data from NORAD IDs using N2YO API
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

3. Get an N2YO API key:
   - Register at https://www.n2yo.com/api/
   - Get your API key from your account
   - Set the API key in the application (File -> Set N2YO API Key)

4. Run the simulator:
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

The simulator can import satellite data using NORAD IDs through the N2YO API:

1. Get your N2YO API key:
   - Register at https://www.n2yo.com/api/
   - The free tier includes 1000 requests per hour

2. Set your API key:
   - Go to File -> Set N2YO API Key
   - Enter your API key
   - The key is stored securely in `~/.satellite_simulator/config.json`

3. Import a satellite:
   - Click "Add Satellite"
   - Enter the NORAD ID
   - The simulator will fetch the latest TLE data
   - Configure additional parameters if needed

## Configuration

The simulator stores configuration in `~/.satellite_simulator/config.json`:
- N2YO API key
- Other settings (to be added)

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


## Acknowledgements

This simulator was ported from a C++/Qt implementation to Python/PyQt5 to enhance accessibility and extensibility.
The original repository can be found here by [FlorentF9](https://github.com/FlorentF9/SatelliteSimulator/).

## Future Improvements

- Integration with real-world satellite data
- Visualization of ground tracks
- Effects of orbital perturbations
- Advanced propulsion modeling
- Multiple planet simulations
