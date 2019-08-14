#!python

from distutils.core import setup

setup(
	name='databese-devutil',
	author='Milan Munko',
	scripts=['get-db-structure.py',
		'patch-database.py',
		'recreate-matviews.py']
)