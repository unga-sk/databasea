#!python

from distutils.core import setup

setup(
	name='databasea',
	author='Milan Munko',
	scripts=[
		'get_db_structure.py',
		'patch_database.py',
		'create_migration.py',
		'databasea_init.py',
		'helper_functions.py'
		],
	packages=['_recreate_matviews']
)