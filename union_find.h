#ifndef UNION_FIND_H
typedef struct UnionFind {
    int* next; 
    int size;
} UnionFind;

void init(UnionFind* rem, int nb_elts);
void join(UnionFind* rem, int x, int y);
int nb_ccs(UnionFind* rem);
void del_uf(UnionFind* rem);
#define UNION_FIND_H
#endif//UNION_FIND_H
