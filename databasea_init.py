#!python

import os
import subprocess

if __name__ == '__main__':

    if not os.path.exists('.env'):
        subprocess.run(['touch', '.env'])
    
    if not os.path.exists('./migrations'):
        subprocess.run(['mkdir', './migrations'])

    if not os.path.exists('./repeatable'):
        subprocess.run(['mkdir', './repeatable'])

    if not os.path.exists('./structure'):
        subprocess.run(['mkdir', './structure'])

    if not os.path.exists('clear_databse.sql'):
        subprocess.run(['touch', 'clear_databse.sql'])

