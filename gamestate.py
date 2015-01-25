
import numpy as np
import pygame as pg

from scipy.stats import powerlaw
from random import randrange
from palette import RED, BLUE, CYAN, WHITE
from planet import PLANET_NAMES, P_IDX, PLANET_IMG
from drawutils import draw_dashed_line, glow


def dist(a, b):
    return np.linalg.norm(np.array(a) - np.array(b))


class Score:
    def __init__(self):
        self._guns = 0
        self._fun = 0


class Planet:
    def __init__(self, idx, pop, coords):
        self._idx = idx
        self._pop = pop
        self._owner = None
        self._visible = False
        self._explorable = False
        self._pos = coords
        self._name = PLANET_NAMES[(P_IDX + idx) % len(PLANET_NAMES)]

        self._img = pg.image.load(PLANET_IMG[(P_IDX + idx) % len(PLANET_IMG)])
        self._img = pg.transform.scale(self._img, (100, 100))

        self._gimg = pg.image.load(PLANET_IMG[(P_IDX + idx) % len(PLANET_IMG)]
                                   .split('.')[0] + 'gray.png')
        self._gimg = pg.transform.scale(self._gimg, (100, 100))

        self._popguns = 0
        self._popfun = self._pop
        self._explorecost = 2
        self._conquercost = int(randrange(pop / 2, pop * 2))

        assert (self._popfun + self._popguns) == self._pop

    def upFun(self):
        if (self._popfun < self._pop):
            self._popfun += 1
            self._popguns -= 1
        assert (self._popfun + self._popguns) == self._pop

    def upGuns(self):
        if (self._popguns < self._pop):
            self._popguns += 1
            self._popfun -= 1
        assert (self._popfun + self._popguns) == self._pop

    def nextTurn(self):
        self._pop += 1
        self._popfun += 1

    def exploredStr(self):
        return "%s: Population: %d Guns: %d" % (self._name, self._pop,
                                                self._conquercost)

    def unknownStr(self):
        return "Unknown planet: Population: ? Guns: ? Explore cost: %d" % \
            self._explorecost

    def funStr(self):
        return "Fun: %d" % self._popfun

    def gunStr(self):
        return "Gun: %d" % self._popguns

    def __str__(self):
        if self._visible:
            return self.exploredStr()
        else:
            return self.unknownStr()


class GameState:
    def __init__(self, lvlmap):
        self._lvlmap = lvlmap

        pops = [max(1, int(x * 10))
                for x in powerlaw.rvs(1.2, size=len(lvlmap.coords()))]

        start_planet = None
        planets = []
        for i in range(0, len(lvlmap.coords())):
            planets.append(Planet(i, pops[i], lvlmap.coords()[i]))

            if (start_planet is None or
                dist((0, 0), planets[-1]._pos) <
                    dist((0, 0), start_planet._pos)):
                start_planet = planets[-1]

        assert start_planet is not None
        start_planet._owner = 'P1'
        start_planet._visible = True
        start_planet._explorable = True
        start_planet._pop = 4
        start_planet._popfun = 4

        for p in planets:
            if p._idx in lvlmap.getNeighbors(start_planet._idx):
                p._explorable = True

        self._planets = planets
        self._info = ''
        self._turn = 1

        self._selected = start_planet
        self._exploreList = set()
        self._conquerList = set()

        self._score = Score()

    def getPlanets(self):
        return self._planets

    def nextTurn(self):
        if self._turn == 20:
            return

        self._turn += 1

        for p in self._exploreList:
            p._visible = True
            for n in self._lvlmap.getNeighbors(p._idx):
                self.getPlanets()[n]._explorable = True

        for p in self._conquerList:
            p._owner = 'P1'
            p._explorecost = 0

        self._exploreList.clear()
        self._conquerList.clear()

        for p in self.getPlanets():
            if p._owner == 'P1':
                self._score._guns += p._popguns
                self._score._fun += p._popfun

            p.nextTurn()

    def upKey(self):
        self._selected.upFun()

    def downKey(self):
        self._selected.upGuns()

    def click(self, pos):
        for p in self.getPlanets():
            if (dist(pos, p._pos) < 40):
                if p._owner == 'P1':
                    self._selected = p

                elif p._visible and p._owner != 'P1':
                    # conquer this planet
                    if p in self._conquerList:
                        self._conquerList.remove(p)
                        self._score._guns += p._conquercost
                        # return guns
                    elif self._score._guns >= p._conquercost:
                        self._conquerList.add(p)
                        self._score._guns -= p._conquercost

                elif p._explorable and not p._visible:
                    if p in self._exploreList:
                        self._exploreList.remove(p)
                        self._score._guns += p._explorecost
                    elif self._score._guns >= p._explorecost:
                        self._exploreList.add(p)
                        self._score._guns -= p._explorecost

    def hover(self, pos):
        self._info = ''
        for p in self.getPlanets():
            if not p._explorable:
                continue
            if (dist(pos, p._pos) < 40):
                self._info = str(p)

    def endGame(self, screen):
        endfont = pg.font.Font(None, 64)
        txt = endfont.render("Game over! Score: %d!" % self._score._fun, True,
                             WHITE)
        screen.blit(txt, (screen.get_width() / 2 - txt.get_width() / 2,
                          screen.get_height() / 2 - txt.get_height() / 2))

        restartfont = pg.font.Font(None, 48)
        txt = restartfont.render("Press enter to begin again", True, WHITE)

        screen.blit(txt, (screen.get_width() / 2 - txt.get_width() / 2,
                          (screen.get_height() / 2 - txt.get_height() / 2) + 32))

    def draw(self, screen):
        font = pg.font.Font(None, 36)
        text = font.render(self._info, True, WHITE)
        turn = font.render("Turn %d Guns: %d Fun: %d " % (self._turn,
                                                          self._score._guns,
                                                          self._score._fun),
                           True, WHITE)

        screen.blit(text, (10, 10))
        screen.blit(turn, (900, 10))

        for p in self._planets:
            if not p._visible and not p._explorable:
                continue

            if p._visible:
                screen.blit(p._img, (p._pos[0] - p._img.get_width() / 2,
                                     p._pos[1] - p._img.get_height() / 2))

                if p._owner == 'P1':
                    oursglow = glow((p._img.get_width(), p._img.get_height()),
                                    CYAN)

                    screen.blit(oursglow, (p._pos[0] - p._img.get_width() / 2,
                                           p._pos[1] - p._img.get_height() / 2))

                    infofont = pg.font.Font(None, 24)
                    funtxt = infofont.render(p.funStr(), True, WHITE)
                    guntxt = infofont.render(p.gunStr(), True, WHITE)

                    screen.blit(funtxt, (p._pos[0] + 35, p._pos[1] - 12))
                    screen.blit(guntxt, (p._pos[0] + 35, p._pos[1] + 12))

                for n in self._lvlmap.getNeighbors(p._idx):
                    neighborp = self.getPlanets()[n]
                    draw_dashed_line(screen, RED, p._pos, neighborp._pos,
                                     width=1, dash_length=5)

            elif p._explorable:
                screen.blit(p._gimg, (p._pos[0] - p._gimg.get_width() / 2,
                                      p._pos[1] - p._gimg.get_height() / 2))

            if p in self._exploreList:
                explore_glow = glow((p._img.get_width(), p._img.get_height()),
                                    BLUE)
                screen.blit(explore_glow, (p._pos[0] - p._img.get_width() / 2,
                                           p._pos[1] - p._img.get_height() / 2))

            if p in self._conquerList:
                conquer_glow = glow((p._img.get_width(), p._img.get_height()),
                                    RED)
                screen.blit(conquer_glow, (p._pos[0] - p._img.get_width() / 2,
                                           p._pos[1] - p._img.get_height() / 2))
        if self._turn == 20:
            self.endGame(screen)
