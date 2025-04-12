"""
Constants module providing simulation parameters and physical constants
"""

import math

class Constants:
    """
    Static class containing physical and simulation constants
    """
    # Numerical constants
    pi = math.pi
    twopi = 2.0 * math.pi
    halfpi = 0.5 * math.pi
    pi2 = math.pi * math.pi
    
    # Physical constants
    G = 6.67384e-11  # Gravitational constant (m^3/kg/s^2)
    
    # Earth constants
    r_earth = 6.3781366e3    # Earth equatorial radius (km)
    J2_earth = 0.0010826359  # J2 factor
    mu_earth = 398600.4415   # Earth mu (km^3/s^2)
    day_earth = 86164.10     # Duration of an earth rotation (s)
    a_geo = 42164.2          # Geostationary orbit (km)
    
    # Program constants
    programName = "Satellite Simulator beta 0.2"
    autoPlay = True         # Start simulation automatically?
    verbose = False          # Print position on stdout?
    writeLog = True          # Keep log file?
    defaultImgPath = "src/assets/earth_4k.jpg"  # Default planet texture
    defaultPlanetName = "Earth"
    minPlanetRadius = 0.1    # Minimal radius of a planet (km)
    maxPlanetRadius = 1.0e6  # Maximum radius of a planet (km)
    minPlanetMu = 0.001      # Minimal mu of a planet (km^3/s^2)
    maxPlanetMu = 1.0e9      # Maximum mu of a planet (km^3/s^2)
    minPlanetDay = 1.0       # Minimal duration of a sideral day (s)
    maxPlanetDay = 1.0e8     # Maximum duration of a sideral day (s)
    minTimeStep = 0.001      # Minimal simulation time step (s)
    maxTimeStep = 60.0       # Maximum simulation time step (s)
    maxSatA = 1.0e6
    minSatTp = 1.0e6