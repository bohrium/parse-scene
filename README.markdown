[//]: # (author: samtenka)
[//]: # (change: 2020-03-28)
[//]: # (create: 2020-03-28)
[//]: # (descrp: top-level documentation for our scene parser for ARC grids)
[//]: # (to use: open and read this document in a web browser.)

# parse-scene

Run `make color-patches`, then `python example.py`, to count the number of
color patches in `example.py`'s example grid.  This count is significant
because its square root lower bounds the number of (potentially overlapping,
monochromatic, axis-aligned) rectangles needed to recover a given image, hence
giving us an optimisti notion of progress that can be plugged into A-star.

This array-heavy operation we implement in C
