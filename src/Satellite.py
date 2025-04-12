from src.Orbit import Orbit
from src.Planet import Planet
from src.Propulsion import Propulsion
from src.PointPol import PointPol

class Satellite:
    """
    Represents a satellite object in the simulation
    """
    
    def __init__(self, orb, planet, prop, name=""):
        """
        Initialize a satellite
        
        Args:
            orb (Orbit): The orbit of the satellite
            planet (Planet): The planet the satellite orbits
            prop (Propulsion): The propulsion system
            name (str, optional): The name of the satellite. Defaults to "".
        """
        self.m_orbit = Orbit(planet, orb.get_a(), orb.get_e(), orb.get_i(), 
                            orb.get_omega(), orb.get_omega_small(), orb.get_tp())
        self.m_planet = planet
        self.m_prop = prop
        self.m_name = name
        self.m_rx = 0.0
        self.m_ry = 0.0
        self.m_rz = 0.0
    
    def update(self, dt):
        """
        Update the satellite state for a time step
        
        Args:
            dt (float): Time step in seconds
        """
        # Update orbit
        self.m_orbit.update(dt)
        # Update satellite position on its orbit
        self.m_orbit.update_position(dt)
    
    def reset(self):
        """Reset the satellite to its initial state"""
        # Reset position to 0
        self.m_orbit.reset()
        # Reset other parameters if needed
        # self.m_prop.reset()
    
    def to_string(self):
        """
        Convert satellite to string representation
        
        Returns:
            str: String representation of the satellite
        """
        output = "----------\n"
        output += f"Name: {self.m_name}\n"
        # output += f"Propulsion: {self.m_prop.to_string()}\n"
        output += self.m_orbit.to_string()
        return output
    
    def get_orbit(self):
        """
        Get the satellite's orbit
        
        Returns:
            Orbit: The satellite's orbit
        """
        return self.m_orbit
    
    def get_planet(self):
        """
        Get the planet the satellite orbits
        
        Returns:
            Planet: The planet
        """
        return self.m_planet
    
    def get_propu(self):
        """
        Get the satellite's propulsion system
        
        Returns:
            Propulsion: The propulsion system
        """
        return self.m_prop
    
    def get_name(self):
        """
        Get the satellite's name
        
        Returns:
            str: The satellite's name
        """
        return self.m_name
    
    def get_rx(self):
        """
        Get rotation around x axis
        
        Returns:
            float: Rotation value
        """
        return self.m_rx
    
    def get_ry(self):
        """
        Get rotation around y axis
        
        Returns:
            float: Rotation value
        """
        return self.m_ry
    
    def get_rz(self):
        """
        Get rotation around z axis
        
        Returns:
            float: Rotation value
        """
        return self.m_rz
    
    def set_name(self, name):
        """
        Set the satellite's name
        
        Args:
            name (str): New name
        """
        self.m_name = name
    
    def set_rx(self, rx):
        """
        Set rotation around x axis
        
        Args:
            rx (float): New rotation value
        """
        self.m_rx = rx
    
    def set_ry(self, ry):
        """
        Set rotation around y axis
        
        Args:
            ry (float): New rotation value
        """
        self.m_ry = ry
    
    def set_rz(self, rz):
        """
        Set rotation around z axis
        
        Args:
            rz (float): New rotation value
        """
        self.m_rz = rz
    
    def get_current_position(self):
        """
        Get the current position of the satellite
        
        Returns:
            PointPol: The position point
        """
        return self.m_orbit.get_position_point()