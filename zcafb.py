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
    version='%(prog)s 1.2')

args = parser.parse_args()

def timestamp_to_datetime(timestamp):
    if timestamp >=0:
        return datetime.datetime.fromtimestamp(timestamp)
    else: # Workaround for Windows 
        return datetime.datetime(1970,1,1) + datetime.timedelta(seconds=int(timestamp))

def rename_folder(c, undo):
    print "Renaming folders..."
    paths=[]
    for row in c.execute('SELECT ZPATIENTID, ZFIRSTNAME, ZLASTNAME, ZGENDER, strftime("%Y-%m-%d",ZDOB), ZDOB, strftime("%Y-%m-%d",\'now\') FROM ZPATIENTINFO'):
        original_path=row[0]
        time1 = timestamp_to_datetime(row[5]+978307200 + 12*60*60)
        #print row[5],row[5]+978307200+12*60*60, time1
        human_path=", ".join([row[2],row[1],row[3], "(" + "-".join([str(time1.year),str(time1.month).zfill(2),str(time1.day).zfill(2)]) + ")",row[0]])
        paths.append((original_path,human_path))
    return paths


def rename_files(c, undo):
    paths_dictionaries=rename_folder(conn.cursor(), args.undo)
    print "Renaming files..."
    
    for row in c.execute('SELECT ZISARCHIVED, ZLASTMODIFIEDDATE, ZRECORDPATH FROM ZVISITRECORDS'):
        old_full_path_with_filename = row[2].split("/")[-2:]
        extension = old_full_path_with_filename[1].split(".")[-1:][0]
        old_relative_path = old_full_path_with_filename[0]
        old_filename = old_full_path_with_filename[1]
        new_relative_path = ""
        
        for key,value in paths_dictionaries:
            if key == old_relative_path:
                new_relative_path = value
                break
        
        t = time.localtime(row[1] + datetime.timedelta(365 * 31 + 8).total_seconds())
        try:
            microseconds = str(row[1]).split(".")[1]
        except:
            microseconds="0"
        new_filename = os.sep.join(
            ["%s %s.%s" % (time.strftime("%Y-%m-%d %H-%M-%S", t), microseconds.zfill(3), extension)])
            
        if row[0]:
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
        
        try:
            if not args.dryrun:
                if(os.path.isfile(src)):
                    if (os.path.isfile(dst)):
                        if args.verbose:
                            print "Overwriting %s to %s" % (src, dst)
                            os.remove(dst)
                    else:
                        if args.verbose:
                            print "Renaming %s to %s" % (src, dst)
                    os.renames(src, dst)
                else:
                    print "Source not found, skip renaming %s to %s" % (src, dst)
                    
        except Exception as ex:
            print "Error occured when renaming %s to %s" % (src, dst)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print message


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
