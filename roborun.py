import pygame
import traceback
import os

#===============================================================================
# TODO:
# - Parent class for all sprites for collisiondetection and animation etc.
# - Some items to collect?
# - Divide code into separate files for clarity.
# - Make world loader and place worlds to text files.
# - Sound effects!
# - Optimize g and player movement for wanted world dynamics.
# - Optimize rendering, dont draw sprites that go outside the game window.
# - Level loader class.
# - Center camera starting position accordding to player spawn position.
# - Start up screen and world selection?
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
camera_speed = 0.06 # Smooth scrolling, how fast camera catches the player. def = 0.06
borders = False # If True camera wont show stuff outside world borders.

lives = 10
reset_lives = lives
g = 1500 # Gravitational acceleration. def = 1500
shoot_count = 10 # Amount of fireballs that can be on air at once.
reset_fire = shoot_count
fireball_lifetime = 250 # def = 250
fireball_speed = 250 # def = 250
player_speed = 200 # def = 200
player_jump_speed = 500 # How high player can jump. def = 500
monster_speed = 70 # def = 70

# Game window.
WIDTH = 960
HEIGHT = 544
window_size = [WIDTH, HEIGHT]

# World templates for testing. 960x544 pixels = 30x17 tiles. (1 tile = 32x32 pixels)
# P = Platform M = monster S = Spawn player
# Choose which one to use from below or create your own. 
# Hint: For convenience use insert to place P, M, S etc.
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
"SM                            ",
"PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

world1 = [
"                              ",
"       M                      ",
"   M            M        M    ",
"              P       M       ",
"      P                       ",
"            M       P       M ",
"                    M         ",
"   PP            M        PP  ",
"         M                    ",
"              P          M    ",
"                   M          ",
"       M   P                 M",
"                           M  ",
"                P  M          ",
"       M                M     ",
"PS                            ",
"PPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

world2 = [
"                              ",
"                              ",
"          PP    M  P    P    P",
"         PPPPPPPPPPP          ",
"   PPPPPPP                    ",
"  PP                          ",
"P                             ",
"P                             ",
"PP                            ",
"PP     P  M  M   P    M PPPP  ",
"PPP    PPPPPPPPPPPPPPPPPPP    ",
"                             P",
"                          P  P",
"                       P  PP P",
"S                   P  PP PPPP",
"PPP   PPP  M   P  PPPPPPPPPPPP",
"PPP   PPPPPPPPPP  PPPPPPPPPPPP",
]

world3 = [
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"                                                            ",
"S                                                           ",
"PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
]

# Choose which world to use.
world = world2

# Set ground level where player falls without platform.
GROUND = len(world) * tile_y + 2048

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

# Class for implementing world scrolling.
class Camera(object):
    def __init__(self, camera_function, world_width, world_height):
        self.camera_function = camera_function
        self.state = pygame.Rect(0, 0, world_width, world_height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, source):
        self.state = self.camera_function(self.state, source.rect)

# Function for moving camera, centered around source_rect.
def camera_function(camera, source_rect):
    # Center camera to source_rect center.
    x = -source_rect.center[0] + int(WIDTH / 2)
    y = -source_rect.center[1] + int(HEIGHT / 2)
    position = pygame.Vector2(camera.topleft)
    # Move the camera, multiplies by camera_speed for smoothness.
    position += (pygame.Vector2((x, y)) 
                       - pygame.Vector2(camera.topleft)) * camera_speed
    camera.topleft = (int(position.x), int(position.y))
    # Set max/min x/y to limit camera from moving outside world borders.
    if borders:
        camera.x = max(-(camera.width - WIDTH), min(0, camera.x))
        camera.y = max(-(camera.height - HEIGHT), min(0, camera.y))
    return camera

def generate_world(world):
    y = 0
    for row in world:
        x = 0
        for element in row:
            if element == "S": # S = Spawn player
                start_pos = [x, y + 1]
            if element == "P": # P = Platform
                platform_part = Tile(x * tile_x, y * tile_y)
                all_tiles.add(platform_part)
            if element == "M": # M = Monster
                monster = Monster(x * tile_x, y * tile_y)
                all_sprites.add(monster)
                all_monsters.add(monster)
            x += 1
        y += 1
    return start_pos

# Show how much lives player has left.
def draw_lives():
    global lives
    for i in range(lives):
        window.blit(pygame.image.load(
            os.path.join(assets,'heart.png')).convert_alpha(), (i * 20 + 4, 4))

def update_window(dt, camera):
    window.fill(backround_color)
    
    # Calls the update() method on all Sprites in the Group.
    all_sprites.update(dt)
    
    # Render world.
    for sprite in all_sprites:
        window.blit(sprite.image, camera.apply(sprite))
    for tile in all_tiles:
        window.blit(tile.image, camera.apply(tile))

    draw_lives()
    pygame.display.flip()
    
def game_over(player):
    global lives
    global shoot_count
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
                return pygame.quit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                lives = reset_lives
                shoot_count = reset_fire
                all_sprites.empty()
                all_tiles.empty()
                all_monsters.empty()
                return main()
    
def main():
    # Let there be light!
    start_pos = generate_world(world)
    
    camera = Camera(camera_function, tile_x * len(world[0]), tile_y * len(world))
    
    # "In a hole in the ground there lived a robot..."
    player = Robot(start_pos[0] * tile_x, start_pos[1] * tile_y)
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
            elif event.type == pygame.KEYDOWN and (
                event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT):
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
        
        camera.update(player)
        update_window(dt, camera)
        
        # Game ends if player runs out of lives or drops out of map.
        global lives
        if lives <= 0 or player.rect.y > (len(world) * tile_y + 512):
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