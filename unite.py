''' author: samtenka
    change: 2020-04-01
    create: 2020-04-01
    descrp: From parse into rectangles, construct version space
    to use:
'''

import numpy as np

from utils import CC, pre, status   # ansi
from utils import secs_endured      # profiling

from vis import str_from_grids, colors
from example import example_grids 
from derender import rects_from_scene
from versions import get_versions, weaken_order, print_program

from collections import namedtuple

Many = namedtuple('Many', 'reps body') 
Rect = namedtuple('Rect', 'topp bott left rght colr')
Attr = namedtuple('Attr', 'type vals') 

def init_scene(rects):
    scene = {}
    for rect in rects:
        r, rr, c, cc, color = rect
        idx = len(scene)
        scene[len(scene)] = Attr('TOPP', {r    }) 
        scene[len(scene)] = Attr('BOTT', {rr   }) 
        scene[len(scene)] = Attr('LEFT', {c    })
        scene[len(scene)] = Attr('RGHT', {cc   }) 
        scene[len(scene)] = Attr('COLR', {color})
        scene[len(scene)] = Rect(idx, idx+1, idx+2, idx+3, idx+4)
    return scene

def print_scene(scene):
    for idx, obj in scene.items():
        print('{:2d}'.format(idx), obj)

#def replace_idx(scene, old, new):

rects = {
    (1, 3, 5, 9, 'R'),
    (7, 9, 5, 9, 'R'),
    (4, 6, 5, 9, 'R'),
    (2, 5, 0, 1, 'B'),
    (2, 5, 2, 3, 'B'),
    (2, 5, 4, 5, 'B'),
}

scene = init_scene(rects)

print_scene(scene)


#def hamming(rect_a, rect_b):
#    return sum(
#        0 if a==b else np.log(10) if (a=='?' or b=='?') else np.log(100)
#        for a,b in zip(rect_a, rect_b)
#    )
#
#def unify(rect_a, rect_b):
#    return tuple(
#        a if a==b else '?'  
#        for a,b in zip(rect_a, rect_b)
#    )
#
#def step(rects):
#    distances = {
#        (i, j): hamming(rect_a, rect_b)
#        for i, rect_a in enumerate(rects)
#        for j, rect_b in enumerate(rects)
#        if i<j
#    }
#    d, i, j = min((d, i, j) for (i,j), d in distances.items())
#    rect_a = rects[i]
#    rect_b = rects[j]
#    print(rect_a)
#    print(rect_b)
#    print(unify(rect_a, rect_b))
#
#step({r:1 for r in rectangles})
