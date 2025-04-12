from Orbit import Orbit
from Planet import Planet
from Propulsion import Propulsion
from PointPol import PointPol

class Satellite:
    """
    Represents a satellite object in the simulation
    """
    
    def __init__(self, orb, planet, prop, name="Satellite", rx=0.0, ry=0.0, rz=0.0):
        """
        Initialize a new satellite
        
        Args:
            orb (Orbit): The satellite's orbit
            planet (Planet): The planet the satellite orbits
            prop (Propulsion): The satellite's propulsion system
            name (str, optional): Name of the satellite. Defaults to "Satellite".
            rx (float, optional): Rotation around x axis. Defaults to 0.0.
            ry (float, optional): Rotation around y axis. Defaults to 0.0.
            rz (float, optional): Rotation around z axis. Defaults to 0.0.
        """
        self.m_orbit = Orbit(orb)  # Create a copy of the orbit
        self.m_planet = planet
        self.m_prop = prop
        self.m_name = name
        self.m_rx = rx
        self.m_ry = ry
        self.m_rz = rz
    
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