import pygame
import random
import time
pygame.font.init()



#COLORS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

#CONSTANT VARIABLES
WIDTH, HEIGHT =  550, 550
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Battle")

#LOAD IMAGES
#BACKGROUND
background = pygame.image.load("background.png")
BG = pygame.transform.scale(background, (WIDTH, HEIGHT))

#ENEMY SHIPS
SPACE_SHIP_ENEMY1 = pygame.image.load("Alixandre.png")
SPACE_SHIP_ENEMY2 = pygame.image.load("Micaias.png")
SPACE_SHIP_ENEMY3 = pygame.image.load("Pauliana.png")
SPACE_SHIP_ENEMY4 = pygame.image.load("Syandra.png")

#PLAYER SHIP
SPACE_SHIP1 = pygame.image.load("Spaceship.png")

#LASER
RED_LASER = pygame.image.load("pixel_laser_red.png")
BLUE_LASER = pygame.image.load("pixel_laser_blue.png")
GREEN_LASER = pygame.image.load("pixel_laser_green.png")

#MUSICS AND SOUNDS

def Main_Menu_theme():
     pygame.mixer.init()
     pygame.mixer.music.load("Main Menu.wav")
     pygame.mixer.music.play(-1) 

def Background_theme():
    pygame.mixer.init()
    pygame.mixer.music.load("Background.wav")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

def Collision_sound():
    pygame.mixer.init()
    collision_sound = pygame.mixer.Sound("collision2.wav")
    collision_sound.set_volume(0.2)
    collision_sound.play()

def Laser_sound():
    pygame.mixer.init()
    laser_sound = pygame.mixer.Sound("laser.wav")
    laser_sound.set_volume(0.1)
    laser_sound.play()

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, surface):
        surface.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class ship:
    COOLDOWN = 30

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.laser_cooldown = 0

    def draw(self, surface):
        surface.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(surface)

    def lasers_move(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health += -10
                Collision_sound()
                self.lasers.remove(laser)

    def cooldown(self):
        if self.laser_cooldown >= self.COOLDOWN:
            self.laser_cooldown = 0
        elif self.laser_cooldown > 0:
            self.laser_cooldown += 1 

    def shoot(self):
        if self.laser_cooldown == 0:
            laser = Laser((self.x-self.ship_img.get_width()/2), (self.y-self.ship_img.get_height()), self.laser_img)
            self.lasers.append(laser)
            self.laser_cooldown = 1

    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()

class Player(ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SPACE_SHIP1
        self.laser_img = RED_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def lasers_move(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        Collision_sound()
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, surface):
        super().draw(surface)
        self.health_bar(surface)

    def health_bar(self, surface):
        pygame.draw.rect(surface, RED, (self.x, self.y + self.ship_img.get_height() + 5, self.ship_img.get_width(), 5))
        pygame.draw.rect(surface, GREEN, (self.x, self.y + self.ship_img.get_height() + 5, self.ship_img.get_width() * (self.health/self.max_health), 5))


class Enemy(ship):
    ENEMY_SHIP_MAP = {
                "enemy1":  (SPACE_SHIP_ENEMY1),
                "enemy2": (SPACE_SHIP_ENEMY2),
                "enemy3": (SPACE_SHIP_ENEMY3) ,
                "enemy4": (SPACE_SHIP_ENEMY4)
                }

    def __init__(self, x, y, number, health = 100):
        super().__init__(x, y, health)
        self.ship_img = self.ENEMY_SHIP_MAP[number]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (int(offset_x), int(offset_y))) != None

def game():
    Background_theme()
    run = True
    FPS = 60
    lives = 3
    level = 0
    player = Player((WIDTH-50)/2, HEIGHT - 80)
    SHIP_SPEED = 5

    enemies = []
    wave = 8 
    enemy_speed = 1

    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 30)

    lost = False
    lost_font = pygame.font.SysFont("comicsans", 40)
    lost_time = 0

    laser_speed = 5

    def window():
        SCREEN.blit(BG, (0,0))
        #DRAW TEXTS
        live_text = main_font.render("LIFES: " + str(lives), 1, WHITE)
        level_text = main_font.render("LEVEL: " + str(level), 1, WHITE)
        SCREEN.blit(live_text, (10,10))
        SCREEN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        #DRAW SHIP
        player.draw(SCREEN)

        #DRAW ENEMIES
        for enemy in enemies:
            enemy.draw(SCREEN)

        #LOST TEXT
        if lost:
            lost_text = lost_font.render("GAME OVER!!", 1, WHITE)
            SCREEN.blit(lost_text, ((WIDTH-lost_text.get_width())/2, HEIGHT/2))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        window()
        if lives <= 0 or player.health == 0:
            lost = True
            lost_time += 1

        if lost:
            if lost_time > 4 * FPS:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave += 5
            for i in range(wave):
                enemy = Enemy(random.randrange(50, WIDTH - 50), random.randrange(-1500, -100), random.choice(["enemy1", "enemy2", "enemy3", "enemy4"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x += -SHIP_SPEED
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < WIDTH:
            player.x += SHIP_SPEED
        if keys[pygame.K_UP] and player.y > 0:
            player.y += -SHIP_SPEED
        if keys[pygame.K_DOWN] and player.y + player.get_height() + 15 < HEIGHT:
            player.y += SHIP_SPEED
        if keys[pygame.K_SPACE]:
            player.shoot()
            Laser_sound()

        for enemy in enemies[:]:
            enemy.move(enemy_speed)

            if collide(enemy, player):
                player.health += -10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.lasers_move(-laser_speed, enemies)


def main_menu():
    run = True
    main_menu_font = pygame.font.SysFont("comicsans", 45)
    Main_Menu_theme()
    while run:
        SCREEN.blit(BG, (0,0))
        main_menu_text = main_menu_font.render("Pressione o mouse para começar", 1, WHITE)
        SCREEN.blit(main_menu_text, ((WIDTH/2 - main_menu_text.get_width()/2), HEIGHT/2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                game()

    pygame.quit()
          
main_menu()

