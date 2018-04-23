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
    version='%(prog)s 1.0')

args = parser.parse_args()


def rename_folder(c, undo):
    print "Renaming folders..."
    for row in c.execute('SELECT ZPATIENTID, ZFIRSTNAME, ZLASTNAME, ZGENDER, strftime("%Y-%m-%d",ZDOB), ZDOB, strftime("%Y-%m-%d",\'now\') FROM ZPATIENTINFO'):
        original_path=row[0]
        human_path=", ".join([row[2],row[1],row[3], "(" + time.strftime("%Y-%m-%d", time.localtime(row[5]+978307200)) + ")",row[0]])
        if undo:
            src = os.sep.join(
                [path, human_path])

            dst = os.sep.join([path, original_path])
            if args.archive:
                src1 = os.sep.join(
                    [args.archive,human_path])
                dst1 = os.sep.join([args.archive, original_path])

        else:
            dst = os.sep.join(
                [path, human_path])
            src = os.sep.join([path, original_path])
            if args.archive:
                dst1 = os.sep.join(
                    [args.archive, human_path])
                src1 = os.sep.join([args.archive, original_path])

        if args.verbose:
            print "Renaming folder %s to %s" % (src, dst)
            if args.archive:
                print "Renaming folder %s to %s" % (src1, dst1)
        try:
            if not args.dryrun:
                os.rename(src, dst)
        except OSError:
            print "Error occured when renaming %s to %s" % (src, dst)

        try:
            if not args.dryrun:
                if args.archive:
                    os.rename(src1, dst1)
        except OSError:
            print "Error occured when renaming %s to %s" % (src, dst)

    return


def rename_files(c, undo):
    # print not args.undo
    if args.undo:
        rename_folder(conn.cursor(), args.undo)

    print "Renaming files..."
    # print args.undo
    for row in c.execute('SELECT * FROM ZVISITRECORDS'):
        file_path = row[16].split("/")[-2:]
        extension = file_path[1].split(".")[-1:][0]
        relative_path = file_path[0]
        original_name = file_path[1]
        t = time.localtime(
            row[14] + datetime.timedelta(365 * 31 + 8).total_seconds())
        microseconds = str(row[14]).split(".")[1]
        new_name = os.sep.join(
            ["%s %s.%s" % (time.strftime("%Y-%m-%d %H-%M-%S", t), microseconds, extension)])
        if row[4]:
            if not args.archive:
                continue
            final_path = os.sep.join([args.archive, relative_path])
        else:
            final_path = os.sep.join([path, relative_path])
        if args.undo:
            src = os.sep.join([final_path, new_name])
            dst = os.sep.join([final_path, original_name])
        else:
            dst = os.sep.join([final_path, new_name])
            src = os.sep.join([final_path, original_name])

        if args.verbose:
            print "Renaming %s to %s" % (src, dst)
        try:
            if not args.dryrun:
                os.rename(src, dst)
        except OSError:
            print "Error occured when renaming %s to %s" % (src, dst)
    if not args.undo:
        rename_folder(conn.cursor(), args.undo)


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
