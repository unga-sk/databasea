#!python

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

import subprocess
import sqlalchemy
import os

if __name__ == "__main__":

    print('Getting structure of database {}'.format(os.getenv('CONNECTION_URL').split('@')[1]))

    print('Connecting to database ...')

    engine = sqlalchemy.create_engine(os.getenv('CONNECTION_URL'))

    conn = engine.connect() 

    try:
        assert engine.dialect.name == 'postgresql', "UNSUPPORTED DATABASE DIALECT"

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
            command = 'pg_dump {0} -t \'{1}.{2}\' --schema-only > ./structure/tables/{1}/{2}.sql'.format(os.getenv('CONNECTION_URL'), table[0], table[1])
            os.system(command)

        for matview in matviews:
            print('Exporting matview definition of {}.{}'.format(matview[0], matview[1]))
            if not os.path.exists('./structure/mat-views/{}'.format(matview[0])):
                os.makedirs('./structure/mat-views/{}'.format(matview[0]))
            command = 'pg_dump {0} -t \'{1}.{2}\' --schema-only > ./structure/mat-views/{1}/{2}.sql'.format(os.getenv('CONNECTION_URL'), matview[0], matview[1])
            os.system(command)

    except Exception as e:
        raise e

    print('Done.')