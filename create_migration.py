#!python

import os
import glob
import time
from pathlib import Path
from helper_functions import getFilesFromDirTree

if __name__ == "__main__":
    try:
        os.chdir('./migrations')

        migrationFiles = getFilesFromDirTree('./')

        if len(migrationFiles) > 0:
            try:
                lastFile = sorted(migrationFiles)[-1]
                lastFileName = lastFile.rsplit('/',1)[-1][0:-4].split('_')[0]
                lastIncrement = lastFileName.split('.')[-1]
                lastDate = lastFileName.split('.')[-2]
                lastPrefix = lastFile.rsplit('/',1)[0] + '/' + '.'.join(lastFileName.split('.')[0:-2])
            except:
                lastDate = ''
                lastPrefix = ''
        else:
            lastDate = ''
            lastPrefix = ''

        prefix = input('Enter file prefix (default {}) - optional: '.format(lastPrefix)) or lastPrefix
        if prefix != '' and prefix[-1] != '/':
            prefix = '{}.'.format(prefix)
        
        suffix = input('Enter file suffix - optional: ')
        if suffix != '':
            suffix = '_{}'.format(suffix)

        date = time.strftime('%y%m%d', time.localtime())

        increment = str(int(lastIncrement)+1).zfill(3) if lastDate == date else '001'

        fileName = '{}{}.{}{}.sql'.format(prefix, date, increment, suffix)

        if not os.path.exists(fileName.rsplit('/',1)[0]) and '/' in fileName:
            os.makedirs(fileName.rsplit('/',1)[0])

        Path(fileName).touch()

    except KeyboardInterrupt:
        pass