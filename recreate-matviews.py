#!python

# params:
#   host
#   port
#   database
#   user
#   pass
#
# example call:
#   recreate-matviews.py --host 12.3.0.4 --port 5432 --database palshare --user milan.munko --passwd ''

import argparse
import sqlalchemy
import glob
import subprocess


if __name__ == "__main__":
    
    #parse args
    parser=argparse.ArgumentParser()
    parser.add_argument('--host', help='database host', default='12.3.0.4')
    parser.add_argument('--port', help='database port', default='5432')
    parser.add_argument('--database', help='database name')
    parser.add_argument('--user', help='database user', default='postgres')
    parser.add_argument('--passwd', help='database password', default='')
    args=parser.parse_args()

    engine = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            'postgres', 
            username = args.user, 
            password = args.passwd, 
            database = args.database,
            host = args.host,
            port = args.port
        )
    )

    conn = engine.connect() 

    try:
        print('Dropping materialized views ...')

        matviews = glob.glob('./structure/mat-views/*/*.sql')

        trans = conn.begin()
        for matview in matviews:
            schema = matview.split('/')[-2]
            view = matview.split('/')[-1].split('.')[-2]
            level = matview.split('/')[-1].split('_')[0]

            print('Dropping {}.{}'.format(schema, view))
            
            if level == '00':
                conn.execute('DROP MATERIALIZED VIEW IF EXISTS {}."{}" CASCADE;'.format(schema, view))
            
        trans.commit()

        matviewTree = {}
        for matview in matviews:
            schema = matview.split('/')[-2]
            level = matview.split('/')[-1].split('_')[0]
            view = matview.split('/')[-1].split('.')[-2]

            if level not in matviewTree.keys():
                matviewTree[level] = [matview]
            else:
                matviewTree[level].append(matview)


        print('Building materialized views ...')
        trans = conn.begin()
        for level in matviewTree.keys():
            for matview in matviewTree[level]:
                print('Building {}'.format(matview))
                cmd = "PGPASSWORD={4} PGOPTIONS=\"--client-min-messages=error\" psql -h {0} -p {1} -U {3} -d {2} -f \"{5}\"".format(args.host, args.port, args.database, args.user, args.passwd, matview)
                subprocess.check_call(cmd, shell=True)
            
        trans.commit()

        print('Populating materialized views ...')
        trans = conn.begin()
        for level in matviewTree.keys():
            for matview in matviewTree[level]:
                schema = matview.split('/')[-2]
                view = matview.split('/')[-1].split('.')[-2]
                print('Refreshing materialized view {}.{}'.format(schema, view))
                conn.execute('REFRESH MATERIALIZED VIEW {}."{}"'.format(schema, view))

        trans.commit()

    except Exception as e: 
        trans.rollback()
        raise e

    conn.close()