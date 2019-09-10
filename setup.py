#!python

from distutils.core import setup

setup(
	name='databese-devutil',
	author='Milan Munko',
	scripts=['get_db_structure.py',
		'patch_database.py',
		'create_migration.py'],
	packages=['_recreate_matviews']
)