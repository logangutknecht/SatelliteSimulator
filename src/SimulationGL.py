from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, pyqtSlot, Qt
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtOpenGL import QGLWidget
import OpenGL.GL as GL
import OpenGL.GLU as GLU

class SimulationGL(QGLWidget):
    """
    Base class for OpenGL simulation widgets
    
    This abstract class provides basic functionality for OpenGL rendering
    with a timer for animation updates.
    """
    
    def __init__(self, frames_per_second=0, parent=None, name=None):
        """
        Initialize the OpenGL widget
        
        Args:
            frames_per_second (int): Target FPS for animation, 0 means no animation
            parent (QWidget, optional): Parent widget
            name (str, optional): Widget name for window title
        """
        super(SimulationGL, self).__init__(parent)
        
        if name:
            self.setWindowTitle(name)
        
        self.t_Timer = None
        
        # Set up animation timer if frames_per_second is specified
        if frames_per_second > 0:
            timer_interval = 1000 // frames_per_second
            self.t_Timer = QTimer(self)
            self.t_Timer.timeout.connect(self.time_out_slot)
            self.t_Timer.start(timer_interval)
    
    def initializeGL(self):
        """
        Initialize OpenGL settings
        
        This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError("initializeGL must be implemented by subclasses")
    
    def resizeGL(self, width, height):
        """
        Handle resize events
        
        This is an abstract method that must be implemented by subclasses.
        
        Args:
            width (int): New width
            height (int): New height
        """
        raise NotImplementedError("resizeGL must be implemented by subclasses")
    
    def paintGL(self):
        """
        Render the OpenGL scene
        
        This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError("paintGL must be implemented by subclasses")
    
    def keyPressEvent(self, key_event):
        """
        Handle key press events
        
        This method can be overridden by subclasses to handle keyboard input.
        
        Args:
            key_event (QKeyEvent): Key event
        """
        # Base implementation does nothing
        pass
    
    @pyqtSlot()
    def time_out_slot(self):
        """
        Timer slot for animation updates
        
        Called at regular intervals to update the OpenGL rendering.
        """
        self.update()  # Use update() instead of updateGL() in newer PyQt versions
    
    def timer(self):
        """
        Get the animation timer
        
        Returns:
            QTimer: The animation timer
        """
        return self.t_Timer