from PyQt5.QtWidgets import QMessageBox, QMenu
from PyQt5.QtGui import QImage, QCursor
from PyQt5.QtCore import QTimer, Qt, pyqtSlot, pyqtSignal
from PyQt5.QtOpenGL import QGLWidget

from OpenGL.GL import *
from OpenGL.GLU import *

from src.SimulationGL import SimulationGL
from src.Simulation import Simulation
from src.GuiConstants import GuiConstants
from src.Constants import Constants
from src.TrackBallCamera import TrackBallCamera
from src.PointPol import PointPol
import math

class SimulationDisplay(SimulationGL):
    """
    OpenGL widget for displaying the simulation in 3D
    """
    
    # Signal emitted when a satellite is selected
    satellite_selected = pyqtSignal(object)
    
    def __init__(self, frames_per_second=GuiConstants.fps, parent=None, name=None, sim=None):
        """
        Initialize the simulation display
        
        Args:
            frames_per_second (int): FPS for animation
            parent (QWidget, optional): Parent widget
            name (str, optional): Widget name
            sim (Simulation, optional): Simulation object
        """
        super(SimulationDisplay, self).__init__(frames_per_second, parent, name)
        
        self.m_sim = sim
        self.planet_texture_path = Constants.defaultImgPath
        self.planet_night_texture_path = None
        self.texture = [0, 0, 0, 0]  # Texture IDs (day, night, satellite, solar panel)
        self.sim_Timer = None
        self.m_selected_sat = None
        self.is_dragging = False
        self.highlighted_sat = None  # Track highlighted satellite
        
        # Always initialize the camera
        self.m_camera = TrackBallCamera()
        self.setCursor(QCursor(Qt.ArrowCursor))
        
        if self.m_sim is not None:
            self.planet_texture_path = self.m_sim.get_planet().get_img_path()
            self.planet_night_texture_path = self.m_sim.get_planet().get_night_img_path()
            self.sim_Timer = QTimer(self)
            self.sim_Timer.timeout.connect(self.sim_update_slot)
            self.sim_Timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
    
    def set_simulation(self, sim):
        """Set the current simulation"""
        self.m_sim = sim
        if self.m_sim is not None:
            # Create timer if it doesn't exist
            if not hasattr(self, 'sim_Timer') or self.sim_Timer is None:
                self.sim_Timer = QTimer(self)
                self.sim_Timer.timeout.connect(self.sim_update_slot)
            
            # Start timer with new interval
            self.sim_Timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
            
            # Load planet textures
            self.planet_texture_path = self.m_sim.get_planet().get_img_path()
            self.planet_night_texture_path = self.m_sim.get_planet().get_night_img_path()
            self.load_texture(self.planet_texture_path, 0)
            if self.planet_night_texture_path:
                self.load_texture(self.planet_night_texture_path, 1)
            
            # Initialize camera
            self.m_camera = TrackBallCamera()
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'm_sim') and self.m_sim is not None:
            del self.m_sim
        if hasattr(self, 'm_camera') and self.m_camera is not None:
            del self.m_camera
    
    @pyqtSlot()
    def sim_update_slot(self):
        """Update the simulation"""
        if self.m_sim is not None:
            self.m_sim.update()
    
    def initializeGL(self):
        """Initialize OpenGL settings"""
        self.load_texture(Constants.defaultImgPath, 0)
        if self.planet_night_texture_path:
            self.load_texture(self.planet_night_texture_path, 1)
        self.load_texture("src/assets/gold_texture.jpg", 2)
        self.load_texture("src/assets/solar_panel_2.jpg", 3)
        
        # Enable lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up light properties
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
        
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    
    def resizeGL(self, width, height):
        """
        Handle window resize events
        
        Args:
            width (int): New width
            height (int): New height
        """
        if height == 0:
            height = 1
            
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def load_texture(self, path, i):
        """
        Load a texture from file
        
        Args:
            path (str): Path to texture image
            i (int): Texture index
        """
        # Load image
        qim_temp_texture = QImage(path)
        if qim_temp_texture.isNull():
            print(f"Failed to load texture: {path}")
            return
            
        # Convert to RGBA format and flip vertically
        qim_texture = qim_temp_texture.convertToFormat(QImage.Format_RGBA8888)
        qim_texture = qim_texture.mirrored(False, True)  # Flip vertically
        
        # Generate texture
        self.texture[i] = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture[i])
        
        # Set texture data and parameters
        glTexImage2D(
            GL_TEXTURE_2D, 0, GL_RGBA, qim_texture.width(), qim_texture.height(),
            0, GL_RGBA, GL_UNSIGNED_BYTE, qim_texture.bits().asstring(qim_texture.byteCount())
        )
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    def draw_ellipse(self, orbit, scale, i, n):
        """
        Draw an orbital ellipse
        
        Args:
            orbit (Orbit): Orbit to draw
            scale (float): Scale factor
            i (int): Satellite index
            n (int): Total number of satellites
        """
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_LINE_LOOP)
        
        # Set color based on satellite index (creates different colors for each satellite)
        h = i * 360.0 / n
        s = 95
        l = 100
        
        # Create QColor from HSL values
        from PyQt5.QtGui import QColor
        c = QColor()
        c.setHsl(int(h), int(s), int(l))
        
        # Set the color for the orbit line
        glColor3d(c.red() / 255.0, c.green() / 255.0, c.blue() / 255.0)
        
        # Draw the elliptical orbit
        m = 0.0
        while m < Constants.twopi:
            pt = orbit.get_point_at(m)
            glVertex3d(pt.get_y() * scale, pt.get_z() * scale, pt.get_x() * scale)
            m += 0.1
            
        glEnd()
        glEnable(GL_TEXTURE_2D)
    
    def paintGL(self):
        """Render the OpenGL scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        if self.m_sim is not None:
            self.m_camera.look()
            
            # Position the sun (light source)
            sun_distance = 100.0  # Arbitrary distance for the sun
            sun_angle = 360.0 * (math.fmod(self.m_sim.t, self.m_sim.get_planet().get_day()) 
                               / self.m_sim.get_planet().get_day())
            sun_x = sun_distance * math.cos(math.radians(sun_angle))
            sun_y = sun_distance * math.sin(math.radians(sun_angle))
            glLightfv(GL_LIGHT0, GL_POSITION, (sun_x, sun_y, 0.0, 1.0))
            
            scale_factor = 25.0
            
            # Get maximum RA for window scaling
            ra_max = 0.0
            for i in range(self.m_sim.nsat()):
                ra = self.m_sim.sat(i).get_orbit().get_ra()
                if ra_max < ra:
                    ra_max = ra
                    
            # Calculate scale
            if ra_max == 0.0:
                ra_max = self.m_sim.get_planet().get_radius() * 3.0
            scale = float(scale_factor / ra_max)
            
            # Get planet apparent size
            r = self.m_sim.get_planet().get_radius() * scale
            
            # Load textures if they have changed
            if self.planet_texture_path != self.m_sim.get_planet().get_img_path():
                self.planet_texture_path = self.m_sim.get_planet().get_img_path()
                self.load_texture(self.planet_texture_path, 0)
            
            if self.planet_night_texture_path != self.m_sim.get_planet().get_night_img_path():
                self.planet_night_texture_path = self.m_sim.get_planet().get_night_img_path()
                if self.planet_night_texture_path:
                    self.load_texture(self.planet_night_texture_path, 1)
            
            # Draw axes
            glDisable(GL_TEXTURE_2D)
            glBegin(GL_LINES)
            
            # Inertial X (red)
            glColor3d(1.0, 0.0, 0.0)
            glVertex3d(0.0, 0.0, 0.0)
            glVertex3d(0.0, 0.0, 3.0 * r)
            
            # Inertial Y (green)
            glColor3d(0.0, 1.0, 0.0)
            glVertex3d(0.0, 0.0, 0.0)
            glVertex3d(3.0 * r, 0.0, 0.0)
            
            # Inertial Z (blue)
            glColor3d(0.0, 0.0, 1.0)
            glVertex3d(0.0, 0.0, 0.0)
            glVertex3d(0.0, 3.0 * r, 0.0)
            
            glEnd()
            glColor3d(1.0, 1.0, 1.0)
            glEnable(GL_TEXTURE_2D)
            
            # Draw planet
            glPushMatrix()
            params = gluNewQuadric()
            gluQuadricTexture(params, GL_TRUE)
            
            # Enable multi-texturing if night texture is available
            if self.planet_night_texture_path:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, self.texture[0])  # Day texture
                glActiveTexture(GL_TEXTURE1)
                glBindTexture(GL_TEXTURE_2D, self.texture[1])  # Night texture
                
                # Calculate day/night blend factor based on sun position
                blend_factor = (math.sin(math.radians(sun_angle)) + 1.0) / 2.0
                glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)
                glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_RGB, GL_INTERPOLATE)
                glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE0_RGB, GL_TEXTURE0)
                glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND0_RGB, GL_SRC_COLOR)
                glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE1_RGB, GL_TEXTURE1)
                glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND1_RGB, GL_SRC_COLOR)
                glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE2_RGB, GL_CONSTANT)
                glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND2_RGB, GL_SRC_COLOR)
                glTexEnvf(GL_TEXTURE_ENV, GL_COMBINE_ALPHA, GL_REPLACE)
                glTexEnvf(GL_TEXTURE_ENV, GL_SOURCE0_ALPHA, GL_TEXTURE0)
                glTexEnvf(GL_TEXTURE_ENV, GL_OPERAND0_ALPHA, GL_SRC_ALPHA)
                glTexEnvf(GL_TEXTURE_ENV, GL_CONSTANT, blend_factor)
            else:
                glBindTexture(GL_TEXTURE_2D, self.texture[0])
            
            # Rotate to set north pole on top
            glRotatef(-90.0, 1.0, 0.0, 0.0)
            
            # Rotate around Z axis based on time
            angle = 360.0 * (math.fmod(self.m_sim.t, self.m_sim.get_planet().get_day()) 
                             / self.m_sim.get_planet().get_day())
            glRotatef(angle, 0.0, 0.0, 1.0)
            
            # Draw the planet sphere
            gluSphere(params, r, 40, 40)
            gluDeleteQuadric(params)
            glPopMatrix()
            
            # Draw each satellite
            for i in range(self.m_sim.nsat()):
                sat = self.m_sim.sat(i)
                
                # Check if this satellite is highlighted
                is_highlighted = (sat == self.highlighted_sat)
                
                # Satellite size, scaled
                s = 300.0 * scale
                
                # Get position
                pos = sat.get_current_position()
                x = float(pos.get_x())
                y = float(pos.get_y())
                z = float(pos.get_z())
                
                # Scale position
                x *= scale
                y *= scale
                z *= scale
                
                # Draw orbit ellipse
                self.draw_ellipse(sat.get_orbit(), scale, i, self.m_sim.nsat())
                
                # Set color based on highlight status
                if is_highlighted:
                    glColor3d(1.0, 1.0, 0.0)  # Yellow highlight
                    # Draw highlight outline
                    glPushMatrix()
                    glTranslatef(y, z, x)
                    glScalef(1.2, 1.2, 1.2)  # Make highlight slightly larger
                    
                    # Draw wireframe box using GL_LINES
                    glDisable(GL_TEXTURE_2D)
                    glDisable(GL_LIGHTING)
                    glLineWidth(2.0)  # Make lines thicker
                    
                    glBegin(GL_LINES)
                    # Front face
                    glVertex3f(-s, -s, s)
                    glVertex3f(s, -s, s)
                    glVertex3f(s, -s, s)
                    glVertex3f(s, s, s)
                    glVertex3f(s, s, s)
                    glVertex3f(-s, s, s)
                    glVertex3f(-s, s, s)
                    glVertex3f(-s, -s, s)
                    
                    # Back face
                    glVertex3f(-s, -s, -s)
                    glVertex3f(s, -s, -s)
                    glVertex3f(s, -s, -s)
                    glVertex3f(s, s, -s)
                    glVertex3f(s, s, -s)
                    glVertex3f(-s, s, -s)
                    glVertex3f(-s, s, -s)
                    glVertex3f(-s, -s, -s)
                    
                    # Connecting lines
                    glVertex3f(-s, -s, s)
                    glVertex3f(-s, -s, -s)
                    glVertex3f(s, -s, s)
                    glVertex3f(s, -s, -s)
                    glVertex3f(s, s, s)
                    glVertex3f(s, s, -s)
                    glVertex3f(-s, s, s)
                    glVertex3f(-s, s, -s)
                    glEnd()
                    
                    glLineWidth(1.0)  # Reset line width
                    glEnable(GL_LIGHTING)
                    glEnable(GL_TEXTURE_2D)
                    glPopMatrix()
                
                glColor3d(1.0, 1.0, 1.0)  # Reset color
                
                # Translate to satellite position
                glTranslatef(y, z, x)
                
                # Draw inertial axes at satellite position
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_LINES)
                
                # Inertial X (red)
                glColor3d(1.0, 0.0, 0.0)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 0.0, 3.0 * s)
                
                # Inertial Y (green)
                glColor3d(0.0, 1.0, 0.0)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(3.0 * s, 0.0, 0.0)
                
                # Inertial Z (blue)
                glColor3d(0.0, 0.0, 1.0)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 3.0 * s, 0.0)
                
                glEnd()
                glColor3d(1.0, 1.0, 1.0)
                glEnable(GL_TEXTURE_2D)
                
                # Rotate according to satellite attitude
                angle1 = 180.0 / Constants.pi * self.m_sim.sat(i).get_ry()
                angle2 = 180.0 / Constants.pi * self.m_sim.sat(i).get_rz()
                angle3 = 180.0 / Constants.pi * self.m_sim.sat(i).get_rx()
                
                glRotatef(angle1, 1.0, 0.0, 0.0)
                glRotatef(angle2, 0.0, 1.0, 0.0)
                glRotatef(angle3, 0.0, 0.0, 1.0)
                
                # Draw satellite axes
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_LINES)
                
                # Satellite X (light red)
                glColor3d(1.0, 0.5, 0.5)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 0.0, 3.0 * s)
                
                # Satellite Y (light green)
                glColor3d(0.5, 1.0, 0.5)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(3.0 * s, 0.0, 0.0)
                
                # Satellite Z (light blue)
                glColor3d(0.5, 0.5, 1.0)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 3.0 * s, 0.0)
                
                glEnd()
                glColor3d(1.0, 1.0, 1.0)
                glEnable(GL_TEXTURE_2D)
                
                # Draw satellite body
                glBindTexture(GL_TEXTURE_2D, self.texture[2])
                glBegin(GL_QUADS)
                
                # Front face
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                glTexCoord2f(s, 0.0)
                glVertex3f(s, -1.0 * s, s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, s)
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, s)
                
                # Back face
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, s, -1.0 * s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                
                # Top face
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, s, s)
                glTexCoord2f(s, 0.0)
                glVertex3f(s, s, s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, -1.0 * s)
                
                # Bottom face
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, s)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                
                # Right face
                glTexCoord2f(s, 0.0)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, s, s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, s)
                
                # Left face
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, s, s)
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                
                glEnd()
                
                # Draw solar panels
                glBindTexture(GL_TEXTURE_2D, self.texture[3])
                
                # Left panel
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-5.0 * s, -0.8 * s, 0.0)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.2 * s, -0.8 * s, 0.0)
                glTexCoord2f(s, s)
                glVertex3f(-1.2 * s, 0.8 * s, 0.0)
                glTexCoord2f(0.0, s)
                glVertex3f(-5.0 * s, 0.8 * s, 0.0)
                glEnd()
                
                # Right panel
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(1.2 * s, -0.8 * s, 0.0)
                glTexCoord2f(s, 0.0)
                glVertex3f(5.0 * s, -0.8 * s, 0.0)
                glTexCoord2f(s, s)
                glVertex3f(5.0 * s, 0.8 * s, 0.0)
                glTexCoord2f(0.0, s)
                glVertex3f(1.2 * s, 0.8 * s, 0.0)
                glEnd()
                
                # Rotate back to draw next satellite
                glRotatef(-angle3, 0.0, 0.0, 1.0)
                glRotatef(-angle2, 0.0, 1.0, 0.0)
                glRotatef(-angle1, 1.0, 0.0, 0.0)
                
                # Translate back to draw next satellite
                glTranslatef(-y, -z, -x)
    
    def sim(self):
        """Get the simulation object"""
        return self.m_sim
    
    def timer(self):
        """Get the simulation timer"""
        return self.sim_Timer
    
    def keyPressEvent(self, event):
        """
        Handle key press events
        
        Args:
            event (QKeyEvent): Key event
        """
        if self.sim() is not None:
            if event.key() == Qt.Key_Space:
                self.sim().toggle_play()
            elif event.key() == Qt.Key_F:
                if self.sim().speed * 1.5 > self.sim().dt / Constants.minTimeStep:
                    self.sim().set_speed(1000 * self.sim().dt)
                    QMessageBox.warning(
                        self,
                        "Maximum speed reached",
                        "Warning: the simulation is running at its highest speed (1000 updates per second).<br>"
                        "To make it run faster, you may increase the time step (<i>Simulation>Configure...</i>)"
                    )
                else:
                    self.sim().set_speed(self.sim().speed * 1.5)
                self.sim_Timer.setInterval(int(1000 * self.sim().dt / self.sim().speed))
            elif event.key() == Qt.Key_S:
                if self.sim().speed / 1.5 < self.sim().dt / Constants.maxTimeStep:
                    self.sim().set_speed(self.sim().dt / Constants.maxTimeStep)
                    QMessageBox.warning(
                        self,
                        "Minimum speed reached",
                        "Warning: the simulation is running at its lowest speed (one update every 60 seconds..."
                        "do you want to fall asleep?).<br>To make it run even slower, you may decrease the "
                        "time step (<i>Simulation>Configure...</i>)"
                    )
                else:
                    self.sim().set_speed(self.sim().speed / 1.5)
                self.sim_Timer.setInterval(int(1000 * self.sim().dt / self.sim().speed))
            elif event.key() == Qt.Key_V:
                self.sim().toggle_verbose()
        
        # Pass event to the parent class
        super(SimulationDisplay, self).keyPressEvent(event)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events
        
        Args:
            event (QMouseEvent): The mouse event
        """
        if event.button() == Qt.RightButton:
            # Check if a satellite was clicked
            sat = self._get_satellite_at_position(event.pos())
            if sat is not None:
                # Toggle highlight if clicking the same satellite
                if self.highlighted_sat == sat:
                    self.highlighted_sat = None
                    self.m_selected_sat = None
                    self.satellite_selected.emit(None)
                else:
                    self.highlighted_sat = sat
                    self._show_satellite_info(sat)
                self.update()  # Force a redraw
                
        elif event.button() == Qt.LeftButton:
            # Start camera movement
            self.is_dragging = True
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            self.m_camera.on_mouse_press(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.m_camera.on_mouse_release(event)
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            self.m_camera.on_mouse_motion(event)
    
    def leaveEvent(self, event):
        """
        Handle mouse leave events
        
        Args:
            event (QEvent): Leave event
        """
        if self.is_dragging:
            self.is_dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))
    
    def wheelEvent(self, event):
        """
        Handle mouse wheel events
        
        Args:
            event (QWheelEvent): Wheel event
        """
        if self.sim() is not None:
            self.m_camera.on_wheel(event)
        
        # Pass event to the parent class
        super(SimulationDisplay, self).wheelEvent(event)
    
    def _get_satellite_at_position(self, pos):
        """
        Get the satellite at the given screen position
        
        Args:
            pos (QPoint): Screen position
            
        Returns:
            Satellite: The satellite at the position, or None if no satellite was found
        """
        if self.m_sim is None:
            return None
            
        # Get device pixel ratio to handle high DPI displays
        device_pixel_ratio = self.devicePixelRatio()
            
        # Convert screen coordinates to OpenGL coordinates
        mouse_x = pos.x() * device_pixel_ratio
        mouse_y = pos.y() * device_pixel_ratio  # Don't flip y coordinate - we'll compare in screen space
        
        # Get the current matrices
        viewport = glGetIntegerv(GL_VIEWPORT)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        
        # Save current matrix state
        glPushMatrix()
        
        # Reset and apply camera transformation (exactly as in paintGL)
        glLoadIdentity()
        self.m_camera.look()
        
        # Get the scale factor (exactly as in paintGL)
        scale_factor = 25.0
        ra_max = 0.0
        for i in range(self.m_sim.nsat()):
            ra = self.m_sim.sat(i).get_orbit().get_ra()
            if ra_max < ra:
                ra_max = ra
        if ra_max == 0.0:
            ra_max = self.m_sim.get_planet().get_radius() * 3.0
        scale = float(scale_factor / ra_max)
        
        # Check each satellite
        closest_sat = None
        min_distance = float('inf')
        
        for i in range(self.m_sim.nsat()):
            sat = self.m_sim.sat(i)
            pos = sat.get_current_position()
            
            # Get position and scale (exactly as in paintGL)
            x_pos = float(pos.get_x()) * scale
            y_pos = float(pos.get_y()) * scale
            z_pos = float(pos.get_z()) * scale
            
            # Project satellite position to screen coordinates
            # Note: We use (y, z, x) order to match the rendering in paintGL
            screen_pos = gluProject(y_pos, z_pos, x_pos, 
                                  glGetDoublev(GL_MODELVIEW_MATRIX),
                                  projection, viewport)
            
            if screen_pos:
                # Get screen coordinates (flip y to match mouse coordinates)
                screen_x = screen_pos[0]
                screen_y = viewport[3] - screen_pos[1]  # Flip y coordinate to match mouse coordinates
                
                # Calculate distance in screen space
                dx = screen_x - mouse_x
                dy = screen_y - mouse_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Print debug info
                print(f"Satellite {sat.get_name()}: screen pos ({screen_x/device_pixel_ratio:.1f}, {screen_y/device_pixel_ratio:.1f}), "
                      f"click pos ({mouse_x/device_pixel_ratio:.1f}, {mouse_y/device_pixel_ratio:.1f}), distance {distance/device_pixel_ratio:.1f}")
                
                # Use a reasonable threshold for picking (50 pixels * device_pixel_ratio)
                if distance < 50 * device_pixel_ratio:
                    if closest_sat is None or distance < min_distance:
                        closest_sat = sat
                        min_distance = distance
        
        # Restore matrix state
        glPopMatrix()
        
        # Print selection result
        if closest_sat:
            print(f"Selected satellite: {closest_sat.get_name()} at distance {min_distance/device_pixel_ratio:.1f} pixels")
        else:
            print(f"No satellite selected. Click position: ({mouse_x/device_pixel_ratio:.1f}, {mouse_y/device_pixel_ratio:.1f})")
        
        return closest_sat
    
    def _show_satellite_info(self, satellite):
        """
        Show satellite information in the side panel
        
        Args:
            satellite (Satellite): The satellite to show information for
        """
        self.m_selected_sat = satellite
        self.satellite_selected.emit(satellite)
    
    def _configure_satellite(self, satellite):
        """
        Open configuration window for the satellite
        
        Args:
            satellite (Satellite): The satellite to configure
        """
        if self.m_sim is not None:
            self.m_sim.set_play(False)
            sat_window = SatelliteWindow(False, satellite, self.m_sim.get_planet())
            sat_window.exec_()
    
    def _remove_satellite(self, satellite):
        """
        Remove the satellite from the simulation
        
        Args:
            satellite (Satellite): The satellite to remove
        """
        if self.m_sim is not None:
            # Ask for confirmation
            reply = QMessageBox.question(
                self,
                "Remove Satellite",
                f"Are you sure you want to remove satellite '{satellite.get_name()}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Find and remove the satellite
                for i in range(self.m_sim.nsat()):
                    if self.m_sim.sat(i) == satellite:
                        self.m_sim.remove_satellite(i)
                        break
                
                # Clear selection if this was the selected satellite
                if self.m_selected_sat == satellite:
                    self.m_selected_sat = None
                    self.satellite_selected.emit(None)
    
    def mouseDoubleClickEvent(self, event):
        pass