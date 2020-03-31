''' author: samtenka
    change: 2020-03-17
    create: 2019-02-23
    descrp: visualize grids
    to use: To display a row of grids:

                from utils import CC
                from vis import str_from_grids
                print(CC + str_from_grids(grids))
'''

import numpy as np
from utils import CC    # ansi

colors = 'KBRGYAPOCN'
render_color = (
    lambda c:
        '@{} \u2588\u2588@D '.format(c)
        if c!='K' else '@D  \u00b7@D '
)
render_number = (lambda n: render_color(colors[n]))

def str_from_grids(grids, render=render_number): 
    ''' Return a colorizable string given a list of (potentially non-uniformly
        shaped) grids of numbers or of colors.
    '''
    if not grids:
        return ''
    heights, widths = (
        [ (g.shape[i] if i<len(g.shape) else 0) for g in grids ]
        for i in range(2)
    )

    lines = ['' for h in range(2+max(heights))]
    for g, H, W in zip(grids, heights, widths):
        lines[0]   += ' {} '.format('_'*2*W)                    # top
        for r in range(H):
            lines[1+r] += '|' + ''.join(                        # content
                render(g[r,c])
                for c in range(W)
            ) + '|'
        lines[1+H] += '`{}`'.format('`'*2*W)                    # bottom
        for h in range(1+H+1, len(lines)):                          
            lines[h] += ' {} '.format(' '*2*W)                  # under padding
    return '\n'.join(lines)

if __name__=='__main__':
    x = np.zeros(shape=(8, 8), dtype=np.byte)
    
    x[:4, :4] = 1
    x[1:3, 1:3] = 0
    
    x[4:, :] = 1 
    x[4, ::1] = 2
    x[5, ::2] = 2
    x[6, ::4] = 2

    print(CC + str_from_grids([x]))
