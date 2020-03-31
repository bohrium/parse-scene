''' author: samtenka
    change: 2020-03-28
    create: 2020-03-28
    descrp: Illustrate fast grid operations exposed via SWIG.  
    to use: Ensure that color_patches module is wrapped by running

                make color_patches
            
            then run

                python example.py  

            and inspect printed output.
'''

import numpy as np

from utils import CC, pre, status   # ansi

from vis import str_from_grids
from color_patches import nb_color_patches

#=============================================================================#
#=====  0. DEFINE EXAMPLE GRIDS  =============================================#
#=============================================================================#

# NOTE: We expect grids to be np arrays with element type np.byte.  The byte
#       values represent colors.  Using bytes instead of ints helps to pack
#       grids more efficiently in memory.  When we operate on large populations
#       of grids, this allows more frequent cache hits.

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.0. Basic Concepts in Isolation  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def archipelagos(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.0.0. draw several disjoint rectangles  -------------#

    for (r, rr, c, cc), color in {
        (1, 3, 0, 4):1, #
        (0, 3, 5, 8):1, # _
        (5, 9, 6, 8):1, #  \__ these two rectangles touch,
        (7, 9, 4, 6):2, # _/   but they differ in color
        (4, 6, 1, 3):2, #  
        (4, 5, 4, 5):3, # }--- a single green dot  
    }.items():
        x[r:rr,c:cc] = color

    return x

def camouflaging(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.0.1. draw two overlapping yellows  -----------------#

    x[4:,6:] = 4 
    x[6:,2:] = 4 

    #-----------------  0.0.2. draw three overlapping grays  -----------------#

    x[1:4,1:4] = 5 
    x[2:5,0:3] = 5 
    x[0:3,2:8] = 5 

    return x

def train_tracks(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.0.3. draw column of horizontal bars  ---------------#

    for i in range(3): 
        x[3*i+1:3*i+3,5:9] = 2 

    #-----------------  0.0.4. draw row of vertical bars  --------------------#

    for i in range(5): 
        x[2:5,2*i:2*i+1] = 1 

    return x

def ghost_corner(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.0.5. draw square floating against background  ------#

    x[:,:] = 8 
    x[1:-1,1:-1] = 9 

    #-----------------  0.0.6. cut square into four floating squares  --------#

    x[3:6,:] = 8 
    x[:,3:6] = 8 

    #-----------------  0.0.7. ghost square in background color  -------------#

    x[2:-2,2:-2] = 8 

    return x

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.1. Challenging Compositions  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

def above_pagoda(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.1.0. draw concentric rectangles...  ----------------#

    x[:,:] = 7
    for i in range(1, 5):
        x[i:-i, i:-i] = i

        #-------------  0.1.1. ... with skywalks hanging out  ----------------#

        if i==1: x[5,:]=5
        if i==2: x[:,4]=6

    return x

def four_paddles(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.1.2. draw stretched and checkered background  ------#

    for i in range(3):
        for j in range(9):
            x[3*i:3*i+3, j] = (i+j)%2 

    #-----------------  0.1.3. draw paddles  ---------------------------------#

    for s in (x, x[::-1, ::-1]): 
        for i in range(2): 
            s[4*i:4*i+3, 0:3] = 2
            s[4*i+1, 2:5] = 3

    return x

def escher_stair():
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.1.4. draw four thin rectangles  --------------------#

    for (r, rr, c, cc), color in {
        (+1,-1,+2,+3):1,
        (+2,+3,+1,-1):2,
        (+1,-1,-3,-2):3,
        (-3,-2,+1,-1):4,
    }.items():
        x[r:rr, c:cc] = color

    #-----------------  0.1.5. pull first rectangle over last  ---------------#

    x[-2-1,2] = 1 

    return x

def box_and_comb(): 
    x = np.zeros(shape=(9, 9), dtype=np.byte)

    #-----------------  0.1.6. draw a rectangle's border  --------------------#

    x[:4, :4] = 1
    x[1:3, 1:3] = 0

    #-----------------  0.1.7. draw a comb shape  ----------------------------#

    x[4:, :] = 1 

    for i in range(3): 
        x[4+i, ::2**i] = 2

    return x

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.2. Package Example Grids  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#---------------------  0.2.0. expose example grids  -------------------------#

example_grids = [
    archipelagos(),
    camouflaging(),
    train_tracks(),
    ghost_corner(),
    above_pagoda(),
    four_paddles(),
    escher_stair(),
    box_and_comb(),
]

if __name__=='__main__':

    #-----------------  0.2.1. display example grids  ------------------------#

    print(CC + str_from_grids(example_grids[:4]))
    print(CC + str_from_grids(example_grids[4:]))
 
    #=========================================================================#
    #=  1. ILLUSTRATE GRID ANALYSIS FUNCTIONS  ===============================#
    #=========================================================================#

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    #~~~~~~~~~  1.0. Illustrate Counting of Color Patches  ~~~~~~~~~~~~~~~~~~~#

    x = box_and_comb() 

    true_nb_patches = 5
    pred_nb_patches = nb_color_patches(x)
    pre(pred_nb_patches == true_nb_patches, 'incorrect patch count!')
    
    status('detected [{}] color patches in this grid:'.format(pred_nb_patches))
    print(CC + str_from_grids([x]))
