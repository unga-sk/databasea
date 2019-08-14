#!python

# params:
#   host
#   port
#   database
#   user
#   pass
#
# example call:
#   get-db-structure.py --host 12.3.0.4 --port 5432 --database palshare --user milan.munko --passwd ''
#
# depends on:
#   pg_dump

import argparse
import sqlalchemy
import os

if __name__ == "__main__":
    
    #parse args
    parser=argparse.ArgumentParser()
    parser.add_argument('--host', help='database host', default='12.3.0.4')
    parser.add_argument('--port', help='database port', default='5432')
    parser.add_argument('--database', help='database name')
    parser.add_argument('--user', help='database user', default='postgres')
    parser.add_argument('--passwd', help='database password', default='')
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
        tables = conn.execute('''
            select table_schema, table_name
            from information_schema.tables
            where table_type = 'BASE TABLE'
            and table_schema in (select schema_name
                                from information_schema.schemata
                                where schema_owner != 'postgres'
                                    or schema_name = 'public')
            order by table_schema, table_name''').fetchall()

        matviews = conn.execute('''
            select schemaname, matviewname
            from pg_matviews
            where schemaname in (select schema_name
                                from information_schema.schemata
                                where schema_owner != 'postgres'
                                    or schema_name = 'public')
            order by schemaname, matviewname;''').fetchall()

        conn.close()
        
        for table in tables:
            print('Exporting table definition of {}.{}'.format(table[0], table[1]))
            if not os.path.exists('./structure/tables/{}'.format(table[0])):
                os.makedirs('./structure/tables/{}'.format(table[0]))
            command = 'PGPASSWORD={4} pg_dump -h {0} -p {1} -U {3} -d {2} -t \'{5}.{6}\' --schema-only > ./structure/tables/{5}/{6}.sql'.format(args.host, args.port, args.database, args.user, args.passwd, table[0], table[1])
            os.system(command)

        for matview in matviews:
            print('Exporting matview definition of {}.{}'.format(matview[0], matview[1]))
            if not os.path.exists('./structure/mat-views/{}'.format(matview[0])):
                os.makedirs('./structure/mat-views/{}'.format(matview[0]))
            command = 'PGPASSWORD={4} pg_dump -h {0} -p {1} -U {3} -d {2} -t \'{5}.{6}\' --schema-only > ./structure/mat-views/{5}/{6}.sql'.format(args.host, args.port, args.database, args.user, args.passwd, matview[0], matview[1])
            os.system(command)

    except Exception as e:
        raise e

    print('Done.')