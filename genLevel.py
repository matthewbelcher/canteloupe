
import random
from scipy.spatial import Delaunay
import numpy as np
import math


class Map:

    def __init__(self, coords, indices, indptr):
        self._coords = coords
        self._indices = indices
        self._indptr = indptr

    def coords(self):
        return self._coords

    def getNeighbors(self, idx):
        nbors = []
        for n in self._indptr[self._indices[idx]:self._indices[idx + 1]]:
            nbors.append(n)
        return nbors

    def distance(self, a, b):
        return np.linalg.norm(np.array(self._coords[a]) - np.array(self._coords[b]))


def generateMap(num, x, y):
    pts = []
    for i in range(0, num):
        newpt = (random.randrange(50, x - 50),
                 random.randrange(50, y - 50))

        # don't generate planets too close together
        overlap = True
        while overlap:
            overlap = False
            newpt = (random.randrange(50, x - 50),
                     random.randrange(50, y - 50))

            for j in range(0, len(pts)):
                if np.linalg.norm(np.array(newpt) - np.array(pts[j])) < 100 * math.sqrt(2):
                    overlap = True

        pts.append(newpt)

    nppts = np.array(pts)

    dela = Delaunay(nppts)

    indices, indptr = dela.vertex_neighbor_vertices

    return Map(pts, indices, indptr)
