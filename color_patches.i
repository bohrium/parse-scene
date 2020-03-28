%module color_patches
%{
  #define SWIG_FILE_WITH_INIT
  #include "union_find.h"
  #include "join_grid.h"
%}

%include "numpy.i"
%init %{
import_array();
%}

%apply (int DIM1, int DIM2, signed char* INPLACE_ARRAY2) {(int height, int width, signed char* arr)};

%include "union_find.h"
%include "join_grid.h"
