import pygame
import traceback
import os

#===============================================================================
# TODO:
# - When colliding platform from below -> player teleports to top.
#    => Fix or prevent jumping through platforms?
# - Monsters moving on platforms?
# - Player shoot fireballs?
# - Ladders?
# - Optimize g, player.speed, player.jumps_speed for platforms.
#===============================================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

FPS = 60 # Target screen refresh rate.
max_dt = 1 / 30 # Cap for delta time.
animation_speed = 6
tile_x = 32
tile_y = 32
g = 1500 # Gravitational acceleration.

# Game window.
WIDTH = 960
HEIGHT = 540
window_size = [WIDTH, HEIGHT]

# Set ground level where player falls without platform.
GROUND = HEIGHT - tile_y

# Class for creating player sprite.
class Robot(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 200
        self.jump_speed = 700
        self.jumping = False
        self.velocity_x = 0
        self.velocity_y = 0
        self.ground = GROUND
        self.left = False
        self.right = False
        self.animation_cycles = 10
        self.frame = 0
        self.images = []
        
        # Load all the images for player movement animation.
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
            # Jump possible only from when on ground.
            self.jumping = False
        else:
            self.velocity_y += g * dt
            # Prevent jumping when falling.
            self.jumping = True
            
    def jump(self):
        self.velocity_y -= self.jump_speed
        self.jumping = True
    
    def update(self, dt):
        self.rect.x += int(self.velocity_x * dt)
        self.rect.y += int(self.velocity_y * dt)
        
        # Set correct value for ground if player is on top of platform.
        colliding_platform = pygame.sprite.spritecollideany(self, all_tiles)
        if colliding_platform is None:
            self.ground = GROUND
        else:
            self.ground = colliding_platform.rect.y - tile_y + 1
        
        # Looping movement to other side of the window when reaching border.
        if self.rect.x > WIDTH:
            self.rect.x = - tile_x
        elif self.rect.x < - tile_x:
            self.rect.x = WIDTH
        
        # Animating player movement.
        if self.left:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif self.right:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + self.animation_cycles]
            self.frame += 1
        else:
            self.image = self.images[20]

# Simple monster class.
class Monster(pygame.sprite.Sprite):
    
    def __init__(self, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.velocity_x = 0
        self.velocity_y = 0
        self.frame = 0
        self.images = []
        self.animation_cycles = 5
        for i in range(0,11):
            img = pygame.image.load(os.path.join
                                    (assets, 'monster' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect  = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location
    
    def update(self, dt):
        self.rect.x += int(self.velocity_x * dt)
        self.rect.y += int(self.velocity_y * dt)
        
        # Looping movement to other side of the window when reaching border.
        if self.rect.x > WIDTH:
            self.rect.x = - tile_x
        elif self.rect.x < - tile_x:
            self.rect.x = WIDTH
        
        # Animating movement.
        if self.velocity_x < 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif self.velocity_x > 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + 5]
            self.frame += 1
        else:
            self.image = self.images[10]
        
class Tile(pygame.sprite.Sprite):
    
    def __init__(self, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(assets,'tile.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location

# x_start and y_start for where platform starts and width times height = amount of tiles used.
def create_platform(x_start, y_start, plat_width, plat_height):
    i = 0
    while i < plat_height:
        j = 0
        while j < plat_width:
            platform_part = Tile(x_start + j * tile_x, y_start + i * tile_y)
            all_tiles.add(platform_part)
            j += 1
        i += 1
        
def update_window(dt):
    window.fill(SKY_BLUE)
    
    # Calls the update() method on all Sprites in the Group.
    all_sprites.update(dt)
    
    # Draws the contained Sprites to the Surface argument. 
    # This uses the Sprite.image attribute for the source surface, 
    # and Sprite.rect for the position.
    all_sprites.draw(window)
    all_tiles.draw(window)

    pygame.display.flip()

def main():
    player = Robot()
    player.rect.x = 0
    player.rect.y = 0
    all_sprites.add(player)
    
    # Testing monsters.
    monster = Monster(0, HEIGHT - tile_y)
    monster.velocity_x = 150
    all_sprites.add(monster)
    monster2 = Monster(WIDTH - tile_x, HEIGHT - tile_y)
    monster2.velocity_x = -150
    all_sprites.add(monster2)
    monster3 = Monster(4 * tile_x, HEIGHT - 13 * tile_y)
    all_sprites.add(monster3)
    
    # Testing platforms.
    create_platform(1 * tile_x, HEIGHT - 2 * tile_y, 7, 1)
    create_platform(12 * tile_x, HEIGHT - 5 * tile_y, 5, 1)
    create_platform(21 * tile_x, HEIGHT - 8 * tile_y, 3, 1)
    create_platform(3 * tile_x, HEIGHT - 12 * tile_y, 4, 2)
    create_platform(18 * tile_x, HEIGHT - 12 * tile_y, 1, 1)
    create_platform(12 * tile_x, HEIGHT - 11 * tile_y, 1, 1)
    create_platform(27 * tile_x, HEIGHT - 11 * tile_y, 2, 1)
    
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
            player.left = True
            player.right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.rect.x += int(player.speed * dt)
            player.right = True
            player.left = False
        else:
            player.left = False
            player.right = False
            
        player.gravity(dt)
        update_window(dt)

if __name__ == "__main__":
    try:
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
        
        # For keeping up time to control screen refresh rate, used in game loop.
        clock = pygame.time.Clock()
        
        all_sprites = pygame.sprite.Group()
        all_tiles = pygame.sprite.Group()
        
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()