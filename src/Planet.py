import math
from src.Constants import Constants

class Planet:
    """
    Represents a planet in the simulation
    """
    
    def __init__(self, mu=Constants.mu_earth, radius=Constants.r_earth, 
                 day=Constants.day_earth, name=Constants.defaultPlanetName,
                 img_path=Constants.defaultImgPath, night_img_path=None):
        """
        Initialize a planet with physical parameters
        
        Args:
            mu (float, optional): Gravitational parameter (km^3/s^2). Defaults to Earth's mu.
            radius (float, optional): Planet radius (km). Defaults to Earth's radius.
            day (float, optional): Sidereal day duration (s). Defaults to Earth's day.
            name (str, optional): Planet name. Defaults to "Earth".
            img_path (str, optional): Path to day texture image. Defaults to Earth texture.
            night_img_path (str, optional): Path to night texture image. Defaults to None.
        """
        self.m_mu = mu
        self.m_radius = radius
        self.m_name = name
        self.m_img_path = img_path
        self.m_night_img_path = night_img_path
        self.m_day = day
    
    def update(self, dt):
        """
        Update planet state for a time step
        
        Args:
            dt (float): Time step in seconds
        """
        # No implementation in the original C++ class
        pass
    
    def get_mu(self):
        """
        Get the gravitational parameter
        
        Returns:
            float: Gravitational parameter (km^3/s^2)
        """
        return self.m_mu
    
    def get_radius(self):
        """
        Get the planet radius
        
        Returns:
            float: Planet radius (km)
        """
        return self.m_radius
    
    def get_day(self):
        """
        Get the sidereal day duration
        
        Returns:
            float: Sidereal day duration (s)
        """
        return self.m_day
    
    def get_name(self):
        """
        Get the planet name
        
        Returns:
            str: Planet name
        """
        return self.m_name
    
    def get_img_path(self):
        """
        Get the texture image path
        
        Returns:
            str: Path to texture image
        """
        return self.m_img_path
    
    def get_night_img_path(self):
        """
        Get the night texture image path
        
        Returns:
            str: Path to night texture image
        """
        return self.m_night_img_path
    
    def set_mu(self, mu):
        """
        Set the gravitational parameter
        
        Args:
            mu (float): New gravitational parameter (km^3/s^2)
        """
        self.m_mu = mu
    
    def set_radius(self, radius):
        """
        Set the planet radius
        
        Args:
            radius (float): New planet radius (km)
        """
        self.m_radius = radius
    
    def set_day(self, day):
        """
        Set the sidereal day duration
        
        Args:
            day (float): New sidereal day duration (s)
        """
        self.m_day = day
    
    def set_name(self, name):
        """
        Set the planet name
        
        Args:
            name (str): New planet name
        """
        self.m_name = name
    
    def set_img_path(self, path):
        """
        Set the texture image path
        
        Args:
            path (str): New path to texture image
        """
        self.m_img_path = path
    
    def set_night_img_path(self, path):
        """
        Set the night texture image path
        
        Args:
            path (str): New path to night texture image
        """
        self.m_night_img_path = path
    
    def a_geo(self):
        """
        Calculate the geostationary orbit radius
        
        Returns:
            float: Geostationary orbit radius (km)
        """
        return math.pow(self.m_mu * self.m_day * self.m_day / (4.0 * Constants.pi2), 1.0/3.0)
    
    def to_string(self):
        """
        Convert planet to string representation
        
        Returns:
            str: String representation of the planet
        """
        output = f"Name: {self.m_name}\n"
        output += f"Radius: {self.m_radius}\n"
        output += f"Mu: {self.m_mu}\n"
        output += f"Day: {self.m_day}\n"
        output += f"ImgPath: {self.m_img_path}\n"
        output += f"NightImgPath: {self.m_night_img_path}\n"
        return output