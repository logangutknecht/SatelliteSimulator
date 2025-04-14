from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QGroupBox, 
                           QFormLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from src.Satellite import Satellite

class SatelliteInfoPanel(QWidget):
    """
    Widget that displays detailed information about a selected satellite
    """
    
    def __init__(self, parent=None):
        """
        Initialize the satellite info panel
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(SatelliteInfoPanel, self).__init__(parent)
        
        # Setup widget appearance
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))  # Set text color to black
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # Create main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignTop)
        
        # Create group boxes for different sections
        self.general_group = QGroupBox("General Information")
        self.orbit_group = QGroupBox("Orbital Parameters")
        self.attitude_group = QGroupBox("Attitude")
        
        # Set text color for group box titles
        self.general_group.setStyleSheet("QGroupBox { color: black; }")
        self.orbit_group.setStyleSheet("QGroupBox { color: black; }")
        self.attitude_group.setStyleSheet("QGroupBox { color: black; }")
        
        # Create form layouts
        self.general_form = QFormLayout()
        self.orbit_form = QFormLayout()
        self.attitude_form = QFormLayout()
        
        # Add labels for each field
        self.name_label = QLabel("No satellite selected")
        self.name_label.setStyleSheet("QLabel { color: black; }")
        name_field_label = QLabel("Name:")
        name_field_label.setStyleSheet("QLabel { color: black; }")
        self.general_form.addRow(name_field_label, self.name_label)
        
        # Orbital parameters
        self.semi_major_axis_label = QLabel("-")
        self.eccentricity_label = QLabel("-")
        self.inclination_label = QLabel("-")
        self.argument_of_perigee_label = QLabel("-")
        self.right_ascension_label = QLabel("-")
        self.true_anomaly_label = QLabel("-")
        
        # Set text color for all orbital parameter labels
        for label in [self.semi_major_axis_label, self.eccentricity_label, 
                     self.inclination_label, self.argument_of_perigee_label,
                     self.right_ascension_label, self.true_anomaly_label]:
            label.setStyleSheet("QLabel { color: black; }")
        
        # Add orbital parameter rows with black text labels
        self.orbit_form.addRow(QLabel("Semi-major axis:"), self.semi_major_axis_label)
        self.orbit_form.addRow(QLabel("Eccentricity:"), self.eccentricity_label)
        self.orbit_form.addRow(QLabel("Inclination:"), self.inclination_label)
        self.orbit_form.addRow(QLabel("Argument of perigee:"), self.argument_of_perigee_label)
        self.orbit_form.addRow(QLabel("Right ascension:"), self.right_ascension_label)
        self.orbit_form.addRow(QLabel("True anomaly:"), self.true_anomaly_label)
        
        # Set text color for row labels
        for i in range(self.orbit_form.rowCount()):
            label_item = self.orbit_form.itemAt(i, QFormLayout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setStyleSheet("QLabel { color: black; }")
        
        # Attitude parameters
        self.rx_label = QLabel("-")
        self.ry_label = QLabel("-")
        self.rz_label = QLabel("-")
        
        # Set text color for all attitude labels
        for label in [self.rx_label, self.ry_label, self.rz_label]:
            label.setStyleSheet("QLabel { color: black; }")
        
        # Add attitude parameter rows with black text labels
        self.attitude_form.addRow(QLabel("Rotation X:"), self.rx_label)
        self.attitude_form.addRow(QLabel("Rotation Y:"), self.ry_label)
        self.attitude_form.addRow(QLabel("Rotation Z:"), self.rz_label)
        
        # Set text color for row labels
        for i in range(self.attitude_form.rowCount()):
            label_item = self.attitude_form.itemAt(i, QFormLayout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setStyleSheet("QLabel { color: black; }")
        
        # Set layouts for group boxes
        self.general_group.setLayout(self.general_form)
        self.orbit_group.setLayout(self.orbit_form)
        self.attitude_group.setLayout(self.attitude_form)
        
        # Add group boxes to main layout
        self.main_layout.addWidget(self.general_group)
        self.main_layout.addWidget(self.orbit_group)
        self.main_layout.addWidget(self.attitude_group)
        
        # Set the main layout
        self.setLayout(self.main_layout)
        
        # Set fixed width
        self.setFixedWidth(300)
    
    def update_satellite_info(self, satellite: Satellite):
        """
        Update the panel with information from the selected satellite
        
        Args:
            satellite (Satellite): The satellite to display information for
        """
        if satellite is None:
            self.clear_info()
            return
            
        # Update general information
        self.name_label.setText(satellite.get_name())
        
        # Update orbital parameters
        orbit = satellite.get_orbit()
        self.semi_major_axis_label.setText(f"{orbit.get_a():.2f} km")
        self.eccentricity_label.setText(f"{orbit.get_e():.6f}")
        self.inclination_label.setText(f"{orbit.get_i():.2f}°")
        self.argument_of_perigee_label.setText(f"{orbit.get_omega():.2f}°")
        self.right_ascension_label.setText(f"{orbit.get_omega_small():.2f}°")
        self.true_anomaly_label.setText(f"{orbit.get_tp():.2f}°")
        
        # Update attitude parameters
        self.rx_label.setText(f"{satellite.get_rx():.2f}°")
        self.ry_label.setText(f"{satellite.get_ry():.2f}°")
        self.rz_label.setText(f"{satellite.get_rz():.2f}°")
    
    def clear_info(self):
        """Clear all information from the panel"""
        self.name_label.setText("No satellite selected")
        self.semi_major_axis_label.setText("-")
        self.eccentricity_label.setText("-")
        self.inclination_label.setText("-")
        self.argument_of_perigee_label.setText("-")
        self.right_ascension_label.setText("-")
        self.true_anomaly_label.setText("-")
        self.rx_label.setText("-")
        self.ry_label.setText("-")
        self.rz_label.setText("-") 