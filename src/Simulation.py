import os
import sys
import datetime
from src.Constants import Constants
from src.Satellite import Satellite
from src.Planet import Planet

class Simulation:
    """
    Represents a satellite orbital simulation
    """
    
    def __init__(self, planet, name, speed=1.0, dt=1.0):
        """
        Initialize a new simulation
        
        Args:
            planet (Planet): The central planet for the simulation
            name (str): Name of the simulation
            speed (float, optional): Simulation speed factor. Defaults to 1.0.
            dt (float, optional): Time step in seconds. Defaults to 1.0.
        """
        self.m_planet = planet
        self.m_name = name
        self.m_satellites = []
        self.sim_t = 0.0
        self.sim_dt = dt
        self.sim_speed = speed
        self.m_play = Constants.autoPlay
        self.m_verbose = Constants.verbose
        self.m_write_log = Constants.writeLog
    
    def update(self):
        """Update the simulation by one time step"""
        if self.m_play:
            # Add time interval to sim time
            self.sim_t += self.dt
            
            # Print info if verbose mode is on
            if self.m_verbose:
                print(f"t = {self.t}")
                for sat in self.m_satellites:
                    print(sat.get_name())
                    print(f"v = {sat.get_orbit().get_v()} / "
                          f"E = {sat.get_orbit().get_e()} / "
                          f"M = {sat.get_orbit().get_m()}")
                    sat.get_current_position().print()
            
            # Update each satellite's orbit and position
            for sat in self.m_satellites:
                sat.update(self.dt)
    
    def add_satellite(self, sat):
        """
        Add a satellite to the simulation
        
        Args:
            sat (Satellite): The satellite to add
        """
        if sat.get_planet() == self.m_planet:
            self.m_satellites.append(sat)
    
    def rem_satellite(self, i):
        """
        Remove a satellite from the simulation
        
        Args:
            i (int): Index of the satellite to remove
        """
        if 0 <= i < len(self.m_satellites):
            del self.m_satellites[i]
    
    def sat(self, i):
        """
        Get a satellite by index
        
        Args:
            i (int): Index of the satellite
            
        Returns:
            Satellite: The satellite at the specified index
        """
        return self.m_satellites[i]
    
    def nsat(self):
        """
        Get the number of satellites in the simulation
        
        Returns:
            int: Number of satellites
        """
        return len(self.m_satellites)
    
    def reset(self):
        """Reset the simulation time to 0 and reset all satellites"""
        # Reset time to 0
        self.sim_t = 0.0
        
        # Reset each satellite's position to initial state
        for sat in self.m_satellites:
            sat.reset()
    
    def reset_all(self):
        """Reset the simulation and remove all satellites"""
        # Reset time to 0
        self.sim_t = 0.0
        
        # Remove all satellites
        self.m_satellites.clear()
    
    def save_to_file(self, path, date):
        """
        Save the simulation state to a file
        
        Args:
            path (str): Path to save the file
            date (str): Current date as a string
            
        Returns:
            int: 0 on success, 1 on failure
        """
        try:
            with open(path, 'w') as file:
                file.write(f"{Constants.programName}\n")
                file.write(f"{date}\n")
                file.write(f"{path}\n")
                file.write(f"----------\n")
                file.write(f"Simulation\n")
                file.write(self.to_string())
                file.write(f"----------\n")
                file.write(f"Planet\n")
                file.write(self.m_planet.to_string())
                file.write(f"----------\n")
                file.write(f"Satellites\n")
                
                for sat in self.m_satellites:
                    file.write(sat.to_string())
            
            return 0
        except:
            return 1
    
    def to_string(self):
        """
        Convert simulation to string representation
        
        Returns:
            str: String representation of the simulation
        """
        output = f"Name: {self.m_name}\n"
        output += f"t: {self.sim_t}\n"
        output += f"dt: {self.sim_dt}\n"
        output += f"Speed: {self.sim_speed}\n"
        output += f"n: {len(self.m_satellites)}\n"
        return output
    
    # Property getters and setters
    @property
    def t(self):
        """Current simulation time"""
        return self.sim_t
    
    def set_t(self, t):
        """Set the current simulation time"""
        self.sim_t = t
    
    @property
    def dt(self):
        """Simulation time step"""
        return self.sim_dt
    
    def set_dt(self, dt):
        """Set the simulation time step"""
        self.sim_dt = dt
    
    @property
    def speed(self):
        """Simulation speed factor"""
        return self.sim_speed
    
    def set_speed(self, speed=1.0):
        """Set the simulation speed factor"""
        self.sim_speed = speed
    
    @property
    def name(self):
        """Simulation name"""
        return self.m_name
    
    def set_name(self, name):
        """Set the simulation name"""
        self.m_name = name
    
    @property
    def play(self):
        """Simulation play state"""
        return self.m_play
    
    def set_play(self, b):
        """Set the simulation play state"""
        self.m_play = b
    
    def toggle_play(self):
        """Toggle the simulation play state"""
        self.m_play = not self.m_play
    
    def toggle_verbose(self):
        """Toggle verbose output"""
        self.m_verbose = not self.m_verbose
    
    @property
    def write_log(self):
        """Whether to write simulation log"""
        return self.m_write_log
    
    def set_write_log(self, b):
        """Set whether to write simulation log"""
        self.m_write_log = b
    
    def get_planet(self):
        """Get the simulation's planet"""
        return self.m_planet