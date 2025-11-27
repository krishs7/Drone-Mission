import pygame
from pygame.joystick import Joystick
import math
import Consts
import ControllerUtils
import Drone
import NetworkUtils

# Initialize Pygame
pygame.init()

drone = Drone.Drone()
pressedPower: bool = False

controllerUtils = ControllerUtils.ControllerUtils()
networkUtils = NetworkUtils.NetworkUtils()

# Controller Type
isKeyboard: bool = True

consts = Consts.Consts()

# Set up display
width, height = 800, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption('3D Drone Simulation')

grey = (150, 150, 150)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
droneColor = red

# Load your ground image
ground_sky_image_original = pygame.image.load("DroneMission-main\\Simulation\\ground.png")
ground_sky_image = pygame.transform.scale(ground_sky_image_original, (800, 120))


# Load your sky image
sky = pygame.image.load("DroneMission-main\\Simulation\\sky.png")
sky = pygame.transform.scale(sky, (800, 480))

# Define drone as a cube
drone_vertices = [
    [1.2, 0.4, 1.2],
    [1.2, 0.4, -1.2],
    [1.2, -0.2, 1.2],
    [1.2, -0.2, -1.2],
    [-1.2, 0.4, 1.2],
    [-1.2, 0.4, -1.2],
    [-1.2, -0.2, 1.2],
    [-1.2, -0.2, -1.2]
]

# Define the faces of the drone
drone_faces = [
    [0, 1, 5, 4],
    [2, 3, 7, 6],
    [0, 1, 3, 2],
    [1, 5, 7, 3],
    [5, 4, 6, 7],
    [4, 0, 2, 6]
]

# Define propellers at the four corners of the top face of the drone
propeller_vertices = [
    [1.4, -0.2, 1.4],
    [1.4, -0.2, -1.4],
    [-1.4, -0.2, 1.4],
    [-1.4, -0.2, -1.4]
]

# Camera properties
fov = 256
camera_z = 5

# Movement speed
speed = 0.1

# Initial angle for propeller rotation
propeller_rotation_angle = 0

# Length of the propeller blades
propeller_length = 10

# Main loop
running = True

controller: Joystick = None

forward_speed = 0.0
lateral_speed = 0.0

# Maximum speed limit
max_speed = 0.5

# left and right wall
xWall = 4.6

# Speed increase/decrease rate (adjust these for slower speed changes)
acceleration_rate = 0.001  
deceleration_rate = 0.001  

# Crash state and speed where the drone will count as crashed
has_crashed = False

# Initialize wind properties
wind_direction = 0  # Angle in radians
wind_strength = 0.01  # Speed at which wind affects the drone

if not isKeyboard:
    controller = controllerUtils.getController()
    controllerCount = controllerUtils.CONTROLLER_COUNT

def calculate_ground_position():
    ground_y = 0.657*drone.position[2]+2.7
    return ground_y

def draw_wind_direction(screen, wind_direction, wind_strength, color):
    start_x, start_y = 50, height - 50  # Position of the arrow's base (bottom-left corner)
    line_length = 50 + wind_strength * 200  # Adjust this factor for visibility
    end_x = start_x + line_length * math.cos(wind_direction)
    end_y = start_y - line_length * math.sin(wind_direction)

    # Draw the main line of the arrow
    pygame.draw.line(screen, color, (start_x, start_y), (end_x, end_y), 3)

    # Draw the arrowhead
    arrow_size = 10  # Size of the arrowhead
    left_arrow = (end_x + arrow_size * math.sin(wind_direction),
                  end_y + arrow_size * math.cos(wind_direction))
    right_arrow = (end_x - arrow_size * math.sin(wind_direction),
                   end_y - arrow_size * math.cos(wind_direction))
    pygame.draw.line(screen, color, (end_x, end_y), left_arrow, 3)
    pygame.draw.line(screen, color, (end_x, end_y), right_arrow, 3)

def hitRightWall():
    drone.position[0] = -4.5

def hitLeftWall():
    drone.position[0] = 4.5

while running:
    
    if drone.position[0] > xWall:
        hitRightWall()
    elif abs(drone.position[0]) > abs(xWall):
        hitLeftWall()
    #invisible wall infront the camera
    if drone.position[2] <-3:
        drone.position[2] = -2.9
        forward_speed = 0
    prev_drone_position = list(drone.position)
    
    if drone.position[1] >= calculate_ground_position():
        drone.position[1] = calculate_ground_position()
        has_crashed = True
    else:
        has_crashed= False

    # Handle crash
    if has_crashed and (forward_speed > 0.06 or lateral_speed > 0.06 or forward_speed < -0.06 or lateral_speed < -0.06):
        # Stop all movement
        forward_speed = 0
        lateral_speed = 0
        drone.power = False
        drone.position = [0,0,0]
        has_crashed=False

    if isKeyboard:
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if keys[pygame.K_SPACE] and not pressedPower:
                pressedPower = True
                drone.TogglePower()
            if not keys[pygame.K_SPACE] and pressedPower:
                pressedPower = False

        if drone.power:
            # Forward/Backward Movement
            if keys[pygame.K_s]:
                if forward_speed >= 0:  # Moving forward or stationary
                    forward_speed = min(forward_speed + acceleration_rate, max_speed)
                    drone.orientation[0] = math.radians(10)  # Pitch adjustment
                else:  # Moving backward, so decelerate first
                    forward_speed = min(forward_speed + deceleration_rate, 0)
                    drone.orientation[0] = 0  # Resetting pitch
            elif keys[pygame.K_w]:
                if forward_speed <= 0:  # Moving backward or stationary
                    forward_speed = max(forward_speed - acceleration_rate, -max_speed)
                    drone.orientation[0] = math.radians(-10)  # Pitch adjustment
                else:  # Moving forward, so decelerate first
                    forward_speed = max(forward_speed - deceleration_rate, 0)
                    drone.orientation[0] = 0  # Resetting pitch
            else:
                # Slow down if no forward/backward keys are pressed
                if forward_speed > 0:
                    forward_speed = max(forward_speed - deceleration_rate, 0)
                elif forward_speed < 0:
                    forward_speed = min(forward_speed + deceleration_rate, 0)
                drone.orientation[0] = 0  # Resetting pitch when not moving

            if keys[pygame.K_r]:
                wind_direction += math.radians(1.9)  # Rotate wind direction
            if keys[pygame.K_t]:
                wind_strength = max(wind_strength, wind_strength + 0.0005)   # Increase wind strength
            if keys[pygame.K_y]:
                wind_strength = max(0, wind_strength - 0.0005)  # Decrease wind strength

            drone.position[0] += wind_strength * math.cos(wind_direction)
            drone.position[2] += wind_strength * math.sin(wind_direction)


            # Lateral Movement (Left/Right)
            if keys[pygame.K_d]:
                lateral_speed = min(lateral_speed + acceleration_rate, max_speed)
                drone.orientation[2] = math.radians(10)
            elif keys[pygame.K_a]:
                lateral_speed = max(lateral_speed - acceleration_rate, -max_speed)
                drone.orientation[2] = math.radians(-10)
            else:
                # Slow down if no lateral keys are pressed
                if lateral_speed > 0:
                    lateral_speed = max(lateral_speed - deceleration_rate, 0)
                elif lateral_speed < 0:
                    lateral_speed = min(lateral_speed + deceleration_rate, 0)
                drone.orientation[2] = 0

            # Apply movement
            dx = -math.sin(drone.orientation[1]) * forward_speed
            dz = -math.cos(drone.orientation[1]) * forward_speed
            drone.position[0] += lateral_speed  # Lateral movement
            drone.position[0] += dx  # Forward/Backward movement
            drone.position[2] += dz

            if keys[pygame.K_q]:
                drone.position[1] += speed
            elif keys[pygame.K_e]:
                drone.position[1] -= speed
    else:
        if pygame.joystick.get_count() < controllerCount:
            print("Disconnection detected")
            # TODO - fix this bug of reconnection ctr att error
            # controller = controllerUtils.getController()
            running = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.JOYBUTTONDOWN:
                btn = event.__getattribute__('button')
                if btn == controllerUtils.MAP.btnMapping["BTN1"] and not pressedPower:
                    pressedPower = True
                    drone.TogglePower()
            if event.type == pygame.JOYBUTTONUP:
                btn = event.__getattribute__('button')
                if btn == controllerUtils.MAP.btnMapping["BTN1"] and pressedPower:
                    pressedPower = False

        # Check if drone power is on
        if drone.power:
            x = controller.get_axis(0)
            y = controller.get_axis(1)
            z = controller.get_axis(3)

            # Adjust the speed based on joystick input
            if abs(x) > consts.DRIFT_VAL or abs(y) > consts.DRIFT_VAL:
                # Increase speed if joystick is moved
                speed = min(speed + acceleration_rate, max_speed)
            else:
                # Decrease speed if joystick is in neutral position
                speed = max(speed - acceleration_rate, 0)

            # Calculate movement direction based on drone orientation
            dx = -math.sin(drone.orientation[1]) * speed
            dz = -math.cos(drone.orientation[1]) * speed

            # Move the drone based on joystick input
            if abs(x) > consts.DRIFT_VAL:
                if x < 0:
                    drone.position[0] += dz
                    drone.position[2] += dx
                    drone.orientation[2] = math.radians(-10)
                else:
                    drone.position[0] -= dz
                    drone.position[2] -= dx
                    drone.orientation[2] = math.radians(10)
            else:
                drone.orientation[2] = 0

            if abs(y) > consts.DRIFT_VAL:
                if y > 0:
                    drone.position[0] += dx
                    drone.position[2] += dz
                    drone.orientation[0] = math.radians(10)
                else:
                    drone.position[0] -= dx
                    drone.position[2] -= dz
                    drone.orientation[0] = math.radians(-10)
            else:
                drone.orientation[0] = 0

            if abs(z) > consts.DRIFT_VAL:
                if z > 0:
                    drone.position[1] += speed
                else:
                    drone.position[1] -= speed


# ----------------------------------------------------------------------------------------------

    # Update propeller rotation angle for the animation
    if drone.power:
        drone.LED = green
        propeller_rotation_angle += math.radians(10)
        if propeller_rotation_angle > 2 * math.pi:
            propeller_rotation_angle -= 2 * math.pi
    else:
        drone.LED = red

    # Blit the combined ground and sky image onto the screen
    win.blit(ground_sky_image, (0, 480))
    win.blit(sky, (0,0))

    # Translations, rotations, and projections of drone vertices and propellers to 2D space
    projected_points = []
    for vertex in drone_vertices + propeller_vertices:
        # Apply pitch rotation
        rotated_x = vertex[0]
        rotated_y = vertex[1] * math.cos(drone.orientation[0]) - \
            vertex[2] * math.sin(drone.orientation[0])
        rotated_z = vertex[1] * math.sin(drone.orientation[0]) + \
            vertex[2] * math.cos(drone.orientation[0])

        # Apply yaw rotation
        final_x = rotated_x * \
            math.cos(drone.orientation[1]) - \
            rotated_z * math.sin(drone.orientation[1])
        final_z = rotated_x * \
            math.sin(drone.orientation[1]) + \
            rotated_z * math.cos(drone.orientation[1])
        final_y = rotated_y

        # Apply roll rotation
        final_y = rotated_y * \
            math.cos(drone.orientation[2]) + \
            final_x * math.sin(drone.orientation[2])
        final_x = rotated_y * - \
            math.sin(drone.orientation[2]) + \
            final_x * math.cos(drone.orientation[2])

        perspective = fov / (final_z + camera_z + drone.position[2])
        projected_x = (final_x + drone.position[0]) * perspective + width // 2
        projected_y = (final_y + drone.position[1]) * perspective + height // 2

        projected_points.append([int(projected_x), int(projected_y)])

    # Fill the faces of the drone
    for face in drone_faces:
        pygame.draw.polygon(
            win, drone.LED, [projected_points[j] for j in face])

    # Draw propeller blades as rotating lines
    for center in projected_points[len(drone_vertices):]:
        x1 = center[0] + propeller_length * math.cos(propeller_rotation_angle)
        y1 = center[1] + propeller_length * math.sin(propeller_rotation_angle)
        x2 = center[0] + propeller_length * \
            math.cos(propeller_rotation_angle + math.pi)
        y2 = center[1] + propeller_length * \
            math.sin(propeller_rotation_angle + math.pi)

        pygame.draw.line(win, drone.LED, (int(x1), int(y1)),
                         (int(x2), int(y2)), 2)

    # Drawing wind direction as an arrow
    draw_wind_direction(win, wind_direction, wind_strength, red)
    pygame.display.flip()
    pygame.time.delay(10)

pygame.quit()
