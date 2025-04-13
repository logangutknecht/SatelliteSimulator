from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QImage, QCursor
from PyQt5.QtCore import QTimer, Qt, pyqtSlot

from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtOpenGL import QGLWidget

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
        self.m_camera = None
        self.texture = [0, 0, 0, 0]  # Texture IDs (day, night, satellite, solar panel)
        self.sim_Timer = None
        
        if self.m_sim is not None:
            self.planet_texture_path = self.m_sim.get_planet().get_img_path()
            self.planet_night_texture_path = self.m_sim.get_planet().get_night_img_path()
            self.sim_Timer = QTimer(self)
            self.sim_Timer.timeout.connect(self.sim_update_slot)
            self.sim_Timer.start(int(1000 * self.m_sim.dt / self.m_sim.speed))
            
            self.m_camera = TrackBallCamera()
            self.setCursor(QCursor(Qt.OpenHandCursor))
    
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
            self.setCursor(QCursor(Qt.OpenHandCursor))
    
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
                # Satellite size, scaled
                s = 300.0 * scale
                
                # Get position
                pos = self.m_sim.sat(i).get_current_position()
                x = float(pos.get_x())
                y = float(pos.get_y())
                z = float(pos.get_z())
                
                # Scale position
                x *= scale
                y *= scale
                z *= scale
                
                # Draw orbit ellipse
                self.draw_ellipse(self.m_sim.sat(i).get_orbit(), scale, i, self.m_sim.nsat())
                glColor3d(1.0, 1.0, 1.0)
                
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
                # Apply rotations in order:
                # 1. ry around Y-axis to point X towards nadir
                # 2. rz around Z-axis to align with orbital plane
                # 3. rx around X-axis to align Y with velocity
                angle1 = 180.0 / Constants.pi * self.m_sim.sat(i).get_ry()  # Y rotation first
                angle2 = 180.0 / Constants.pi * self.m_sim.sat(i).get_rz()  # Z rotation second
                angle3 = 180.0 / Constants.pi * self.m_sim.sat(i).get_rx()  # X rotation last
                
                glRotatef(angle1, 0.0, 1.0, 0.0)  # Y rotation
                glRotatef(angle2, 0.0, 0.0, 1.0)  # Z rotation
                glRotatef(angle3, 1.0, 0.0, 0.0)  # X rotation
                
                # Draw satellite axes
                glDisable(GL_TEXTURE_2D)
                glBegin(GL_LINES)
                
                # Satellite X (light red) - nadir direction
                glColor3d(1.0, 0.5, 0.5)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(3.0 * s, 0.0, 0.0)
                
                # Satellite Y (light green) - velocity vector
                glColor3d(0.5, 1.0, 0.5)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 3.0 * s, 0.0)
                
                # Satellite Z (light blue) - completes right-handed system
                glColor3d(0.5, 0.5, 1.0)
                glVertex3d(0.0, 0.0, 0.0)
                glVertex3d(0.0, 0.0, 3.0 * s)
                
                glEnd()
                glColor3d(1.0, 1.0, 1.0)
                glEnable(GL_TEXTURE_2D)
                
                # Draw satellite body
                glBindTexture(GL_TEXTURE_2D, self.texture[2])
                glBegin(GL_QUADS)
                
                # Front face (X+, nadir direction)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, 0.0)
                glVertex3f(s, s, -1.0 * s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, -1.0 * s, s)
                
                # Back face (X-, anti-nadir)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                
                # Top face (Y+, velocity direction)
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, s, s)
                glTexCoord2f(s, 0.0)
                glVertex3f(s, s, s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, -1.0 * s)
                
                # Bottom face (Y-, anti-velocity)
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, s)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                
                # Right face (Z+)
                glTexCoord2f(s, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, s)
                glTexCoord2f(s, s)
                glVertex3f(-1.0 * s, s, s)
                glTexCoord2f(0.0, s)
                glVertex3f(s, s, s)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(s, -1.0 * s, s)
                
                # Left face (Z-)
                glTexCoord2f(0.0, 0.0)
                glVertex3f(-1.0 * s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, 0.0)
                glVertex3f(s, -1.0 * s, -1.0 * s)
                glTexCoord2f(s, s)
                glVertex3f(s, s, -1.0 * s)
                glTexCoord2f(0.0, s)
                glVertex3f(-1.0 * s, s, -1.0 * s)
                
                glEnd()
                
                # Draw solar panels
                glBindTexture(GL_TEXTURE_2D, self.texture[3])
                
                # Rotate solar panels to align with orbital plane
                glPushMatrix()
                # Rotate 90 degrees around Z-axis to align with orbital plane
                glRotatef(90.0, 0.0, 0.0, 1.0)
                
                # Left panel (Z-)
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
                
                # Right panel (Z+)
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
                
                glPopMatrix()  # Restore the previous transformation matrix
                
                # Rotate back to draw next satellite
                glRotatef(-angle3, 1.0, 0.0, 0.0)  # Undo X rotation
                glRotatef(-angle2, 0.0, 0.0, 1.0)  # Undo Z rotation
                glRotatef(-angle1, 0.0, 1.0, 0.0)  # Undo Y rotation
                
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
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move events
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if self.sim() is not None:
            self.m_camera.on_mouse_motion(event)
        
        # Pass event to the parent class
        super(SimulationDisplay, self).mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if self.sim() is not None:
            if event.button() == Qt.LeftButton:
                self.setCursor(QCursor(Qt.ClosedHandCursor))
                self.m_camera.on_mouse_press(event)
        
        # Pass event to the parent class
        super(SimulationDisplay, self).mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events
        
        Args:
            event (QMouseEvent): Mouse event
        """
        if self.sim() is not None:
            if event.button() == Qt.LeftButton:
                self.setCursor(QCursor(Qt.OpenHandCursor))
                self.m_camera.on_mouse_release(event)
        
        # Pass event to the parent class
        super(SimulationDisplay, self).mouseReleaseEvent(event)
    
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