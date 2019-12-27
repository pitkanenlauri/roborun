import pygame
import traceback
import os

#===============================================================================
# TODO:
# - Remove multi jump.
# - Acceleration to max speed when starting to move?
# - Encapsulate game initialization?
# - Add enemies
# - Shoot fireballs?
# - Add platforms.
# - Ladders.
# - Platform collisions.
# - Optimize g, player.speed, player.jumps_speed for platforms
#===============================================================================

# Colors.
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

# Target screen refresh rate.
FPS = 60
# Gravitational acceleration.
g = 1500
# Cap for delta time.
max_dt = 1 / 30
# Set ground level. (to be removed when checking ground from platform top)
ground = 500 - 32

# Variables for animation.
animation_cycles = 10
animation_speed = 6
left = False
right = False

# Game window.
WIDTH = 1000
HEIGHT = 500
window_size = [WIDTH, HEIGHT]

# Initialize PyGame and create game window.
pygame.init()
pygame.display.set_caption("Roborun")
window = pygame.display.set_mode(window_size)

# Set path to game assets dir.
game_dir = os.path.dirname(__file__)
assets = os.path.join(game_dir, 'assets')

# Set window icon.
pygame.display.set_icon(pygame.image.load(os.path.join
                                          (assets, 'robo12.png')).convert_alpha())

clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()

class Robot(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 200
        self.jump_speed = 500
        self.velocity_x = 0
        self.velocity_y = 0
        self.frame = 0
        self.images = []
        
        for i in range(1,22):
            img = pygame.image.load(os.path.join
                                    (assets, 'robo' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect  = self.image.get_rect()
    
    def gravity(self, dt):
        if self.rect.y >= ground and self.velocity_y >= 0:
            self.velocity_y = 0
            self.rect.y = ground
        else:
            self.velocity_y += int(g * dt)
            
    def jump(self):
        self.velocity_y -= self.jump_speed
    
    def update(self, dt, left, right):
        self.rect.x += int(self.velocity_x * dt)
        self.rect.y += int(self.velocity_y * dt)
        
        # Looping movement to other side of the window when reaching border.
        if self.rect.x > WIDTH:
            self.rect.x = -32
        elif self.rect.x < -32:
            self.rect.x = WIDTH
        
        if left:
            if self.frame >= animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif right:
            if self.frame >= animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + 10]
            self.frame += 1
        else:
            self.image = self.images[20]
    
def update_window(dt, left, right):
    window.fill(SKY_BLUE)
    
    # Calls the update() method on all Sprites in the Group.
    all_sprites.update(dt, left, right)
    
    # Draws the contained Sprites to the Surface argument. 
    # This uses the Sprite.image attribute for the source surface, 
    # and Sprite.rect for the position.
    all_sprites.draw(window)

    pygame.display.flip()

def main():
    
    player = Robot()
    player.rect.x = 0
    player.rect.y = 0
    all_sprites.add(player)
    
    # Game loop.
    while True:
        
        # Creating Delta Time to make movement independent of frame rate.
        dt = clock.tick(FPS) / 1000
        if dt > max_dt:
            dt = max_dt
        
        for event in pygame.event.get():
            # Closes game window.
            if (event.type == pygame.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return pygame.quit()
            # Initiate jump on releasing space key.
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                player.jump()
                
        keys = pygame.key.get_pressed()
                 
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.rect.x -= int(player.speed * dt)
            left = True
            right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.rect.x += int(player.speed * dt)
            right = True
            left = False
        else:
            left = False
            right = False

# For ladders. Check if colliding ladder sprite to work?
#         elif keys[pygame.K_UP] or keys[pygame.K_w]:
#             player.rect.y -= int(player.speed * dt)
#             print('Up!')
#         elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
#             player.rect.y += int(player.speed * dt)
#             print('Down!')
        
        player.gravity(dt)
        update_window(dt, left, right)

if __name__ == "__main__":
    try:
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()