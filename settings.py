# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)
LIGHT_RED = (237,18,29) #(237,22,33)#(238,38,48)#(239,50,60)#(255,26,26)

# Layers
PLAYER_LAYER = 3
BULLET_LAYER = 3
MOB_LAYER = 2

# game settings
WIDTH = 1024   
HEIGHT = 700  
FPS = 60
TITLE = "PLATFORMER"
BGCOLOR = BROWN

TILESIZE = 70
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player settings
PLAYER_HEALTH = 100
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = .61 #0.8
PLAYER_JUMP = 17 #20


# Mob settings
MOB_HEALTH = 100
MOB_LIST = ['Mob_snail', 'Mob_slime', 'Mob_fly', 'Mob_alien']
MOB_IMG = {'Mob_snail': ['snailWalk1.png', 'snailWalk2.png'],
           'Mob_slime': ['slimeWalk1.png', 'slimeWalk2.png'],
           'Mob_fly': ['flyFly1.png', 'flyFly2.png'],
           'Mob_alien': ['e_walk_1.png', 'e_walk_2.png']}
MOB_DEAD = {'Mob_snail': 'snailDead.png',
            'Mob_slime': 'slimeDead.png',
            'Mob_fly': 'flyDead.png',
            'Mob_alien': 'eDead.png'}

# Obstacles settings
OBS_LIST = ['Obstacles_cactus', 'Obstacles_spike']

# Weapon settings
BULLET_IMG = 'bullet.png'
MOB_BULLET_IMG = 'fireball.png'

# Effects
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_soft.png"

# Powerups
lives1_img = 'lives1.png'
lives2_img = 'lives2.png'

# sound
LEVEL_SND = 'level_start.wav'
LEVEL_END_SND = 'level_comp.wav'
ALIEN_DIE_SND = 'alien_die.wav'
PLAYER_DIE_SND = 'go.wav'
MOB_DIE_SND = 'kill_mob.wav'
JUMP_SND = 'jump.wav'
SHOOT_SND = 'shoot.wav'
Lives_snd = 'Powerup.wav'
CLICK_SND = 'mouse_click.aif'

# music
GO_MUSIC = 'Game Over.ogg'
INTRO_MUSIC = 'Intro.ogg'
BG_MUSIC = 'Happy Tune.ogg'

# File
HS_FILE = 'highscore.txt'

# images
INTRO_IMG = 'intro.jpg'
CONTROLS_IMG = 'controls.jpg'
GO_IMG = 'go.jpg'
