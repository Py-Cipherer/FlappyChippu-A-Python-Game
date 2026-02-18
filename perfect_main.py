import json
import os
import random
import sys
import pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

FPS = 32
SCREENWIDTH = 400
SCREENHEIGHT = 600
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
FPSCLOCK = pygame.time.Clock()

GROUNDY = int(SCREENHEIGHT * 0.8)

GAME_SPRITES = {}
GAME_SOUNDS = {}

PLAYER = "gallery/fritters/bird.png"
BACKGROUND = "gallery/fritters/background.png"
PIPE = "gallery/fritters/pipe.png"
HIGHSCORE_FILE = "highscore.json"
FONT_SCORE = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 18)
FONT_TIMER = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 28)

POWERUPS = []
POWERUP_TYPES = ['shield', 'phaser']
POWERUP_DURATION = {'shield': 10, 'phaser': 5}

NEXT_POWERUP_TIME = 0
ACTIVE_POWERUP = None
POWERUP_END_TIME = 0

SHIELD_USED = False
INVINCIBLE_UNTIL = 0
PAUSED = False

# ------------------ UI -------------------------

def loadHighScore():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            return json.load(f).get("highscore", 0)
    return 0


def saveHighScore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump({"highscore": score}, f)


def drawPowerupTimer():
    if ACTIVE_POWERUP:
        remaining = max(0, (POWERUP_END_TIME - pygame.time.get_ticks()) // 1000)
        timer_text = FONT_TIMER.render(f"{remaining}sec", True, (0, 255, 255))
        SCREEN.blit(timer_text, (SCREENWIDTH - 60, 10))


def drawActivePowerupIcon():
    if ACTIVE_POWERUP:
        icon = pygame.transform.scale(GAME_SPRITES[ACTIVE_POWERUP], (32, 32))
        SCREEN.blit(icon, (10, 10))


def pauseScreen():
    font = pygame.font.SysFont(None, 50)
    text = font.render("PAUSED", True, (255, 255, 255))
    SCREEN.blit(text, (SCREENWIDTH // 2 - 80, SCREENHEIGHT // 2 - 20))
    pygame.display.update()


# ------------------ GAME ----------------------------

def welcomeScreen():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key in (K_SPACE, K_UP):
                GAME_SOUNDS['start'].play()
                return

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['message'], (0, 0))
        SCREEN.blit(GAME_SPRITES['player'], (SCREENWIDTH//2 - 20, SCREENHEIGHT//4))
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def getPipePair():
    gap = 150
    pipeX = SCREENWIDTH + 10
    lowerY = random.randint(int(SCREENHEIGHT * 0.35), int(GROUNDY - gap - 20))

    upperPipe = pygame.transform.scale(
        GAME_SPRITES['pipe'][0],
        (GAME_SPRITES['pipe'][0].get_width(), lowerY - gap)
    )

    lowerPipe = pygame.transform.scale(
        GAME_SPRITES['pipe'][1],
        (GAME_SPRITES['pipe'][1].get_width(), int(GROUNDY - lowerY))
    )

    return {'x': pipeX, 'upper': upperPipe, 'upper_y': 0,
            'lower': lowerPipe, 'lower_y': lowerY}


def isCollide(px, py, pipes):
    global ACTIVE_POWERUP, SHIELD_USED, INVINCIBLE_UNTIL

    if pygame.time.get_ticks() < INVINCIBLE_UNTIL:
        return False

    if py > GROUNDY - 25 or py < 0:
        GAME_SOUNDS['die'].play()
        return True

    if ACTIVE_POWERUP == 'phaser':
        return False

    playerW = GAME_SPRITES['player'].get_width()
    playerH = GAME_SPRITES['player'].get_height()
    pipeW = GAME_SPRITES['pipe'][0].get_width()

    for p in pipes:
        if px + playerW > p['x'] and px < p['x'] + pipeW:
            if py < p['upper'].get_height() or py + playerH > p['lower_y']:

                if ACTIVE_POWERUP == 'shield' and not SHIELD_USED:
                    SHIELD_USED = True
                    ACTIVE_POWERUP = None   # shield disappears after one hit
                    INVINCIBLE_UNTIL = pygame.time.get_ticks()+800 #0.8 sec grace
                    return False

                GAME_SOUNDS['die'].play()
                return True
    return False


def spawnPowerUp(pipe):
    ptype = random.choice(POWERUP_TYPES)
    x = pipe['x'] + 20
    y = random.randint(pipe['upper'].get_height() + 30, pipe['lower_y'] - 30)
    POWERUPS.append({'type': ptype, 'x': x, 'y': y})


def drawScore(score):
    digits = [int(x) for x in str(score)]
    x = (SCREENWIDTH - sum(GAME_SPRITES['numbers'][d].get_width() for d in digits)) // 2
    for d in digits:
        SCREEN.blit(GAME_SPRITES['numbers'][d], (x, 20))
        x += GAME_SPRITES['numbers'][d].get_width()

def drawHighScore(highscore):
    score_text = FONT_SCORE.render(f"HIGHSCORE: {highscore}", True, (255, 215, 0))
    SCREEN.blit(score_text, (SCREENWIDTH//4, 5))

def gameover(score,highscore):
    SCREEN.blit(GAME_SPRITES['background'], (0, 0))
    SCREEN.blit(GAME_SPRITES['gameover'], (0, SCREENHEIGHT//2 - 100))
    if score > highscore:
        saveHighScore(score)
    game_end_hs = loadHighScore()
    text = FONT_SCORE.render(f"HIGHSCORE:{game_end_hs}", True, (255, 215, 0))
    SCREEN.blit(text, (SCREENWIDTH//4, SCREENHEIGHT//2 +22))
    pygame.display.update()
    pygame.time.wait(2000)

def mainGame():
    global NEXT_POWERUP_TIME, ACTIVE_POWERUP, POWERUP_END_TIME, PAUSED, SHIELD_USED
    try:
        highscore = loadHighScore()
    except FileNotFoundError:
        pass
    
    score = 0
    playerx, playery = SCREENWIDTH // 5, SCREENHEIGHT // 5
    playerVelY = -9
    pipeVelX = -4

    pipes = [getPipePair(), getPipePair()]
    pipes[1]['x'] += SCREENWIDTH // 2

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    PAUSED = not PAUSED
                if not PAUSED and event.key in (K_SPACE, K_UP):
                    playerVelY = -8
                    GAME_SOUNDS['svoosh'].play()

        if PAUSED:
            pauseScreen()
            FPSCLOCK.tick(5)
            continue

        current_time = pygame.time.get_ticks()

        if current_time > NEXT_POWERUP_TIME:
            spawnPowerUp(random.choice(pipes))
            NEXT_POWERUP_TIME = current_time + random.randint(15000, 20000)

        for pu in POWERUPS[:]:
            pu['x'] += pipeVelX

            if (playerx < pu['x'] < playerx + GAME_SPRITES['player'].get_width() and
                playery < pu['y'] < playery + GAME_SPRITES['player'].get_height()):

                if ACTIVE_POWERUP == pu['type']:
                    POWERUP_END_TIME = current_time + POWERUP_DURATION[pu['type']] * 1000
                else:
                    ACTIVE_POWERUP = pu['type']
                    SHIELD_USED = False
                    POWERUP_END_TIME = current_time + POWERUP_DURATION[pu['type']] * 1000

                POWERUPS.remove(pu)

        if ACTIVE_POWERUP and current_time > POWERUP_END_TIME:
            ACTIVE_POWERUP = None

        playerVelY += 1
        playery += min(playerVelY, GROUNDY - playery)

        for p in pipes:
            p['x'] += pipeVelX

        if pipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            pipes.pop(0)
            pipes.append(getPipePair())

        playerMid = playerx + GAME_SPRITES['player'].get_width() // 2
        for p in pipes:
            pipeMid = p['x'] + GAME_SPRITES['pipe'][0].get_width() // 2
            if pipeMid <= playerMid < pipeMid + 4:
                score += 1
                GAME_SOUNDS['point'].play()

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['base'], (0, GROUNDY))

        if ACTIVE_POWERUP == 'phaser':
            GAME_SPRITES['player'].set_alpha(140)
        else:
            GAME_SPRITES['player'].set_alpha(255)

        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        if ACTIVE_POWERUP == 'shield':
            pygame.draw.circle(SCREEN, (0, 200, 255),
                               (playerx + 20, playery + 20), 30, 2)

        for p in pipes:
            SCREEN.blit(p['upper'], (p['x'], p['upper_y']))
            SCREEN.blit(p['lower'], (p['x'], p['lower_y']))

        for pu in POWERUPS:
            SCREEN.blit(GAME_SPRITES[pu['type']], (pu['x'], pu['y']))

        drawScore(score)
        drawHighScore(highscore)
        drawActivePowerupIcon()
        drawPowerupTimer()

        if isCollide(playerx, playery, pipes):
            return gameover(score,highscore)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


#------------- ASSETS -------------------

pygame.display.set_caption("Flappy Chippu by PyCipherer")

GAME_SPRITES['numbers'] = [pygame.transform.scale(
    pygame.image.load(f"gallery/fritters/{i}.png").convert_alpha(), (40, 60)) for i in range(10)]

GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
GAME_SPRITES['base'] = pygame.image.load("gallery/fritters/base.png").convert_alpha()
GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
GAME_SPRITES['message'] = pygame.image.load("gallery/fritters/msg.png").convert_alpha()
GAME_SPRITES['gameover'] = pygame.image.load("gallery/fritters/title.png").convert_alpha()

GAME_SPRITES['pipe'] = (
    pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
    pygame.image.load(PIPE).convert_alpha())

GAME_SPRITES['shield'] = pygame.image.load("gallery/fritters/shield.png").convert_alpha()
GAME_SPRITES['phaser'] = pygame.image.load("gallery/fritters/phaser_suit.png").convert_alpha()

GAME_SOUNDS['point'] = pygame.mixer.Sound("gallery/sounds/point.mp3")
GAME_SOUNDS['point'].set_volume(0.2)
GAME_SOUNDS['svoosh'] = pygame.mixer.Sound("gallery/sounds/svoosh.mp3")
GAME_SOUNDS['die'] = pygame.mixer.Sound("gallery/sounds/die.mp3")
GAME_SOUNDS['start'] = pygame.mixer.Sound("gallery/sounds/start.mp3")


while True:
    welcomeScreen()
    mainGame()
