import pygame
import math
import time

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Ball in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Ball properties
ball_radius = 15
ball_pos = [WIDTH // 2, HEIGHT // 2]
ball_vel = [5, -5]
GRAVITY = 0.2
FRICTION = 0.99

# Hexagon properties
hex_radius = 200
hex_center = [WIDTH // 2, HEIGHT // 2]
hex_angle = 0
rotation_speed = 0.02  # radians per frame

def rotate_point(point, angle, center):
    """Rotate a point around a center by given angle in radians"""
    temp_x = point[0] - center[0]
    temp_y = point[1] - center[1]
    
    rotated_x = temp_x * math.cos(angle) - temp_y * math.sin(angle)
    rotated_y = temp_x * math.sin(angle) + temp_y * math.cos(angle)
    
    return [rotated_x + center[0], rotated_y + center[1]]

def get_hexagon_vertices(center, radius, angle):
    """Generate vertices of a rotating hexagon"""
    vertices = []
    for i in range(6):
        vertex_angle = angle + i * math.pi / 3
        x = center[0] + radius * math.cos(vertex_angle)
        y = center[1] + radius * math.sin(vertex_angle)  # Fixed: changed vertex_aspect_angle to vertex_angle
        vertices.append([x, y])
    return vertices

def line_intersection(p1, p2, p3, p4):
    """Find intersection point between two line segments if it exists"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:  # Lines are parallel
        return None
        
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    
    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return [x, y]
    return None

def reflect_velocity(pos, vel, wall_start, wall_end):
    """Calculate new velocity after bouncing off a wall"""
    # Wall vector
    wall_vec = [wall_end[0] - wall_start[0], wall_end[1] - wall_start[1]]
    wall_len = math.sqrt(wall_vec[0]**2 + wall_vec[1]**2)
    normal = [-wall_vec[1]/wall_len, wall_vec[0]/wall_len]
    
    # Dot product of velocity and normal
    dot = vel[0] * normal[0] + vel[1] * normal[1]
    
    # Reflect velocity
    new_vel = [vel[0] - 2 * dot * normal[0], vel[1] - 2 * dot * normal[1]]
    return new_vel

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Update ball physics
    ball_vel[1] += GRAVITY  # Apply gravity
    ball_vel[0] *= FRICTION  # Apply friction
    ball_vel[1] *= FRICTION
    
    # Calculate next position
    next_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]
    
    # Get current hexagon vertices
    vertices = get_hexagon_vertices(hex_center, hex_radius, hex_angle)
    
    # Check collision with each wall
    for i in range(6):
        wall_start = vertices[i]
        wall_end = vertices[(i + 1) % 6]
        
        intersection = line_intersection(
            ball_pos, next_pos,
            wall_start, wall_end
        )
        
        if intersection:
            # Move ball to intersection point
            ball_pos = intersection.copy()
            # Reflect velocity
            ball_vel = reflect_velocity(ball_pos, ball_vel, wall_start, wall_end)
            # Reduce velocity after bounce (energy loss)
            ball_vel[0] *= 0.8
            ball_vel[1] *= 0.8
            break
    else:
        # No collision, update position normally
        ball_pos = next_pos.copy()
    
    # Update hexagon rotation
    hex_angle += rotation_speed
    
    # Clear screen
    screen.fill(BLACK)
    
    # Draw hexagon
    pygame.draw.polygon(screen, WHITE, vertices, 2)
    
    # Draw ball
    pygame.draw.circle(screen, RED, [int(ball_pos[0]), int(ball_pos[1])], ball_radius)
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()