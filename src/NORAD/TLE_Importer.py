from skyfield.api import load, EarthSatellite
import datetime
from src.Orbit import Orbit
from src.Planet import Planet
import numpy as np

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
        # Get the current time
        now = self.ts.now()
        
        # Get the satellite's position and velocity
        position = satellite.at(now)
        
        # Extract position and velocity vectors
        r = position.position.km
        v = position.velocity.km_per_s
        
        # Calculate orbital elements from position and velocity
        # Using standard orbital mechanics formulas
        
        # Calculate specific angular momentum
        h = np.cross(r, v)
        h_mag = np.linalg.norm(h)
        
        # Calculate eccentricity vector
        mu = planet.get_mu()
        r_mag = np.linalg.norm(r)
        e_vec = np.cross(v, h) / mu - r / r_mag
        e = np.linalg.norm(e_vec)
        
        # Calculate semi-major axis
        v_mag = np.linalg.norm(v)
        a = 1.0 / (2.0 / r_mag - v_mag * v_mag / mu)
        
        # Calculate inclination
        i = np.arccos(h[2] / h_mag)
        
        # Calculate right ascension of ascending node
        n = np.cross([0, 0, 1], h)
        n_mag = np.linalg.norm(n)
        Omega = np.arccos(n[0] / n_mag)
        if n[1] < 0:
            Omega = 2 * np.pi - Omega
        
        # Calculate argument of perigee
        omega = np.arccos(np.dot(n, e_vec) / (n_mag * e))
        if e_vec[2] < 0:
            omega = 2 * np.pi - omega
        
        # Create orbit object for simulator
        return Orbit(planet, a, e, i, Omega, omega)