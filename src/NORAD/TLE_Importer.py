from skyfield.api import load, EarthSatellite
import datetime
from src.Orbit import Orbit
from src.Planet import Planet

class TLEImporter:
    def __init__(self):
        self.ts = load.timescale()
    
    def fetch_satellite_by_norad_id(self, norad_id):
        """Fetch satellite TLE data from Celestrak by NORAD ID"""
        satellites = load.tle_file(f'https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}')
        if not satellites:
            return None
        return satellites[0]
    
    def convert_to_simulator_orbit(self, satellite, planet):
        """Convert a skyfield satellite to simulator orbit parameters"""
        # Extract orbital elements
        a = satellite.model.a * 1000  # Semi-major axis in km
        e = satellite.model.e  # Eccentricity
        i = satellite.model.i  # Inclination in radians
        Omega = satellite.model.Om  # Right ascension of ascending node in radians
        omega = satellite.model.w  # Argument of perigee in radians
        
        # Create orbit object for simulator
        return Orbit(planet, a, e, i, Omega, omega)