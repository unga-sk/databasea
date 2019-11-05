#!python

from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')

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

    doRecreateMatviews = False

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
        
        elif engine.dialect.name == 'mssql':
            defaultSchema = 'dbo'
            if len(conn.execute('SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \'dbo\' AND TABLE_NAME = \'db_version\'').fetchall()) == 0:
                trans = conn.begin()
                conn.execute('CREATE TABLE dbo.db_version ("migration" NVARCHAR(250) PRIMARY KEY, "timestamp" DATETIME DEFAULT CURRENT_TIMESTAMP, "user" NVARCHAR(MAX) DEFAULT CURRENT_USER)')
                trans.commit()

        else:
            raise Exception('UNSUPPORTED DATABASE DIALECT')

        executedMigrations = conn.execute('SELECT "migration" FROM {}.db_version ORDER BY "migration"'.format(defaultSchema)).fetchall()

        executedMigrations = [migration[0] for migration in executedMigrations]
        
        migrations = glob.glob('./migrations/*')
        migrations = [migration.split('/')[-1] for migration in migrations]

        unappliedMigrations = list(set(migrations) - set(executedMigrations))
        unappliedMigrations.sort()

        for migration in unappliedMigrations:
            print('Applying migration {}'.format(migration))
            trans = conn.begin()

            if 'recreate_matviews' in migration:
                doRecreateMatviews = True
                if engine.dialect.name == 'postgresql':
                    recreateMatviews.postgres.recreateMatviews(conn)
            else:
                executeSqlFile('./migrations/{}'.format(migration),conn)

            conn.execute('INSERT INTO {}.db_version ("migration", "user") values (\'{}\', \'{}\')'.format(defaultSchema, migration, engine.url.translate_connect_args()['username']))
            trans.commit()

        if doRecreateMatviews:
            if engine.dialect.name == 'postgresql':
                    recreateMatviews.postgres.populateMatviews(conn)

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
        conn.close()
        raise e

    conn.close()