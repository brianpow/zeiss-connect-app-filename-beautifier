#!/usr/bin/python

import sqlite3
import os
import argparse
import datetime
import time

parser = argparse.ArgumentParser(
    description='Zeiss Connect App Filename Beautifier. Licence: AGPL-v3.0')
parser.add_argument('paths', default=[
                    ''], nargs='*', help='Path of iTunes Backup [default: current working directory]')
parser.add_argument('-d', '--dryrun', dest='dryrun',
                    action='store_true', help='Dry run, don\'t rename any files')
parser.add_argument('-a', '--archive', dest='archive',
                    help='Rename archived file saved by Zeiss Connect App via share folder too')
parser.add_argument('-u', '--undo', dest='undo',
                    action='store_true', help='Undo rename')
parser.add_argument('-v', '--verbose', dest='verbose',
                    action='count', help='Be more verbose')
parser.add_argument(
    '-V',
    '--version',
    action='version',
    version='%(prog)s 1.1')

args = parser.parse_args()


def get_folders(c, undo):
    paths=[]
    for row in c.execute('SELECT ZPATIENTID, ZFIRSTNAME, ZLASTNAME, ZGENDER, strftime("%Y-%m-%d",ZDOB), ZDOB, strftime("%Y-%m-%d",\'now\') FROM ZPATIENTINFO'):
        original_path=row[0]
        human_path=", ".join([row[2],row[1],row[3], "(" + time.strftime("%Y-%m-%d", time.localtime(row[5]+978307200)) + ")",row[0]])
        paths.append((original_path,human_path))
    return paths


def rename_files(c, undo):
    paths_dictionaries=get_folders(conn.cursor(), args.undo)
    full_paths_dictionaries = []
    print "Renaming files..."
    
    for row in c.execute('SELECT * FROM ZVISITRECORDS'):
        old_full_path_with_filename = row[18].split("/")[-2:]
        extension = old_full_path_with_filename[1].split(".")[-1:][0]
        old_relative_path = old_full_path_with_filename[0]
        old_filename = old_full_path_with_filename[1]
        new_relative_path = ""
        
        for key,value in paths_dictionaries:
            if key == old_relative_path:
                new_relative_path = value
                break
        
        t = time.localtime(
            row[14] + datetime.timedelta(365 * 31 + 8).total_seconds())
        microseconds = str(row[15]).split(".")[1]
        new_filename = os.sep.join(
            ["%s %s.%s" % (time.strftime("%Y-%m-%d %H-%M-%S", t), microseconds, extension)])
            
        if row[4]:
            if not args.archive:
                continue
            old_full_path = os.sep.join([args.archive, old_relative_path])
            new_full_path = os.sep.join([args.archive, new_relative_path])
        else:
            old_full_path = os.sep.join([path, old_relative_path])
            new_full_path = os.sep.join([path, new_relative_path])

        if args.undo:
            src = os.sep.join([new_full_path, new_filename])
            dst = os.sep.join([old_full_path, old_filename])
        else:
            dst = os.sep.join([new_full_path, new_filename])
            src = os.sep.join([old_full_path, old_filename])
        
        full_paths_dictionaries.append((src,dst))
        if args.verbose:
            print "Renaming %s to %s" % (src, dst)
        try:
            if not args.dryrun:
                os.renames(src, dst)
        except OSError:
            print "Error occured when renaming %s to %s" % (src, dst)


for path in args.paths:
    path = os.sep.join([path, 'AppDomain-in.zeiss.med.opmicommunicator',
                        'Documents'])
    db = os.sep.join([path, 'SingleViewCoreData.sqlite'])
    if not os.path.isfile(db):
        print "Unable to locate database file at %s" % (db)
        continue

    print "Processing %s..." % (db)
    conn = sqlite3.connect(db)  # ,detect_types=sqlite3.PARSE_DECLTYPES)
    rename_files(conn.cursor(), args.undo)
