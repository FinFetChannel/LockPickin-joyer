import pygame as pg
import math #numpy as np
import random
from datetime import timedelta
import asyncio

async def main():
    pg.event.set_grab(1)
    font = pg.font.SysFont("Courier New", 50, 1)
    screen = pg.display.set_mode((800, 600))
    cover = pg.image.load('assets/cover.jpg').convert()
    helper = pg.image.load('assets/help.jpg').convert()
    door = pg.image.load('assets/door.png').convert_alpha()
    core = pg.image.load('assets/lock.png').convert_alpha()
    lock_cover = pg.Surface.subsurface(core, (0,0, 103, 206))
    pick = pg.image.load('assets/pick.png').convert_alpha()
    tensioner = pg.image.load('assets/tensioner.png').convert_alpha()
    meter = pg.image.load('assets/meter.png').convert_alpha()
    buffer = pg.surface.Surface(screen.get_size())
    clock = pg.time.Clock()
    pg.mouse.set_visible(0)
    sounds = load_sounds()

    running = 1
    side2side = [0, 0]
    audio_delay = 0
    tension = 0
    binding_msg = 1
    mouse_vertical = 400
    times = Highscores()#[40.001, 60.001, 80.001, 100.001]

    lock3 = Buttons([20, 200], ' 3 Pins ', font, [255, 230, 63])
    lock4 = Buttons([20, 280], ' 4 Pins ', font, [255, 180, 83])
    lock5 = Buttons([20, 360], ' 5 Pins ', font, [255, 130, 103])
    lock6 = Buttons([20, 440], ' 6 Pins ', font, [255, 80, 123])
    exit = Buttons([20, 520], ' Exit ', font, [255, 52, 63])
    restart = Buttons([20, 280], ' Restart ', font, [255, 152, 63])
    again = Buttons([20, 440], ' Try Again ', font, [255, 152, 63])
    select = Buttons([20, 360], ' Select Screen ', font, [255, 152, 63])
    help = Buttons([20, 440], ' Help ', font, [255, 152, 63])
    go_on = Buttons([20, 200], ' Continue ', font, [255, 152, 63])

    pause = 1
    new_game = 1
    timer = 0

    sounds['intro'].play()
    buffer.blit(cover, (0,0))
    await splash_screen('', buffer, clock, font, screen, delay=480)
    sounds['intro'].stop()
    blank = pg.surface.Surface((800, 600), pg.SRCALPHA)

    while running:

        elapsed_time = clock.tick()*0.001
        current_time = pg.time.get_ticks()

        surf = blank.copy()
        rotated_pick = blank.copy()

        for event in pg.event.get():
            if event.type == pg.QUIT: running = 0
            if not new_game:
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: pause = not(pause)

        clicked = pg.mouse.get_pressed()[0]

        if pause:
            p_mouse = list(pg.mouse.get_pos())
            screen.blit(buffer, (0,0))
            # title.render(screen, [30,30], 1)

            if exit.render(screen, p_mouse, clicked):
                running = 0

            if new_game:

                time_y = 120
                screen.blit(font.render('Best time:', 1, (255, 255, 255)), (500, time_y))
                for time in times.times:
                    time_y += 80
                    time_str = str(timedelta(seconds=time))
                    screen.blit(font.render(time_str[2:-4], 1, (255, 255, 255)), (525, time_y))

                number_of_pins = 0

                if lock3.render(screen, p_mouse, clicked):
                    number_of_pins = 3
                elif lock4.render(screen, p_mouse, clicked):
                    number_of_pins = 4
                elif lock5.render(screen, p_mouse, clicked):
                    number_of_pins = 5
                elif lock6.render(screen, p_mouse, clicked):
                    number_of_pins = 6

                if number_of_pins > 0:
                    lock = Lock(number_of_pins)

                    sounds['tension'].play()
                    buffer.fill(lock.color)
                    buffer.blit(door, (0,0))
                    background = buffer.copy()
                    buffer.blit(core, (297,197))
                    await splash_screen('', buffer, clock, font, screen, delay=160)
                    buffer.blit(tensioner, (395,10))
                    await splash_screen('w tension, mouse to pick', buffer, clock, font, screen, delay=240)
                    sounds['tension'].stop()
                    background.blit(meter, (0,0))

                    pause = 0
                    new_game = 0
                    timer = 0
                    binding_msg = 1
            
            else:
                if select.render(screen, p_mouse, clicked):
                    new_game = 1
                    buffer.blit(cover, (0,0))
                    pg.time.wait(200)
                
                if lock.open:
                    time_str = str(timedelta(seconds=timer))
                    screen.blit(font.render(str(lock.number_of_pins) + " Pins open in " + time_str[2:-4], 1, (255, 255, 255)), (50, 100))
                    if again.render(screen, p_mouse, clicked):
                        sounds['fluke'].play()
                        audio_delay = current_time + 3500#1000*sounds['fluke'].get_length()
                        lock.reset()
                        pause = 0
                        timer = 0
                        binding_msg = 1
                else:
                    if help.render(screen, p_mouse, clicked):
                        await splash_screen('', helper, clock, font, screen)
                    
                    if go_on.render(screen, p_mouse, clicked):
                        pause = 0

                    if restart.render(screen, p_mouse, clicked):
                        lock.reset()
                        pause = 0
                        timer = 0
                        binding_msg = 1

            pg.draw.polygon(screen, (200, 50, 50), ((p_mouse), (p_mouse[0]+20, p_mouse[1]+22), (p_mouse[0], p_mouse[1]+30)))

        else:
            pressed_keys = pg.key.get_pressed()
            if lock.lock_angle > 5 and lock.lock_angle < 89.9:
                lock.lock_angle += lock.lock_angle*elapsed_time
                if current_time > audio_delay and lock.lock_angle < 50:
                    sounds['turning'].play()
                    audio_delay = current_time + 2000#1000*sounds['turning'].get_length()
            elif lock.lock_angle > 89.9 and not lock.open:
                lock.open = 1
                sounds['turning'].stop()
                sounds['open'].play()
                pg.time.wait(2000)#int(1000*sounds['open'].get_length()))
                tension = 0
                pause = 1
                if times.times[lock.number_of_pins - 3] > timer:
                    times.times[lock.number_of_pins - 3] = timer
                    times.save()
                    
            if pressed_keys[ord('w')]: tension += random.uniform(0.2, 0.8 + tension)*elapsed_time

            if tension > 0.3 and lock.lock_angle < 5:    
                lock.lock_angle += elapsed_time*10
                lock.lock_angle = min(max(lock.lock_angle, 0), lock.angles[lock.binding_pin])
                tension -= 0.1*elapsed_time
            tension -= elapsed_time*(0.05 + tension/5)
            tension = min(max(tension, 0), 1)

            if not lock.open:
                timer += elapsed_time

            p_mouse[0] = min(max(pg.mouse.get_pos()[0], 300), 500)
            p_mouse[1] = min(max(pg.mouse.get_pos()[1], 300), 500)

            if not clicked:
                mouse_vertical = p_mouse[1]
                side2side = [0,0]

            elif p_mouse[1] < 400 and lock.lock_angle > lock.angles[lock.binding_pin] - 0.01:
                p_mouse[1] = mouse_vertical
                current_pin = int(lock.number_of_pins - (p_mouse[1] - 280)/(80/(lock.number_of_pins+1)) + .99)

                if current_pin in lock.set_pins and current_time > audio_delay:
                    sounds['set'][current_pin].play()
                    audio_delay = current_time + 2000#1000*sounds['set'][current_pin].get_length()

                elif current_pin == lock.binding_order[lock.binding_pin] and tension > 0.3:

                    if tension > 0.7:
                        if current_time > audio_delay:
                            sounds['strongly'].play()
                            audio_delay = current_time + 1700#1000*sounds['strongly'].get_length()
                    
                    elif abs((p_mouse[0]-300)/200 - lock.key[current_pin]) < 0.01:
                        if audio_delay > current_time:
                            pg.time.wait(min(1000, int(audio_delay - current_time)))
                            elapsed_time = clock.tick(60)*0.001
                        if random.uniform(0,1) > 0.5:
                            sounds['clicking1'].play()
                        else:
                            sounds['clicking2'].play()
                        lock.set_pins.append(current_pin)
                        lock.binding_pin += 1
                        binding_msg = 1
                        sounds['click'][current_pin].play()
                        audio_delay = pg.time.get_ticks() + 2000#1000*sounds['click'][current_pin].get_length()
                    
                    elif binding_msg and current_time > audio_delay:
                        sounds['binding'][current_pin].play()
                        audio_delay = current_time + 2000#1000*sounds['binding'][current_pin].get_length()
                        binding_msg = 0

                elif current_pin > -1 and tension > 0.3:
                    if (p_mouse[0]-300)/200 > 0.99:
                        side2side[0] = 1
                    elif (p_mouse[0]-300)/800 < 0.01:
                        side2side[1] = 1
                    if side2side[0] and side2side[1]:
                        side2side = [0,0]
                        if current_time > audio_delay:
                            sounds['nothing'][current_pin].play()
                            audio_delay = current_time + 2000 #1000*sounds['nothing'][current_pin].get_length()
                else:
                    if current_time > audio_delay:
                        sounds['nopin'].play()
                        audio_delay = current_time + 1000

                pg.display.set_caption(str(current_pin) + ' ' + str(clock.get_fps()))
            else:        
                p_mouse[1] = mouse_vertical

            pg.mouse.set_pos(p_mouse)
            
            pickx = (max(200, min(500, p_mouse[1])) - 300)  
            rotated_pick.blit(pick, (302+pickx, 250+pickx))
            rotated_pick, rect = rot_center(rotated_pick, -(p_mouse[0]-400)/20, 400, 300)
            
            surf.blit(core, (297,197))
            surf.blit(rotated_pick, rect)
            surf.blit(lock_cover, (297,197))
            surf.blit(tensioner, (395,10))
            surf, rect = rot_center(surf, -lock.lock_angle, 400, 300)

            # buffer.fill(lock.color)
            # buffer.blit(door, (0,0))
            buffer = background.copy()
            buffer.blit(surf, rect)
            # buffer.blit(meter, (0,0))
            pg.draw.rect(buffer, [255, 255, 255], [0, 550 - tension*500, 50, 10])
            screen.blit(buffer, (0,0))
            
            time_str = str(timedelta(seconds=timer))
            screen.blit(font.render(time_str[2:-4], 1, (255, 255, 255)), (525, 100))

        pg.display.update()
        await asyncio.sleep(0)  # very important, and keep it 0
        if not running:
            pg.quit()
            return

class Lock():
    def __init__(self, number_of_pins):
        self.number_of_pins = number_of_pins    
        self.pin_positions = []
        self.binding_order = []
        self.angles = [random.uniform(0.5,1)]
        self.key = []
        self.color = [255, 230 - (number_of_pins-2)*50, 63 + 60*(number_of_pins-3)]
        for pin in range(number_of_pins):
            self.pin_positions.append(0)
            self.key.append(random.uniform(0.1,0.9))
            if pin < number_of_pins - 1:
                self.angles.append(self.angles[-1]+random.uniform(0.2, 0.6))
            else:
                self.angles.append(90)
            binding = random.randint(0, number_of_pins-1)
            while binding in self.binding_order:
                binding = random.randint(0, number_of_pins-1)
            self.binding_order.append(binding)

        self.binding_pin = 0
        self.open = 0
        self.set_pins = []
        self.lock_angle = 0
    
    def reset(self):
        self.binding_pin = 0
        self.open = 0
        self.set_pins = []
        self.lock_angle = 0

def rot_center(image, angle, x, y):   
    rotated_image = pg.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)

    return rotated_image, new_rect

def load_sounds():
    sounds = {}
    sounds['intro'] = pg.mixer.Sound('assets/sounds/intro.mp3')
    sounds['tension'] = pg.mixer.Sound('assets/sounds/tension.mp3')
    sounds['open'] = pg.mixer.Sound('assets/sounds/open.mp3')
    sounds['fluke'] = pg.mixer.Sound('assets/sounds/fluke.mp3')
    sounds['clicking1'] = pg.mixer.Sound('assets/sounds/clicking1.mp3')
    sounds['clicking2'] = pg.mixer.Sound('assets/sounds/clicking2.mp3')
    sounds['turning'] = pg.mixer.Sound('assets/sounds/turning.mp3')
    sounds['strongly'] = pg.mixer.Sound('assets/sounds/strongly.mp3')
    sounds['nopin'] = pg.mixer.Sound('assets/sounds/nopin.mp3')
    sounds['nothing'] = []
    sounds['binding'] = []
    sounds['click'] = []
    sounds['set'] = []
    for i in range(6):
        sounds['nothing'].append(pg.mixer.Sound('assets/sounds/nothing'+str(i+1)+'.mp3'))
        sounds['binding'].append(pg.mixer.Sound('assets/sounds/binding'+str(i+1)+'.mp3'))
        sounds['click'].append(pg.mixer.Sound('assets/sounds/click'+str(i+1)+'.mp3'))
        sounds['set'].append(pg.mixer.Sound('assets/sounds/set'+str(i+1)+'.mp3'))

    return sounds

class Buttons():
    def __init__(self, pos, text, font, color=[255, 212, 63]):
        self.pos = pos
        self.size = font.size(text)
        self.rect = pg.rect.Rect(pos[0]-5, pos[1]-5, self.size[0]+10, self.size[1]+10)
        self.text = font.render(text, 1, [5, 43, 126])
        pg.draw.rect(self.text, color, [0, 0, self.size[0], self.size[1]], border_radius=7)
        self.text.blit(font.render(text, 1, [5, 43, 126]), [0,0])

    def render(self, surf, p_mouse, click):
        surf.blit(self.text, self.pos)
        if self.rect.collidepoint(p_mouse[0], p_mouse[1]):
            if click:
                pg.draw.rect(surf, [82, 101, 159], self.rect, width=5, border_radius=5)
                return 1
            else:
                pg.draw.rect(surf, [176, 43, 44], self.rect, width=5, border_radius=5)
        
        return 0

async def splash_screen(msg, splash, clock, font, screen, delay=1000):
    running = 1
    clickdelay = 0
    while running:
        clickdelay += 1
        clock.tick(60)
        surf = splash.copy()
        ticks = pg.time.get_ticks()/200
        surf.blit(font.render(msg, 1, (0, 0, 0)), (50, 530+5*math.sin(ticks-1)))
        surf.blit(font.render(msg, 1, (255, 255, 255)), (52, 530+5*math.sin(ticks)))

        p_mouse = pg.mouse.get_pos()
        pg.draw.polygon(surf, (200, 50, 50), ((p_mouse), (p_mouse[0]+20, p_mouse[1]+22), (p_mouse[0], p_mouse[1]+30)))

        screen.blit(surf, (0,0))
        pg.display.update()

        for event in pg.event.get():
            if event.type == pg.KEYDOWN or event.type == pg.MOUSEBUTTONDOWN and clickdelay > 30:
                return
            elif event.type == pg.QUIT:
                pg.quit()
        if clickdelay == 500:
            msg = "Press any key..."
        if clickdelay > delay:
            return
        await asyncio.sleep(0)  # very important, and keep it 0

class Highscores():
    def __init__(self):
        try:
            a_file = open("assets/h.s")
            file_contents = a_file.read(); a_file.close()
            self.times = file_contents.splitlines()
            for i in range(len(self.times)):
                self.times[i] = float(self.times[i])**math.pi
        except:
            self.times = [40.001, 60.001, 80.001, 100.001]
    
    def save(self):
        with open("assets/h.s", "w") as file:
            for i in range(len(self.times)):
                file.write(str(self.times[i]**(1/math.pi))+'\n') # separate lines for readability

# if __name__ == '__main__':
pg.init()
pg.display.set_caption("LockPickin'joyer by FinFET")
asyncio.run( main() )
    # pg.quit()
