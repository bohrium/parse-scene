''' author: samtenka
    change: 2020-03-31
    create: 2020-03-31
    descrp: 
    to use:
'''

import numpy as np

from utils import CC, pre, status   # ansi
from utils import secs_endured      # profiling

from vis import str_from_grids
from color_patches import nb_color_patches
from example import example_grids 

def diff(pred, ref):
    z = ref.copy() 
    z[pred==ref] = 0 
    return z

def metric_top(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    z = diff(pred, ref)
    return nb_color_patches(z)**0.5 / 2.0

def metric_geo(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    return np.count_nonzero((pred!=ref) + 0)

def combined_metric(pred, ref):
    return (
        max(3**0.5/2, metric_top(pred, ref)), 
        metric_geo(pred, ref),
    )

def get_corners(ref):
    corners = set()
    h, w = ref.shape
    emb = np.zeros((h+2, w+2), dtype=np.byte) 
    emb[1:-1, 1:-1] = ref
    for r in range(h+1):
        for c in range(w+1):
            if (
                emb[r  ,c  ]==emb[r  ,c+1] and 
                emb[r+1,c  ]==emb[r+1,c+1]
            ) or (
                emb[r  ,c  ]==emb[r+1,c  ] and 
                emb[r  ,c+1]==emb[r+1,c+1]
            ):
                continue
            corners.add((r,c))
    return corners

def get_next(base, ref, d, corners): 

    metrics = {}

    for r in range(9):
        for rr in range(r+1, 9+1):
            active_cols = [
                c for c in range(9+1)
                if (r,c) in corners or (rr,c) in corners
            ] 
            for ci in range(len(active_cols)):
                c = active_cols[ci]
                y = base.copy()

                for cci in range(ci+1, len(active_cols)):
                    cc = active_cols[cci]
                    colors = set(
                        x[a,b] for a in (r, rr-1) for b in (c, cc-1) if x[a,b]
                    )
                    for color in colors:
                        y[r:rr, c:cc] = color
                        metrics[((r,rr,c,cc), color)] = d(y,x), -(rr-r)*(cc-c)  
    
    best = min(((v,k) for k,v in metrics.items())) 
    return best

def demonstrate(x, use_top=True, use_geo=False, print_diffs=False, print_intermediates=False):
    corners = get_corners(x)
    
    intermediate_scenes = []
    
    base = np.zeros((9, 9), dtype=np.byte)
    
    while True:
        best = get_next(base, x, d=metric, corners=corners)
        (val, _), ((r,rr,c,cc), color) = best
        y = base.copy()
        y[r:rr, c:cc] = color
    
        intermediate_scenes.append(y) 
        base = y
    
        if print_diffs:
            print(CC + str_from_grids([x, y, diff(y,x)]))

        if np.count_nonzero(diff(y,x))==0:
            break
    
    if print_intermediates:
        for i in range(0, len(intermediate_scenes), 8):
            print(CC + str_from_grids(intermediate_scenes[i:i+8]))

    return len(intermediate_scenes)


if __name__=='__main__':
    start = secs_endured()

    metrics_by_nm = {}
    metrics_by_nm['top'] = combined_metric 
    #metrics_by_nm['geo' ] = metric_geo      

    for i, x in enumerate(example_grids):
        status('parsing scene [{}] greedily ... '.format(i), end='')
        for nm, metric in metrics_by_nm.items():
            status('[{}] '.format(nm), end='')
            nb_steps = demonstrate(x)
            status('takes [{:2d}] steps    '.format(nb_steps), end='')
        print()
    
    end = secs_endured()
    status('parsed [{}] scenes in [{:.2f}] secs per scene'.format(
        len(example_grids),
        (end-start) / len(example_grids)
    ))
