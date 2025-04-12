import math
from src.Point import Point
from src.PointCart import PointCart

class PointPol(Point):
    """
    Represents a point in polar coordinates (r, theta, phi)
    """
    
    def __init__(self, r=0.0, theta=0.0, phi=0.0):
        """
        Initialize a polar point
        
        Args:
            r (float, optional): Radius. Defaults to 0.0.
            theta (float, optional): Azimuthal angle in radians. Defaults to 0.0.
            phi (float, optional): Polar angle in radians. Defaults to 0.0.
        """
        super(PointPol, self).__init__()
        self.m_r = r
        self.m_theta = theta
        self.m_phi = phi
    
    def __init_from_point(self, p):
        """
        Initialize from another Point
        
        Args:
            p (Point): Another point object
        """
        self.m_r = p.get_r()
        self.m_theta = p.get_theta()
        self.m_phi = p.get_phi()
    
    # Python's special methods for operator overloading
    def __eq__(self, p):
        """
        Equality operator
        
        Args:
            p (Point): Another point to compare with
            
        Returns:
            bool: True if points are equal
        """
        return (self.m_r == p.get_r() and 
                self.m_theta == p.get_theta() and 
                self.m_phi == p.get_phi())
    
    def __iadd__(self, p):
        """
        In-place addition operator (+=)
        
        Args:
            p (Point): Point to add
            
        Returns:
            PointPol: Self after addition
        """
        # Create cartesian copy of point to use adding operator
        tmp = PointCart(self)
        tmp += p
        # Reconvert to polar point
        copy = PointPol(0)
        copy.__init_from_point(tmp)
        self.m_r = copy.m_r
        self.m_theta = copy.m_theta
        self.m_phi = copy.m_phi
        return self
    
    def __isub__(self, p):
        """
        In-place subtraction operator (-=)
        
        Args:
            p (Point): Point to subtract
            
        Returns:
            PointPol: Self after subtraction
        """
        # Create cartesian copy of point to use subtraction operator
        tmp = PointCart(self)
        tmp -= p
        # Reconvert to polar point
        copy = PointPol(0)
        copy.__init_from_point(tmp)
        self.m_r = copy.m_r
        self.m_theta = copy.m_theta
        self.m_phi = copy.m_phi
        return self
    
    def __add__(self, p):
        """
        Addition operator (+)
        
        Args:
            p (Point): Point to add
            
        Returns:
            PointPol: New point representing the sum
        """
        copy = PointPol(0)
        copy.__init_from_point(self)
        copy += p
        return copy
    
    def __sub__(self, p):
        """
        Subtraction operator (-)
        
        Args:
            p (Point): Point to subtract
            
        Returns:
            PointPol: New point representing the difference
        """
        copy = PointPol(0)
        copy.__init_from_point(self)
        copy -= p
        return copy
    
    # Getter and setter methods
    def get_r(self):
        """Get radius"""
        return self.m_r
    
    def set_r(self, val):
        """Set radius"""
        self.m_r = val
    
    def get_theta(self):
        """Get azimuthal angle"""
        return self.m_theta
    
    def set_theta(self, val):
        """Set azimuthal angle"""
        self.m_theta = val
    
    def get_phi(self):
        """Get polar angle"""
        return self.m_phi
    
    def set_phi(self, val):
        """Set polar angle"""
        self.m_phi = val
    
    # Cartesian coordinate conversions
    def get_x(self):
        """Get x cartesian coordinate"""
        return self.m_r * math.cos(self.m_theta) * math.cos(self.m_phi)
    
    def get_y(self):
        """Get y cartesian coordinate"""
        return self.m_r * math.sin(self.m_theta) * math.cos(self.m_phi)
    
    def get_z(self):
        """Get z cartesian coordinate"""
        return self.m_r * math.sin(self.m_phi)
    
    def print(self):
        """Print the point coordinates"""
        print(f"Polar Point: r={self.m_r}, theta={self.m_theta}, phi={self.m_phi}")
        print(f"Cartesian: x={self.get_x()}, y={self.get_y()}, z={self.get_z()}")