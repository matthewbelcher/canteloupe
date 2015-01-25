#!/usr/bin/python

from genLevel import generateMap
from gamestate import GameState
from random import randrange


def resetGame(size):
    lvlmap = generateMap(20, size[0], size[1])
    state = GameState(lvlmap)

    return lvlmap, state


def main(argv):
    import pygame as pg

    pg.init()
    pg.mixer.init(44100, -16, 1, 4096)

    size = (int(argv[0]), int(argv[1]))

    screen = pg.display.set_mode(size)

    pg.display.set_caption("Space Cantelope 4X!")

    clock = pg.time.Clock()
    exiting = False

    bg = pg.image.load("PIA13128.jpg")
    bg = pg.transform.scale(bg, size)

    sounds = [pg.mixer.Sound('Alien1.ogg'),
              pg.mixer.Sound('Alien2.ogg'),
              pg.mixer.Sound('Giant.ogg'),
              pg.mixer.Sound('Normal.ogg')]

    lvlmap, state = resetGame(size)

    while not exiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exiting = True
            if event.type == pg.MOUSEBUTTONDOWN:
                state.click(event.pos)
            if event.type == pg.MOUSEMOTION:
                state.hover(event.pos)
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    state.nextTurn()
                    if (randrange(0, 10) < 5):
                        sounds[randrange(0, len(sounds))].play()
                elif event.key == pg.K_UP:
                    state.upKey()
                elif event.key == pg.K_DOWN:
                    state.downKey()
                elif event.key == pg.K_RETURN and state._turn == 20:
                    lvlmap, state = resetGame(size)

        screen.blit(bg, [0, 0])

        state.draw(screen)

        pg.display.flip()

        clock.tick(60)

    pg.quit()

if __name__ == "__main__":
    main([1280, 720])
