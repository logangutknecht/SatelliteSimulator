from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtGui import QPalette, QColor, QKeyEvent
from src.Simulation import Simulation
from src.GuiConstants import GuiConstants
import sys

class Monitor(QWidget):
    """
    Widget that displays simulation information at the bottom of the window
    """
    
    def __init__(self, sim, parent=None, refresh_rate=0):
        """
        Initialize the monitor widget
        
        Args:
            sim (Simulation): The simulation to monitor
            parent (QWidget, optional): Parent widget. Defaults to None.
            refresh_rate (int, optional): Refresh rate in milliseconds. Defaults to 0 (uses simulation rate).
        """
        super(Monitor, self).__init__(parent)
        
        self.m_sim = sim
        self.m_refresh_rate = refresh_rate
        
        # Setup widget appearance
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(100, 100, 100))
        palette.setColor(QPalette.Foreground, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(palette)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create layout
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        # Create labels
        self.title_label = QLabel(self)
        self.time_label = QLabel(self)
        
        # Add widgets to layout
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.time_label)
        
        # Update labels if simulation is available
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
        
        # Set the layout
        self.setLayout(self.main_layout)
        
        # Setup timer
        self.m_timer = QTimer()
        if self.m_refresh_rate == 0 and self.m_sim is not None:
            self.m_timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
        else:
            self.m_timer.start(refresh_rate)
        
        # Connect signals
        self.m_timer.timeout.connect(self.update_slot)
        
        # Position the widget
        if parent:
            self.move(0, parent.height() - GuiConstants.monitorH)
            self.setMinimumSize(parent.width(), GuiConstants.monitorH)
    
    def set_simulation(self, sim):
        """
        Set a new simulation to monitor
        
        Args:
            sim (Simulation): The simulation object
        """
        self.m_sim = sim
        
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
            
            if self.m_refresh_rate == 0:
                self.m_timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
    
    @pyqtSlot()
    def update_slot(self):
        """Update the display with current simulation information"""
        if self.m_sim is not None:
            self.title_label.setText(self.m_sim.name)
            self.time_label.setText(f"t = {self.m_sim.t} s")
            
            if self.m_refresh_rate == 0:
                self.m_timer.setInterval(int(1000 * self.m_sim.dt / self.m_sim.speed))
    
    def on_resize(self, w, h):
        """
        Handle parent widget resize events
        
        Args:
            w (int): New width
            h (int): New height
        """
        self.move(0, h - GuiConstants.monitorH)
        self.setMinimumSize(w, GuiConstants.monitorH)
    
    def keyPressEvent(self, event):
        """
        Handle key press events
        
        Args:
            event (QKeyEvent): Key event
        """
        if event.key() == Qt.Key_A:
            print("jcsuej")
            self.move(0, 50)