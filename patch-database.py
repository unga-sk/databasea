#!python

# params:
#   host
#   port
#   database
#   user
#   pass
#
# example call:
#   python3 patch_database.py --host 127.0.0.1 --port 5432 --database palshare --user milan.munko --passwd ''

import argparse
import sqlalchemy
import glob
import subprocess

def executeSqlFile(path):
    file=open(path)
    if path[-4:] == '.sql':
        escaped_sql = sqlalchemy.text(file.read())
        conn.execute(escaped_sql)
    elif path[-4:] == '.run':
        line = file.readline()
        while line:
            cmd = "PGPASSWORD={4} psql -h {0} -p {1} -U {3} -d {2} -c \"{5}\"".format(args.host, args.port, args.database, args.user, args.passwd, line)
            subprocess.check_call(cmd, shell=True)
            line = file.readline()
    elif path[-3:] == '.sh':
        subprocess.check_call('/bin/sh -c {}'.format(path), shell=True)
        

if __name__ == "__main__":

    #parse args
    parser=argparse.ArgumentParser()
    parser.add_argument('--host', help='database host', default='postgres.in.ai-maps.com')
    parser.add_argument('--port', help='database port', default='5432')
    parser.add_argument('--database', help='database name')
    parser.add_argument('--user', help='database user', default='postgres')
    parser.add_argument('--passwd', help='database password', default='')
    parser.add_argument('--type', help='operation type', default='upgrade', choices={"upgrade", "patch-only"})
    args=parser.parse_args()


    print('Patching database {3}:{4}@{0}:{1}/{2}'.format(args.host, args.port, args.database, args.user, args.passwd))

    print('Connecting to database ...')

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
        print('Applying patches ...')
        executedPatches = conn.execute('SELECT commit_number FROM public.db_version WHERE type = \'bugfix\' ORDER BY commit_number').fetchall()
        executedPatches = [patch[0] for patch in executedPatches]
        
        patches = glob.glob('./patches/*')
        patches = [patche.split('/')[-1] for patche in patches ]

        unappliedPatches = list(set(patches) - set(executedPatches))
        unappliedPatches.sort()

        for patche in unappliedPatches:
            print('Applying patch {}'.format(patche))
            trans = conn.begin()
            executeSqlFile('./patches/{}'.format(patche))
            conn.execute('INSERT INTO db_version (type, commit_number) values (\'bugfix\',\'{}\')'.format(patche))
            trans.commit()

        if args.type == 'upgrade':
            print('Applying changes ...')
            executedChanges = conn.execute('SELECT commit_number FROM public.db_version WHERE type = \'change\' ORDER BY commit_number').fetchall()
            executedChanges = [patch[0] for patch in executedChanges]

            changes = glob.glob('./develop/*')
            changes = [change.split('/')[-1] for change in changes ]

            unappliedChanges = list(set(changes) - set(executedChanges))
            unappliedChanges.sort()

            for change in unappliedChanges:
                print('Applying change {}'.format(change))
                trans = conn.begin()
                executeSqlFile('./develop/{}'.format(change))
                conn.execute('INSERT INTO db_version (type, commit_number) values (\'change\',\'{}\')'.format(change))
                trans.commit()

        print('Applying repeatable scripts ...')
        maintenanceSqls = glob.glob('./repeatable/*')
        maintenanceSqls.sort()

        for maintenanceSql in maintenanceSqls:
            print('Applying {}'.format(maintenanceSql.split('/')[-1]))
            trans = conn.begin()
            executeSqlFile(maintenanceSql)
            trans.commit()

        print('Done.')

    except Exception as e: 
        trans.rollback()
        raise e

    conn.close()