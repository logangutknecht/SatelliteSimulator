from PyQt5.QtWidgets import (QDialog, QGridLayout, QFormLayout, QGroupBox, 
                            QLineEdit, QLabel, QDoubleSpinBox, QPushButton, 
                            QFileDialog, QCheckBox, QMessageBox)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal, pyqtSlot
import os
from src.Constants import Constants
from src.Simulation import Simulation

class ConfigureWindow(QDialog):
    """
    ConfigureWindow provides a dialog to configure simulation parameters
    """
    
    def __init__(self, is_new, sim, parent=None):
        """
        Initialize the configure window
        
        Args:
            is_new (bool): True if creating a new simulation, False if editing existing
            sim (Simulation): The simulation to configure
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(ConfigureWindow, self).__init__(parent)
        
        self.m_is_new = is_new
        self.m_sim = sim
        
        # Setup window properties
        self.setModal(True)
        self.setWindowTitle("Configure simulation")
        
        # Create layouts
        self.main_layout = QGridLayout()
        self.sim_frame = QGroupBox("General information", self)
        self.planet_frame = QGroupBox("Planet", self)
        self.settings_frame = QGroupBox("Simulation settings", self)
        
        # Add frames to layout
        self.main_layout.addWidget(self.sim_frame, 0, 0, 1, 2)
        self.main_layout.addWidget(self.planet_frame, 1, 0)
        self.main_layout.addWidget(self.settings_frame, 1, 1)
        
        # Create form layouts for each section
        self.sim_form = QFormLayout(self.sim_frame)
        self.planet_form = QFormLayout(self.planet_frame)
        self.settings_form = QFormLayout(self.settings_frame)
        
        # General information section
        self.name_field = QLineEdit()
        self.sim_form.addRow("Simulation name:", self.name_field)
        
        # Planet configuration section
        self.planet_name_field = QLineEdit()
        self.planet_form.addRow("Planet name:", self.planet_name_field)
        
        # Planet radius
        self.planet_radius = QDoubleSpinBox()
        self.planet_radius.setMinimum(Constants.minPlanetRadius)
        self.planet_radius.setMaximum(Constants.maxPlanetRadius)
        self.planet_radius.setDecimals(4)
        self.planet_radius.setSingleStep(1.0)
        self.planet_form.addRow("Radius (km):", self.planet_radius)
        
        # Planet mu
        self.planet_mu = QDoubleSpinBox()
        self.planet_mu.setMinimum(Constants.minPlanetMu)
        self.planet_mu.setMaximum(Constants.maxPlanetMu)
        self.planet_mu.setDecimals(4)
        self.planet_mu.setSingleStep(1.0)
        self.planet_form.addRow("mu (km^3/s^2):", self.planet_mu)
        
        # Planet day duration
        self.planet_day = QDoubleSpinBox()
        self.planet_day.setMinimum(Constants.minPlanetDay)
        self.planet_day.setMaximum(Constants.maxPlanetDay)
        self.planet_day.setSingleStep(1.0)
        self.planet_form.addRow("Sideral day duration (s):", self.planet_day)
        
        # Planet texture
        self.planet_img_field = QLineEdit()
        self.planet_img_field.setReadOnly(True)
        self.planet_form.addRow("Planet texture:", self.planet_img_field)
        self.planet_img_field.installEventFilter(self)
        
        # Planet texture preview
        self.planet_label = QLabel()
        self.planet_form.addRow("Preview:", self.planet_label)
        
        # Simulation settings
        self.dt_field = QDoubleSpinBox()
        self.dt_field.setMinimum(Constants.minTimeStep)
        self.dt_field.setMaximum(Constants.maxTimeStep)
        self.dt_field.setDecimals(3)
        self.settings_form.addRow("Time step:", self.dt_field)
        self.dt_field.valueChanged.connect(self.update_speed_limits)
        
        self.speed_field = QDoubleSpinBox()
        self.speed_field.setMinimum(self.dt_field.value() / Constants.maxTimeStep)
        self.speed_field.setMaximum(self.dt_field.value() / Constants.minTimeStep)
        self.settings_form.addRow("Simulation speed factor:", self.speed_field)
        
        self.write_log_field = QCheckBox()
        self.settings_form.addRow("Write simulation into log file", self.write_log_field)
        
        self.auto_play_field = QCheckBox()
        self.settings_form.addRow("Start simulation automatically", self.auto_play_field)
        
        # Confirm button
        self.confirm_button = QPushButton()
        if is_new:
            self.confirm_button.setText("Start simulation")
        else:
            self.confirm_button.setText("Apply and reset simulation")
        self.confirm_button.setDefault(True)
        self.main_layout.addWidget(self.confirm_button, 2, 0, 1, 2)
        self.setLayout(self.main_layout)
        
        # If existing simulation, use its values in form
        if not is_new:
            self.name_field.setText(sim.name)
            self.planet_name_field.setText(sim.get_planet().get_name())
            self.planet_img_field.setText(sim.get_planet().get_img_path())
            self.planet_pix = QPixmap(sim.get_planet().get_img_path())
            self.planet_label.setPixmap(self.planet_pix.scaled(300, 150))
            self.planet_radius.setValue(sim.get_planet().get_radius())
            self.planet_mu.setValue(sim.get_planet().get_mu())
            self.planet_day.setValue(sim.get_planet().get_day())
            self.dt_field.setValue(sim.dt)
            self.speed_field.setValue(sim.speed)
            if sim.play:
                self.auto_play_field.setChecked(True)
            if sim.write_log:
                self.write_log_field.setChecked(True)
        else:
            # Default simulation name
            self.name_field.setText("New_Simulation")
            # Default planet name
            self.planet_name_field.setText(Constants.defaultPlanetName)
            # Default texture path
            self.planet_img_field.setText(Constants.defaultImgPath)
            # Default planet texture
            self.planet_pix = QPixmap(Constants.defaultImgPath)
            self.planet_label.setPixmap(self.planet_pix.scaled(300, 150))
            # Default time step
            self.dt_field.setValue(1.0)
            # Default speed
            self.speed_field.setValue(1.0)
            # Default planet characteristics (earth)
            self.planet_radius.setValue(Constants.r_earth)
            self.planet_mu.setValue(Constants.mu_earth)
            self.planet_day.setValue(Constants.day_earth)
            
            self.write_log_field.setChecked(Constants.writeLog)
            self.auto_play_field.setChecked(Constants.autoPlay)
        
        # Connect signals
        self.confirm_button.clicked.connect(self.confirm_slot)
    
    def eventFilter(self, obj, event):
        """
        Filter events to handle custom interactions
        
        Args:
            obj (QObject): The object that triggered the event
            event (QEvent): The event that was triggered
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if obj == self.planet_img_field and event.type() == QEvent.MouseButtonPress:
            img_path = QFileDialog.getOpenFileName(
                self, 
                "Select an image for your planet", 
                os.getcwd(), 
                "Images (*.jpg *.jpeg *.png *.bmp *.gif)"
            )[0]  # PyQt returns a tuple (filepath, filter)
            
            if img_path:
                self.planet_img_field.setText(img_path)
                self.planet_pix = QPixmap(img_path)
                self.planet_label.setPixmap(self.planet_pix.scaled(300, 150))
            return False  # Let the event continue to the edit
        return False
    
    @pyqtSlot()
    def confirm_slot(self):
        """
        Handle confirm button click
        """
        if not self.name_field.text():
            QMessageBox.warning(self, "Empty name", "Please enter a simulation name!")
            return
            
        if not self.planet_name_field.text():
            QMessageBox.warning(self, "Empty name", "Please enter a planet name!")
            return
            
        # Update simulation with form values
        self.m_sim.get_planet().set_day(self.planet_day.value())
        self.m_sim.get_planet().set_mu(self.planet_mu.value())
        self.m_sim.get_planet().set_radius(self.planet_radius.value())
        self.m_sim.get_planet().set_name(self.planet_name_field.text())
        self.m_sim.get_planet().set_img_path(self.planet_img_field.text())
        self.m_sim.set_name(self.name_field.text())
        self.m_sim.set_play(self.auto_play_field.isChecked())
        self.m_sim.set_write_log(self.write_log_field.isChecked())
        self.m_sim.set_speed(self.speed_field.value())
        self.m_sim.set_dt(self.dt_field.value())
        self.m_sim.reset()
        
        self.done(QDialog.Accepted)
    
    @pyqtSlot(float)
    def update_speed_limits(self, value):
        """
        Update speed limits based on time step
        
        Args:
            value (float): The new time step value
        """
        self.speed_field.setMinimum(value / Constants.maxTimeStep)
        self.speed_field.setMaximum(value / Constants.minTimeStep)