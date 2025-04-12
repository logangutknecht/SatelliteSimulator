from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QMouseEvent, QWheelEvent
from OpenGL.GLU import gluLookAt
from OpenGL.GL import glRotated

class TrackBallCamera:
    """
    Camera that provides trackball-like rotation and zoom functionality
    for 3D viewing
    """
    
    def __init__(self):
        """Initialize the trackball camera with default values"""
        self.m_hold = False
        self.m_dist = 40.0
        self.m_x_angle = 0.0
        self.m_y_angle = 0.0
        self.m_scroll_sens = 0.05
        self.m_motion_sens = 0.15
        self.m_last_pos = QPoint()
    
    def look(self):
        """Set the camera viewing transformation"""
        gluLookAt(0.0, 0.0, self.m_dist,
                  0.0, 0.0, 0.0,
                  0.0, 1.0, 0.0)
        glRotated(self.m_x_angle, 1.0, 0.0, 0.0)
        glRotated(self.m_y_angle, 0.0, 1.0, 0.0)
    
    def on_mouse_motion(self, event):
        """
        Handle mouse movement events
        
        Args:
            event (QMouseEvent): Mouse movement event
        """
        if self.m_hold:
            dx = event.x() - self.m_last_pos.x()
            dy = event.y() - self.m_last_pos.y()
            self.m_x_angle += dy * self.m_motion_sens
            self.m_y_angle += dx * self.m_motion_sens
            self.m_last_pos = event.pos()
    
    def on_mouse_press(self, event):
        """
        Handle mouse press events
        
        Args:
            event (QMouseEvent): Mouse press event
        """
        if not self.m_hold:
            self.m_hold = True
            self.m_last_pos = event.pos()
    
    def on_mouse_release(self, event):
        """
        Handle mouse release events
        
        Args:
            event (QMouseEvent): Mouse release event
        """
        if self.m_hold:
            self.m_hold = False
    
    def on_wheel(self, event):
        """
        Handle mouse wheel events for zooming
        
        Args:
            event (QWheelEvent): Mouse wheel event
        """
        self.m_dist -= event.angleDelta().y() * self.m_scroll_sens
        if self.m_dist < 0.1:
            self.m_dist = 0.1
    
    def on_key_pressed(self, event):
        """
        Handle key press events
        
        Args:
            event (QEvent): Key press event
        """
        # No implementation in original
        pass
    
    def set_motion_sens(self, s):
        """
        Set mouse motion sensitivity
        
        Args:
            s (float): Sensitivity value
        """
        self.m_motion_sens = s
    
    def set_scroll_sens(self, s):
        """
        Set scroll wheel sensitivity
        
        Args:
            s (float): Sensitivity value
        """
        self.m_scroll_sens = s