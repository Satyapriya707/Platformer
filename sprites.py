import pygame as pg
from settings import *
from random import choice, randrange
from os import path
from tilemap import *
vec = pg.math.Vector2

game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, 'img')


class Bullet(pg.sprite.Sprite):
    def __init__(self, game):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.last_update = 0
        self.image = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        if self.game.player.vel.x >= 0:
            self.rect.centerx = self.game.player.hit_rect.right
        else:
            self.rect.centerx = self.game.player.hit_rect.left
        self.rect.centery = self.game.player.hit_rect.centery + 20
        self.hit_rect = self.rect
        self.value = randrange(-5,5)/10
        self.start = pg.time.get_ticks()
        self.temp = randrange(3,7)
        if self.game.player.vel.x < 0:
            self.temp *= -1

    def update(self):
        self.rect.x += self.temp
        self.rect.y += self.value
        self.hit_rect.center = self.rect.center
        if pg.time.get_ticks() - self.start > 1500:
            self.kill()
        


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.width = w
        self.height = h
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.stand_img
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(x, y, w, h)
        self.pos = vec(x + w/2, y + h)
        self.rect.midbottom = self.pos
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.last_shot = pg.time.get_ticks()
        self.health = 100
        self.dead = False
        self.check = True
        self.score = 0
        # load high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highest_score = int(f.read())
            except:
                self.highest_score = 0

    def load_images(self):
        self.stand_img = pg.image.load(path.join(img_folder, 'stand.png')).convert_alpha()
        self.stand_img.set_colorkey(BLACK)
        self.walk_frames_r = [pg.image.load(path.join(img_folder, 'walk_1.png')).convert_alpha(),
                                pg.image.load(path.join(img_folder, 'walk_2.png')).convert_alpha()]
        self.walk_frames_l = []
        for frame in self.walk_frames_r:
            frame.set_colorkey(BLACK)
            self.walk_frames_l.append(pg.transform.flip(frame, True, False))
        self.jump_img = pg.image.load(path.join(img_folder, 'jump.png')).convert_alpha()
        self.jump_img.set_colorkey(BLACK)
        self.duck_img = pg.image.load(path.join(img_folder, 'duck.png')).convert_alpha()
        self.duck_img.set_colorkey(BLACK)
        self.hurt_img = pg.image.load(path.join(img_folder, 'hurt.png')).convert_alpha()
        self.hurt_img.set_colorkey(BLACK)

    def Shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > 250:
            self.game.shoot_snd.play()
            self.last_shot = now
            Bullet(self.game)

    def jump(self):
        # jump only if standing on a platform
        self.hit_rect.y += 5
        hits = pg.sprite.spritecollide(self, self.game.platforms, False, collide_hit_rect)
        i_hits = pg.sprite.spritecollide(self, self.game.items, False, collide_hit_rect)
        self.hit_rect.y -= 5
        if (hits or i_hits) and not self.jumping:
            self.game.jump_snd.play()
            self.jumping = True
            self.vel.y = -PLAYER_JUMP

    def Dead(self):
        if self.check:
            right = self.rect.right
            bottom = self.rect.bottom
            self.image = self.hurt_img
            self.rect = self.image.get_rect()
            self.rect.right = right 
            self.rect.bottom = bottom
            self.check = False
            self.hit_rect = self.rect

    def update(self):
        if self.dead:
            self.Dead()
        else:
            self.animate()
            self.acc = vec(0, PLAYER_GRAV)
            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                self.acc.x = -PLAYER_ACC
            if keys[pg.K_RIGHT]:
                self.acc.x = PLAYER_ACC
            if keys[pg.K_DOWN]:
                bottom = self.rect.bottom
                self.image = self.duck_img
                if self.vel.x < 0:
                    self.image =  pg.transform.flip(self.duck_img, True, False)
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
                self.hit_rect = pg.Rect(0,0,self.width,56)
                self.hit_rect.midbottom = self.pos
            if keys[pg.K_KP0]:
                self.Shoot()
        # apply friction
        self.acc.x += self.vel.x * PLAYER_FRICTION
        # equations of motion
        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        if self.dead:
            self.vel.x = 0
            self.acc.x = 0
            self.acc.y *= .3
            self.vel.y = 5
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH - self.rect.width/2:
            self.pos.x = WIDTH - self.rect.width/2
        if self.pos.x < 0 + self.rect.width/2:
            self.pos.x = 0 + self.rect.width/2
        self.rect.midbottom = self.pos
        self.hit_rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()
        if self.vel.x != 0:
            self.walking = True
        else:
            self.walking = False            
        # show walk animation
        if self.walking:
            if now - self.last_update > 180:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames_l)
                bottom = self.rect.bottom
                if self.vel.x > 0:
                    self.image = self.walk_frames_r[self.current_frame]
                else:
                    self.image = self.walk_frames_l[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
        # show idle animation
        if not self.jumping and not self.walking:
            bottom = self.rect.bottom
            self.image = self.stand_img
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
        # show jump animation
        if self.jumping:
            bottom = self.rect.bottom
            self.image = self.jump_img
            if self.vel.x < 0:
                self.image = pg.transform.flip(self.jump_img, True, False)
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom

            
class Platform(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.platforms
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        

class Item(pg.sprite.Sprite):
    def __init__(self, game, Type, x, y, w, h):
        self.groups = game.items, game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = Type
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
        self.img1 = pg.image.load(path.join(img_folder, lives1_img)).convert_alpha()
        self.img2 = pg.image.load(path.join(img_folder, lives2_img)).convert_alpha()
        self.img1.set_colorkey(BLACK)
        self.img2.set_colorkey(BLACK)
        self.image = self.img1
        self.img_rect = self.image.get_rect()
        self.img_rect.center = self.rect.center

        def update(self):
            self.img_rect.center = self.rect.center


class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.obstacles
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Mob_bullet(pg.sprite.Sprite):
    def __init__(self, mob, game):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.mob_bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.mob = mob
        self.last_update = 0
        self.image = pg.image.load(path.join(img_folder, MOB_BULLET_IMG)).convert_alpha()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        if self.mob.dir_wrt_player == 'right':
            self.rect.centerx = self.mob.hit_rect.left
        else:
            self.rect.centerx = self.mob.hit_rect.right
        self.rect.centery = self.mob.rect.centery + 20
        self.hit_rect = self.rect
        if self.mob.hit_rect.y <= self.game.player.hit_rect.y:
            self.value = randrange(6,11)/10
        elif self.mob.hit_rect.y > self.game.player.hit_rect.y:
            self.value = randrange(-10,-5)/10
        if self.mob.dir_wrt_player == 'right':
            self.change = -randrange(3,7)
        else:
            self.change = randrange(3,7)
        self.start = pg.time.get_ticks()

    def update(self):
        self.rect.x += self.change
        self.rect.y += self.value
        self.hit_rect.center = self.rect.center
        if pg.time.get_ticks() - self.start > 1500:
            self.kill()


class Mob(pg.sprite.Sprite):
    def __init__(self, game, Type, x, y, w, h, roam_len):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.type = Type
        self.image_1 = game.mob_img[self.type][0].copy()
        self.image_1.set_colorkey(BLACK)
        self.image_1_right = pg.transform.flip(self.image_1, True, False)
        self.image_2 = game.mob_img[self.type][1].copy()
        self.image_2.set_colorkey(BLACK)
        self.image_2_right = pg.transform.flip(self.image_2, True, False)
        self.image_3 = pg.image.load(path.join(img_folder, MOB_DEAD[self.type])).convert_alpha()
        self.image_3.set_colorkey(BLACK)
        self.image = self.image_1
        self.rect = self.image.get_rect()
        self.hit_rect = pg.Rect(x, y, w, h)
        self.rect.midbottom = self.hit_rect.midbottom
        self.vx = -1 #randrange(1, 3)
        self.dist = 0
        self.dead = False
        self.last_shot = pg.time.get_ticks()
        self.health = 100
        self.interval = 1000
        self.roam_len = roam_len
        self.last_update = pg.time.get_ticks()
        self.img_l = [self.image_1, self.image_2]
        self.img_r = [self.image_1_right, self.image_2_right]
        self.current_frame = 0
        self.dir_wrt_player = 'right'
        
    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 5)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, WHITE, pg.Rect(0, 0, int(self.rect.width), 5))
            pg.draw.rect(self.image, col, self.health_bar)
                     
    def update(self):
        if self.dead == True:
            midbottom = self.rect.midbottom
            self.image = self.image_3
            self.rect = self.image.get_rect()
            self.rect.midbottom = midbottom
            self.hit_rect.center = self.rect.center
        else:
            self.now = pg.time.get_ticks()
            self.rect.x += self.vx
            self.dist += self.vx 
            if self.dist > self.roam_len/2 or self.dist < -self.roam_len/2:
                self.dist = 0
                self.vx *= -1
            midbottom = self.rect.midbottom
            if self.type == 'Mob_alien':
                if self.now - self.last_update > 180:
                    self.last_update = self.now
                    self.current_frame = (self.current_frame + 1) % len(self.img_l)
                    bottom = self.rect.bottom
                    if self.hit_rect.x > self.game.player.hit_rect.x:
                        self.dir_wrt_player = 'right'
                        self.image = self.img_l[self.current_frame]
                    else:
                        self.dir_wrt_player = 'left'
                        self.image = self.img_r[self.current_frame]
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = midbottom
                    self.hit_rect.midbottom = self.rect.midbottom
            else:
                if self.vx < 0:
                    self.image = self.image_1
                else:
                    self.image = self.image_2
                self.rect = self.image.get_rect()
                self.rect.midbottom = midbottom
                self.hit_rect.midbottom = self.rect.midbottom
            if self.type == 'Mob_alien':
                self.draw_health()
                now = pg.time.get_ticks()
                if now - self.last_shot > self.interval:
                    self.interval = randrange(1000,2000)
                    self.last_shot = now
                    Mob_bullet(self, self.game)
