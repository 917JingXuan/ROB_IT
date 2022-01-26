import os, random, csv, pygame
from pygame import mixer
import json

pygame.init()
mixer.init()

#define screen size
SCREEN_WIDTH = 1550
SCREEN_HEIGHT = 800

#draw screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Rob It')
clock = pygame.time.Clock()

data = {
    'level': int(1),
    'sound': float(0.1),
    'sound_fx': float(0.1)
}
try:
    with open('game_data.txt') as data_file:
        data = json.load(data_file)
except:
    print("Json file was not found")


#define variables
FPS = 60
GRAVITY = 0.78
screen_scroll = 0
bg_scroll = 0
scroll_thresh = 500
ROWS = 25
start_game = False
info_game = False
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 50
MAX_LEVELS = 4
volume = 0.1
text_sound = round(data["sound"] * 10)
text_sound_fx = round(data["sound"] * 10)


moving_left = False
moving_right = False
shoot = False
RED = (255, 0, 0)

#load music and sounds
pygame.mixer.music.load('Assets/song.mp3')
pygame.mixer.music.set_volume(data["sound"])
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('Assets/jump.wav')
jump_fx.set_volume(data["sound_fx"])
coin_fx = pygame.mixer.Sound('Assets/coin.wav')
coin_fx.set_volume(data["sound_fx"])
bullet_fx = pygame.mixer.Sound('Assets/bullet.mp3')
bullet_fx.set_volume(data["sound_fx"])
lose_fx = pygame.mixer.Sound('Assets/lose.mp3')
lose_fx.set_volume(data["sound"])


# images
start_img = pygame.image.load('Pictures/start_button_dark.png').convert_alpha()
restart_img = pygame.image.load('Pictures/restart_button.png').convert_alpha()
bg_img = pygame.image.load('Pictures/Background.png').convert_alpha()
menu_img = pygame.image.load('Pictures/menu_light.png').convert_alpha()
win_img = pygame.image.load('Pictures/youwon_dark_menu.png').convert_alpha()
lose_img = pygame.image.load('Pictures/youlose_dark_menu.png').convert_alpha()
exit_img = pygame.image.load('Pictures/exit_button.png').convert_alpha()
option_img = pygame.image.load('Pictures/options_button.png').convert_alpha()
option_menu_img = pygame.image.load('Pictures/option_menu.png').convert_alpha()
menu_bttn_img = pygame.image.load('Pictures/menu_button.png').convert_alpha()
menu_bttn2_img = pygame.image.load('Pictures/menu_button.png').convert_alpha()
left_img = pygame.image.load('Pictures/left_volume.png').convert_alpha()
right_img = pygame.image.load('Pictures/right_volume.png').convert_alpha()
left2_img = pygame.image.load('Pictures/left_volume.png').convert_alpha()
right2_img = pygame.image.load('Pictures/right_volume.png').convert_alpha()
#store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'Pictures/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)


bullet_image = pygame.image.load('Pictures/bullet.png')
coin_image = pygame.image.load('Pictures/32.png').convert_alpha()
item_boxes = {
    'Coins': coin_image
}

# define font

font = pygame.font.Font('Assets/INVASION2000.TTF', 40)
Font = pygame.font.SysFont('Futura', 60)

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.fill('black')
    width = bg_img.get_width()
    for x in range(5):
        screen.blit(bg_img, ((x * width) - bg_scroll * 0.5, 0))

def reset():
    enemy_group.empty()
    bullet_group.empty()
    coin_group.empty()
    exit_group.empty()
    trap_group.empty()
    decoration_group.empty()

    # tile_list
    data = []
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)
    return data

class Player(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.health = 1
        self.max_health = self.health
        self.coins = 0
        self.shoot_cooldown = 0
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 200, 20)
        self.idling = False
        self.idling_counter = 0

        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'Pictures/{self.char_type}/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Pictures/{self.char_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        dx = 0
        dy = 0
        screen_scroll = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump == True and self.in_air == False:
            self.vel_y = -16
            self.jump = False
            self.in_air = True

        # apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        # check collision
        for tile in world.obstacle_list:
            # x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if ai hit the wall
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #check if above the ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with trap
        if pygame.sprite.spritecollide(self, trap_group, False):
            lose_fx.play()
            self.health = 0


        #check collision if fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            lose_fx.play()
            self.health = 0


        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # next level
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - scroll_thresh and bg_scroll < (world.level_lenght * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < scroll_thresh and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            bullet_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot()

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_right = True
                    else:
                        ai_right = False
                    ai_left = not ai_right
                    self.move(ai_left, ai_right)
                    self.update_action(1)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)

                    if self.move_counter > 64:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter < 0:
                        self.idling = False

        #camera
        self.rect.x += screen_scroll



    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        #iterate through each value in level data file
        self.level_lenght = len(data[0])
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 1 and tile <= 5 or tile >= 34 and tile <= 36:#floor
                        self.obstacle_list.append(tile_data)
                    elif tile == 0 or tile >= 6 and tile <= 28:#fence and house
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 29:#trap
                        trap = Trap(img, x * TILE_SIZE, y * TILE_SIZE)
                        trap_group.add(trap)
                    elif tile == 30:#player
                        player = Player('player', x * TILE_SIZE, y * TILE_SIZE, 1.9, 5)
                    elif tile == 31:#enemy
                        enemy = Player('enemy', x * TILE_SIZE, y * TILE_SIZE, 1.9, 3)
                        enemy_group.add(enemy)
                    elif tile == 32:#coins
                        coin = Coin('Coins', x * TILE_SIZE, y * TILE_SIZE, 2.5, 2.5)
                        coin_group.add(coin)
                    elif tile == 33:#exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)
                    elif tile >= 37 and tile <= 45 or tile == 49:#fence and house
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    if tile >= 46 and tile <= 48:#floor
                        self.obstacle_list.append(tile_data)


        return player

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # camera
        self.rect.x += screen_scroll


class Trap(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        # camera
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed) + screen_scroll
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH - 100:
            self.kill()

        # level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 1
                lose_fx.play()
                self.kill()

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False

        #get mouse position
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        #draw button
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

class Coin(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        # load all images for the players
        animation_types = ['coins']
        for animation in animation_types:
            # reset temporary list of images
            temp_list = []
            # count number of files in the folder
            num_of_frames = len(os.listdir(f'Pictures/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'Pictures/{animation}/{i}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def update_animation(self):
        # update animation
        ANIMATION_COOLDOWN = 80
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        # check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


    def update(self):
        # camera
        self.rect.x += screen_scroll
        # chek if the player has picked the coins
        if pygame.sprite.collide_rect(self, player):
            player.coins += 1
            coin_fx.play()

            self.kill()

start_button = Button(SCREEN_WIDTH // 2 - 158, SCREEN_HEIGHT // 2 - 60, start_img, 1)
restart_button = Button(SCREEN_WIDTH // 2 - 158, SCREEN_HEIGHT // 2 - -15, restart_img, 1)
exit_button = Button(SCREEN_WIDTH // 2 - 158, SCREEN_HEIGHT // 2 - -90, exit_img, 1)
option_button = Button(SCREEN_WIDTH // 2 - 158, SCREEN_HEIGHT // 2 - -15, option_img, 1)
menu_button = Button(SCREEN_WIDTH // 2 - 550, SCREEN_HEIGHT // 2 - -250, menu_bttn_img, 1)
menu_button2 = Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 15, menu_bttn2_img, 1)
right_button = Button(SCREEN_WIDTH // 2 + 160, SCREEN_HEIGHT // 2 - 55, right_img, 1)
left_button = Button(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 - 55, left_img, 1)
right_button2 = Button(SCREEN_WIDTH // 2 + 160, SCREEN_HEIGHT // 2 + 100, right2_img, 1)
left_button2 = Button(SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 2 + 100, left2_img, 1)

bullet_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
trap_group = pygame.sprite.Group()


#create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)
# load in level data and create world
with open(f'level{data["level"]}.csv', newline='')as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)
world = World()
player = world.process_data(world_data)

run = True
while run:
    with open('game_data.txt', 'w') as data_file:
        json.dump(data, data_file)

    clock.tick(FPS)
    if start_game == False:
        #main menu
        if info_game == False:
            screen.blit(menu_img, (0, 0))
            if start_button.draw(screen):
                start_game = True
            if exit_button.draw(screen):
                run = False
            if option_button.draw(screen):
                info_game = True
        else:
            screen.blit(option_menu_img, (0, 0))
            if menu_button.draw(screen):
                info_game = False
            if right_button.draw(screen) and text_sound < 10:
                text_sound += 1
                data["sound"] += volume
                pygame.mixer.music.set_volume(data["sound"])
                lose_fx.set_volume(data["sound"])
            if left_button.draw(screen) and text_sound > 0:
                text_sound -= 1
                data["sound"] -= volume
                pygame.mixer.music.set_volume(data["sound"])
                lose_fx.set_volume(data["sound"])
            if right_button2.draw(screen) and text_sound_fx < 10:
                text_sound_fx += 1
                data["sound_fx"] += volume
                coin_fx.set_volume(data["sound_fx"])
                jump_fx.set_volume(data["sound_fx"])
                bullet_fx.set_volume(data["sound_fx"])
            if left_button2.draw(screen) and text_sound_fx > 0:
                text_sound_fx -= 1
                data["sound_fx"] -= volume
                coin_fx.set_volume(data["sound_fx"])
                jump_fx.set_volume(data["sound_fx"])
                bullet_fx.set_volume(data["sound_fx"])
            if text_sound == 10:
                draw_text(f'{text_sound}', font, 'white', SCREEN_WIDTH // 2 + 70, SCREEN_HEIGHT // 2 - 35)

            else:
                draw_text(f'{text_sound}', font, 'white', SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 - 35)
            if text_sound_fx == 10:
                draw_text(f'{text_sound_fx}', font, 'white', SCREEN_WIDTH // 2 + 70, SCREEN_HEIGHT // 2 + 125)

            else:
                draw_text(f'{text_sound_fx}', font, 'white', SCREEN_WIDTH // 2 + 80, SCREEN_HEIGHT // 2 + 125)




    else:
        # update background
        draw_bg()

        # draw world map
        world.draw()

        draw_text(f'Coins: {player.coins} / 10', font, 'black', 10, 35)
        exit_group.update()
        exit_group.draw(screen)
        trap_group.update()
        trap_group.draw(screen)
        decoration_group.update()
        decoration_group.draw(screen)
        bullet_group.update()
        bullet_group.draw(screen)
        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        for coin in coin_group:
            coin.update_animation()
            coin.draw()
            coin.update()

        if player.alive:

            if player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)

            bg_scroll -= screen_scroll
            #levelz_complete
            if level_complete and player.coins == 10:
                if data['level'] >= MAX_LEVELS:
                    screen.blit(win_img, (0,0))
                    player.vel_y = 0
                    player.speed = 0
                    if menu_button2.draw(screen):
                        start_game = False
                        data['level'] = 0


                else:
                    data['level'] += 1
                    bg_scroll = 0
                    world_data = reset()
                    with open(f'level{data["level"]}.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player = world.process_data(world_data)

            elif level_complete:
                screen_scroll = 0
                screen.blit(lose_img, (0, 0))
                player.vel_y = 0
                player.speed = 0
                if restart_button.draw(screen):
                    bg_scroll = 0
                    world_data = reset()
                    with open(f'level{data["level"]}.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player = world.process_data(world_data)


        else:
            screen_scroll = 0
            screen.blit(lose_img ,(0,0))
            pygame.mixer.music.set_volume(0)
            if restart_button.draw(screen):
                bg_scroll = 0
                world_data = reset()
                with open(f'level{data["level"]}.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',')
                    for x, row in enumerate(reader):
                        for y, tile in enumerate(row):
                            world_data[x][y] = int(tile)
                world = World()
                player = world.process_data(world_data)
                pygame.mixer.music.set_volume(data["sound"])


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w and player.alive:
                player.jump = False

    pygame.display.update()

pygame.quit()