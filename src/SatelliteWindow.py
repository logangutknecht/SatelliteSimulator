from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QGroupBox, QFormLayout,
                           QPushButton, QLineEdit, QDoubleSpinBox, QMessageBox)
from PyQt5.QtCore import pyqtSlot, QRegExp
from PyQt5.QtGui import QRegExpValidator
import math
from src.Constants import Constants
from src.Satellite import Satellite
from src.Planet import Planet
from src.NORAD.TLE_Importer import TLEImporter

class SatelliteWindow(QDialog):
    """
    Dialog for configuring a satellite in the simulation
    """
    
    def __init__(self, is_new, sat, planet, parent=None):
        """
        Initialize the satellite configuration dialog
        
        Args:
            is_new (bool): True if creating a new satellite, False if editing
            sat (Satellite): The satellite to configure
            planet (Planet): The planet the satellite orbits
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(SatelliteWindow, self).__init__(parent)
        
        self.m_is_new = is_new
        self.m_sat = sat
        self.m_planet = planet
        
        # Set window properties
        self.setModal(True)
        self.setWindowTitle("Configure satellite")
        
        # Create layout
        self.main_layout = QVBoxLayout()
        self.sat_frame = QGroupBox("General information", self)
        self.orb_frame = QGroupBox("Orbit", self)
        self.att_frame = QGroupBox("Attitude", self)
        self.prop_frame = QGroupBox("Propulsion engine", self)
        
        # Add frames to layout
        self.main_layout.addWidget(self.sat_frame)
        self.main_layout.addWidget(self.orb_frame)
        self.main_layout.addWidget(self.att_frame)
        self.main_layout.addWidget(self.prop_frame)
        
        # Create form layouts
        self.sat_form = QFormLayout(self.sat_frame)
        self.orb_form = QFormLayout(self.orb_frame)
        self.att_form = QFormLayout(self.att_frame)
        self.prop_form = QFormLayout(self.prop_frame)
        
        # General information section
        self.sat_name_field = QLineEdit()
        
        # Set validator to prevent spaces and brackets
        filter_regex = QRegExp("^[^\]\[ ]+$")
        validator = QRegExpValidator(filter_regex)
        self.sat_name_field.setValidator(validator)
        
        self.sat_form.addRow("Satellite name:", self.sat_name_field)
        self.import_button = QPushButton("Import satellite")
        self.sat_form.addWidget(self.import_button)


        # NORAD ID field and import button
        self.norad_id_field = QLineEdit()
        self.import_from_norad_button = QPushButton("Import from NORAD ID")
        self.sat_form.addRow("NORAD ID:", self.norad_id_field)
        self.sat_form.addWidget(self.import_from_norad_button)
        
        # Connect NORAD button
        self.import_from_norad_button.clicked.connect(self.import_from_norad_slot)
    
        
        # Orbit section
        # Semi-major axis
        self.a_box = QDoubleSpinBox()
        self.a_box.setDecimals(3)
        self.a_box.setSingleStep(1.0)
        self.a_box.setMinimum(self.m_planet.get_radius())
        self.a_box.setMaximum(Constants.maxSatA)
        self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
        self.orb_form.addRow("Semimajor axis (km):", self.a_box)
        
        # Eccentricity
        self.e_box = QDoubleSpinBox()
        self.e_box.setDecimals(8)
        self.e_box.setSingleStep(0.01)
        self.e_box.setMinimum(0.0)
        self.e_box.setMaximum(0.999)
        self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
        self.orb_form.addRow("Eccentricity:", self.e_box)
        
        # Inclination
        self.i_box = QDoubleSpinBox()
        self.i_box.setDecimals(4)
        self.i_box.setSingleStep(0.1)
        self.i_box.setMinimum(0.0)
        self.i_box.setMaximum(Constants.pi)
        self.i_box.setToolTip(f"[{self.i_box.minimum()}, {self.i_box.maximum()}]")
        self.orb_form.addRow("Inclination (rad):", self.i_box)
        
        # Longitude of the ascending node
        self.om_box = QDoubleSpinBox()
        self.om_box.setDecimals(4)
        self.om_box.setSingleStep(0.1)
        self.om_box.setMinimum(0.0)
        self.om_box.setMaximum(Constants.twopi)
        self.om_box.setToolTip(f"[{self.om_box.minimum()}, {self.om_box.maximum()}]")
        self.orb_form.addRow("Longitude of the ascending node (rad):", self.om_box)
        
        # Argument of periapsis
        self.om_small_box = QDoubleSpinBox()
        self.om_small_box.setDecimals(4)
        self.om_small_box.setSingleStep(0.1)
        self.om_small_box.setMinimum(0.0)
        self.om_small_box.setMaximum(Constants.twopi)
        self.om_small_box.setToolTip(f"[{self.om_small_box.minimum()}, {self.om_small_box.maximum()}]")
        self.orb_form.addRow("Argument of periapsis (rad):", self.om_small_box)
        
        # Epoch
        self.tp_box = QDoubleSpinBox()
        self.tp_box.setDecimals(4)
        self.tp_box.setSingleStep(1.0)
        period = 1.0 / Constants.twopi * math.sqrt(pow(self.a_box.value(), 3.0) / self.m_planet.get_mu())
        self.tp_box.setRange(-period, period)
        self.tp_box.setToolTip(f"[{self.tp_box.minimum()}, {self.tp_box.maximum()}]")
        self.orb_form.addRow("Epoch (s) - can be negative:", self.tp_box)
        
        # Attitude section
        # Rotation around X
        self.rx_box = QDoubleSpinBox()
        self.rx_box.setDecimals(4)
        self.rx_box.setSingleStep(0.1)
        self.rx_box.setMinimum(0.0)
        self.rx_box.setMaximum(Constants.twopi)
        self.rx_box.setToolTip(f"[{self.rx_box.minimum()}, {self.rx_box.maximum()}]")
        self.att_form.addRow("Rotation around X axis (rad):", self.rx_box)
        
        # Rotation around Y
        self.ry_box = QDoubleSpinBox()
        self.ry_box.setDecimals(4)
        self.ry_box.setSingleStep(0.1)
        self.ry_box.setMinimum(0.0)
        self.ry_box.setMaximum(Constants.twopi)
        self.ry_box.setToolTip(f"[{self.ry_box.minimum()}, {self.ry_box.maximum()}]")
        self.att_form.addRow("Rotation around Y axis (rad):", self.ry_box)
        
        # Rotation around Z
        self.rz_box = QDoubleSpinBox()
        self.rz_box.setDecimals(4)
        self.rz_box.setSingleStep(0.1)
        self.rz_box.setMinimum(0.0)
        self.rz_box.setMaximum(Constants.twopi)
        self.rz_box.setToolTip(f"[{self.rz_box.minimum()}, {self.rz_box.maximum()}]")
        self.att_form.addRow("Rotation around Z axis (rad):", self.rz_box)
        
        # Propulsion section (TODO)
        
        # Confirm button
        self.confirm_button = QPushButton()
        if is_new:
            self.confirm_button.setText("Add satellite")
        else:
            self.confirm_button.setText("Apply")
        self.confirm_button.setDefault(True)
        self.main_layout.addWidget(self.confirm_button)
        
        # Set the layout
        self.setLayout(self.main_layout)
        
        # If existing satellite, use its values in form, else default values
        if not is_new:
            self.sat_name_field.setText(self.m_sat.get_name())
            self.a_box.setValue(self.m_sat.get_orbit().get_a())
            self.a_box.setMinimum(self.m_planet.get_radius() / (1.0 - self.m_sat.get_orbit().get_e()))
            self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
            self.e_box.setValue(self.m_sat.get_orbit().get_e())
            self.e_box.setMaximum(1.0 - self.m_planet.get_radius() / self.m_sat.get_orbit().get_a())
            self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
            self.i_box.setValue(self.m_sat.get_orbit().get_i())
            self.om_box.setValue(self.m_sat.get_orbit().get_omega())
            self.om_small_box.setValue(self.m_sat.get_orbit().get_omega_small())
            self.tp_box.setValue(self.m_sat.get_orbit().get_tp())
            self.rx_box.setValue(self.m_sat.get_rx())
            self.ry_box.setValue(self.m_sat.get_ry())
            self.rz_box.setValue(self.m_sat.get_rz())
        else:
            self.sat_name_field.setText("Satellite")
            self.a_box.setValue(self.m_planet.a_geo())
            self.e_box.setValue(0.0)
            self.i_box.setValue(0.0)
            self.om_box.setValue(0.0)
            self.om_small_box.setValue(0.0)
            self.tp_box.setValue(0.0)
            self.rx_box.setValue(0.0)
            self.ry_box.setValue(0.0)
            self.rz_box.setValue(0.0)
        
        # Connect signals
        self.a_box.valueChanged.connect(self.on_a_changed)
        self.e_box.valueChanged.connect(self.on_e_changed)
        self.confirm_button.clicked.connect(self.confirm_slot)
    
    @pyqtSlot(float)
    def on_a_changed(self, a):
        """
        Handle changes to the semi-major axis value
        
        Args:
            a (float): New semi-major axis value
        """
        # Update e maximum
        self.e_box.setMaximum(1.0 - self.m_planet.get_radius() / a)
        self.e_box.setToolTip(f"[{self.e_box.minimum()}, {self.e_box.maximum()}]")
        
        # Update tp range
        period = 1.0 / Constants.twopi * math.sqrt(pow(self.a_box.value(), 3.0) / self.m_planet.get_mu())
        self.tp_box.setRange(-period, period)
        self.tp_box.setToolTip(f"[{self.tp_box.minimum()}, {self.tp_box.maximum()}]")
    
    @pyqtSlot(float)
    def on_e_changed(self, e):
        """
        Handle changes to the eccentricity value
        
        Args:
            e (float): New eccentricity value
        """
        # Update a minimum
        self.a_box.setMinimum(self.m_planet.get_radius() / (1.0 - e))
        self.a_box.setToolTip(f"[{self.a_box.minimum()}, {self.a_box.maximum()}]")
    
    @pyqtSlot()
    def confirm_slot(self):
        """Handle confirm button click"""
        if not self.sat_name_field.text():
            QMessageBox.warning(self, "Empty name", "Please enter a satellite name!")
            return
        
        # Update satellite with form values
        self.m_sat.set_name(self.sat_name_field.text())
        self.m_sat.get_orbit().set_a(self.a_box.value())
        self.m_sat.get_orbit().set_e(self.e_box.value())
        self.m_sat.get_orbit().set_i(self.i_box.value())
        self.m_sat.get_orbit().set_omega(self.om_box.value())
        self.m_sat.get_orbit().set_omega_small(self.om_small_box.value())
        self.m_sat.get_orbit().set_tp(self.tp_box.value())
        self.m_sat.set_rx(self.rx_box.value())
        self.m_sat.set_ry(self.ry_box.value())
        self.m_sat.set_rz(self.rz_box.value())
        
        self.done(QDialog.Accepted)

    @pyqtSlot()
    def import_from_norad_slot(self):
        """Import satellite data from NORAD ID"""
        norad_id = self.norad_id_field.text()
        if not norad_id:
            QMessageBox.warning(self, "Invalid NORAD ID", "Please enter a valid NORAD ID.")
            return
            
        try:
            importer = TLEImporter()
            satellite = importer.fetch_satellite_by_norad_id(norad_id)
            
            if not satellite:
                QMessageBox.warning(self, "Satellite Not Found", 
                                f"Could not find satellite with NORAD ID {norad_id}.")
                return
                
            # Convert to orbit parameters and update the UI
            orbit = importer.convert_to_simulator_orbit(satellite, self.m_planet)
            
            # Update the satellite's orbit with the imported parameters
            self.m_sat.get_orbit().set_a(orbit.get_a())
            self.m_sat.get_orbit().set_e(orbit.get_e())
            self.m_sat.get_orbit().set_i(orbit.get_i())
            self.m_sat.get_orbit().set_omega(orbit.get_omega())
            self.m_sat.get_orbit().set_omega_small(orbit.get_omega_small())
            
            # Update form fields with the imported data
            self.a_box.setValue(orbit.get_a())
            self.e_box.setValue(orbit.get_e())
            self.i_box.setValue(orbit.get_i())
            self.om_box.setValue(orbit.get_omega())
            self.om_small_box.setValue(orbit.get_omega_small())
            
            # Set satellite name from TLE if available
            self.sat_name_field.setText(satellite.name)
            self.m_sat.set_name(satellite.name)
            
            QMessageBox.information(self, "Import Successful", 
                                f"Successfully imported data for satellite {satellite.name}.")
                                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", 
                            f"An error occurred while importing the satellite data: {str(e)}")