#!python

from dotenv import load_dotenv
load_dotenv()

import sqlalchemy
import os
import glob
import subprocess

import _recreate_matviews as recreateMatviews

def executeSqlFile(path, conn):
    file=open(path)
    escaped_sql = sqlalchemy.text(file.read())
    conn.execute(escaped_sql)
        

if __name__ == "__main__":

    print('Migrating database {}'.format( os.getenv('CONNECTION_URL').split('@')[1]) )

    print('Connecting to database ...')

    engine = sqlalchemy.create_engine(os.getenv('CONNECTION_URL'))

    conn = engine.connect()  

    try:
        print('Applying migrations ...')

        if engine.dialect.name == 'postgresql':
            defaultSchema = 'public'
            if conn.execute('SELECT NOT EXISTS (SELECT 1 FROM pg_tables WHERE schemaname = \'public\' AND tablename = \'db_version\')').fetchone()[0]:
                trans = conn.begin()
                conn.execute('CREATE TABLE public.db_version ("migration" TEXT PRIMARY KEY, "timestamp" TIMESTAMPTZ DEFAULT NOW(), "user" TEXT DEFAULT CURRENT_USER)')
                trans.commit()
            
            executedMigrations = conn.execute('SELECT "migration" FROM public.db_version ORDER BY "migration"').fetchall()
        
        else:
            raise Exception('UNSUPPORTED DATABASE DIALECT')

        executedMigrations = [migration[0] for migration in executedMigrations]
        
        migrations = glob.glob('./migrations/*')
        migrations = [migration.split('/')[-1] for migration in migrations]

        unappliedMigrations = list(set(migrations) - set(executedMigrations))
        unappliedMigrations.sort()

        for migration in unappliedMigrations:
            print('Applying migration {}'.format(migration))
            
            if 'recreate_matviews' in migration:
                if engine.dialect.name == 'postgresql':
                    recreateMatviews.postgres.recreateMatviews(conn)
            else:
                trans = conn.begin()
                executeSqlFile('./migrations/{}'.format(migration),conn)
                conn.execute('INSERT INTO {}.db_version ("migration", "user") values (\'{}\', \'{}\')'.format(defaultSchema, migration, engine.url.translate_connect_args()['username']))
                trans.commit()

        print('Applying repeatable scripts ...')
        maintenanceSqls = glob.glob('./repeatable/*')
        maintenanceSqls.sort()

        for maintenanceSql in maintenanceSqls:
            print('Applying {}'.format(maintenanceSql.split('/')[-1]))
            trans = conn.begin()
            executeSqlFile(maintenanceSql, conn)
            trans.commit()

        print('Done.')

    except Exception as e: 
        try:
            trans.rollback()
        except:
            pass
        raise e

    conn.close()