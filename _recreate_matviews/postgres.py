import sqlalchemy
import os
import glob

from patch_database import executeSqlFile

def getMatviews():
    return glob.glob('./structure/mat-views/*/*.sql')

def getMatviewTree():
    matviewTree = {}

    matviews = getMatviews()

    for matview in matviews:
        schema = matview.split('/')[-2]
        level = matview.split('/')[-1].split('_')[0]
        view = matview.split('/')[-1].split('.')[-2]

        if level not in matviewTree.keys():
            matviewTree[level] = [matview]
        else:
            matviewTree[level].append(matview)

    return matviewTree

def populateMatviews(conn):
    try:
        print('Populating materialized views ...')

        matviewTree = getMatviewTree()

        trans = conn.begin()
        for level in matviewTree.keys():
            for matview in matviewTree[level]:
                schema = matview.split('/')[-2]
                view = matview.split('/')[-1].split('.')[-2]
                print('Refreshing materialized view {}.{}'.format(schema, view))
                conn.execute('REFRESH MATERIALIZED VIEW {}."{}"'.format(schema, view))

        trans.commit()
    except Exception as e: 
        raise e

def recreateMatviews(conn):
    try:
        print('Dropping materialized views ...')

        matviews = getMatviews()

        trans = conn.begin()
        for matview in matviews:
            schema = matview.split('/')[-2]
            view = matview.split('/')[-1].split('.')[-2]
            level = matview.split('/')[-1].split('_')[0]

            print('Dropping {}.{}'.format(schema, view))
            
            if level == '00':
                conn.execute('DROP MATERIALIZED VIEW IF EXISTS {}."{}" CASCADE;'.format(schema, view))
            
        trans.commit()

        matviewTree = getMatviewTree()

        print('Building materialized views ...')
        trans = conn.begin()
        for level in matviewTree.keys():
            for matview in matviewTree[level]:
                print('Building {}'.format(matview))
                executeSqlFile(matview,conn)
            
        trans.commit()

    except Exception as e: 
        raise e