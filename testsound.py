import pygame as pg

pg.init()
pg.mixer.init(44100, -16, 1, 2048)

s = pg.mixer.Sound('Normal.ogg')

chan = s.play()

while chan.get_busy():
    pg.time.delay(100)
