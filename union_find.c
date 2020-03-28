#include <stdlib.h>
#include "union_find.h"

void init(UnionFind* rem, int nb_elts)
{
    rem->size = nb_elts; 
    rem->next = malloc(sizeof(int)*nb_elts); 
    for (int i=0; i!=nb_elts; ++i) {
        rem->next[i] = i;
    }
}
int ancestor(UnionFind* rem, int x)
{
    int old;
    do {
        old = x;
        x = rem->next[old];
    } while ( x != old );
    return x;
}
void set_par(UnionFind* rem, int x, int p) 
{
    int old;
    do {
        old = x;
        x = rem->next[old];
        rem->next[old] = p;
    } while ( x != old );
}
void join(UnionFind* rem, int x, int y)
{
    int ax = ancestor(rem, x);
    int ay = ancestor(rem, y);
    int a_min = ax<ay ? ax : ay;
    set_par(rem, x, a_min);
    set_par(rem, y, a_min);
}
int nb_ccs(UnionFind* rem)
{
    int nb=0;
    for (int i=0; i!=rem->size; ++i) {
        if (rem->next[i]==i) { ++nb; }
    }
    return nb;
}
void del_uf(UnionFind* rem)
{
    free(rem->next);
}
