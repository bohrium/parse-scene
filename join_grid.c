#include <stdlib.h>
#include "join_grid.h"
#include "union_find.h"

int nb_color_patches(int height, int width, signed char* arr)
{
    if ( height*width == 0 ) { return 0; }

    UnionFind rem;
    init(&rem, height*width);
    int r, c;

    /* upper left body */
    for (r=0; r!=height-1; ++r) {
        for (c=0; c!=width-1; ++c) {
            int idx   = r*width + c; 
            int right = idx + 1;
            int down  = idx + width;
            if (arr[idx] == arr[right]) { join(&rem, idx, right); }
            if (arr[idx] == arr[down ]) { join(&rem, idx, down ); }
        }
    }

    /* bottom row */
    r = height-1; {
        for (c=0; c!=width-1; ++c) {
            int idx   = r*width + c; 
            int right = idx + 1;
            if (arr[idx] == arr[right]) { join(&rem, idx, right); }
        }
    }

    /* rightmost col */
    c = width-1; {
        for (r=0; r!=height-1; ++r) {
            int idx   = r*width + c; 
            int down  = idx + width;
            if (arr[idx] == arr[down ]) { join(&rem, idx, down ); }
        }
    }

    int ccs = nb_ccs(&rem);
    del_uf(&rem);
    return ccs;
}

