import pygame
import traceback
import os

#===============================================================================
# TODO:
# - Some items to collect?
# - Divide code into separate files for clarity.
# - Sound effects!
# - Camera system for moving backround?
# - Optimize g and player movement for wanted map dynamics.
#
#===============================================================================

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (32, 32, 32)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

backround_color = GREY

FPS = 60 # Target screen refresh rate.
max_dt = 1 / 20 # Cap for delta time.
animation_speed = 6
tile_x = 32
tile_y = 32

lives = 10
reset_lives = lives
g = 1500 # Gravitational acceleration. default = 1500
shoot_count = 10 # Amount of fireballs that can be on air at once.
fireball_lifetime = 250 # How long fireball stays in the air. def = 250
fireball_speed = 250 # def = 250
player_speed = 200 # def = 200
player_jump_speed = 500 # How high player can jump. def = 500
monster_speed = 70 # def = 70

# Game window.
WIDTH = 960
HEIGHT = 544
window_size = [WIDTH, HEIGHT]

# Set ground level where player falls without platform.
GROUND = 10000

# World templates. 960x544 pixels = 30x17 tiles. (1 tile = 32x32 pixels)
# W = wall M = monster
# Choose which one to use from below or create your own. 
# Hint: For convenience use insert to add W's and M's.
world0 = [
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
"                              ",
" M                            ",
"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

world1 = [
"                              ",
"       M                      ",
"   M            M        M    ",
"              W       M       ",
"      W                       ",
"            M       W       M ",
"                    M         ",
"   WW            M        WW  ",
"         M                    ",
"              W          M    ",
"                   M          ",
"       M   W                 M",
"                           M  ",
"                W  M          ",
"       M                M     ",
"W                             ",
"WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
]

world2 = [
"                              ",
"                              ",
"          WWWW  M  W    W    W",
"         WWWWWWWWWWW          ",
"   WWWWWWW                    ",
"  WW                          ",
"W                             ",
"W                             ",
"WW                            ",
"WW     W  M  M   W   W M WWW  ",
"WWW    WWWWWWWWWWWWWWWWWWW    ",
"                             W",
"                          W  W",
"                       W  WW W",
"                    W  WW WWWW",
"WWW   WWW  M   W  WWWWWWWWWWWW",
"WWW   WWWWWWWWWW  WWWWWWWWWWWW"
]

# Choose which world to use.
world = world2

# Class for creating player sprite.
class Robot(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.hit_time = 100
        self.speed = player_speed
        self.jump_speed = player_jump_speed 
        self.jumping = False
        self.shooting_right = True
        self.velocity_x = 0
        self.velocity_y = 0
        self.ground = GROUND
        self.frame = 0
        self.images = []
        self.animation_cycles = 10
        
        # Load all the images for player movement animation.
        for i in range(1,22):
            img = pygame.image.load(
                os.path.join(assets, 'robo' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def gravity(self, dt):
        if self.rect.bottom > self.ground and self.velocity_y >= 0:
            self.velocity_y = 0
            self.rect.bottom = self.ground + 1
            # Jumping possible when on ground.
            self.jumping = False
        else:
            # v = v_0 + a*t
            self.velocity_y += g * dt
            # Prevent jumping when falling.
            self.jumping = True
    
    def jump(self):
        self.velocity_y -= self.jump_speed
        self.jumping = True

    def shoot_fireball(self):
        global shoot_count
        if shoot_count > 0:
            shoot_count -= 1
            if self.shooting_right:
                fireball = Fireball(fireball_speed, self.rect.x, self.rect.y - 1)
                all_sprites.add(fireball)
            else:
                fireball = Fireball(-fireball_speed, self.rect.x, self.rect.y - 1)
                all_sprites.add(fireball)

    def update(self, dt):
        self.gravity(dt)
        
        # Moving player in x direction. x = x_0 + v_x*t
        self.rect.x += int(self.velocity_x * dt)
        
        # Collision detection in x direction.
        colliding_tile = pygame.sprite.spritecollideany(self, all_tiles)
        if colliding_tile is None:
            self.ground = GROUND
        # Hitting wall from left.
        elif self.velocity_x > 0  and self.ground != colliding_tile.rect.top:
            self.rect.right = colliding_tile.rect.left
            self.velocity_x = 0
        # Hitting wall from right.
        elif self.velocity_x < 0 and self.ground != colliding_tile.rect.top:
            self.rect.left = colliding_tile.rect.right
            self.velocity_x = 0
        
        # Moving player in y direction. y = y_0 + v_y*t
        self.rect.y += int(self.velocity_y * dt)
        
        # Collision detection in y direction.
        colliding_tile = pygame.sprite.spritecollideany(self, all_tiles)
        if colliding_tile is None:
            self.ground = GROUND
        # Hitting the ceiling.
        elif self.velocity_y < 0:
            self.rect.top = colliding_tile.rect.bottom
            self.velocity_y = 0
            self.ground = GROUND
        # Hitting the floor.
        elif self.velocity_y > 0:
            self.velocity_y = 0
            self.ground = colliding_tile.rect.top
        
        # Check if monsters got you.
        global lives
        colliding_monster = pygame.sprite.spritecollideany(self, all_monsters)
        if (colliding_monster is not None) and (self.hit_time >= 100):
            lives -= 1
            self.jump()
            self.hit_time = 0
        self.hit_time += 1
            
        # Restricting player movement to inside game window.
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity_x = 0
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x = 0

        # Animating player movement.
        if self.velocity_x < 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif self.velocity_x > 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + self.animation_cycles]
            self.frame += 1
        else:
            self.image = self.images[20]

# Fireball projectile class which player can shoot.
class Fireball(pygame.sprite.Sprite):
    def __init__(self, velocity_x, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.velocity_x = velocity_x
        self.lifetime = fireball_lifetime
        self.frame = 0
        self.images = []
        self.animation_cycles = 3
        for i in range(0,6):
            img = pygame.image.load(
                os.path.join(assets, 'fireball' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect  = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location
    
    def update(self, dt):
        global shoot_count
        self.rect.x += int(self.velocity_x * dt)
        
        # Check if fireball hits monsters.
        colliding_monster = pygame.sprite.spritecollideany(self, all_monsters)
        if colliding_monster is None:
            self.lifetime -= 1
        else:
            colliding_monster.kill()
            shoot_count += 1
            self.kill()
        
        # Check if fireball hits tiles.
        colliding_tile = pygame.sprite.spritecollideany(self, all_tiles)
        if colliding_tile is not None:
            shoot_count += 1
            self.kill()
        
        if self.lifetime == 0:
            shoot_count += 1
            self.kill()
        
        # Animating fireball movement.
        if self.velocity_x < 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif self.velocity_x > 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + self.animation_cycles]
            self.frame += 1
        else:
            self.image = self.images[0]
            
# Simple monster class.
class Monster(pygame.sprite.Sprite):
    
    def __init__(self, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.velocity_x = monster_speed
        self.velocity_y = 0
        self.frame = 0
        self.images = []
        self.animation_cycles = 5
        for i in range(0,11):
            img = pygame.image.load(
                os.path.join(assets, 'monster' + str(i) + '.png')).convert_alpha()
            self.images.append(img)
        self.image = self.images[0]
        self.rect  = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location

    def update(self, dt):
        self.rect.x += int(self.velocity_x * dt)
        
        # Collision detection in x direction.
        colliding_tile = pygame.sprite.spritecollideany(self, all_tiles)
        if colliding_tile is not None:
            # Hitting wall from left.
            if self.velocity_x > 0  and self.rect.bottom != colliding_tile.rect.top:
                self.rect.right = colliding_tile.rect.left
                self.velocity_x *= -1
            # Hitting wall from right.
            elif self.velocity_x < 0 and self.rect.bottom != colliding_tile.rect.top:
                self.rect.left = colliding_tile.rect.right
                self.velocity_x *= -1
        
        # Keeps monster inside the game window.
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.velocity_x *= -1
        if self.rect.left < 0:
            self.rect.left = 0
            self.velocity_x *= -1
        
        # Animating monster movement.
        if self.velocity_x < 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed]
            self.frame += 1
        elif self.velocity_x > 0:
            if self.frame >= self.animation_cycles * animation_speed:
                self.frame = 0
            self.image = self.images[self.frame//animation_speed + self.animation_cycles]
            self.frame += 1
        else:
            self.image = self.images[10]

# Class for generating tile object.        
class Tile(pygame.sprite.Sprite):
    
    def __init__(self, x_location, y_location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            os.path.join(assets,'tile.png')).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x_location
        self.rect.y = y_location

def generate_world(world):
    y = 0
    for row in world:
        x = 0
        for element in row:
            if element == "W": # W = Wall
                platform_part = Tile(x * tile_x, y * tile_y)
                all_tiles.add(platform_part)
            if element == "M": # M = Monster
                monster = Monster(x * tile_x, y * tile_y)
                all_sprites.add(monster)
                all_monsters.add(monster)
            x += 1
        y += 1

# Show how much lives player has left.
def draw_lives():
    global lives
    for i in range(lives):
        window.blit(pygame.image.load(
            os.path.join(assets,'heart.png')).convert_alpha(), (i * 20 + 4, 4))

def update_window(dt):
    window.fill(backround_color)
    
    # Calls the update() method on all Sprites in the Group.
    all_sprites.update(dt)
    
    # Draws the contained Sprites to the Surface argument. 
    # This uses the Sprite.image attribute for the source surface, 
    # and Sprite.rect for the position.
    all_sprites.draw(window)
    all_tiles.draw(window)
    draw_lives()

    pygame.display.flip()
    
def game_over(player):
    global lives
    window.fill(BLACK)
    font = pygame.font.Font('freesansbold.ttf', 16)
    text = font.render("Game over  -  Press n for new game!", True, WHITE)
    window.blit(text, (int(WIDTH / 2) - int(text.get_rect().width / 2), 256))
    window.blit(player.images[20], (int(WIDTH / 2) - 16, 200))
    pygame.display.flip()
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if (event.type == pygame.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                lives = reset_lives
                all_sprites.empty()
                all_tiles.empty()
                all_monsters.empty()
                return main()
    
def main():
    # Let there be light!
    generate_world(world)
    
    # "In a hole in the ground there lived a robot..."
    player = Robot(0 * tile_x, 15 * tile_y)
    all_sprites.add(player)
    
    # Game loop.
    while True:
        
        # Creating Delta Time to make movement independent of frame rate.
        dt = clock.tick(FPS) / 1000
        if dt > max_dt:
            dt = max_dt
        
        for event in pygame.event.get():
            # Close game window with red X button or Esc.
            if (event.type == pygame.QUIT or
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return pygame.quit()
            # Initiate jump on pressing space key.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not player.jumping:
                    player.jump()
            # Shoot fireballs when pressing right shift.
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RSHIFT:
                player.shoot_fireball()
                
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.velocity_x = - player.speed
            player.shooting_right = False
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.velocity_x = player.speed
            player.shooting_right = True
        else:
            player.velocity_x = 0

        update_window(dt)
        
        # Game ends if player runs out of lives or drops out of map.
        global lives
        if lives <= 0 or player.rect.y > 1000:
            game_over(player)
            return
    
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
        pygame.display.set_icon(pygame.image.load(
            os.path.join(assets, 'robo12.png')).convert_alpha())
        
        # For keeping up time to control screen refresh rate, used in game loop.
        clock = pygame.time.Clock()
        
        # Make groups for handling sprites.
        all_sprites = pygame.sprite.Group()
        all_tiles = pygame.sprite.Group()
        # For handling interaction with monsters, monsters are also in all_sprites.
        all_monsters = pygame.sprite.Group()
        
        main()
    except:
        traceback.print_exc()
        pygame.quit()
        input()