color_patches:
	swig -python color_patches.i
	python setup.py build
	cp build/*/*.so .
