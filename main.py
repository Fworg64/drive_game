#!/bin/usr/python3

## Drive Game
# Shows a flat textured terrain image with 2.5 dimension sprites

import pygame
import pygame.gfxdraw
import cv2
import numpy as np

# Procedurally generate texture with obstacles

# Calculate perspective transform to and from ground plane

SCREEN_W = 120
SCREEN_H = 90

relative_ground_positions = [(1.0, 0.5), # Near left
                               (2.0, 0.5), # Far left
                               (2.0, -0.5), # Far right
                               (1.0, -0.5)] # Near right

screen_ground_positions = [(SCREEN_W/2.0 - SCREEN_W/7.0, SCREEN_H * 0.45),
                           (SCREEN_W/2.0 - SCREEN_W/12.0, SCREEN_H/3.0),
                           (SCREEN_W/2.0 + SCREEN_W/12.0, SCREEN_H/3.0),
                           (SCREEN_W/2.0 + SCREEN_W/7.0, SCREEN_H * 0.45)]

rover_polygon = [(0.3, -0.3),
                 (0.5, 0.0),
                 (0.3, 0.3),
                 (-0.3, 0.3),
                 (-0.3, -0.3)]


camera_to_ground_tf = cv2.getPerspectiveTransform(
  np.float32(screen_ground_positions),
  np.float32(relative_ground_positions)
)

ground_to_camera_tf = cv2.getPerspectiveTransform(
  np.float32(relative_ground_positions),
  np.float32(screen_ground_positions)
)

vanishing_point = ground_to_camera_tf @ np.float32([(10000), (0), (1)])
vanishing_point[0] /= vanishing_point[2]
vanishing_point[1] /= vanishing_point[2]
print(vanishing_point[0:2])

print(camera_to_ground_tf)

# Get field of view at vanishing point

left_ext = camera_to_ground_tf @ np.float32([0, vanishing_point[1], 1])
#right_ext = camera_to_ground_tf @ np.float32([SCREEN_W vanishing_point[1], 1])
fov_2 = np.arctan2(left_ext[1]/left_ext[2], 10000)
fov_rad = 2.0 * fov_2
print(f"Field of View: {2.0 * fov_2 * 180 / 3.1415}")

# Sun vector
sun_angle = -0.5 # rad CCW
sun_vec_x = np.cos(sun_angle)
sun_vec_y = np.sin(sun_angle)

crater_x = 7
crater_y = 3
crater_r = 2
       
rock_x = 2
rock_y = -0.5
rock_r = 0.75
       

def get_ground_points(x,y, cam_x=0, cam_y=0, cam_th=0):
  ground_pose = camera_to_ground_tf @ np.float32([(x), (y), (1.0)])
  if np.abs(ground_pose[2]) > 1e-5:
    ground_pose[0] /= ground_pose[2]
    ground_pose[1] /= ground_pose[2]
    ground_pose[2] /= ground_pose[2]

  # Convert to absolute coord from relative camera coord
  camera_ground_to_abs_ground_tf = np.float32(
    [[np.cos(cam_th), -np.sin(cam_th), cam_x],
    [np.sin(cam_th), np.cos(cam_th), cam_y],
    [0.0, 0.0, 1.0]])

  abs_pose = camera_ground_to_abs_ground_tf @ ground_pose
  abs_pose[0] /= abs_pose[2]
  abs_pose[1] /= abs_pose[2]

  return abs_pose[0], abs_pose[1]

print(relative_ground_positions)

for point in screen_ground_positions:
  ground_coord = get_ground_points(point[0], point[1])
  print(ground_coord)

def get_camera_point(gx, gy):
  cam_pose = ground_to_camera_tf @ np.float32([(gx), (gy), (1.0)])
  cam_pose[0] /= cam_pose[2]
  cam_pose[1] /= cam_pose[2]
  return cam_pose[0], cam_pose[1]

# Display flat texture
def get_ground_color(gx, gy, cam_x=0, cam_y=0):
    dist = np.sqrt(exe*exe + wye*wye)
    base_col = (0,0,0)
    if dist < 100:
       base_col = (0, 0, 255- 255 * dist/100.0)
       if dist > 10 and dist < 12:
           base_col = (0,255,0)
       
       # Check for crater
       crater_dist = np.sqrt((gx - crater_x)**2 + (gy - crater_y)**2)
       if (crater_dist < crater_r):
         crater_product = sun_vec_x * (gx - crater_x) \
                        + sun_vec_y * (gy - crater_y)
         crater_product = crater_product / crater_r
         crater_product = max(0, crater_product)
         reflecty_product = sun_vec_x * (crater_x - cam_x) \
                          + sun_vec_y * (crater_y - cam_y)
         reflecty_product /= np.sqrt((cam_x - crater_x)**2 + (cam_y - crater_y)**2)
         reflecty_product = max(0, reflecty_product)
         col = (255*np.sqrt(crater_product*reflecty_product), 
                base_col[1], base_col[2]*np.sqrt(reflecty_product*crater_product))
         base_col = col

       # Check for rock
       rock_dist = np.sqrt((gx - rock_x)**2 +(gy - rock_y)**2)
       if (rock_dist < rock_r):
         rock_product = sun_vec_x * (rock_x - gx) \
                      + sun_vec_y * (rock_y - gy)
         rock_product /= rock_r
         rock_product = max(0, rock_product)
         reflecty_product = sun_vec_x * (rock_x - cam_x) \
                          + sun_vec_y * (rock_y - cam_y)
         reflecty_product /= np.sqrt((cam_x - rock_x)**2 + (cam_y - rock_y)**2)
         reflecty_product = max(0, reflecty_product)
         col = (reflecty_product*255, 255*rock_product*reflecty_product, base_col[2]*rock_product)
         base_col = col

    return base_col


# Display perspective texture

# Display 2.5d sprites for rocks

# Display gradient texture for negative obstacles

# Tilt perspective image for vehicle incline



pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
clock = pygame.time.Clock()
running = True

pygame.display.set_caption("Hello World")

camera_x = 0
camera_y = 0
camera_th = 0
robot_r = 0.3


last_ticks = 0
curr_ticks = 0
while running:
  curr_ticks = pygame.time.get_ticks()
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_w or event.key ==pygame.K_UP:
        camera_x += 0.5 * np.cos(camera_th) 
        camera_y += 0.5 * np.sin(camera_th)
        print("FORWARD")
      elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
        camera_x += -0.5 * np.cos(camera_th) 
        camera_y += -0.5 * np.sin(camera_th)
        print("BACKWARD")
      elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
        camera_th += 0.1
        print("CCW")
      elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
        camera_th -= 0.1
        print("CW")
        

  # Do ray tracing with ground plane
  for px in range(SCREEN_W):
    for py in range(int(vanishing_point[1]),SCREEN_H):
        # Do inverse transform for point to relative ground plane position
        exe, wye = get_ground_points(px, py, camera_x, camera_y, camera_th)
        col = get_ground_color(exe, wye, camera_x, camera_y)
        # Calculate absolute ground coordinates

        # Pick color from recorded ground texture
        pygame.gfxdraw.pixel(screen, px, py, col)
    for py in range(0, int(vanishing_point[1])):
        point_ang = fov_rad * (px - SCREEN_W/2.0)/SCREEN_W - camera_th
        sun_product = (-sun_vec_x * np.cos(point_ang) + sun_vec_y * np.sin(point_ang) + 1) / 2.0
        sun_product = sun_product * sun_product * sun_product * sun_product
        sun_product *= 1.0 - ((py - int(vanishing_point[1])/2.0) / (int(vanishing_point[1])/2.0))**2
        col = (200*sun_product, 230*sun_product, 255*sun_product)
        pygame.gfxdraw.pixel(screen, px, py, col)
        
  # Plot calibration target points (rasterized)
  pygame.draw.polygon(screen,  (5, 50, 20), 
    [get_camera_point(x,y) for x,y in rover_polygon],
    0)
  pygame.draw.line(screen, (255, 0, 0), 
    get_camera_point(*relative_ground_positions[1]),
    get_camera_point(*relative_ground_positions[2]))
  pygame.draw.line(screen, (255, 0, 0), 
    get_camera_point(*relative_ground_positions[3]),
    get_camera_point(*relative_ground_positions[0]))
  pygame.draw.line(screen, (255,255,255), (0,vanishing_point[1]), (SCREEN_W, vanishing_point[1]))
  # Rasterize rocks by plotting sprite at X,Y with scaling

  # Check for collision with rock or crater
  crater_dist = np.sqrt((camera_x - crater_x)**2 + (camera_y - crater_y)**2)
  rock_dist   = np.sqrt((camera_x - rock_x)**2 + (camera_y - rock_y)**2)
  crater_dist = crater_dist - crater_r - robot_r
  rock_dist = rock_dist - rock_r - robot_r
  print(f"Robot X: {camera_x:.4f}, Robot Y: {camera_y:.4f}, Robot Th: {camera_th}.")
  print(f"Rock Dist: {rock_dist:.4f}, Crater Dist: {crater_dist}")

  pygame.display.flip()
  clock.tick(10)
  print(curr_ticks - last_ticks)
  last_ticks = curr_ticks

pygame.quit()
