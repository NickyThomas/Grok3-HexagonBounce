import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH = 900
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bouncing Balls in Spinning Hexagon")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BUTTON_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Ball properties
BALL_RADIUS = 15
GRAVITY = 0.2
FRICTION = 0.99
BALL_MASS = 1
DEFAULT_BOUNCE = 0.8  # Default bounce factor (energy retention)
bounce_factor = DEFAULT_BOUNCE  # Current bounce factor

# Hexagon properties
HEX_RADIUS = 200
hex_center = [WIDTH // 2 - 50, HEIGHT // 2]
hex_angle = 0
rotation_speed = 0.02

# Button properties
BUTTON_WIDTH = 100
BUTTON_HEIGHT = 40
ADD_BUTTON_POS = [WIDTH - 120, 50]
REMOVE_BUTTON_POS = [WIDTH - 120, 110]
BOUNCY_BUTTON_POS = [WIDTH - 120, 170]
RESTORE_BUTTON_POS = [WIDTH - 120, 230]

class Ball:
    def __init__(self):
        self.pos = [hex_center[0], hex_center[1]]
        self.vel = [random.uniform(-5, 5), random.uniform(-5, 5)]
        self.color = random.choice(BUTTON_COLORS)

def get_hexagon_vertices(center, radius, angle):
    """Generate vertices of a rotating hexagon"""
    vertices = []
    for i in range(6):
        vertex_angle = angle + i * math.pi / 3
        x = center[0] + radius * math.cos(vertex_angle)
        y = center[1] + radius * math.sin(vertex_angle)
        vertices.append([x, y])
    return vertices

def line_point_distance(line_start, line_end, point):
    """Calculate distance from point to line segment"""
    px = point[0] - line_start[0]
    py = point[1] - line_start[1]
    lx = line_end[0] - line_start[0]
    ly = line_end[1] - line_start[1]
    line_len_sq = lx*lx + ly*ly
    if line_len_sq == 0:
        return math.sqrt(px*px + py*py)
    t = max(0, min(1, (px*lx + py*ly) / line_len_sq))
    closest_x = line_start[0] + t * lx
    closest_y = line_start[1] + t * ly
    dx = point[0] - closest_x
    dy = point[1] - closest_y
    return math.sqrt(dx*dx + dy*dy)

def reflect_velocity(vel, wall_start, wall_end):
    """Calculate new velocity after bouncing off a wall"""
    wall_vec = [wall_end[0] - wall_start[0], wall_end[1] - wall_start[1]]
    wall_len = math.sqrt(wall_vec[0]**2 + wall_vec[1]**2)
    normal = [-wall_vec[1]/wall_len, wall_vec[0]/wall_len]
    dot = vel[0] * normal[0] + vel[1] * normal[1]
    return [vel[0] - 2 * dot * normal[0], vel[1] - 2 * dot * normal[1]]

def ball_collision(ball1, ball2):
    """Handle collision between two balls"""
    dx = ball2.pos[0] - ball1.pos[0]
    dy = ball2.pos[1] - ball1.pos[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < 2 * BALL_RADIUS and distance > 0:
        nx = dx / distance
        ny = dy / distance
        rvx = ball2.vel[0] - ball1.vel[0]
        rvy = ball2.vel[1] - ball1.vel[1]
        vel_along_normal = rvx * nx + rvy * ny
        
        if vel_along_normal > 0:
            return
        
        impulse = 2 * vel_along_normal / (BALL_MASS + BALL_MASS)
        ball1.vel[0] += impulse * BALL_MASS * nx
        ball1.vel[1] += impulse * BALL_MASS * ny
        ball2.vel[0] -= impulse * BALL_MASS * nx
        ball2.vel[1] -= impulse * BALL_MASS * ny
        
        overlap = 2 * BALL_RADIUS - distance
        ball1.pos[0] -= overlap * nx * 0.5
        ball1.pos[1] -= overlap * ny * 0.5
        ball2.pos[0] += overlap * nx * 0.5
        ball2.pos[1] += overlap * ny * 0.5

def draw_button(pos, text, active):
    """Draw a button and return its rect"""
    rect = pygame.Rect(pos[0], pos[1], BUTTON_WIDTH, BUTTON_HEIGHT)
    color = WHITE if active else GRAY
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return rect

# Initial ball
balls = [Ball()]

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if add_button_rect.collidepoint(mouse_pos):
                balls.append(Ball())
            elif remove_button_rect.collidepoint(mouse_pos) and len(balls) > 0:
                balls.pop()
            elif bouncy_button_rect.collidepoint(mouse_pos):
                bounce_factor = min(1.0, bounce_factor + 0.1)  # Increase bounciness, cap at 1.0
            elif restore_button_rect.collidepoint(mouse_pos):
                bounce_factor = DEFAULT_BOUNCE  # Restore default bounciness

    # Get current hexagon vertices
    vertices = get_hexagon_vertices(hex_center, HEX_RADIUS, hex_angle)

    # Update all balls
    for ball in balls:
        ball.vel[1] += GRAVITY
        ball.vel[0] *= FRICTION
        ball.vel[1] *= FRICTION
        
        next_pos = [ball.pos[0] + ball.vel[0], ball.pos[1] + ball.vel[1]]
        
        collision_detected = False
        for i in range(6):
            wall_start = vertices[i]
            wall_end = vertices[(i + 1) % 6]
            dist = line_point_distance(wall_start, wall_end, next_pos)
            
            if dist <= BALL_RADIUS:
                wall_vec = [wall_end[0] - wall_start[0], wall_end[1] - wall_start[1]]
                wall_len = math.sqrt(wall_vec[0]**2 + wall_vec[1]**2)
                normal = [-wall_vec[1]/wall_len, wall_vec[0]/wall_len]
                penetration = BALL_RADIUS - dist
                ball.pos[0] += normal[0] * penetration
                ball.pos[1] += normal[1] * penetration
                ball.vel = reflect_velocity(ball.vel, wall_start, wall_end)
                ball.vel[0] *= bounce_factor  # Use dynamic bounce factor
                ball.vel[1] *= bounce_factor
                collision_detected = True
                break
        
        if not collision_detected:
            ball.pos = next_pos.copy()

    # Check ball-to-ball collisions
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball_collision(balls[i], balls[j])

    # Update hexagon rotation
    hex_angle += rotation_speed

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.polygon(screen, WHITE, vertices, 2)
    
    for ball in balls:
        pygame.draw.circle(screen, ball.color, [int(ball.pos[0]), int(ball.pos[1])], BALL_RADIUS)

    # Draw buttons
    add_button_rect = draw_button(ADD_BUTTON_POS, "Add Ball", True)
    remove_button_rect = draw_button(REMOVE_BUTTON_POS, "Remove", len(balls) > 0)
    bouncy_button_rect = draw_button(BOUNCY_BUTTON_POS, "More Bouncy", bounce_factor < 1.0)
    restore_button_rect = draw_button(RESTORE_BUTTON_POS, "Restore", bounce_factor != DEFAULT_BOUNCE)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()