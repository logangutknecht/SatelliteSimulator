from PyQt5.QtWidgets import (QMainWindow, QAction, QMenu, QMessageBox, 
                           QFileDialog, QStatusBar)
from PyQt5.QtGui import QIcon, QCloseEvent, QResizeEvent
from PyQt5.QtCore import QDateTime, pyqtSlot, Qt
import os
import sys
from datetime import datetime
from simulation_display import SimulationDisplay
from gui_constants import GuiConstants
from constants import Constants
from configure_window import ConfigureWindow
from satellite_window import SatelliteWindow
from monitor import Monitor
from planet import Planet
from simulation import Simulation
from orbit import Orbit
from satellite import Satellite
from propulsion import Propulsion

class MainWindow(QMainWindow):
    """
    The main application window, responsible for menus, UI, and interactions
    """
    
    def __init__(self, parent=None):
        """
        Initialize the main window
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(MainWindow, self).__init__(parent)
        
        # Set window properties
        self.setWindowTitle(Constants.programName)
        self.setWindowIcon(QIcon("icon.png"))
        
        # Initialize instance variables
        self.m_sim_display = None
        self.m_monitor = None
        self.action_toggle_play = None
        self.m_hovered_sat = ""
        
        # Set up menus
        self._setup_menus()
        
        # Add simulation display
        self.m_sim_display = SimulationDisplay(GuiConstants.fps, self, "3D simulation rendering")
        self.m_sim_display.move(0, 0)
        self.m_sim_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.m_sim_display)
        
        # Add simulation monitor
        self.m_monitor = Monitor(None, self.m_sim_display)
        
        # Make monitor invisible at the beginning
        self.m_monitor.setVisible(False)
    
    def _setup_menus(self):
        """Set up the application menus and actions"""
        # Create main menus
        self.menu_file = self.menuBar().addMenu("&File")
        self.menu_sim = self.menuBar().addMenu("&Simulation")
        self.menu_sat = self.menuBar().addMenu("&Satellites")
        self.menu_help = self.menuBar().addMenu("&?")
        
        # File menu
        action_new = QAction("&New simulation", self)
        self.menu_file.addAction(action_new)
        action_new.setShortcut("Ctrl+N")
        
        action_open = QAction("&Open existing simulation", self)
        self.menu_file.addAction(action_open)
        action_open.setShortcut("Ctrl+O")
        
        action_save = QAction("&Save simulation", self)
        self.menu_file.addAction(action_save)
        action_save.setShortcut("Ctrl+S")
        
        self.menu_file.addSeparator()
        
        action_quit = QAction("&Quit", self)
        self.menu_file.addAction(action_quit)
        action_quit.setShortcut("Ctrl+Q")
        
        # Simulation menu
        self.action_toggle_play = QAction("", self)
        self.menu_sim.addAction(self.action_toggle_play)
        self.action_toggle_play.setShortcut("Space")
        
        # Set initial text based on autoPlay constant
        if Constants.autoPlay:
            self.action_toggle_play.setText("Pause")
        else:
            self.action_toggle_play.setText("Play")
        
        self.menu_sim.addSeparator()
        
        action_configure = QAction("Configure", self)
        self.menu_sim.addAction(action_configure)
        action_configure.setShortcut("Ctrl+C")
        
        self.menu_sim.addSeparator()
        
        action_reset = QAction("Reset to t = 0", self)
        self.menu_sim.addAction(action_reset)
        action_reset.setShortcut("Ctrl+R")
        
        action_reset_all = QAction("Reset all", self)
        self.menu_sim.addAction(action_reset_all)
        action_reset_all.setShortcut("Ctrl+Shift+R")
        
        # Satellites menu
        # List of all satellites will be inserted here...
        self.menu_sat.addSeparator()
        
        action_add_sat = QAction("Add new satellite", self)
        self.menu_sat.addAction(action_add_sat)
        action_add_sat.setShortcut("Ctrl+A")
        
        # Help menu
        action_about = QAction("About", self)
        self.menu_help.addAction(action_about)
        
        # Connect signals/slots
        action_quit.triggered.connect(self.close)
        action_about.triggered.connect(self.about_qt)
        self.action_toggle_play.triggered.connect(self.toggle_play_slot)
        action_configure.triggered.connect(self.configure_slot)
        action_reset.triggered.connect(self.reset_slot)
        action_reset_all.triggered.connect(self.reset_all_slot)
        action_new.triggered.connect(self.new_slot)
        action_open.triggered.connect(self.open_slot)
        action_save.triggered.connect(self.save_slot)
        action_add_sat.triggered.connect(self.add_satellite_slot)
        
        # Connect satellite menu actions
        self.menu_sat.hovered.connect(self.hovered_satellite_slot)
    
    def about_qt(self):
        """Display the Qt About dialog"""
        QMessageBox.aboutQt(self)
    
    @pyqtSlot()
    def toggle_play_slot(self):
        """Toggle play/pause of the simulation"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            self.m_sim_display.sim().toggle_play()
            if self.m_sim_display.sim().play:
                self.action_toggle_play.setText("Pause")
            else:
                self.action_toggle_play.setText("Play")
    
    @pyqtSlot()
    def configure_slot(self):
        """Open the configuration dialog"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            self.m_sim_display.sim().set_play(False)
            conf_window = ConfigureWindow(False, self.m_sim_display.sim())
            if conf_window.exec_():
                self.setWindowTitle(self.m_sim_display.sim().name)
                self.m_sim_display.timer().setInterval(
                    1000 * self.m_sim_display.sim().dt / self.m_sim_display.sim().speed
                )
    
    @pyqtSlot()
    def add_satellite_slot(self):
        """Add a new satellite to the simulation"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            self.m_sim_display.sim().set_play(False)
            
            # Allocate new satellite
            sat = Satellite(
                Orbit(self.m_sim_display.sim().get_planet(), 1.0, 0.0, 0.0),
                self.m_sim_display.sim().get_planet(),
                Propulsion()
            )
            sat_window = SatelliteWindow(True, sat, self.m_sim_display.sim().get_planet())
            
            if sat_window.exec_():
                # Check whether satellite with the same name exists, if yes rename it
                suffix = 1
                sat_name = sat.get_name()
                doublon = True
                
                while doublon:
                    doublon = False
                    for i in range(self.m_sim_display.sim().nsat()):
                        if self.m_sim_display.sim().sat(i).get_name() == sat_name:
                            doublon = True
                            sat_name = sat.get_name() + f"[{suffix}]"
                            suffix += 1
                            break
                
                # Inform user if satellite has been renamed
                if sat_name != sat.get_name():
                    QMessageBox.information(
                        self,
                        "Name conflict",
                        f"A satellite named {sat.get_name()} already exists. "
                        f"The created satellite has been automatically renamed to {sat_name}"
                    )
                    sat.set_name(sat_name)
                
                self.m_sim_display.sim().add_satellite(sat)
                self.update_sat_menu()
    
    @pyqtSlot()
    def rem_satellite_slot(self):
        """Remove the currently hovered satellite"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            for i in range(self.m_sim_display.sim().nsat()):
                if self.m_sim_display.sim().sat(i).get_name() == self.m_hovered_sat:
                    # Ask confirmation
                    response = QMessageBox.question(
                        self,
                        "Remove satellite",
                        "Remove this satellite?<br/>If you did not export your satellite, "
                        "its configuration will be lost.",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if response == QMessageBox.Yes:
                        self.m_sim_display.sim().rem_satellite(i)
                        self.update_sat_menu()
                    return
    
    @pyqtSlot(QAction)
    def hovered_satellite_slot(self, action):
        """Handle satellite menu item hover events"""
        if (action.text() != "Add new satellite" and
            action.text() != "Configure" and
            action.text() != "Remove"):
            self.m_hovered_sat = action.text()
    
    @pyqtSlot()
    def conf_satellite_slot(self):
        """Configure the currently hovered satellite"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            self.m_sim_display.sim().set_play(False)
            
            for i in range(self.m_sim_display.sim().nsat()):
                if self.m_sim_display.sim().sat(i).get_name() == self.m_hovered_sat:
                    sat_window = SatelliteWindow(
                        False,
                        self.m_sim_display.sim().sat(i),
                        self.m_sim_display.sim().get_planet()
                    )
                    sat_window.exec_()
                    self.update_sat_menu()
                    return
    
    def closeEvent(self, event):
        """Handle the window close event"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            self.m_sim_display.sim().set_play(False)
            
            # Save and close simulation
            response = self.show_save_msg_box("Quit")
            
            if response == QMessageBox.Save:
                # Save and quit
                self.save_simulation()
                event.accept()
            elif response == QMessageBox.Discard:
                # Just quit
                event.accept()
            else:  # QMessageBox.Cancel or default
                # Don't quit
                event.ignore()
                return
            
            del self.m_sim_display.sim()
            self.m_sim_display.set_simulation(None)
    
    @pyqtSlot()
    def new_slot(self):
        """Create a new simulation"""
        if self.m_sim_display is not None:
            if self.m_sim_display.sim() is not None:
                self.m_sim_display.sim().set_play(False)
                
                # Save and close simulation
                response = self.show_save_msg_box("New simulation")
                
                if response == QMessageBox.Save:
                    # Save and continue
                    self.save_simulation()
                elif response == QMessageBox.Discard:
                    # Continue without saving
                    pass
                else:  # QMessageBox.Cancel or default
                    # Quit creating a new simulation
                    return
                
                del self.m_sim_display.sim()
                self.m_sim_display.set_simulation(None)
                self.m_monitor.set_simulation(None)
            
            # Allocate new simulation
            planet = Planet()
            name = "New_Simulation"
            
            sim = Simulation(planet, name)
            
            new_window = ConfigureWindow(True, sim)
            if new_window.exec_():
                self.m_sim_display.set_simulation(sim)
                self.m_monitor.set_simulation(sim)
                # Force load planet texture
                self.m_sim_display.load_texture(self.m_sim_display.sim().get_planet().get_img_path(), 0)
                
                self.setWindowTitle(self.m_sim_display.sim().name)
                self.m_sim_display.timer().setInterval(
                    1000 * self.m_sim_display.sim().dt / self.m_sim_display.sim().speed
                )
                self.update_sat_menu()
            
            # Update monitor size
            self.m_monitor.on_resize(self.m_sim_display.width(), self.m_sim_display.height())
            self.m_monitor.setVisible(True)
    
    @pyqtSlot()
    def open_slot(self):
        """Open an existing simulation"""
        if self.m_sim_display is not None:
            if self.m_sim_display.sim() is not None:
                self.m_sim_display.sim().set_play(False)
                
                # Save and close simulation
                response = self.show_save_msg_box("Open simulation")
                
                if response == QMessageBox.Save:
                    # Save and continue
                    self.save_simulation()
                elif response == QMessageBox.Discard:
                    # Continue without saving
                    pass
                else:  # QMessageBox.Cancel or default
                    # Quit opening a simulation
                    return
                
                del self.m_sim_display.sim()
                self.m_sim_display.set_simulation(None)
                self.m_monitor.set_simulation(None)
            
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open simulation",
                os.getcwd(),
                "Simulations (*.sim)"
            )
            
            if file_path:
                try:
                    # Open and parse file
                    with open(file_path, 'r') as file:
                        lines = file.readlines()
                    
                    # Default values
                    sim_name = ""
                    sim_time = 0.0
                    sim_dt = 1.0
                    sim_speed = 1.0
                    n = 0
                    planet_name = Constants.defaultPlanetName
                    planet_radius = Constants.r_earth
                    planet_mu = Constants.mu_earth
                    planet_day = Constants.day_earth
                    planet_img = Constants.defaultImgPath
                    sat_names = []
                    orbit_a = []
                    orbit_e = []
                    orbit_i = []
                    orbit_om = []
                    orbit_om_small = []
                    orbit_tp = []
                    orbit_m = []
                    
                    # Parse file content
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        if line == "----------":
                            i += 1
                            section = lines[i].strip()
                            
                            if section == "Simulation":
                                # Simulation name
                                i += 1
                                sim_name = lines[i].split(': ')[1].strip()
                                
                                # Current time
                                i += 1
                                sim_time = float(lines[i].split(': ')[1].strip())
                                
                                # Time step
                                i += 1
                                sim_dt = float(lines[i].split(': ')[1].strip())
                                
                                # Speed
                                i += 1
                                sim_speed = float(lines[i].split(': ')[1].strip())
                                
                                # Number of satellites
                                i += 1
                                n = int(lines[i].split(': ')[1].strip())
                            
                            elif section == "Planet":
                                # Planet name
                                i += 1
                                planet_name = lines[i].split(': ')[1].strip()
                                
                                # Planet radius
                                i += 1
                                planet_radius = float(lines[i].split(': ')[1].strip())
                                
                                # Planet mu
                                i += 1
                                planet_mu = float(lines[i].split(': ')[1].strip())
                                
                                # Planet day
                                i += 1
                                planet_day = float(lines[i].split(': ')[1].strip())
                                
                                # Planet imgPath
                                i += 1
                                planet_img = lines[i].split(': ')[1].strip()
                            
                            elif section == "Satellites":
                                sat_names = [""] * n
                                orbit_a = [0.0] * n
                                orbit_e = [0.0] * n
                                orbit_i = [0.0] * n
                                orbit_om = [0.0] * n
                                orbit_om_small = [0.0] * n
                                orbit_tp = [0.0] * n
                                orbit_m = [0.0] * n
                                
                                for j in range(n):
                                    # Skip separation line
                                    i += 1
                                    
                                    # Satellite name
                                    i += 1
                                    sat_names[j] = lines[i].split(': ')[1].strip()
                                    
                                    # a
                                    i += 1
                                    orbit_a[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # e
                                    i += 1
                                    orbit_e[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # i
                                    i += 1
                                    orbit_i[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # Omega
                                    i += 1
                                    orbit_om[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # omega
                                    i += 1
                                    orbit_om_small[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # tp
                                    i += 1
                                    orbit_tp[j] = float(lines[i].split(': ')[1].strip())
                                    
                                    # M
                                    i += 1
                                    orbit_m[j] = float(lines[i].split(': ')[1].strip())
                        i += 1
                    
                    # Allocate simulation
                    planet = Planet(planet_mu, planet_radius, planet_day, planet_name, planet_img)
                    sim = Simulation(planet, sim_name, sim_speed, sim_dt)
                    sim.set_t(sim_time)
                    
                    # Add satellites and set their position
                    for j in range(n):
                        orbit = Orbit(
                            planet,
                            orbit_a[j],
                            orbit_e[j],
                            orbit_i[j],
                            orbit_om[j],
                            orbit_om_small[j],
                            orbit_tp[j]
                        )
                        orbit.set_m(orbit_m[j])
                        sat = Satellite(orbit, planet, Propulsion(), sat_names[j])
                        sim.add_satellite(sat)
                    
                    self.m_sim_display.set_simulation(sim)
                    self.m_monitor.set_simulation(sim)
                    
                    # Force load planet texture
                    self.m_sim_display.load_texture(
                        self.m_sim_display.sim().get_planet().get_img_path(),
                        0
                    )
                    
                    self.setWindowTitle(self.m_sim_display.sim().name)
                    self.m_sim_display.timer().setInterval(
                        1000 * self.m_sim_display.sim().dt / self.m_sim_display.sim().speed
                    )
                    self.m_sim_display.update_gl()
                    self.update_sat_menu()
                
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error opening simulation {file_path}: {str(e)}"
                    )
            
            # Update monitor size
            self.m_monitor.on_resize(self.m_sim_display.width(), self.m_sim_display.height())
            self.m_monitor.setVisible(True)
    
    @pyqtSlot()
    def reset_slot(self):
        """Reset the simulation to t=0"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            # Pause
            self.m_sim_display.sim().set_play(False)
            # Reset
            self.m_sim_display.sim().reset()
    
    @pyqtSlot()
    def reset_all_slot(self):
        """Reset the entire simulation, removing all satellites"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            # Pause
            self.m_sim_display.sim().set_play(False)
            
            # Ask confirmation
            response = QMessageBox.question(
                self,
                "Reset all simulation",
                "Remove all satellites and reset simulation?<br/>"
                "If you did not export your satellites, their configuration will be lost.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if response == QMessageBox.Yes:
                # Remove all satellites and reset
                self.m_sim_display.sim().reset_all()
                self.update_sat_menu()
    
    def show_save_msg_box(self, title):
        """
        Show save confirmation dialog
        
        Args:
            title (str): Dialog title
            
        Returns:
            int: User's response (QMessageBox.Save, QMessageBox.Discard, or QMessageBox.Cancel)
        """
        save_question_box = QMessageBox(self)
        save_question_box.setWindowTitle(title)
        save_question_box.setIcon(QMessageBox.Question)
        
        save_question_box.addButton(QMessageBox.Save)
        save_question_box.addButton(QMessageBox.Discard)
        save_question_box.addButton(QMessageBox.Cancel)
        
        save_question_box.setDefaultButton(QMessageBox.Save)
        
        save_question_box.setText(
            "Do you want to save your current simulation?<br/>"
            "If you click \"Discard\", you will lose your simulation current state "
            "and unsaved settings. Only the logged data will be kept on disk."
        )
        
        return save_question_box.exec_()
    
    def save_simulation(self):
        """Save the current simulation to a file"""
        if self.m_sim_display is not None and self.m_sim_display.sim() is not None:
            # Pause
            self.m_sim_display.sim().set_play(False)
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save simulation",
                f"{self.m_sim_display.sim().name}.sim",
                "Simulations (*.sim)"
            )
            
            if file_path:
                try:
                    current_time = QDateTime.currentDateTime().toString()
                    result = self.m_sim_display.sim().save_to_file(file_path, current_time)
                    if result != 0:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Error saving simulation {self.m_sim_display.sim().name}.sim"
                        )
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error saving simulation: {str(e)}"
                    )
    
    @pyqtSlot()
    def save_slot(self):
        """Slot for save action"""
        self.save_simulation()
    
    def update_sat_menu(self):
        """Update the satellites menu with current satellites"""
        self.menu_sat.clear()
        
        # List of all satellites
        if self.m_sim_display and self.m_sim_display.sim():
            for i in range(self.m_sim_display.sim().nsat()):
                sat_menu = self.menu_sat.addMenu(self.m_sim_display.sim().sat(i).get_name())
                
                conf_action = QAction("Configure", self)
                rem_action = QAction("Remove", self)
                
                sat_menu.addAction(conf_action)
                sat_menu.addAction(rem_action)
                
                conf_action.triggered.connect(self.conf_satellite_slot)
                rem_action.triggered.connect(self.rem_satellite_slot)
        
        self.menu_sat.addSeparator()
        
        action_add_sat = QAction("Add new satellite", self)
        self.menu_sat.addAction(action_add_sat)
        action_add_sat.setShortcut("Ctrl+A")
        
        action_add_sat.triggered.connect(self.add_satellite_slot)
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super(MainWindow, self).resizeEvent(event)
        if self.m_monitor:
            self.m_monitor.on_resize(event.size().width(), event.size().height())