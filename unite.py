''' author: samtenka
    change: 2020-04-03
    create: 2020-04-03
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

AttrNode = namedtuple('Attr', 'plate atype vals_by_draw') 
DrawNode = namedtuple('Draw', 'plate dtype attrs') # draws and plates

def init_scene(rectangles):
    attrs = {}
    draws = {}

    for rect in rectangles:
        A, B, C, D, E = range(len(attrs), len(attrs)+5) 
        F = len(draws) 

        r, rr, c, cc, color = rect

        attrs[A] = AttrNode(None, 'TOP', {F:r    }) 
        attrs[B] = AttrNode(None, 'BOT', {F:rr   }) 
        attrs[C] = AttrNode(None, 'LEF', {F:c    })
        attrs[D] = AttrNode(None, 'RIG', {F:cc   }) 
        attrs[E] = AttrNode(None, 'CLR', {F:color})

        draws[F] = DrawNode(None, 'RECT', [A, B, C, D, E])

    return attrs, draws

def print_scene(attrs, draws):
    for idx, (p, t, vbds) in attrs.items():
        print(CC+'@O {:2d}@D : @G {}@D \t {}\t {{{}}}@D '.format(
            idx, '-' if p is None else p, t,
            ', '.join('@G {}@D :{}'.format(k,v) for k,v in vbds.items())
        ))
    for idx, (p, t, aa) in draws.items():
        print(CC+'@G {:2d}@D : @G {}@D \t {}\t [{}]@D '.format(
            idx, '-' if p is None else p, t,
            ', '.join('@O {}@D '.format(a) for a in aa)
        ))

def unite_attrs(attrs, draws, idx_a, idx_b):
    if idx_a==idx_b: pass

    attr_a = attrs[idx_a]
    attr_b = attrs[idx_b]

    pre(attr_a.plate==attr_b.plate, 'cannot unite attrs from distinct plates!')
    pre(attr_a.atype==attr_b.atype, 'cannot unite attrs of distinct types!')

    _draw = attr_a.vals_by_draw.copy()
    _draw.update(attr_b.vals_by_draw) 
    attr = AttrNode(
        attr_a.plate,
        attr_a.atype,
        _draw,
    )
    attrs[idx_a] = attr
    del attrs[idx_b]
    
    for draw_idx in attr.vals_by_draw:
        draw = draws[draw_idx]
        if idx_b in draw.attrs:
            draws[draw_idx] = DrawNode(
                draw.plate,
                draw.dtype,
                [idx_a if ai==idx_b else ai for ai in draw.attrs]
            )

def unite_draws(attrs, draws, idx_a, idx_b):
    if idx_a==idx_b: pass

    draw_a = draws[idx_a]
    draw_b = draws[idx_b]

    pre(draw_a.plate==draw_b.plate, 'cannot unite draws from distinct plates!')
    pre(draw_a.dtype==draw_b.dtype, 'cannot unite draws of distinct types!')
    pre(draw_a.attrs==draw_b.attrs, 'cannot unite draws with distinct parents!')

    homo_attrs = []
    hetr_attrs = []
    for attr_idx in draw_a.attrs:
        attr = attrs[attr_idx]
        if attr.vals_by_draw[idx_a] == attr.vals_by_draw[idx_b]:
            homo_attrs.append(attr_idx)
        else:
            pre(set(attr.vals_by_draw.keys()) == {idx_a, idx_b},
                'cannot unite draws with elsewhere-used hetr attribute!'
            )
            hetr_attrs.append(attr_idx)

    plate_idx = max(draws.keys())+1 if draws else 0 
    attr_idx = max(attrs.keys())+1 if attrs else 0
    draws[plate_idx] = DrawNode(
        draw_a.plate,
        'PLATE',
        [attr_idx],
    )
    attrs[attr_idx] = AttrNode(
        draw_a.plate,
        'REP',
        {plate_idx:2},
    )

    # remove edges to draw_b: 
    for attr_idx in homo_attrs:
        attr = attrs[attr_idx]
        attrs[attr_idx] = AttrNode(
            attr.plate, 
            attr.atype,
            {k:v for k,v in attr.vals_by_draw.items() if k!=idx_b}
        )
    for attr_idx in hetr_attrs:
        attr = attrs[attr_idx]
        attrs[attr_idx] = AttrNode(
            plate_idx,
            attr.atype,
            {idx_a:(attr.vals_by_draw[idx_a], attr.vals_by_draw[idx_b])}
        )

    draw = DrawNode(
        plate_idx,
        draw_a.dtype,
        draw_a.attrs
    )
    draws[idx_a] = draw
    del draws[idx_b]
 
rectangles = {
    (1, 2, 4, 8, 'R'),
    (1, 2, 3, 4, 'B'),
}

attrs, draws = init_scene(rectangles)
print_scene(attrs, draws)
print()
unite_attrs(attrs, draws, 0, 5)
unite_attrs(attrs, draws, 1, 6)
unite_attrs(attrs, draws, 2, 7)
unite_attrs(attrs, draws, 3, 8)
unite_attrs(attrs, draws, 4, 9)
print_scene(attrs, draws)
print()
unite_draws(attrs, draws, 0, 1)
print_scene(attrs, draws)


