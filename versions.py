''' author: samtenka
    change: 2020-03-31
    create: 2020-03-31
    descrp: From parse into rectangles, construct version space
    to use:
                from derender import rects_from_scene
                from versions import get_versions, weaken_order, print_program

                rects = rects_from_scene(my_grid)
                minrects, supmasks, maximalss = get_versions(my_grid, rects)
                dag = weaken_order(minrects, supmasks, maximalss)
                print_program(dag, minrects, supmasks, maximalss)
'''

import numpy as np

from utils import CC, pre, status   # ansi
from utils import secs_endured      # profiling
from utils import uniform           # math

from vis import str_from_grids, colors
from example import example_grids 

from derender import rects_from_scene, build_from, diff, visualize_construction

#=============================================================================#
#=====  0. VERSION SPACE FOR INDIVIDUAL RECTANGLE  ===========================#
#=============================================================================#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.0. Compute Confining Mask in Efficient Representation  ~~~~~#

def compute_maximals(minrect, supmask):
    h, w = supmask.shape
    r, rr, c, cc = minrect

    col_pairs = [
        (C,CC) for C in range(0,c+1) for CC in range(cc,w+1)
        if (supmask[r:rr,C:CC]).all()
    ]

    expansions = [] 
    while col_pairs:
        #-------------  0.0.0. reset probe  ----------------------------------#

        c, cc = col_pairs.pop() 
        R, RR, C, CC = r, rr, c, cc

        #-------------  0.0.1. heighten probe maximally  ---------------------#

        while 0<=R-1 and supmask[R-1:R,c:cc].all(): R -= 1
        while RR+1<=h and supmask[RR:RR+1,c:cc].all(): RR += 1

        #-------------  0.0.2. check that probe can be widened no further  ---#

        if (
            (0<=C-1 and supmask[R:RR,C-1:C].all()) or
            (CC+1<=w and supmask[R:RR,CC:CC+1].all())
        ): continue

        #-------------  0.0.3. yield probe  ----------------------------------#

        expansions.append((R, RR, C, CC))

    return expansions

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.1. Manually Crafted Correctness Test  ~~~~~~~~~~~~~~~~~~~~~~#

def test_compute_maximals():
    minrect = (3, 5, 2, 4)
    mr,mrr,mc,mcc = minrect

    supmask_a = np.ones((6,6), dtype=np.byte)
    supmask_a[4:6,0:2] = 0
    supmask_a[0:1,0:2] = 0
    supmask_a[0:3,4:5] = 0

    supmask_b = np.ones((6,6), dtype=np.byte)
    supmask_b[0:3,0:1] = 0
    supmask_b[0:2,0:2] = 0
    supmask_b[0:1,0:3] = 0
    supmask_b[-1:,-1:] = 0

    for supmask, nb_maximals in [(supmask_a, 2), (supmask_b, 6)]:
        maximals = compute_maximals(minrect, supmask)
        pre(len(maximals)==nb_maximals, 'maximals test failed!')

        decorated_supmask = supmask.copy() * 3
        decorated_supmask[mr:mrr,mc:mcc] = 4

        rendered_maximals = []
        for r,rr,c,cc in maximals: 
            y = np.zeros((6,6), dtype=np.byte)
            y[r:rr,c:cc] = 1
            y[mr:mrr,mc:mcc] = 4
            rendered_maximals.append(y)

        print(CC+str_from_grids([decorated_supmask] + rendered_maximals))

#=============================================================================#
#=====  1. VERSION SPACE FOR SCENE OF ORDERED RECTANGLES  ====================#
#=============================================================================#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  1.0. Rectangles Communicate by Dynamic Programming  ~~~~~~~~~~#

def get_versions(x, rects): 
    minrects = []
    supmasks = [] 
    maximalss = []

    #-----------------  1.0.0. remove effectless rectangles  -----------------#

    new_rects = []
    for i, r in enumerate(rects):
        without = build_from(rects[:i]+rects[i+1:], x.shape)[-1]
        effects = diff(without, x)
        if effects.any():
            new_rects.append(r)
    rects = new_rects
    
    #-----------------  1.0.1. for each rectangle...  ------------------------#

    for i, ((r, rr, c, cc), color) in enumerate(rects):
        y = np.zeros(x.shape, dtype=np.byte) 
        y[r:rr, c:cc] = color
    
        #-------------  1.0.2. ...compute its minimal responsibility...  -----#

        before  = build_from(rects[ : i], x.shape)[-1]
        after   = build_from(rects[i+1:], x.shape)[-1]
        without = build_from(minrects[:i]+rects[i+1:], x.shape)[-1]
        effects = diff(without, x)
        pre(effects.any(), 'uh oh!  effectless rectangle!')
    
        nz = np.nonzero(effects)
        minrect = ((min(nz[0]),max(nz[0])+1, min(nz[1]),max(nz[1])+1))
        mr, mrr, mc, mcc = minrect
        minrects.append((minrect, color))
        minrect_rendered = np.zeros(x.shape, dtype=np.byte) 
        minrect_rendered[mr:mrr, mc:mcc] = 1
    
        #-------------  1.0.3. ...and its confining mask...  -----------------#

        supmask = np.logical_or(x==color, after!=0)
        maximals = compute_maximals(minrect, supmask)
        maximalss.append(maximals)
        supmask = build_from([(mm, 1) for mm in maximals], x.shape)[-1] 
        supmasks.append(supmask)

    return minrects, supmasks, maximalss

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  1.1. Relax Toset to Poset Based on Confining Masks  ~~~~~~~~~~#

def weaken_order(minrects, supmasks, maximalss):
    under = [
        [
            int(i<j and (np.logical_and(sm_a, sm_b)).any())
            for j, sm_b in enumerate(supmasks)
        ]
        for i, sm_a in enumerate(supmasks) 
    ]

    dag = []
    remaining_nodes = set(range(len(rects)))
    while remaining_nodes:
        n = min(remaining_nodes)
        cohort = set([n])
        for i in remaining_nodes:
            for j in remaining_nodes: 
                if under[j][i]:
                    break
            else:
                cohort.add(i)
        remaining_nodes = remaining_nodes.difference(cohort)
        dag.append(cohort)

    return dag

#=============================================================================#
#=====  2. VISUALIZATION OF PROGRAM VERSIONS  ================================#
#=============================================================================#

def print_program(dag, minrects, supmasks, maximalss):
    for cohort in dag:
        print('{')
        for i in cohort:
            (r, rr, c, cc), color = rects[i]
            (mr, mrr, mc, mcc), _ = minrects[i]
            maximals = maximalss[i]
            print(CC + '    ' + '   or   '.join(
                'rect({}, {}, {}, {}, @{} {}@D )'.format( 
                    '[{}..{}]'.format(r, mr)   if r !=mr  else str(r ),
                    '[{}..{}]'.format(mrr, rr) if rr!=mrr else str(rr),
                    '[{}..{}]'.format(c, mc)   if c !=mc  else str(c ),
                    '[{}..{}]'.format(mcc, cc) if cc!=mcc else str(cc),
                    colors[color],
                    colors[color]
                )
                for r,rr,c,cc in maximals
            ))
        print('}', end=' ')
    print()

def sample_rects_from(dag, minrects, supmasks, maximalss):
    rects = []
    for cohort in dag:
        for i in cohort:
            (mr, mrr, mc, mcc), color = minrects[i]
            (Mr, Mrr, Mc, Mcc) = uniform(maximalss[i])
            r = uniform(range(Mr , mr +1)) 
            rr= uniform(range(mrr, Mrr+1)) 
            c = uniform(range(Mc , mc +1)) 
            cc= uniform(range(mcc, Mcc+1)) 
            rects.append(((r, rr, c, cc), color))
    return rects

#=============================================================================#
#=====  3. INTERACTIVE LOOP  =================================================#
#=============================================================================#

if __name__=='__main__':

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.0. Parse Command Line Arguments  ~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    import sys
    params = {
        'scene_idx': 0,
        'test_maximals': False,
    }

    for arg in sys.argv[1:]:
        terms = arg.split('=') 
        pre(len(terms)==2 and terms[0] in params,
            'ill-formatted argument {}'.format(arg)
        )
        params[terms[0]] = eval(terms[1])

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.1. Test compute_maximals for Correctness  ~~~~~~~~~~~~~~~~~~#

    if params['test_maximals']:
        test_compute_maximals()

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.2. Obtain Joint Version Space from Rectangles  ~~~~~~~~~~~~~#

    x = example_grids[params['scene_idx']]
    rects = rects_from_scene(x)
    minrects, supmasks, maximalss = get_versions(x, rects)
    dag = weaken_order(minrects, supmasks, maximalss)
    print_program(dag, minrects, supmasks, maximalss)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  3.3. Display Sample Trajectories from Version Space  ~~~~~~~~~#

    for _ in range(2):
        new_rects = sample_rects_from(dag, minrects, supmasks, maximalss)
        visualize_construction(x, new_rects, print_diffs=False, row_len=9)
