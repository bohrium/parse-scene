''' author: samtenka
    change: 2020-03-31
    create: 2020-03-31
    descrp: 
    to use:
'''

import numpy as np

from utils import CC, pre, status   # ansi

from vis import str_from_grids
from color_patches import nb_color_patches
from example import example_grids 

def diff(pred, ref):
    z = ref.copy() 
    z[pred==ref] = 0 
    return z

def dist_top(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    z = diff(pred, ref)
    return nb_color_patches(z)**0.5 / 2.0

def dist_geo(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    return np.count_nonzero((pred!=ref) + 0)

def combined_dist(pred, ref):
    return (
        max(3**0.5/2, dist_top(pred, ref)), 
        dist_geo(pred, ref),
    )

def get_next(base, ref, d): 
    dists = {}
    for r in range(9):
       for c in range(9):
            for rr in range(r+1, 9+1):
                y = base.copy()
                for cc in range(c+1,9+1):
                    colors = set(x[a,b] for a in (r, rr-1) for b in (c, cc-1))
                    for color in colors:
                        y[r:rr, c:cc] = color
                        dists[((r,rr,c,cc), color)] = d(y,x), -(rr-r)*(cc-c)  
    
    best = min(((v,k) for k,v in dists.items())) 
    return best

for i in range(8):
    x = example_grids[i] 
    for nm, dist in {
        #'l1':dist_geo,
        'top':combined_dist
    }.items():
        status('parsing greedily based on [{}] metric:'.format(nm))
        constructions = []

        base = np.zeros((9, 9), dtype=np.byte)

        old_val = (0.0, 0.0)
        while True:
            best = get_next(base, x, d=dist)
            (val, _), ((r,rr,c,cc), color) = best
            y = base.copy()
            y[r:rr, c:cc] = color
            constructions.append(y) 

            base = y

            if np.count_nonzero(diff(y,x))==0:
                break
        
            old_val = val

        for i in range(0, len(constructions), 8):
            print(CC + str_from_grids(constructions[i:i+8]))
    input()
