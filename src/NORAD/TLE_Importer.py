from skyfield.api import load, EarthSatellite
import datetime
from src.Orbit import Orbit
from src.Planet import Planet
import numpy as np
import logging
import requests
from io import StringIO
import json

class TLEImporter:
    def __init__(self):
        self.ts = load.timescale()
        logging.basicConfig(level=logging.INFO)
    
    def fetch_satellite_by_norad_id(self, norad_id):
        """Fetch satellite TLE data from keeptrack.space by NORAD ID"""
        try:
            # keeptrack.space API endpoint for satellite data
            url = f'https://api.keeptrack.space/v2/sat/{norad_id}'
            
            logging.info(f"Fetching TLE data from: {url}")
            
            response = requests.get(url)
            
            # Log the full response for debugging
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response content: {response.text}")
            
            if response.status_code != 200:
                logging.error(f"Failed to fetch TLE data. Status code: {response.status_code}")
                return None
                
            data = response.json()
            logging.info(f"Parsed JSON response: {data}")
            
            if "error" in data:
                logging.error(f"API Error: {data['error']}")
                return None
            
            # Extract TLE lines from the response
            tle_line1 = data.get("TLE_LINE_1")
            tle_line2 = data.get("TLE_LINE_2")
            
            if not tle_line1 or not tle_line2:
                logging.error("Missing TLE lines in response")
                return None
            
            # Create satellite object directly from TLE lines
            satellite = EarthSatellite(tle_line1, tle_line2, data.get("NAME", norad_id), self.ts)
            
            if str(data.get("NORAD_CAT_ID")) == str(norad_id):
                logging.info(f"Successfully found satellite with NORAD ID {norad_id}")
                logging.info(f"Satellite name: {satellite.name}")
                return satellite
            else:
                logging.error(f"Found satellite with different NORAD ID: {data.get('NORAD_CAT_ID')}")
                return None
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error while fetching TLE data: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {str(e)}")
            logging.error(f"Raw response: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Error fetching TLE data: {str(e)}")
            return None
    
    def convert_to_simulator_orbit(self, satellite, planet):
        """Convert a skyfield satellite to simulator orbit parameters"""
        try:
            # Get the current time
            now = self.ts.now()
            
            # Get the satellite's position and velocity
            position = satellite.at(now)
            
            # Extract position and velocity vectors
            r = position.position.km
            v = position.velocity.km_per_s
            
            logging.info(f"Position vector: {r}")
            logging.info(f"Velocity vector: {v}")
            
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
            
            # Calculate inclination - use direct value since we'll handle direction with Omega/omega
            i = np.arccos(h[2] / h_mag)
            
            # Calculate right ascension of ascending node
            n = np.cross([0, 0, 1], h)
            n_mag = np.linalg.norm(n)
            if n_mag < 1e-10:  # Handle near-polar orbits
                Omega = 0.0
            else:
                Omega = np.arccos(n[0] / n_mag)
                if n[1] < 0:
                    Omega = 2 * np.pi - Omega
                # Add 180 degrees and subtract 60 degrees to align with Earth texture
                Omega = (Omega + np.pi - np.pi/4 - np.pi/12) % (2 * np.pi)
            
            # Calculate argument of perigee
            if n_mag < 1e-10:  # Handle near-polar orbits
                omega = np.arctan2(e_vec[1], e_vec[0])
            else:
                omega = np.arccos(np.dot(n, e_vec) / (n_mag * e))
                if e_vec[2] < 0:
                    omega = 2 * np.pi - omega
                # Add 180 degrees to maintain correct perigee position
                omega = (omega + np.pi) % (2 * np.pi)
            
            logging.info(f"Calculated orbital elements:")
            logging.info(f"a = {a} km")
            logging.info(f"e = {e}")
            logging.info(f"i = {i} rad")
            logging.info(f"Omega = {Omega} rad")
            logging.info(f"omega = {omega} rad")
            
            # Create orbit object for simulator
            return Orbit(planet, a, e, i, Omega, omega)
            
        except Exception as e:
            logging.error(f"Error converting to simulator orbit: {str(e)}")
            raise