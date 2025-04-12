from skyfield.api import load, EarthSatellite
import datetime
from src.Orbit import Orbit
from src.Planet import Planet
import numpy as np
import logging
import requests
from io import StringIO
from src.config_manager import ConfigManager
import json

class TLEImporter:
    def __init__(self):
        self.ts = load.timescale()
        logging.basicConfig(level=logging.INFO)
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        self.api_key = self.config_manager.get_api_key()
        if not self.api_key:
            logging.error("N2YO API key not found. Please set it in the File menu.")
    
    def fetch_satellite_by_norad_id(self, norad_id):
        """Fetch satellite TLE data from N2YO by NORAD ID"""
        try:
            if not self.api_key:
                logging.error("N2YO API key not set. Please set it in the File menu.")
                return None
            
            # N2YO API endpoint for TLE data
            url = f'https://api.n2yo.com/rest/v1/satellite/tle/{norad_id}'
            params = {
                'apiKey': self.api_key
            }
            
            logging.info(f"Fetching TLE data from: {url}")
            logging.info(f"Using API key: {self.api_key[:4]}...{self.api_key[-4:]}")
            
            response = requests.get(url, params=params)
            
            # Log the full response for debugging
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response content: {response.text}")
            
            if response.status_code != 200:
                logging.error(f"Failed to fetch TLE data. Status code: {response.status_code}")
                return None
                
            data = response.json()
            logging.info(f"Parsed JSON response: {data}")
            
            if not data.get('tle'):
                logging.error("No TLE data in response")
                if 'error' in data:
                    logging.error(f"API Error: {data['error']}")
                return None
            
            # Extract TLE lines from the response
            tle_lines = data['tle'].split('\r\n')
            if len(tle_lines) != 2:
                logging.error(f"Invalid TLE format. Expected 2 lines, got {len(tle_lines)}")
                return None
            
            tle_line1 = tle_lines[0]
            tle_line2 = tle_lines[1]
            
            if not tle_line1 or not tle_line2:
                logging.error("Missing TLE lines in response")
                return None
            
            # Create satellite object directly from TLE lines
            satellite = EarthSatellite(tle_line1, tle_line2, data['info']['satname'], self.ts)
            
            if str(data['info']['satid']) == str(norad_id):
                logging.info(f"Successfully found satellite with NORAD ID {norad_id}")
                logging.info(f"Satellite name: {satellite.name}")
                return satellite
            else:
                logging.error(f"Found satellite with different NORAD ID: {satellite.model.satnum}")
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