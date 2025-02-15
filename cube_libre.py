# "Cube Libre"
#
# This is a "cubistic" puzzle/adventure game, where you are a cube consisting of smaller cubes.
# The idea is that whenever you hit something, your main cube (that consists of smaller cubes) breaks a little.
# Another core concept is that you must navigate through a laser maze to a portal with your cube, and keep as many cubes of your main cube intact while at it.
# The idea is to finally transcend as a 1x1 single cube into the heavens and join the stars.
#
# By FlyingFathead (w/ a little help from imaginary digital friends) // Dec 2023 - Dec 2024
# https://github.com/FlyingFathead/pygame-opengl-polygon-demos

version_number = "0.12.61"

import os
import pygame

from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# import numpy as np # should you need numpy
import random

# Detect if running under Wayland
is_wayland = 'WAYLAND_DISPLAY' in os.environ

# Set environment variables based on the detected windowing system
if is_wayland:
    # Attempt to use native Wayland support if available
    print("[INFO] Detected Wayland. Attempting to use native Wayland support.")
    # Potentially set other SDL environment variables here if needed
else:
    # Default to X11
    print("[INFO] Using X11 as the windowing system.")

# Define the dimensions of the main cube
cube_size = 5  # Number of small cubes per side
cube_spacing = 1.0  # Increased spacing to avoid overlap
cube_break_velocity_factor = 0.3  # Adjust this to make cubes fly off faster or slower

# Calculate the step size for positioning small cubes
step = cube_spacing

# Movement speed
default_move_speed = 0.1
# Define Z-axis movement speed
z_default_move_speed = 0.1

# Initialize Pygame and create a window
pygame.init()
display = (800, 600)

# portal_position = (0.0, 0.0, 20.0)  # Position of the portal (x, y, z)
# portal_position = (18.0, 0.0, 18.0)
portal_position = (18.0, 0.0, -18.0)
portal_size = 5.0  # Width and height of the portal
portal_color = (0.0, 1.0, 1.0)  # Cyan color for glowing effect
portal_glow_steps = 10  # Number of overlapping quads for the glow effect
portal_glow_alpha = 0.3  # Initial alpha for the glow

# # Request an OpenGL 3.3 core profile context
# pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
# pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
# pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)

# Using numerical value for compatibility profile
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, 0x00002)

# Request OpenGL 3.3 compatibility profile
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_COMPATIBILITY)

# pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

try:
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
except pygame.error as e:
    print(f"Pygame failed to set display mode with OpenGL: {e}")
    pygame.quit()
    quit()

# Set the window title with version number
pygame.display.set_caption(f"Cube Libre (demo, v.{version_number})")

# Verify OpenGL version
version = glGetString(GL_VERSION)
if version:
    version_string = version.decode()
    print(f"OpenGL version: {version_string}")
    
    # Extract major and minor version numbers
    version_parts = version_string.split(' ')[0]
    major_minor = version_parts.split('.')[:2]
    
    try:
        major, minor = map(int, major_minor)
    except ValueError:
        print(f"Unexpected OpenGL version format: {version_string}")
        pygame.quit()
        quit()
    
    if major < 3:
        print("OpenGL version is below 3.0. VAOs and VBOs may not be supported.")
        pygame.quit()
        quit()
else:
    print("Failed to retrieve OpenGL version.")
    pygame.quit()
    quit()

# Enable depth testing
glEnable(GL_DEPTH_TEST)

# Set perspective and translate
try:
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -20.0)  # Move the view farther back
except OpenGL.error.GLError as e:
    print(f"OpenGL Error during gluPerspective or glTranslatef: {e}")
    pygame.quit()
    quit()

""" # Using numpy to define vertices
vertices = np.array([-0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5, -0.5,  0.5,
        0.5,  0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,
        0.5, -0.5, -0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5,  0.5, -0.5,
       -0.5,  0.5, -0.5, -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5,
       -0.5, -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5, -0.5,
        0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5,
        0.5,  0.5, -0.5,  0.5, -0.5, -0.5], dtype=np.float32) """

# Define the vertices for a cube
vertices = [
    # Front face
    -0.5, -0.5, 0.5,
    0.5, -0.5, 0.5,
    0.5, 0.5, 0.5,
    -0.5, 0.5, 0.5,

    # Back face
    0.5, -0.5, -0.5,
    -0.5, -0.5, -0.5,
    -0.5, 0.5, -0.5,
    0.5, 0.5, -0.5,

    # Top face
    -0.5, 0.5, 0.5,
    0.5, 0.5, 0.5,
    0.5, 0.5, -0.5,
    -0.5, 0.5, -0.5,

    # Bottom face
    -0.5, -0.5, 0.5,
    0.5, -0.5, 0.5,
    0.5, -0.5, -0.5,
    -0.5, -0.5, -0.5,

    # Left face
    -0.5, -0.5, 0.5,
    -0.5, 0.5, 0.5,
    -0.5, 0.5, -0.5,
    -0.5, -0.5, -0.5,

    # Right face
    0.5, -0.5, 0.5,
    0.5, 0.5, 0.5,
    0.5, 0.5, -0.5,
    0.5, -0.5, -0.5,
]

# Create a VBO to store the vertex data
try:
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 4, (GLfloat * len(vertices))(*vertices), GL_STATIC_DRAW)
except OpenGL.error.GLError as e:
    print(f"OpenGL Error during VBO setup: {e}")
    pygame.quit()
    quit()

# glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW) # if using numpy

# Create a VAO to store the vertex attribute configuration
try:
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # Specify vertex attribute pointers
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

    # Unbind the VAO and VBO
    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
except OpenGL.error.GLError as e:
    print(f"OpenGL Error during VAO/VBO setup: {e}")
    pygame.quit()
    quit()

# Initialize rotation angles
angle_x, angle_y, angle_z = 0.0, 0.0, 0.0
rotation_speed = 1.0  # Adjust rotation speed as needed

# Define a function to generate random RGB colors
def random_color():
    return [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)]

class Cube:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.color = self.random_color()  # Assign a random color at creation
        self.is_destroyed = False
        self.flash_duration = 0.2  # Duration of flash effect in seconds
        self.time_since_destroyed = 0  # Time since the cube was destroyed
        self.rotation = 0.0  # Initialize rotation angle

    @staticmethod
    def random_color():
        return [random.uniform(0, 1) for _ in range(3)]

    # Add other necessary methods and attributes

    # upon destruction
    def destroy(self):
        print("Destroying cube")  # Debugging statement        
        # Change color to white/grey for the flash effect
        self.color = [0.8, 0.8, 0.8]
        # Set velocity for flying off
        # self.velocity = [random.uniform(-1, 1), random.uniform(1, 2), random.uniform(-1, 1)]        
        # Set lower velocity for flying off
        
        # old method
        # self.velocity = [random.uniform(-0.5, 0.5), random.uniform(0.5, 1), random.uniform(-0.5, 0.5)]

        # Use the velocity factor here
        self.velocity = [
            random.uniform(-0.5, 0.5) * cube_break_velocity_factor,
            random.uniform(0.5, 1) * cube_break_velocity_factor,
            random.uniform(-0.5, 0.5) * cube_break_velocity_factor
        ]

        # Add angular velocity for swirling effect
        self.angular_velocity = random.uniform(-3, 3) # Degrees per second
        self.is_destroyed = True
        self.time_since_destroyed = 0  # Reset timer on destruction        

    # Reset the cube's animation state
    def reset_animation_state(self):
        self.color = self.random_color()
        self.is_destroyed = False
        self.velocity = [0.0, 0.0, 0.0]
        self.angular_velocity = 0.0

# start position variable
start_position = (-18.0, 0.0, -18.0)  # For example, near the edge of the horizon grid

# When initializing cubes, incorporate the start_position offset:
cubes = [[[Cube(x + start_position[0], 
                 y + start_position[1], 
                 z + start_position[2]) 
           for z in range(-cube_size // 2, cube_size // 2)]
          for y in range(-cube_size // 2, cube_size // 2)]
         for x in range(-cube_size // 2, cube_size // 2)]

# # Initialize cubes (no variables)
# cubes = [[[Cube(x, y, z) for z in range(-cube_size // 2, cube_size // 2)] 
#           for y in range(-cube_size // 2, cube_size // 2)] 
#          for x in range(-cube_size // 2, cube_size // 2)]

# Movement speed
default_move_speed = 0.1

# Assuming the horizon is at a fixed Y-coordinate
horizon_y = -5

# Initialize a destruction timer
destruction_cooldown = 0.0
max_destruction_rate = 0.5  # 1.0 = One cube per second

# Define the number of stars
num_stars = 1000

# Generate random positions for stars
stars = [(random.uniform(-50, 50), random.uniform(-50, 50), random.uniform(-50, 50)) for _ in range(num_stars)]

def draw_stars():
    glPointSize(2)  # Adjust point size for visibility
    glBegin(GL_POINTS)
    for star in stars:
        glVertex3fv(star)
    glEnd()

# draw the portal
def draw_portal():
    glPushMatrix()
    # No glTranslatef here!    
    # glTranslatef(*portal_position)
    
    # Enable blending for the glowing effect
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Draw the main portal quad
    glColor4f(*portal_color, 1.0)  # Full opacity for the main portal
    glBegin(GL_QUADS)
    half_size = portal_size / 2
    glVertex3f(-half_size, -half_size, 0.0)
    glVertex3f(half_size, -half_size, 0.0)
    glVertex3f(half_size, half_size, 0.0)
    glVertex3f(-half_size, half_size, 0.0)
    glEnd()
    
    # Create a glowing effect by drawing larger, semi-transparent quads
    for i in range(1, portal_glow_steps + 1):
        scale = 1.0 + (i * 0.2)  # Increase size for each glow layer
        alpha = portal_glow_alpha / i  # Decrease alpha for each layer
        glColor4f(*portal_color, alpha)
        glPushMatrix()
        glScalef(scale, scale, scale)
        glBegin(GL_QUADS)
        glVertex3f(-half_size, -half_size, 0.0)
        glVertex3f(half_size, -half_size, 0.0)
        glVertex3f(half_size, half_size, 0.0)
        glVertex3f(-half_size, half_size, 0.0)
        glEnd()
        glPopMatrix()
    
    glDisable(GL_BLEND)
    glPopMatrix()

# Movement function updated for x and y directions
def move_cubes(delta_x, delta_y):
    for row in cubes:
        for layer in row:
            for cube in layer:
                cube.x += delta_x
                cube.y += delta_y

# horizon collision detection
def check_collision_with_horizon(cube):
    if cube.y <= horizon_y:
        print(f"Collision detected for cube at ({cube.x}, {cube.y}, {cube.z})")
        return True
    return False

# Update cube positions based on velocity
def update_cubes(delta_time):
    global screen_shake_timer, flash_timer
    # Reduce timers based on the time passed since the last frame
    #if screen_shake_timer > 0:
    #    screen_shake_timer -= delta_time
    if flash_timer > 0:
        flash_timer -= delta_time    
    for x in range(-cube_size // 2, cube_size // 2):
        for y in range(-cube_size // 2, cube_size // 2):
            for z in range(-cube_size // 2, cube_size // 2):
                cube = cubes[x][y][z]
                if cube.is_destroyed:
                    cube.time_since_destroyed += delta_time
                    if cube.time_since_destroyed > cube.flash_duration:
                        # Only move cubes after the flash duration
                        cube.x += cube.velocity[0] * delta_time
                        cube.y += cube.velocity[1] * delta_time
                        cube.z += cube.velocity[2] * delta_time
                        cube.rotation += cube.angular_velocity * delta_time  # This line should now work

    """ # Render the scene multiple times with decreasing opacity to simulate motion blur
    for i in range(3):
        glPushMatrix()
        # Apply transformation for motion blur effect
        glTranslatef(i * blur_factor, i * blur_factor, 0)  # Adjust blur_factor as needed
        glColor4f(1, 1, 1, 0.5 / (i + 1))  # Decrease alpha to make it more transparent
        # Draw the scene again (you need to adjust this to match your drawing code)
        draw_scene()
        glPopMatrix() """

# draw the wireframe horizon
def draw_wireframe_horizon():
    glColor3f(1.0, 1.0, 1.0)  # White color
    glLineWidth(1)  # Set line width
    glBegin(GL_LINES)

    # Horizontal lines
    for z in range(-20, 21, 2):  # Adjust range and step for density
        glVertex3f(-20, -5, z)  # Adjust Y-coordinate for vertical position
        glVertex3f(20, -5, z)

    # Vertical lines
    for x in range(-20, 21, 2):  # Adjust range and step for density
        glVertex3f(x, -5, -20)  # Starting from far distance
        glVertex3f(x, -5, 20)   # Up to close distance

    glEnd()

def destroy_one_cube_per_layer():
    global screen_shake_timer, flash_timer  # Ensure these globals are declared if needed
    # Iterate through each layer
    for y in range(-cube_size // 2, cube_size // 2):
        layer_affected = False
        for x in range(-cube_size // 2, cube_size // 2):
            for z in range(-cube_size // 2, cube_size // 2):
                cube = cubes[x][y][z]
                if cube and not cube.is_destroyed and check_collision_with_horizon(cube):
                    if not layer_affected:
                        # Choose a random cube to destroy
                        random_x = random.randint(-cube_size // 2, cube_size // 2 - 1)
                        random_z = random.randint(-cube_size // 2, cube_size // 2 - 1)
                        cubes[random_x][y][random_z].destroy()  # Call destroy method
                        layer_affected = True
                    break
        if layer_affected:
            trigger_hit_effects()  # Trigger effects when a cube is destroyed

def gradient_color(y):
    # Assuming the vertical range is from -cube_size/2 to cube_size/2
    gradient_start = [1, 0, 0] # Red at the top
    gradient_end = [0, 0, 1] # Blue at the bottom
    factor = (y + cube_size/2) / cube_size # Normalize y to range [0, 1]
    color = [
        gradient_start[0] * (1 - factor) + gradient_end[0] * factor,
        gradient_start[1] * (1 - factor) + gradient_end[1] * factor,
        gradient_start[2] * (1 - factor) + gradient_end[2] * factor
    ]
    return color

def update_star_positions(offset_x, offset_y, offset_z):
    global stars
    stars = [(x + offset_x, y + offset_y, z + offset_z) for (x, y, z) in stars]

def draw_scene():
    # Rendering
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glPushMatrix()

    # # Portal drawing, isolated:
    # glPushMatrix()  # Portal push #B
    # glTranslatef(*portal_position)
    # draw_portal()
    # glPopMatrix()   # Pop #B (portal done)    

    # Rotate the entire scene
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    glRotatef(angle_z, 0, 0, 1)

    # Draw the portal now
    glPushMatrix()
    glTranslatef(*portal_position)
    draw_portal()
    glPopMatrix()

    # Draw wireframe horizon
    draw_wireframe_horizon()

    # Draw stars
    glColor3f(1, 1, 1)  # White stars
    draw_stars()

    # Apply gradient in the cube rendering loop
    for x in range(-cube_size // 2, cube_size // 2):
        for y in range(-cube_size // 2, cube_size // 2):
            for z in range(-cube_size // 2, cube_size // 2):
                cube = cubes[x][y][z]
                glPushMatrix()
                glTranslatef(cube.x * step, cube.y * step, cube.z * step)
                if cube.is_destroyed:
                    # Render the cube with a different style if it's destroyed
                    glColor4f(1.0, 1.0, 1.0, 0.5)  # Example: white and semi-transparent
                else:
                    gradient_color_value = gradient_color(cube.y)
                    glColor3fv(gradient_color_value)
                glBindVertexArray(vao)
                glDrawArrays(GL_QUADS, 0, 24)
                glBindVertexArray(0)
                glPopMatrix()

    # # Draw cubes with rotation around their own center
    # for x in range(-cube_size // 2, cube_size // 2):
    #     for y in range(-cube_size // 2, cube_size // 2):
    #         for z in range(-cube_size // 2, cube_size // 2):
    #             cube = cubes[x][y][z]
    #             glPushMatrix()
    #             # Translate to cube position
    #             glTranslatef(cube.x * step, cube.y * step, cube.z * step)
                
    #             # Apply individual cube rotation
    #             # Comment out or remove the lines below to stop individual cube rotation
    #             # glRotatef(angle_x, 1, 0, 0)
    #             # glRotatef(angle_y, 0, 1, 0)
    #             # glRotatef(angle_z, 0, 0, 1)

    #             # Set cube color and draw
    #             glColor3fv(cube.color)
    #             glBindVertexArray(vao)
    #             glDrawArrays(GL_QUADS, 0, 24)
    #             glBindVertexArray(0)
    #             glPopMatrix()

    glPopMatrix()    

def move_cubes(direction, default_move_speed):
    # Choose a single cube to move based on direction
    # For simplicity, let's always move the cube at the center
    center_index = cube_size // 2
    cube_to_move = cubes[center_index][center_index][center_index]

    if direction == "LEFT":
        cube_to_move.x -= default_move_speed
    elif direction == "RIGHT":
        cube_to_move.x += default_move_speed
    elif direction == "UP":
        cube_to_move.y += default_move_speed
    elif direction == "DOWN":
        cube_to_move.y -= default_move_speed

# check if all cubes are destroyed
def all_cubes_destroyed(cubes):
    return all(cube.is_destroyed for row in cubes for layer in row for cube in layer)

# # reset all cubes
def reset_cubes(cubes):
    for x_idx in range(-cube_size // 2, cube_size // 2):
        for y_idx in range(-cube_size // 2, cube_size // 2):
            for z_idx in range(-cube_size // 2, cube_size // 2):
                cubes[x_idx][y_idx][z_idx] = Cube(x_idx + start_position[0],
                                                  y_idx + start_position[1],
                                                  z_idx + start_position[2])
                cube = cubes[x_idx][y_idx][z_idx]
                cube.reset_animation_state()

# def reset_cubes(cubes):
#     # Logic to reset the cubes to their initial state
#     for x in range(-cube_size // 2, cube_size // 2):
#         for y in range(-cube_size // 2, cube_size // 2):
#             for z in range(-cube_size // 2, cube_size // 2):
#                 cubes[x][y][z] = Cube(x, y, z)  # Recreate the cube
#                 cube.reset_animation_state()  # Reset animation state

# flash the screen
def flash_screen(duration=1000, steps=255):
    # Duration of the flash in milliseconds
    # Steps are how many levels of fading we have

    # Fade to white
    for i in range(steps):
        alpha = i / steps
        glClearColor(alpha, alpha, alpha, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        pygame.display.flip()
        pygame.time.wait(duration // (steps * 2))  # Wait proportionally to fade duration

    # Hold the white screen
    pygame.time.wait(duration // steps)  # Hold the white screen for a moment

    # Fade back into the game
    for i in range(steps, -1, -1):
        alpha = i / steps
        glClearColor(alpha, alpha, alpha, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        draw_scene()  # Draw the game scene with the faded alpha overlay
        pygame.display.flip()
        pygame.time.wait(duration // (steps * 2))  # Wait proportionally to fade duration

    # Reset clear color to game's background color
    glClearColor(0, 0, 0, 1)  # Assuming black is the game's background color

# Additional global variables for effects
screen_shake_duration = 0.5  # Duration of the shake in seconds
screen_shake_timer = 0  # Current shake timer
flash_duration = 0.3  # Duration of the flash in seconds
flash_timer = 0  # Current flash timer

def trigger_hit_effects():
    global screen_shake_timer, flash_timer
    screen_shake_timer = screen_shake_duration
    flash_timer = flash_duration

def update_effects(delta_time):
    global screen_shake_timer, flash_timer
    if screen_shake_timer > 0:
        screen_shake_timer -= delta_time
    if flash_timer > 0:
        flash_timer -= delta_time

def apply_screen_shake():
    if screen_shake_timer > 0:
        shake_intensity = 0.5  # Adjust as needed
        random_offset_x = random.uniform(-shake_intensity, shake_intensity)
        random_offset_y = random.uniform(-shake_intensity, shake_intensity)
        glTranslatef(random_offset_x, random_offset_y, 0)

def render_flash_effect():
    if flash_timer > 0:
        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Set orthographic projection to cover the whole screen
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(-1, 1, -1, 1)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Set the color to red with the alpha based on flash_timer
        glColor4f(1.0, 0.0, 0.0, min(flash_timer / flash_duration, 1.0))

        # Draw a full-screen quad for the red flash effect
        glBegin(GL_QUADS)
        glVertex2f(-1, -1)
        glVertex2f(1, -1)
        glVertex2f(1, 1)
        glVertex2f(-1, 1)
        glEnd()

        # Restore matrices and disable blending
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glDisable(GL_BLEND)

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Get the state of all keyboard keys
    keys = pygame.key.get_pressed()

    # shift multiplier for movement speed
    shift_multiplier = 3.0 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 1.0

    # Check if CTRL is pressed
    ctrl_pressed = (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL])

    # Now handle movements
    # Vertical movement (Y-axis)
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        for row in cubes:
            for layer in row:
                for cube in layer:
                    cube.y += default_move_speed * shift_multiplier
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        for row in cubes:
            for layer in row:
                for cube in layer:
                    cube.y -= default_move_speed * shift_multiplier

    # Z-axis movement keys (Q/E) always move along Z-axis
    if keys[pygame.K_q]:
        for row in cubes:
            for layer in row:
                for cube in layer:
                    cube.z += z_default_move_speed * shift_multiplier
    if keys[pygame.K_e]:
        for row in cubes:
            for layer in row:
                for cube in layer:
                    cube.z -= z_default_move_speed * shift_multiplier

    # If CTRL is pressed, A/D or LEFT/RIGHT move along Z-axis instead of X-axis
    if ctrl_pressed:
        # A/LEFT increase Z
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            for row in cubes:
                for layer in row:
                    for cube in layer:
                        cube.z += z_default_move_speed * shift_multiplier
        # D/RIGHT decrease Z
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            for row in cubes:
                for layer in row:
                    for cube in layer:
                        cube.z -= z_default_move_speed * shift_multiplier
    else:
        # Normal behavior (no CTRL): A/LEFT and D/RIGHT move along X-axis
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            for row in cubes:
                for layer in row:
                    for cube in layer:
                        cube.x -= default_move_speed * shift_multiplier
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            for row in cubes:
                for layer in row:
                    for cube in layer:
                        cube.x += default_move_speed * shift_multiplier

    # Calculate delta time
    delta_time = pygame.time.get_ticks() / 1000.0

    # Update effects
    update_effects(delta_time)

    # Check for collisions and destroy one cube per layer
    destruction_cooldown -= delta_time
    if destruction_cooldown <= 0:
        destroy_one_cube_per_layer()
        destruction_cooldown = 1.0 / max_destruction_rate

    # Update cube positions and flash status
    update_cubes(delta_time)

    # Check if all cubes are destroyed
    if all_cubes_destroyed(cubes):
        flash_screen()  # Flash the screen
        reset_cubes(cubes)  # Reset the cubes to start over
        continue  # Skip the rest of the loop to start with a fresh screen

    # Clear the screen
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Apply screen shake
    glPushMatrix()  # Save the current state of transformations
    if screen_shake_timer > 0:
        apply_screen_shake()

    draw_scene()

    glPushMatrix()        # Save the current transformation state
    glLoadIdentity()      # Reset transformations
    glTranslatef(*portal_position)
    # draw_portal()
    glPopMatrix()         # Restore the original transformation state

    # Restore the original state after shake
    glPopMatrix()

    # Render the flash effect over the scene if needed
    if flash_timer > 0:
        render_flash_effect()

    # Update sway angles
    angle_x += rotation_speed
    angle_y += rotation_speed
    angle_z += rotation_speed

    pygame.display.flip()
    pygame.time.wait(10)
