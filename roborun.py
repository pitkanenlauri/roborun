import pygame
import traceback
import os

#===============================================================================
# TODO:
# - When colliding platform from below -> player teleports to top.
#    => Fix or prevent jumping through platforms?
# - Add enemies
# - Shoot fireballs?
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
# Set ground level where player falls without platform.
GROUND = 500 - 32

# Variables for animation.
animation_cycles = 10
animation_speed = 6
left = False
right = False
tile_x = 32
tile_y = 32

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
all_platforms = pygame.sprite.Group()

class Robot(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 200
        self.jump_speed = 700
        self.jumping = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.frame = 0
        self.images = []
        self.ground = HEIGHT - 32
        
        for i in range(1,22):
            img = pygame.image.load(os.path.join
                                    (assets, 'robo' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect  = self.image.get_rect()
    
    def gravity(self, dt):
        if self.rect.y >= self.ground and self.velocity_y >= 0:
            self.velocity_y = 0
            self.rect.y = self.ground
            # Jump possible only from "solid ground".
            self.jumping = False
        else:
            self.velocity_y += g * dt
            # Prevent jumping when falling.
            self.jumping = True
            
            
    def jump(self):
        self.jumping = True
        self.velocity_y -= self.jump_speed
    
    def update(self, dt, left, right):
        self.rect.x += int(self.velocity_x * dt)
        self.rect.y += int(self.velocity_y * dt)
        
        # Set correct value for ground if player is on top of platform.
        colliding_platform = pygame.sprite.spritecollideany(self, all_platforms)
        if colliding_platform is None:
            self.ground = GROUND
        else:
            self.ground = colliding_platform.rect.y - tile_y + 1
        
        # Looping movement to other side of the window when reaching border.
        if self.rect.x > WIDTH:
            self.rect.x = - tile_x
        elif self.rect.x < - tile_x:
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

class Platfrom(pygame.sprite.Sprite):
    
    def __init__(self, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(assets,'tile.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location

# x and y for where platform starts and width times height = amount of tiles used.
def create_platform(x, y, plat_width, plat_height):
    i = 0
    while i < plat_height:
        j = 0
        while j < plat_width:
            platform = Platfrom(x + j * tile_x, y + i * tile_x)
            all_platforms.add(platform)
            j += 1
        i += 1
        
def update_window(dt, left, right):
    window.fill(SKY_BLUE)
    
    # Calls the update() method on all Sprites in the Group.
    all_sprites.update(dt, left, right)
    
    # Draws the contained Sprites to the Surface argument. 
    # This uses the Sprite.image attribute for the source surface, 
    # and Sprite.rect for the position.
    all_sprites.draw(window)
    all_platforms.draw(window)

    pygame.display.flip()

def main():
    
    player = Robot()
    player.rect.x = 0
    player.rect.y = 0
    all_sprites.add(player)
    
    # Platforms for testing.
    create_platform(1 * tile_x, HEIGHT - 2 * tile_y, 7, 2)
    create_platform(12 * tile_x, HEIGHT - 5 * tile_y, 5, 1)
    create_platform(21 * tile_x, HEIGHT - 8 * tile_y, 3, 1)
    create_platform(3 * tile_x, HEIGHT - 12 * tile_y, 4, 2)
    create_platform(18 * tile_x, HEIGHT - 12 * tile_y, 1, 1)
    create_platform(12 * tile_x, HEIGHT - 12 * tile_y, 1, 1)
    
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not player.jumping:
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