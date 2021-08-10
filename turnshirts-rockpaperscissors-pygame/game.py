# (c) TurnShirts.com 2021
# - Totally Awesome T-Shirts with a twist
#
# Player selects Rock,Paper, Scissors Game to win t-shirts
# Timer counts down and goes down to 1 second - 10 levels
# Computer flips through shirts and selects on, player has to react.
# Each win adds a t-shirt to your basket (Adverts)
# http://www.penguintutor.com/projects/pygamezero-retropiepicade
# https://pygame-zero.readthedocs.io/en/stable/ide-mode.html
# https://stackoverflow.com/questions/30720665/countdown-timer-in-pygame
import pygame
import random

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_RETURN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
    JOYBUTTONDOWN,
    JOYBUTTONUP
)

states =     {
            'demo_mode': [
                    {'alert':           {'alerts': ['Press','To','Play'], 'position':0, 'reset_position': 0 }},
                    {'press_start':     {'reset_counter': 1, 'counter':1}},
                    {'computer_select': {'player_active': True, 'reset_counter': 8, 'counter':8}},
                    {'count_down:level0':      {'player_active': True, 'reset_counter': 4, 'counter':4 }},
                    {'advert':          {'reset_counter': 3, 'counter':3}},
                    {'wait':            {'reset_counter': 1, 'counter':1}},
                    {'reset':           {}}
                ],

            'play_mode': [
                    {'alert':               {'alerts': ['Rock?','Paper?','Scissors?','GO!'],'position':0, 'reset_position': 0 }},
                    {'computer_select':     {'player_active': True, 'reset_counter': 5, 'counter':5}},
                    {'count_down:level0':       {'player_active': True, 'reset_counter': 5, 'counter':5,'repeat':2, 'game_repeat':2}},
                    {'count_down:level1':       {'player_active': True, 'reset_counter': 3, 'counter':3,'repeat':3, 'game_repeat':3}},
                    {'count_down:level2':       {'player_active': True, 'reset_counter': 1, 'counter':1 }},
                    {'show_winner':         { 'reset_counter': 2, 'counter': 2 }},
                    {'wait':                { 'reset_counter': 3, 'counter':3}},
                    {'gameover':            {'text': ['GAME','OVER'],'position':0, 'reset_position': 0 }},
                    {'reset':               {}}
            ]
        }

states_lookup = {}
for x in states:
    states_lookup[x] = [list(i.keys())[0] for i in states[x]]

game_mode = 'demo_mode'
game_step = 0
score = 0
level = 0
wld = {'win' : 0, 'lose': 0, 'draw': 0 }

# Sprites
# GRINGO | MARACAS | GUARD
# GRINGO | MARACAS | GUARD
SQW = 200
SQH = 390
SPRITE = pygame.transform.smoothscale(pygame.image.load('mexicanwave-sprite-600x390-3x1.png'), (int(SQW*3), int(SQH*1)))
SPRITES = [None] * (3 * 1)
for x in range(3):
    for y in range(1):
        SPRITES[x+(y*1) + y] = pygame.Surface.subsurface(SPRITE, (x*SQW, y*SQH, SQW, SQH))
sprite_select = 0

# Define constants for the screen width and height
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
JOYSTICK_AXIS_LEFT_RIGHT = 0
JOYSTICK_AXIS_UP_DOWN = 1
DEMO_MODE = True
# Define a player object by extending pygame.sprite.Sprite
# The surface drawn on the screen is now an attribute of 'player'
class Spugg(pygame.sprite.Sprite):
    def __init__(self,identity,sprite,scale):
        super(Spugg, self).__init__()
        self.surf = SPRITES[sprite]
        if('scale' == scale):
            self.surf = pygame.transform.scale(self.surf, (100,195))
        self.identity = identity
        #self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

class Advert(pygame.sprite.Sprite):
    def __init__(self,image):
        super(Advert, self).__init__()
        img = pygame.image.load(image)
        img = pygame.transform.scale(img,(800,600))
        self.surf = img.convert()
        #self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
        )

class Logo(pygame.sprite.Sprite):
    def __init__(self,image):
        super(Logo, self).__init__()
        img = pygame.image.load(image)
        img = pygame.transform.scale(img,(165,62)) # 664,250
        self.surf = img.convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - SCREEN_HEIGHT/7))

class Selector(pygame.sprite.Sprite):
    def __init__(self):
        super(Selector, self).__init__()
        self.positions = [
                            {'position': (100,100),'key': 'rock','sprite': 0},
                            {'position': (100,300),'key': 'paper','sprite': 1},
                            {'position': (100,500),'key': 'scissors','sprite': 2}
                         ]
        self.current = 1
        self.width = 140
        self.height = 195
        self.border = 30
        self.surf = pygame.Surface((self.width, self.height))
        self.surf.fill((0, 0, 0))
        self.rect = self.surf.get_rect(
            center=self.positions[self.current]['position']
        )

        self.surfInner = pygame.Surface((self.width - self.border, self.height - self.border))
        self.surfInner.fill((255, 255, 255))
        self.rectInner = self.surfInner.get_rect(
            center=self.rect.center
        )
        self.speed = random.randint(5, 20)

    # Move the sprite based on speed
    # Remove the sprite when it passes the left edge of the screen
    def update(self):
        self.rect.move_ip(-self.speed, 0)
        if self.rect.right < 0:
            self.kill()

    def move(self, direction):
        self.current=self.current + direction
        if(self.current < 0 ):
            self.current = len(self.positions) - 1
        if(self.current >= len(self.positions)):
            self.current = 0
        self.rect.center = self.positions[self.current]['position']
        self.rectInner.center = self.rect.center

def reset(gmode, game_reset = False):
    for astep,gstep in enumerate(states[gmode]):
        for gvar in gstep:
            for option in gstep[gvar]:
                if ( "reset_" in option ):
                    reset_option = option.replace('reset_','')
                    states[gmode][astep][gvar][reset_option] = states[gmode][astep][gvar][option]
                if ( game_reset and "game_" in option ):
                    reset_option = option.replace('game_','')
                    states[gmode][astep][gvar][reset_option] = states[gmode][astep][gvar][option]

def resetAll():
    reset('demo_mode', True)
    reset('play_mode', True)
    wld = {'win' : 0, 'lose': 0, 'draw': 0 }

def show_winner():
    player  = spuggs[player_selection.current].identity
    computer = computer_spuggs[computer_select].identity
    aBEATSc = {'paper': 'rock','rock': 'scissors','scissors': 'paper'}
    if ( player == computer):
        return(0)
    else:
        if ( player in aBEATSc ):
            if ( aBEATSc[player] == computer ):
                return 1
            else:
                return -1
        else:
            return -1

pygame.init()
pygame.mixer.init() # add this line
pygame.joystick.init()
# Free Sounds: https://mixkit.co/free-sound-effects/game/

sound_on = True
click_sound = ''
lose_sound = ''
win_sound = ''
go_sound = ''

if sound_on:
    click_sound = pygame.mixer.Sound('click.wav')
    lose_sound = pygame.mixer.Sound('lose.wav')
    win_sound = pygame.mixer.Sound('treasure.wav')
    go_sound = pygame.mixer.Sound('win.wav')

# Initialize pygame

clock = pygame.time.Clock()
EVENT_COUNTDOWN = pygame.USEREVENT + 1
pygame.time.set_timer(EVENT_COUNTDOWN, 1000)
EVENT_COUNTDOWN_LEVEL_SKIP = pygame.USEREVENT + 2
pygame.time.set_timer(EVENT_COUNTDOWN_LEVEL_SKIP, 100)
EVENT_SWAP_SPUGG = pygame.USEREVENT + 3
pygame.time.set_timer(EVENT_SWAP_SPUGG, 100)
EVENT_PRESS_START = pygame.USEREVENT + 4
pygame.time.set_timer(EVENT_PRESS_START, 1000)
EVENT_ADVERT = pygame.USEREVENT + 5
pygame.time.set_timer(EVENT_ADVERT, 2000)
EVENT_WATCH = pygame.USEREVENT + 6
pygame.time.set_timer(EVENT_WATCH, 1000)
EVENT_JOYSTICK = pygame.USEREVENT + 7
pygame.time.set_timer(EVENT_JOYSTICK, 100)
# Create the screen object
# The size is determined by the constant SCREEN_WIDTH and SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Instantiate player. Right now, this is just a rectangle.
player_selection = Selector()
adverts = []
for advert_image in ['advert_rps_site.png','rps-offline.png']:
    adverts.append(Advert(advert_image))

advert_random = random.randint(0,len(adverts)-1)
#count_down = Selection()
spuggs = []
for item in player_selection.positions:
    spugg = Spugg(item['key'],item['sprite'],'scale')
    spugg.rect.center = item['position']
    spuggs.append(spugg)

computer_spuggs = []
for item in player_selection.positions:
    spugg = Spugg(item['key'],item['sprite'],'no-scale')
    spugg.rect.center = ( SCREEN_WIDTH - (SCREEN_WIDTH / 2), SCREEN_HEIGHT / 2 )
    computer_spuggs.append(spugg)

logo = Logo('logo.png')
# computer_rps = Player("paper.png")
# Variable to keep the main loop running
running = True

text = ''
for astep,step in enumerate(states[game_mode]):
    if ('count_down' in step):
        text = str(states[game_mode][astep]['count_down']['counter']).rjust(3)

font        = pygame.font.SysFont(None, 120)
win         = font.render('WIN', True, (0,0,0))
lose        = font.render('LOSE', True, (0,0,0))
fontLarge   = pygame.font.SysFont(None, 220)
fontSmall   = pygame.font.SysFont(None, 70)
go          = fontLarge.render('GO!', True, (0,0,0))
alert       = ''
gameover    = ''
lives_default = 3
lives       = 0
win_lose_draw = 0

fonts = pygame.font.get_fonts()
computer_select = random.randint(0,2)

joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

# Main loop
while running:
    step =  step_as_name = next(iter(states[game_mode][game_step]))
    # for loop through the event queue
    for event in pygame.event.get():
        # Check for KEYDOWN event
        if event.type == KEYDOWN:
            # If the Esc key is pressed, then exit the main loop
            if event.key == K_ESCAPE:
                running = False
            if event.key == K_RETURN:
                if(game_mode == 'demo_mode'):
                    game_mode = 'play_mode'
                    game_step = 0
                    lives = lives_default
                    level = 0
                    reset(game_mode)
            if event.key == K_UP and 'player_active' in states[game_mode][game_step][step]:
                player_selection.move(-1) and 'player_active' in states[game_mode]
                if sound_on:
                    pygame.mixer.Sound.play(click_sound)
            if event.key == K_DOWN and 'player_active' in states[game_mode][game_step][step]:
                player_selection.move(1)
                if sound_on:
                    pygame.mixer.Sound.play(click_sound)
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 3:
                if(game_mode == 'demo_mode'):
                    game_mode = 'play_mode'
                    game_step = 0
                    level = 0
                    lives = lives_default
                    reset(game_mode)
            if event.button == 4:
                running = False
            if event.button == 0 and 'player_active' in states[game_mode][game_step][step]:
                if sound_on:
                    pygame.mixer.Sound.play(click_sound)
                player_selection.move(-1) and 'player_active' in states[game_mode]
            if event.button == 1 and 'player_active' in states[game_mode][game_step][step]:
                if sound_on:
                    pygame.mixer.Sound.play(click_sound)
                player_selection.move(1) and 'player_active' in states[game_mode]
        if event.type == EVENT_COUNTDOWN_LEVEL_SKIP and 'count_down' in step_as_name:
            # Skip Level if not CURRENT LEVEL
            if step != 'count_down:level' + str(level):
                game_step += 1
        if event.type == EVENT_COUNTDOWN and 'count_down:level' + str(level) in states[game_mode][game_step]:
            states[game_mode][game_step]['count_down:level' + str(level)]['counter'] -= 1
            if states[game_mode][game_step]['count_down:level' + str(level)]['counter'] >= 0:
                text = str(states[game_mode][game_step]['count_down:level' + str(level)]['counter']).rjust(3)
            else:
                game_step += 1
        if event.type == EVENT_SWAP_SPUGG and 'computer_select' in states[game_mode][game_step]:
            computer_select = random.randint(0,2)
            states[game_mode][game_step]['computer_select']['counter'] -= 1
            if ( states[game_mode][game_step]['computer_select']['counter'] <= 0 ):
                game_step += 1
        if event.type == EVENT_PRESS_START and 'press_start' in states[game_mode][game_step]:
            #states[game_mode][game_step]['press_start']['counter'] = states[game_mode][game_step]['press_start']['counter_init']
            states[game_mode][game_step]['press_start']['counter'] -= 1
            if ( states[game_mode][game_step]['press_start']['counter'] <= 0 ):
                game_step += 1
        if event.type == EVENT_ADVERT and 'advert' in states[game_mode][game_step]:
            #states[game_mode][game_step]['press_start']['counter'] = states[game_mode][game_step]['press_start']['counter_init']
            states[game_mode][game_step]['advert']['counter'] -= 1
            advert_random = random.randint(0,len(adverts)-1)
            if ( states[game_mode][game_step]['advert']['counter'] <= 0 ):
                game_step += 1
        if event.type == EVENT_JOYSTICK and 'player_active' in states[game_mode][game_step][step]:
            joystick_count = pygame.joystick.get_count()
            for i in range(joystick_count):
                joystick = pygame.joystick.Joystick(i)
                #joystick.init()
                try:
                    jid = joystick.get_instance_id()
                except AttributeError:
                    # get_instance_id() is an SDL2 method
                    jid = joystick.get_id()

                axes = joystick.get_numaxes()
                for i in range(axes):
                 axis = joystick.get_axis(i)
                 if i == JOYSTICK_AXIS_UP_DOWN and axis < 0 : # UP
                     player_selection.move(-1)
                     if sound_on:
                         pygame.mixer.Sound.play(click_sound)
                 if i == JOYSTICK_AXIS_UP_DOWN and axis > 0: # DOWN
                     player_selection.move(1)
                     if sound_on:
                        pygame.mixer.Sound.play(click_sound)

                hats = joystick.get_numhats()
                for i in range(hats):
                    hat = joystick.get_hat(i)
        if event.type == EVENT_WATCH:
            if 'reset' in states[game_mode][game_step]:
                reset(game_mode)
                game_step = 0
            if 'wait' in states[game_mode][game_step]:
                states[game_mode][game_step]['wait']['counter'] -= 1
                if ( states[game_mode][game_step]['wait']['counter'] <= 0 ):
                    game_step += 1
            if 'alert' in states[game_mode][game_step]:
                sprite_select = random.randint(0,len(SPRITES) -1)

                if states[game_mode][game_step]['alert']['position'] > len(states[game_mode][game_step]['alert']['alerts'])-1:
                    pygame.mixer.Sound.play(go_sound)
                    game_step += 1
                else:
                    position = states[game_mode][game_step]['alert']['position']
                    alert = states[game_mode][game_step]['alert']['alerts'][position]
                    states[game_mode][game_step]['alert']['position'] += 1
            if 'gameover' in states[game_mode][game_step]:
                if lives > 0:
                    count_down_level_step = states_lookup['play_mode'].index('count_down:level' + str(level))
                    if 'repeat' in states[game_mode][count_down_level_step]['count_down:level' + str(level)]:
                        states[game_mode][count_down_level_step]['count_down:level' + str(level)]['repeat'] -= 1
                        if(states[game_mode][count_down_level_step]['count_down:level' + str(level)]['repeat'] == 0):
                            level += 1
                    game_step += 1
                else:
                    if states[game_mode][game_step]['gameover']['position'] > len(states[game_mode][game_step]['gameover']['text'])-1:
                        resetAll()
                        level = 0
                        game_step = 0
                        game_mode = "demo_mode"
                    else:
                        position = states[game_mode][game_step]['gameover']['position']
                        gameover = states[game_mode][game_step]['gameover']['text'][position]
                        states[game_mode][game_step]['gameover']['position'] += 1
        if 'show_winner' in states[game_mode][game_step]:
                win_lose_draw = show_winner()
                if ( win_lose_draw == 0 ):
                    wld['draw'] += 1
                elif ( win_lose_draw == 1 ):
                    wld['win'] += 1
                elif ( win_lose_draw == -1 ):
                    wld['lose'] += 1
                lives += win_lose_draw
                game_step += 1
                if ( win_lose_draw == 1 and sound_on):
                    pygame.mixer.Sound.play(win_sound)
                if ( win_lose_draw == -1 and sound_on):
                    pygame.mixer.Sound.play(lose_sound)

        if event.type == QUIT:
            running = False

    # Fill the screen with black
    screen.fill((255, 255, 255))

    if 'alert' in states[game_mode][game_step]:
        screen.blit(SPRITES[sprite_select],SPRITES[sprite_select].get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
        alert_text = fontLarge.render(alert, True, (0, 0, 0))
        alert_text_rect = alert_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(alert_text, alert_text_rect)
    elif 'gameover' in states[game_mode][game_step]:
        gameover_text = fontLarge.render(gameover, True, (0, 0, 0))
        gameover_text_rect = gameover_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(gameover_text, gameover_text_rect)
    else:
        # screen.blit(countdown, (340, 20))
        if ( win_lose_draw == 1 or win_lose_draw == 0):
            screen.blit(win, (500, 320))
        if ( win_lose_draw == -1 or win_lose_draw == 0):
            screen.blit(lose, (500, 420))
        #screen.blit(go, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(font.render(text, True, (0, 0, 0)), (340, 20))

        screen.blit(font.render(str(level), True, (0, 0, 0)), (340, 100))

        screen.blit(player_selection.surf,player_selection.rect)
        screen.blit(player_selection.surfInner,player_selection.rectInner)

        pos = 0
        for key in wld:
            pos += 60
            screen.blit(fontSmall.render(str(wld[key]) + ' ' + key, True, (0, 0, 0)), (540, 40+pos))

        for spugg in spuggs:
            screen.blit(spugg.surf,spugg.rect)

        screen.blit(computer_spuggs[computer_select].surf,computer_spuggs[computer_select].rect)

        if 'advert' in states[game_mode][game_step]:
            screen.blit(adverts[advert_random].surf,adverts[advert_random].rect)

    if game_mode == 'play_mode':
        screen.blit(fontSmall.render( "lives:" + str(lives).rjust(3), True, (0, 0, 0)), (540, 00))
        screen.blit(fontSmall.render( "level:" + str(level).rjust(3), True, (0, 0, 0)), (540, 40))

    pygame.display.flip()

pygame.quit()
