#!python

import os
import glob
import time
from pathlib import Path

if __name__ == "__main__":
    os.chdir('./migrations')

    lastFile = sorted(glob.glob('*'))[-1][0:-4].split('_')[0]
    lastIncrement = lastFile.split('.')[-1]
    lastDate = lastFile.split('.')[-2]
    lastPrefix = '.'.join(lastFile.split('.')[0:-2])

    prefix = input('Enter file prefix (default {}) - optional: '.format(lastPrefix)) or lastPrefix
    if prefix != '':
        prefix = '{}.'.format(prefix)
    
    suffix = input('Enter file suffix - optional: ')
    if suffix != '':
        suffix = '_{}'.format(suffix)

    date = time.strftime('%y%m%d', time.localtime())

    increment = str(int(lastIncrement)+1).zfill(3) if lastDate == date else '001'

    fileName = '{}{}.{}{}.sql'.format(prefix, date, increment, suffix)

    Path(fileName).touch()