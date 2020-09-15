# Intro Music -> https://soundcloud.com/alexandr-zhelanov
# 'Happy Tune' -> http://opengameart.org/users/syncopika
# Game Over Music -> https://opengameart.org/users/kistol
# Art from Kenney.nl

import pygame as pg
import sys
from random import choice, random
from os import path
from settings import *
from sprites import *
from tilemap import *


# HUD functions
def draw_player_health(surf, x, y, pct, BAR_LENGTH, BAR_HEIGHT):
    if pct < 0:
        pct = 0
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 4, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.load_data()

    def draw_text(self, text, font_name, color, size, x, y, align="topleft"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(**{align: (x, y)})
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        self.music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')
        self.title_font = path.join(img_folder, 'Impacted2.0.ttf')
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))
        self.mob_img = {}
        for img_type in MOB_IMG:
            self.mob_img[img_type] = []
            for img in MOB_IMG[img_type]:
                self.mob_img[img_type].append(pg.image.load(path.join(img_folder, img)).convert_alpha())
                
        # lighting effect
        self.fog = pg.Surface((WIDTH, HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        # Sound loading
        self.level_snd = pg.mixer.Sound(path.join(snd_folder, LEVEL_SND))
        self.level_snd.set_volume(0.3)
        self.level_end_snd = pg.mixer.Sound(path.join(snd_folder, LEVEL_END_SND))
        self.alien_die_snd = pg.mixer.Sound(path.join(snd_folder, ALIEN_DIE_SND))
        self.player_die_snd = pg.mixer.Sound(path.join(snd_folder, PLAYER_DIE_SND))
        self.mob_die_snd = pg.mixer.Sound(path.join(snd_folder, MOB_DIE_SND))
        self.jump_snd = pg.mixer.Sound(path.join(snd_folder, JUMP_SND))
        self.shoot_snd = pg.mixer.Sound(path.join(snd_folder, SHOOT_SND))
        self.lives_snd = pg.mixer.Sound(path.join(snd_folder, Lives_snd))
        self.mouse_click = pg.mixer.Sound(path.join(snd_folder, CLICK_SND))
        
        

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.mob_bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.map = TiledMap(path.join(self.map_folder, 'level1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2,
                             tile_object.y + tile_object.height / 2)
            if tile_object.name == 'Level_complete':
                self.comp_rect = pg.Rect(tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'Player':
                self.player = Player(self, tile_object.x, tile_object.y,
                                     tile_object.width, tile_object.height)
            if tile_object.name == 'Ground':
                Platform(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in OBS_LIST:
                Obstacle(self, tile_object.x, tile_object.y,
                         tile_object.width, tile_object.height)
            if tile_object.name in MOB_LIST:
                Mob(self, tile_object.name, tile_object.x, tile_object.y,
                    tile_object.width, tile_object.height, int(tile_object.roam_len))
            if tile_object.name in ['Lives']:
                Item(self, tile_object.name, tile_object.x, tile_object.y,
                     tile_object.width, tile_object.height)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.check = 0
        pg.mixer.music.load(path.join(self.music_folder, BG_MUSIC))
        self.level_snd.play()

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.clock.tick(FPS) 
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):

        # Game Loop - Update
        self.all_sprites.update()

        # Free fall
        if self.player.pos.y > HEIGHT:
            self.playing = False
            self.player_die_snd.play()
            now = pg.time.get_ticks()
            while pg.time.get_ticks() - now < 1000:
                pass
            if self.player.score > self.player.highest_score:
                self.player.highest_score = self.player.score
                with open(path.join(self.player.dir, HS_FILE), 'w') as f:
                    f.write(str(self.player.score))
            show_go_screen(self.player.score, self.player.highest_score)

        # check if player hits a platform - only if falling
        if self.player.vel.y > 0 and self.player.dead == False:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False, collide_hit_rect)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.bottom :
                        self.player.vel.y = 0
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.jumping = False

        # check if player hits an obstacle
        obs_hits = pg.sprite.spritecollide(self.player, self.obstacles, False, collide_hit_rect)
        if obs_hits:
            self.player.dead = True
            
        # check if player hits an item
        if self.player.vel.y > 0 and self.player.dead == False:
            i_hits = pg.sprite.spritecollide(self.player, self.items, False, collide_hit_rect)
            if i_hits:
                self.check += 1
                self.player.vel.y = 0
                self.player.pos.y = i_hits[0].hit_rect.top + 1
                self.player.jumping = False
                if self.check == 1:
                    i_hits[0].image =  i_hits[0].img2
                    self.player.health += 40
                    self.lives_snd.play()
                    if self.player.health > 100:
                        self.player.health = 100

        # check if bullet hits mob
        b_hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, False)
        for hit in b_hits:
            if not hit.dead:
                for bullet in b_hits[hit]:
                    bullet.kill()
                if not hit.type == 'Mob_alien':                
                    if not hit.dead:
                        self.player.score += 10
                        self.mob_die_snd.play()
                    hit.dead = True
                else:
                    if not hit.dead:
                        hit.health -= 10
                        self.alien_die_snd.play()
                    if hit.health <= 0:
                        hit.health = 0
                        if not hit.dead:
                            self.player.score += 100
                            self.mob_die_snd.play()
                        hit.dead = True

        # check if mob bullet hits the player
        p_hits = pg.sprite.spritecollide(self.player, self.mob_bullets, True,  collide_hit_rect)
        for hit in p_hits:
            self.player.health -= 5
            if self.player.health <= 0:
                self.player.health = 0
                self.player.dead = True
                    
        # hit mobs?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in mob_hits:
            if self.player.vel.y > 0:
                if hit.hit_rect.top <= self.player.hit_rect.bottom <= hit.hit_rect.bottom - 3 :
                    if (hit.hit_rect.left <= self.player.hit_rect.right <= hit.hit_rect.right or \
                                hit.hit_rect.left <= self.player.hit_rect.left <= hit.hit_rect.right or \
                                self.player.hit_rect.left <= hit.hit_rect.left <=  hit.hit_rect.right <= self.player.hit_rect.right) \
                                and hit.dead == False :
                        if not hit.type == 'Mob_alien':
                            hit.dead = True
                            self.player.score += 10
                            self.mob_die_snd.play()
                        else:
                            self.player.dead = True
            if hit.hit_rect.left <= self.player.hit_rect.right <= hit.hit_rect.right or \
                        hit.hit_rect.left <= self.player.hit_rect.left <= hit.hit_rect.right :
                if not self.player.hit_rect.bottom < hit.hit_rect.bottom - 3 and hit.dead == False:                    
                    self.player.dead = True

        # if player reaches top 1/4 of screen
        if self.player.rect.centerx >= WIDTH / 2 and self.map_rect.right > WIDTH:
            self.comp_rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
            self.map_rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
            for sprite in self.mobs:
                sprite.rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
                sprite.hit_rect.midbottom = sprite.rect.midbottom
                #sprite.hit_rect.x -= (self.player.vel.x + .5*self.player.acc.x)
            for sprite in self.platforms:
                sprite.rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
                #sprite.hit_rect.x -= (self.player.vel.x + .5*self.player.acc.x)
            for sprite in self.items:
                sprite.rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
                #sprite.hit_rect.x -= (self.player.vel.x + .5*self.player.acc.x)
            for sprite in self.obstacles:
                sprite.rect.x -= int(self.player.vel.x + .5*self.player.acc.x)
                #sprite.hit_rect.x -= (self.player.vel.x + .5*self.player.acc.x)
            self.player.pos.x -= (self.player.vel.x + .5*self.player.acc.x)

        # Level complete
        if self.comp_rect.left <= self.player.hit_rect.right <= self.comp_rect.right or\
               self.player.hit_rect.left <= self.comp_rect.left <= self.comp_rect.right <= self.player.hit_rect.right:
            if self.player.hit_rect.bottom >= self.comp_rect.bottom:
                self.player.pos.y = self.comp_rect.bottom + 2
                self.player.rect.midbottom = self.player.pos
                self.player.hit_rect.midbottom = self.player.pos
                self.all_sprites.update()
                self.draw()
                pg.display.flip()
                now = pg.time.get_ticks()
                i = 0
                while pg.time.get_ticks() - now < 3000:
                    i += 1
                    if i <= 2:
                        self.level_end_snd.play()
                    self.draw_text("LEVEL COMPLETE", self.title_font, RED, 105, WIDTH / 2, HEIGHT / 2, align="center")
                    pg.display.flip()
                    self.clock.tick(1)
                self.playing = False
                if self.player.score > self.player.highest_score:
                    self.player.highest_score = self.player.score
                    with open(path.join(self.player.dir, HS_FILE), 'w') as f:
                        f.write(str(self.player.score))
##                game_intro(self.player.highest_score)
                you_won(self.player.score, self.player.highest_score)

    def render_fog(self):
        # draw the light mask (gradient) onto fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.player.hit_rect.center 
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0,0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.map_rect)
        self.all_sprites.draw(self.screen)
        for sprite in self.platforms:
##            if isinstance(sprite, Mob):
##                sprite.draw_health()
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, sprite.hit_rect, 1)
        for sprite in self.all_sprites:
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, sprite.hit_rect, 1)
        for sprite in self.obstacles:
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, sprite.hit_rect, 1)
        for sprite in self.items:
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, sprite.hit_rect, 1)
        if self.draw_debug:
            pg.draw.rect(self.screen, CYAN, self.comp_rect, 1)
        if self.night:
            self.render_fog()            
        # HUD functions
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH, 100, 20)
        self.draw_text("Score - " + str(self.player.score), self.title_font, GREEN, 40, WIDTH / 2, 30, align="center")
        if self.paused:
            pause(self.player.highest_score)                           
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.paused = not self.paused
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_DOWN:
                    self.player.hit_rect = pg.Rect(0,0,self.player.width,self.player.height)
                    self.player.hit_rect.midbottom = self.player.pos

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False


ratio = int(1024/480)
ratio1 = int(700/600)

def button(highest_score, text, x, y, width, height, inactive_color, active_color, action = None):

    screen = g.screen
    clock = g.clock
    active = 0
    cur = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()
    if x + width > cur[0] > x and y + height > cur[1] > y:
        outline_rect = pg.Rect(x, y, width, height)
        fill_rect = pg.Rect(x, y, width, height)
        pg.draw.rect(screen, active_color, fill_rect)
        pg.draw.rect(screen, WHITE, outline_rect, 2)
        if click[0] == 1 and action != None:
            g.mouse_click.play()
            if action == "quit":
                g.draw_text(text, g.title_font, WHITE, 30, x+int(width/2), y+int(height/2)-3, align="center")
                active = 1
                Exit()

            if action == "controls":
                active = 1
                game_controls(highest_score)

            if action == "play":
                active = 1

            if action == "back":
                active = 1

            if action == "resume":
                active = 1

            if action == "restart":
                active = 1

            if action == "main":
                active = 1
                
    else:
        outline_rect = pg.Rect(x, y, width, height)
        fill_rect = pg.Rect(x, y, width, height)
        pg.draw.rect(screen, inactive_color, fill_rect)
        pg.draw.rect(screen, WHITE, outline_rect, 2)

    g.draw_text(text, g.title_font, WHITE, 30, x+int(width/2), y+int(height/2)-3, align="center")
    return active


def game_controls(highest_score):

    screen = g.screen
    clock = g.clock
    gcont = True

    screen.fill(BLACK)
    cont_img = pg.image.load(path.join(img_folder, CONTROLS_IMG)).convert_alpha()
    cont_img.set_colorkey(BLACK)
    screen.blit(cont_img, (0,0))
    g.draw_text("CONTROLS", g.title_font, WHITE, 70, int(WIDTH / 2), int(HEIGHT * .2), align="center")
    g.draw_text("JUMP - SPACEBAR", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .42), align="center")
    g.draw_text("MOVE PLAYER - LEFT AND RIGHT ARROWS", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .5), align="center")
    g.draw_text("PAUSE - ESC", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .66), align="center")
    g.draw_text("SHOOT - NUM0", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .58), align="center")
    g.draw_text("DUCK - DOWN ARROW", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .74), align="center")
    g.draw_text("NIGHT MODE - N", g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .82), align="center")
    g.draw_text("HIGHEST SCORE - "+str(highest_score), g.title_font, WHITE, 35, WIDTH / 2, int(HEIGHT * .9), align="center")

    while gcont:
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()        

        back_select = button(highest_score, "Back", 25,25,100,50, RED, LIGHT_RED, action="back")

        if back_select == 1:
            gcont = False

        pg.display.flip()

        clock.tick(FPS)


def Exit():

    screen = g.screen
    clock = g.clock
    exit_game = True
    
    while exit_game:
        
        cur = pg.mouse.get_pos()
        click = pg.mouse.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
                
        pg.draw.rect(screen, WHITE, (37*ratio, 247*ratio1, 400*ratio + 6, 100*ratio1 + 6))
        
        if 37*ratio + 2 + 200*ratio > cur[0] > 37*ratio + 2 and 297*ratio1 + 4 +50*ratio1 > cur[1] > 297*ratio1 + 4:
            pg.draw.rect(screen, LIGHT_RED, (37*ratio + 2, 297*ratio1 + 4, 200*ratio, 50*ratio1))
            pg.draw.rect(screen, RED, (237*ratio + 4, 297*ratio1 + 4, 200*ratio, 50*ratio1))
            if click[0] == 1:
                g.mouse_click.play()
                exit_game = False
                pg.quit()
                sys.exit()
        elif 237*ratio + 4 + 200*ratio > cur[0] > 237*ratio + 4 and  297*ratio1 + 4 + 50*ratio1 > cur[1] >  297*ratio1 + 4:
            pg.draw.rect(screen, RED, (37*ratio + 2, 297*ratio1 + 4, 200*ratio, 50*ratio1))
            pg.draw.rect(screen, LIGHT_RED, (237*ratio + 4, 297*ratio1 + 4, 200*ratio, 50*ratio1))
            if click[0] == 1:
                g.mouse_click.play()
                exit_game = False
        else:
            pg.draw.rect(screen, RED, (37*ratio + 2, 297*ratio1 + 4, 200*ratio, 50*ratio1))
            pg.draw.rect(screen, RED, (237*ratio + 4, 297*ratio1 + 4, 200*ratio, 50*ratio1))
        
        pg.draw.rect(screen, RED, (37*ratio + 2, 247*ratio1 + 2, 400*ratio + 2, 50*ratio1))
        g.draw_text("Are you sure you want to exit ?", g.title_font, WHITE, 25, int(37*ratio + 2 + ((400*ratio + 2)/2)), int(247*ratio1 + 2 + (50*ratio1/2)), align="center")
        g.draw_text("Yes", g.title_font, WHITE, 25, int(37*ratio + 2+(200*ratio/2)), int(297*ratio1 + 4 +(50*ratio1/2)), align="center")
        g.draw_text("No", g.title_font, WHITE, 25, int(237*ratio + 4 + (200*ratio/2)), int(297*ratio1 + 4 +(50*ratio1/2)), align="center")

        pg.display.flip()

        clock.tick(FPS)


def game_intro(highest_score):

    pg.mixer.music.load(path.join(g.music_folder, INTRO_MUSIC))
    pg.mixer.music.play(loops=-1)
    screen = g.screen
    clock = g.clock
    intro = True
    intro_img = pg.image.load(path.join(img_folder, INTRO_IMG)).convert_alpha()
    intro_img.set_colorkey(BLACK)
    
    while intro:

        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

        screen.fill(BLACK)
        screen.blit(intro_img, (0,0))
        
        g.draw_text("Welcome to platformer !", g.title_font, WHITE, 60, int(WIDTH / 2), int(HEIGHT * .2), align="center")
        g.draw_text("The objective is to shoot or kick on top of the enemies", g.title_font, WHITE, 30, WIDTH / 2, int(HEIGHT * .45), align="center")
        g.draw_text("and avoid any sort of other contact with", g.title_font, WHITE, 30, WIDTH / 2, int(HEIGHT * .5), align="center")
        g.draw_text("the enemies and the obstacles.", g.title_font, WHITE, 30, WIDTH / 2, int(HEIGHT * .55), align="center")

        play_select = button(highest_score, "Play", 190*ratio,int(HEIGHT * .7),100*ratio,50*ratio1, RED, LIGHT_RED, action ="play")
        controls_select = button(highest_score, "Controls", 90*ratio,int(HEIGHT * .85),100*ratio,50*ratio1, RED, LIGHT_RED, action="controls")
        quit_select = button(highest_score, "Quit", 290*ratio,int(HEIGHT * .85),100*ratio,50*ratio1, RED, LIGHT_RED, action="quit")

        if play_select == 1:
            g.level_snd.set_volume(0.3)
            g.new()
            g.run()
            intro = False

        pg.display.flip()

        clock.tick(FPS)


def pause(highest_score):

    screen = g.screen
    clock = g.clock
    paused = True
    pg.image.save(screen,"screenshot_game.jpg")
    screen.blit(g.dim_screen, (0, 0))
    
    while paused:
        for event in pg.event.get():    
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    g.paused = False
                    paused = False
       
        g.draw_text("Paused", g.title_font, RED, 70, int(WIDTH / 2), int(HEIGHT * .2), align="center")

        resume_select = button(highest_score, "Resume", 90*ratio,int(HEIGHT * .5),100*ratio,50*ratio1, RED, LIGHT_RED, action="resume")
        restart_select = button(highest_score, "Restart", 290*ratio,int(HEIGHT * .5),100*ratio,50*ratio1, RED, LIGHT_RED, action="restart")
        controls_select = button(highest_score, "Controls", 90*ratio,int(HEIGHT * .7),100*ratio,50*ratio1, RED, LIGHT_RED, action="controls")
        main_select = button(highest_score, "Main", 290*ratio,int(HEIGHT * .7),100*ratio,50*ratio1, RED, LIGHT_RED, action="main")
        
        if resume_select == 1 or restart_select == 1 or main_select == 1:
            g.paused = False
            paused = False
        if restart_select == 1:
            g.new()
            g.run()
        if main_select == 1:
            game_intro(highest_score)
        if controls_select == 1:
            img = pg.image.load("screenshot_game.jpg").convert_alpha()
            screen.blit(img, (0, 0))
            screen.blit(g.dim_screen, (0, 0))

        pg.display.flip()
        clock.tick(FPS)        
    
        
def show_go_screen(score, highest_score):

    pg.mixer.music.load(path.join(g.music_folder, GO_MUSIC))
    pg.mixer.music.play(loops=-1)
    screen = g.screen
    clock = g.clock
    game_over = True
    go_img = pg.image.load(path.join(img_folder, GO_IMG)).convert_alpha()
    go_img.set_colorkey(BLACK)
    
    while game_over:
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

        screen.fill(BLACK)
        screen.blit(go_img, (0,0))
        g.draw_text("Game Over!", g.title_font, WHITE, 65, int(WIDTH / 2), int(HEIGHT * .15), align="center")
        g.draw_text("Your Score - "+str(score), g.title_font, WHITE, 50, WIDTH / 2, int(HEIGHT * .4), align="center")
        g.draw_text("Highest Score - "+str(highest_score), g.title_font, WHITE, 50, WIDTH / 2, int(HEIGHT * .5), align="center")

        play_select = button(highest_score, "Play Again", 60*ratio,int(HEIGHT * .7),150*ratio,50*ratio1, RED, LIGHT_RED, action="play")
        controls_select = button(highest_score, "Controls", 270*ratio,int(HEIGHT * .7),150*ratio,50*ratio1, RED, LIGHT_RED, action="controls")
        quit_select = button(highest_score, "Quit", 190*ratio,int(HEIGHT * .85),100*ratio,50*ratio1, RED, LIGHT_RED, action ="quit")

        if play_select == 1:
            game_over = False
            g.new()
            g.run()

        pg.display.flip()

        clock.tick(FPS)


def you_won(score, highest_score):

    pg.mixer.music.load(path.join(g.music_folder, GO_MUSIC))
    pg.mixer.music.play(loops=-1)
    screen = g.screen
    clock = g.clock
    game_over = True
    go_img = pg.image.load(path.join(img_folder, GO_IMG)).convert_alpha()
    go_img.set_colorkey(BLACK)
    
    while game_over:
        for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

        screen.fill(BLACK)
        screen.blit(go_img, (0,0))
        g.draw_text("You Won!", g.title_font, WHITE, 65, int(WIDTH / 2), int(HEIGHT * .15), align="center")
        g.draw_text("Your Score - "+str(score), g.title_font, WHITE, 50, WIDTH / 2, int(HEIGHT * .4), align="center")
        g.draw_text("Highest Score - "+str(highest_score), g.title_font, WHITE, 50, WIDTH / 2, int(HEIGHT * .5), align="center")

        play_select = button(highest_score, "Play Again", 60*ratio,int(HEIGHT * .7),150*ratio,50*ratio1, RED, LIGHT_RED, action="play")
        controls_select = button(highest_score, "Controls", 270*ratio,int(HEIGHT * .7),150*ratio,50*ratio1, RED, LIGHT_RED, action="controls")
        quit_select = button(highest_score, "Quit", 190*ratio,int(HEIGHT * .85),100*ratio,50*ratio1, RED, LIGHT_RED, action ="quit")

        if play_select == 1:
            game_over = False
            g.new()
            g.run()

        pg.display.flip()

        clock.tick(FPS)

        
# create the game object
g = Game()
g.level_snd.set_volume(0)
g.new()
game_intro(g.player.highest_score)
