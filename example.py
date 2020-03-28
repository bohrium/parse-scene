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
from color_patches import nb_color_patches

#=============================================================================#
#=====  0. ILLUSTRATE COUNTING OF COLOR PATCHES  =============================#
#=============================================================================#

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.0. Create Example Grid  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

# NOTE: We expect grids to be np arrays with element type np.byte.  The byte
#       values represent colors.  Using bytes instead of ints helps to pack
#       grids more efficiently in memory.  When we operate on large populations
#       of grids, this allows more frequent cache hits.

x = np.zeros(shape=(8, 8), dtype=np.byte)

#---------------------  0.0.0. draw a rectangle's border  --------------------#

x[:4, :4] = 1
x[1:3, 1:3] = 0

#---------------------  0.0.1. draw a comb shape  ----------------------------#

x[4:, :] = 1 
x[4, ::1] = 2
x[5, ::2] = 2
x[6, ::4] = 2

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~  0.1. Check Color Patch Prediction Against Truth  ~~~~~~~~~~~~~#

actual    = 5
predicted = nb_color_patches(x)
assert predicted == actual

print('(  {}  ) color patches detected in array:'.format(predicted))
print(x)
