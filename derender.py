''' author: samtenka
    change: 2020-03-31
    create: 2020-03-31
    descrp: Greedily parse scenes into rectangles   
    to use: Use exposed methods like so:

                from derender import rects_from_scene, build_from 
                rects = rects_from_scene(x)
                ((r, rr, c, cc), color) = rects[0]  # first rectangle
                intermediates = build_from(rects, x.shape)

            Or, to see parses of example scenes under different heuristics, run

                python derender.py use_top=True use_geo=False

            To time greedy search under the topological heuristic, run

                python derender.py clock=True vis=False

'''

import numpy as np

from utils import CC, pre, status   # ansi
from utils import secs_endured      # profiling

from vis import str_from_grids
from color_patches import nb_color_patches
from example import example_grids 

#=============================================================================#
#=====  0. GREEDY SEARCH  ====================================================#
#=============================================================================#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.0. Heuristic Distance Metrics  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#---------------------  0.0.0. pixel distance  -------------------------------#

def metric_geo(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    return np.count_nonzero((pred!=ref) + 0)

#---------------------  0.0.1. topology-aware distance  ----------------------#

def diff(pred, ref):
    z = ref.copy() 
    z[pred==ref] = 0 
    return z

def metric_top(pred, ref):
    if np.logical_and(pred!=0, ref==0).any():
        return float('+inf')
    z = diff(pred, ref)
    return nb_color_patches(z)**0.5 / 2.0

#---------------------  0.0.2. mixed heuristic switches from top to geo  -----#

def metric_combined(pred, ref):
    return (
        max(3**0.5/2, metric_top(pred, ref)), 
        metric_geo(pred, ref),
    )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.1. Greedy Step  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#---------------------  0.1.0. find cell corners that could be rect corners  -#

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

def get_next(base, x, d, corners): 
    h, w = x.shape

    #-----------------  0.1.1. for each rect with a data-matching corner... --#

    rects_by_dist = {}
    for r in range(h):
        for rr in range(r+1, h+1):
            active_cols = [
                c for c in range(w+1)
                if (r,c) in corners or (rr,c) in corners
            ] # note: is sorted
            for ci in range(len(active_cols)-1):
                c = active_cols[ci]

                y = base.copy()
                for cci in range(ci+1, len(active_cols)):
                    cc = active_cols[cci]

                    #-  0.1.2. ...consider possible colors... ----------------#

                    colors = set(
                        x[a,b] for a in (r, rr-1) for b in (c, cc-1) if x[a,b]
                    )
                    for color in colors:
                        y[r:rr, c:cc] = color
                        rects_by_dist[((r,rr,c,cc), color)] = d(y,x), -(rr-r)*(cc-c)  

    #-----------------  0.1.3. ...and return best  ---------------------------#
    
    best = min(((v,k) for k,v in rects_by_dist.items())) 
    return best

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.2. Greedy Loop  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def rects_from_scene(x, metric=metric_combined):
    corners = get_corners(x)

    intermediate_scenes = []
    rectangles = [] 

    base = np.zeros(x.shape, dtype=np.byte)
    while True:
        best = get_next(base, x, d=metric, corners=corners)
        (val, _), ((r,rr,c,cc), color) = best
        y = base.copy()
        y[r:rr, c:cc] = color

        rectangles.append(((r,rr,c,cc), color))
        intermediate_scenes.append(y) 
        base = y
    
        if np.count_nonzero(diff(y,x))==0:
            break
    
    return rectangles

#=============================================================================#
#=====  2. TIME-INTEGRATION AND VISUALIZATION  ===============================#
#=============================================================================#

def build_from(rectangles, shape):
    intermediates = [] 
    base = np.zeros(shape, dtype=np.byte)
    intermediates.append(base.copy())
    for ((r, rr, c, cc), color) in rectangles:
        base[r:rr, c:cc] = color 
        intermediates.append(base.copy())
    return intermediates

def visualize_construction(x, rectangles, print_diffs=True, row_len=8): 
    print()
    intermediates = build_from(rectangles, x.shape)[1:]
    differences = [diff(base, x) for base in intermediates][1:]

    for i in range(0, len(rectangles), row_len):
        print(CC + str_from_grids(intermediates[i:i+row_len]))
        if print_diffs:
            print(CC + str_from_grids(differences[i:i+row_len]))

#=============================================================================#
#=====  3. INTERACTIVE LOOP  =================================================#
#=============================================================================#

if __name__=='__main__':

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.0. Command Line Parameters  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    import sys
    params = {
        'vis'    :True,
        'clock'  :False,
        'use_top':True,
        'use_geo':False,
    }
    for arg in sys.argv[1:]:
        terms = arg.split('=') 
        pre(len(terms)==2 and terms[0] in params,
            'ill-formatted argument {}'.format(arg)
        )
        params[terms[0]] = (terms[1]=='True') 

    metrics_by_nm = {}

    if params['use_top']: metrics_by_nm['top'] = metric_combined
    if params['use_geo']: metrics_by_nm['geo' ] = metric_geo 

    if params['clock']:
        pre(not params['vis'] and len(metrics_by_nm)==1,
            'to compare speeds, we need *one* metric specified and no vis'
        )

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.1. Display Derendering Output  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    start = secs_endured()

    for i, x in enumerate(example_grids):
        status('parsing scene [{}] greedily ... '.format(i), end='')
        for nm, metric in metrics_by_nm.items():
            status('[{}] '.format(nm), end='')
            rects = rects_from_scene(x, metric)
            status('takes [{:2d}] steps    '.format(len(rects)), end='')
            if params['vis']:
                visualize_construction(x, rects)
                input(CC + '@O next?@D ')
        print()
    
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.2. Report Timing Info  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    if params['clock']:
        end = secs_endured()
        status('parsed [{}] scenes in [{:.2f}] secs per scene'.format(
            len(example_grids),
            (end-start) / (len(example_grids) * len(metrics_by_nm)) 
        ))
