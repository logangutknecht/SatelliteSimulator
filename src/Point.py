from abc import ABC, abstractmethod

class Point(ABC):
    """
    Abstract base class for points in 3D space
    
    This class defines the interface that all point types must implement,
    whether they use Cartesian, polar, or other coordinate systems.
    """
    
    def __init__(self):
        """Initialize a base point"""
        pass
    
    @abstractmethod
    def get_x(self):
        """
        Get the x coordinate
        
        Returns:
            float: X coordinate in Cartesian system
        """
        pass
    
    @abstractmethod
    def get_y(self):
        """
        Get the y coordinate
        
        Returns:
            float: Y coordinate in Cartesian system
        """
        pass
    
    @abstractmethod
    def get_z(self):
        """
        Get the z coordinate
        
        Returns:
            float: Z coordinate in Cartesian system
        """
        pass
    
    @abstractmethod
    def get_r(self):
        """
        Get the radius
        
        Returns:
            float: Radius in polar coordinates
        """
        pass
    
    @abstractmethod
    def get_theta(self):
        """
        Get the azimuthal angle
        
        Returns:
            float: Azimuthal angle in polar coordinates (radians)
        """
        pass
    
    @abstractmethod
    def get_phi(self):
        """
        Get the polar angle
        
        Returns:
            float: Polar angle in polar coordinates (radians)
        """
        pass
    
    def print(self):
        """Print the point coordinates in both Cartesian and polar systems"""
        print(f"[x,y,z] = [{self.get_x()},{self.get_y()},{self.get_z()}]")
        print(f"[r,theta,phi] = [{self.get_r()},{self.get_theta()},{self.get_phi()}]")