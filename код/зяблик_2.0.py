from random import randint
import pygame
from os import path
import time

img_dir = path.join(path.dirname("__file__"), 'img')
snd_dir = path.join(path.dirname("__file__"), 'snd')
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
width = 1920
height = 1080
fps = 120
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Догони зяблика")
# графика
background = pygame.transform.scale(pygame.image.load(path.join(img_dir, "background.png")), (width, height))
background_rect = background.get_rect()
eye = pygame.image.load(path.join(img_dir, "eye.png"))
beer = pygame.transform.scale(pygame.image.load(path.join(img_dir, "beer.png")), (50, 50))
finch = [pygame.transform.scale(pygame.image.load(path.join(img_dir, "flying_finch.png")), (150, 150)),
         pygame.transform.scale(pygame.image.load(path.join(img_dir, "soaring_finch.png")), (150, 150))]
dead_finch = pygame.transform.scale(pygame.image.load(path.join(img_dir, "dead_finch.png")), (150, 150))
# аудио
hook = pygame.mixer.Sound(path.join(snd_dir, 'hook.wav'))
preview = pygame.mixer.Sound(path.join(snd_dir, 'preview.wav'))
music = pygame.mixer.Sound(path.join(snd_dir, 'music.wav'))
clash = pygame.mixer.Sound(path.join(snd_dir, 'clash.wav'))
loss = pygame.mixer.Sound(path.join(snd_dir, 'loss.wav'))
victory = pygame.mixer.Sound(path.join(snd_dir, 'victory.wav'))
baf = pygame.mixer.Sound(path.join(snd_dir, 'baf.wav'))
music.set_volume(0.07)
clash.set_volume(0.07)
loss.set_volume(0.07)
# рекордное прохождение
result = music.get_length() * 2
len_music = music.get_length() * 2
record = result
is_record = False


def end_game(text, size, y, sound):  # экран завершения игры
    afk_time = pygame.time.get_ticks()
    music.stop()
    sound.play()
    screen.blit(background, background_rect)
    draw_text(text, size, y)
    draw_text("Время - " + str(f"{time_to_death // 60:.{0}f}") + " : " + str(f"{time_to_death % 60:.{0}f}"), 70, 300)
    pygame.display.flip()
    while pygame.time.get_ticks() - afk_time < 4000:
        pass
    sound.stop()


def menu():  # главное меню с возможностью начать игру занова или выйти
    music.stop()
    preview.play(-1)
    screen.blit(background, background_rect)
    if is_record:
        draw_text("Рекорд - " + str(f"{record // 60:.{0}f}") + " : " + str(f"{record % 60:.{0}f}"), 70, 50, 250)
    draw_text("CATCH THE FINCH ", 150, 190)
    draw_text("ДОГОНИ ЗЯБЛИКА", 60, 350)
    draw_text("НАЧАТЬ", 100, 490)
    draw_text("ВЫЙТИ", 100, 640)
    pygame.display.flip()
    wait = True
    # главное меня до тех пор, пока игрок не нажал начать
    while wait:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    if (590 >= ev.pos[1] >= 490) and (width / 2 + 160 >= ev.pos[0] >= width / 2 - 160):
                        preview.stop()
                        wait = False
                        return True
                    if (740 >= ev.pos[1] >= 640) and (width / 2 + 145 >= ev.pos[0] >= width / 2 - 145):
                        pygame.quit()
                        return False


def draw_text(text, size, y, x=width / 2):  # текст
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    screen.blit(text_surface, text_rect)


def clashed(self):  # проверка врезался ли игрок в столб
    if eye.rect.right >= self.rect.left >= eye.rect.left + 50:
        if self.rect.y == 0:
            if self.q - 6 > eye.rect.top:
                eye.rect.x -= 6
                clash.play()
        else:
            if self.rect.y < eye.rect.y + 146:
                eye.rect.x -= 6
                clash.play()


class Mobs(pygame.sprite.Sprite):  # все мобы
    def __init__(self, image, x, y=height / 2 + 75):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.baf = False
        self.drinker = False
        self.speedy = 0
        self.speedx = 0
        self.fly = 0
        self.beer_drink = 0
        self.rect = self.image.get_rect()
        self.radius = 70
        self.rect.x = x
        self.rect.y = y
        self.old_time = pygame.time.get_ticks()
        self.baf_time = pygame.time.get_ticks()


class Eye(Mobs):  # игрок
    def update(self):
        now = pygame.time.get_ticks()
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        # управление глазов с помощью стрелов вверх и вниз
        if keystate[pygame.K_UP]:
            self.speedy = -10
        if keystate[pygame.K_DOWN]:
            self.speedy = 10
        # появиться тгроку вверху или вниху если вылетел за экран
        if self.rect.top > height:
            self.rect.top = 0
        if self.rect.bottom < 0:
            self.rect.bottom = height
        self.rect.y += self.speedy
        # постоянное движение вперед
        if now - self.old_time >= 58:
            self.rect.x += 1
            self.old_time = pygame.time.get_ticks()
        if not self.drinker:
            hit = pygame.sprite.spritecollide(eye, power, False, pygame.sprite.collide_circle)  # игрок подобрал бонус
            if hit:
                baf.play()
                beer.rect.x = -50
                self.beer_drink += 1
                if self.beer_drink == 3:  # бонус можно подбирать не больше 3 раз
                    self.drinker = True
                self.baf_time = now
                self.baf = True
                self.speedx = 1
        if now - self.baf_time > 2000:  # бонус действует 2 секунды
            self.baf = False
            self.speedx = 0
        self.rect.x += self.speedx


class Bird(Mobs):  # зяблик
    def update(self):
        now = pygame.time.get_ticks()
        # постоянное движение вперед
        if now - self.old_time >= 315:
            self.fly = 0 ** self.fly
            self.image = finch[0 ** self.fly]
            self.rect.x += 1
            self.old_time = pygame.time.get_ticks()
        self.rect.y += self.speedy
        self.speedy = 0


class Beer(Mobs):  # бонус
    def update(self):
        now = pygame.time.get_ticks()
        if self.rect.x < 0:
            self.rect.x = width
            self.rect.y = randint(100, height - 100)
            self.speedx = 0
        # раз в 30 секунд вылетает бонус
        if (now - self.old_time > 30000) and not eye.drinker:
            self.speedx = -7
            self.old_time = now
        self.rect.x += self.speedx


class Pipe(pygame.sprite.Sprite):  # столбы
    def __init__(self, random_y, wid, s):
        pygame.sprite.Sprite.__init__(self)
        self.q = random_y
        self.image = pygame.Surface((50, self.q))
        self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
        self.rect = self.image.get_rect()
        self.rect.x = width + 10 + wid
        self.rect.y = s
        self.speed = 6

    def update(self):
        self.rect.x -= self.speed
        # если столб улетел за экран - рисовать занова
        if self.rect.x < - 50:
            self.rect.x = width
            self.q = h
            if self.rect.y == 0:
                self.image = pygame.Surface((50, self.q))
            else:
                self.image = pygame.Surface((50, height - self.q - 300))
                self.rect.y = self.q + 300
            self.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
        # если eye под бафом - не врезаться
        if not eye.baf:
            clashed(self)
        # путь для птицы
        if 250 > self.rect.left - bird.rect.left > 0:
            if self.rect.y == 0:
                if bird.rect.centerx >= width:
                    bird.rect.y = self.q + 75
                elif self.q > bird.rect.top - 75:
                    bird.speedy = 50
            else:
                bird.speedy = -50


# создание объектов
all_sprites = pygame.sprite.Group()
power = pygame.sprite.Group()
nps = pygame.sprite.Group()
eye = Eye(eye, 150)
beer = Beer(beer, 1920, randint(100, height - 100))
bird = Bird(finch[1], 1400)
all_sprites.add(eye, bird, beer)
nps.add(bird)
power.add(beer)
pipe = [0, 1, 2, 3, 4, 5, 6, 7]
for i in range(0, 4):  # создание 4 столбов (верхний и низ)
    pipe[i] = Pipe(randint(0, height - 300), i * 500, 0)
    pipe[i + 4] = Pipe(height - pipe[i].q - 300, i * 500, pipe[i].q + 300)
    all_sprites.add(pipe[i + 4], pipe[i])
game_over = True
play = True

while play:  # цикл самой игры, если игра завершена начать заново
    # обновление всех переменных если игрок начал заново
    if game_over:
        time_to_death = music.get_length() * 2
        eye.rect.x = 150
        eye.rect.y = height / 2 - 75
        bird.rect.y = randint(100, height - 100)
        bird.rect.x = 1400
        beer.rect.x = 1920
        eye.beer_drink = 0
        eye.drinker = False
        beer.speedx = 0
        for i in range(0, 4):
            pipe[i].rect.x = width + i * 500
            pipe[i + 4].rect.x = width + i * 500
        if not menu():
            play = False
        music.play(2)
        beer.old_time = pygame.time.get_ticks()
        old_time = pygame.time.get_ticks()
        game_over = False
    clock.tick(fps)
    # если нажат крестик, закрыть игру
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
    # таймер
    timer = pygame.time.get_ticks()
    if timer - old_time >= 1000:
        time_to_death -= 1
        old_time = pygame.time.get_ticks()
    h = randint(0, height - 300)
    all_sprites.update()
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(str(f"{time_to_death // 60:.{0}f}") + " : " + str(f"{time_to_death % 60:.{0}f}"), 40, 50)
    pygame.display.flip()
    # время вышло
    if time_to_death < 1:
        end_game("ЗЯБЛИК УЛЕТЕЛ", 100, height / 2 - 50, loss)
        game_over = True
    # игрок догнал зяблика
    hits = pygame.sprite.spritecollide(eye, nps, False, pygame.sprite.collide_circle)
    if hits:
        hook.play()
        bird.image = dead_finch
        screen.blit(background, background_rect)
        all_sprites.draw(screen)
        pygame.display.flip()
        time.sleep(1)
        is_record = True
        result = len_music - time_to_death
        if result < record:
            record = result
        end_game("ПОБЕДА", 100, height / 2 - 50, victory)
        game_over = True
    # игрок улетел за экран
    if eye.rect.x < -177:
        end_game("ЗЯБЛИК УЛЕТЕЛ", 100, height / 2 - 50, loss)
        game_over = True

pygame.quit()
