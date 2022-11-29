import random
import pygame
from pygame.locals import *
from spritesheet import Spritesheet
from entity import Entity, outline





class Player(Entity):
    def __init__(self, *args):
        super().__init__(*args)
        self.velocity = [0, 0]
        self.speed = 0.8
        self.accel = 0.2
        self.air_time = 0
        self.jump = 19
        self.eating = 0
        self.await_eat = 0
        self.chomp = False
        self.angry = 0
        self.squish_velocity = 0
        self.hurt_timer = 0

    def update(self, gd):
        super().update(1 / 60)

        if self.angry > 0:
            self.angry -= 1

        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        if gd.completed_level < 60:
            self.scale[1] += self.squish_velocity
            self.scale[1] = max(0.3, min(self.scale[1], 1.7))
            self.scale[0] = 2 - self.scale[1]

            if self.scale[1] > 1:
                self.squish_velocity -= 0.02
            elif self.scale[1] < 1:
                self.squish_velocity += 0.02
            if self.squish_velocity > 0:
                self.squish_velocity -= 0.008
            if self.squish_velocity < 0:
                self.squish_velocity += 0.008

            if self.squish_velocity != 0:
                if (abs(self.squish_velocity) < 0.03) and (abs(self.scale[1] - 1) < 0.06):
                    self.scale[1] = 1
                    self.squish_velocity = 0

        rects = [t[1] for t in gd.level_map.get_nearby_rects(self.center)]
        if gd.completed_level < 60:
            self.velocity[1] = min(4, self.velocity[1] + 0.25)
        if (abs(self.velocity[0]) > self.speed) or (not (gd.input[0] or gd.input[1])) or self.eating:
            if abs(self.velocity[0]) <= self.speed:
                self.velocity[0] *= 0.85
            else:
                self.velocity[0] *= 0.97
        if abs(self.velocity[0]) < 0.1:
            self.velocity[0] = 0

        if gd.completed_level > 60:
            self.rotation += 18
            self.scale = [max(0, 1 - (gd.completed_level - 60) / 30), max(0, 1 - (gd.completed_level - 60) / 30)]
            self.velocity[1] = -0.3

        if not self.eating and not self.chomp and not gd.completed_level:
            if gd.input[0]:
                self.flip[0] = True
                if self.velocity[0] > -self.speed:
                    self.velocity[0] -= self.accel
                    self.velocity[0] = max(-self.speed, self.velocity[0])
            if gd.input[1]:
                self.flip[0] = False
                if self.velocity[0] < self.speed:
                    self.velocity[0] += self.accel
                    self.velocity[0] = min(self.speed, self.velocity[0])
            if gd.input[2]:
                if self.jump > 0:
                    if self.jump == 19:
                        self.velocity[0] *= 4
                        gd.add_animation('jump', (self.pos[0] - 5, self.pos[1]))
                        #sounds['jump'].play()
                        if gd.tutorial == 2:
                            gd.tutorial = 1
                    self.jump -= 1
                    self.velocity[1] = -4.6
                    self.air_time = 6
                    if self.jump <= 0:
                        gd.input[2] = False
            elif self.jump < 19:
                self.jump = 0
        else:
            self.set_action('idle', force=not self.chomp)
            gd.input = [False, False, False]
            self.jump = 0

        if self.air_time > 5:
            if not self.hurt_timer:
                self.set_action('jump')
            if self.jump == 19:
                self.jump = 0
        else:
            self.jump = 19
            if self.await_eat:
                self.eating = self.await_eat
                self.await_eat = 0
            if gd.input[0] or gd.input[1]:
                if not self.hurt_timer:
                    self.set_action('walk')
            else:
                if not self.hurt_timer:
                    self.set_action('idle')

        self.flash = False
        if self.hurt_timer or (gd.anger > 55):
            if random.random() < 0.4:
                self.flash = True
            if self.hurt_timer:
                self.set_action('hurt')

        if self.chomp:
            self.active_animation.play(3 / 60)
            if self.active_animation.frame > 15:
                self.chomp = False

        self.air_time += 1
        collisions = self.move(self.velocity, rects)
        if collisions['top']:
            self.jump = 0
            gd.input[2] = False
        if collisions['bottom']:
            if self.velocity[1] > 2:
                self.squish_velocity = -0.15
                gd.screenshake = 8
                gd.add_animation('stomp', (self.pos[0] - 14, self.pos[1]))
                #sounds['land'].play()
                damage_r = pygame.Rect(self.pos[0] - 24, self.pos[1] + 15, 68, 10)
                hit_enemy = False
                for enemy in gd.enemies:
                    if enemy.rect.colliderect(damage_r):
                        hit_enemy = True
                        enemy.dead = True
                        enemy.set_action('hurt', force=True)
                        enemy.velocity[1] = -(random.random() * 3 + 3)
                '''if hit_enemy:
                    sounds['hit'].play()'''
            self.air_time = 0
        if collisions['top'] or collisions['bottom']:
            self.velocity[1] = 1
        if collisions['left'] or collisions['right']:
            self.velocity[0] = 0


pygame.init()
DISPLAY_W,DISPLAY_H = 480,270
canvas = pygame.surface((DISPLAY_W,DISPLAY_H))
window = pygame.display.set_mode((DISPLAY_W,DISPLAY_H))
pygame.display.set_caption('Runner')
clock = pygame.time.Clock()
test_font = pygame.font.Font('C:/Users/NPC/Documents/Pygame/font/Pixeltype.ttf', 50)
game_active = False
start_time = 0
score = 0

#Groups
sky_surface = pygame.image.load('C:/Users/NPC/Downloads/ninja game/png/BG2.png').convert()
player = pygame.image.load('C:/Users/NPC/Downloads/ninja game/png/Character-ninja/Idle__000.png').convert_alpha()

my_spritesheet = Spritesheet('sprite.png')
trainer = [my_spritesheet.parse_sprite('Idle__000.png'), my_spritesheet.parse_sprite('Idle__001.png'),my_spritesheet.parse_sprite('Idle__002.png'),my_spritesheet.parse_sprite('Idle__003.png'),my_spritesheet.parse_sprite('Idle__004.png'),my_spritesheet.parse_sprite('Idle__005.png'),my_spritesheet.parse_sprite('Idle__006.png'),my_spritesheet.parse_sprite('Idle__007.png'),my_spritesheet.parse_sprite('Idle__008.png'),my_spritesheet.parse_sprite('Idle__009.png'),]
index = 0

while True:
	for event in pygame.event.get():
            if event.key == pygame.K_SPACE:
                index = (index + 1) % len(trainer)



    canvas.blit(trainer[index],(128, DISPLAY_H - 128))
    window.blit(canvas,(0,0))
    pygame.display.update()
