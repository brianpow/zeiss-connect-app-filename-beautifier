#!/usr/bin/python

import sqlite3
import os
import argparse
import platform
import datetime
import time
import logging

def process_begin(db, document_root, args):
    log.info("Processing %s..." % (db))
    conn = sqlite3.connect(db)  # ,detect_types=sqlite3.PARSE_DECLTYPES)
    rename_files(conn, document_root, args)

def main():
    path = os.path.join(os.environ["HOMEPATH"], "Desktop",'EXTARO 300')
    parser = argparse.ArgumentParser(
        description='Zeiss Connect App Filename Beautifier. Licence: AGPL-v3.0')
    parser.add_argument('paths', default=[], nargs='*', help='Path of iTunes Backup [default: current working directory]')
    parser.add_argument('-d', '--dryrun', dest='dryrun',
                        action='store_true', help='Dry run, don\'t rename any files')
    parser.add_argument('-a', '--archive', dest='archive',
                        help='Rename archived file saved by Zeiss Connect App via share folder too  (default: %(default)s)')
    parser.add_argument('-u', '--undo', dest='undo',
                        action='store_true', help='Undo rename (default: %(default)s)')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='count', help='Be more verbose')
    parser.add_argument('-l','--log', 
    default='INFO', 
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help='Set the logging level (default: %(default)s)'
    )
    parser.add_argument('-c','--copy', nargs="?", default=path,
    help='Copy instead of rename (default: %(default)s)'
    )
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 1.2')

    args = parser.parse_args()
    print(args.copy)
    log_level = getattr(logging, args.log.upper(), logging.INFO)
    log.setLevel(log_level)
    
    if len(args.paths):
        for path in args.paths:
            path = os.sep.join([path, 'AppDomain-in.zeiss.med.opmicommunicator',
                                'Documents'])
            db = os.sep.join([path, 'SingleViewCoreData.sqlite'])
            if not os.path.isfile(db):
                log.error("Unable to locate database file at %s" % (db))
                continue

            process_begin(db, args)
    else:
        home = os.path.expanduser("~")
        
        backup_paths = ["."]
        if platform.system() == 'Darwin':
            backup_paths.append(os.sep.join(
                [home, 'Library/Application Support/MobileSync/Backup']))
        elif platform.system() == 'Windows':
            backup_paths.extend([
                os.sep.join([home, r'Apple\MobileSync\Backup']),
                os.sep.join([home, r'Apple Computer\MobileSync\Backup']),
                os.sep.join([home, r'AppData\Roaming\Apple\MobileSync\Backup']),
                os.sep.join([home, r'AppData\Roaming\Apple Computer\MobileSync\Backup'])
            ])

        valid_path = []
        
        for backup_path in backup_paths:
            if os.path.exists(backup_path):
                for folder in os.listdir(backup_path):
                    full_path=os.sep.join([backup_path, folder])
                    
                    if len(folder) == 40 and validate_backup_path(full_path):
                        valid_path.append(full_path)
                    else:
                         log.debug("%s is not a valid backup path" % (full_path))

        if len(valid_path) == 0:
            log.error("Unable to locate database file automatically.")
            return False
        
        if len(valid_path) > 1:
            for i, val in enumerate(valid_path):
                log.info("%2d: %s" % (i, val))
                index = input("Please select a path: ")
                path = valid_path[int(index)]
        elif len(valid_path) == 1:
            path = valid_path[0]
        
        db_root, document_root, file = validate_backup_path(path)
        process_begin(os.sep.join([db_root, file]), document_root, args)
        os.startfile(document_root)
        


def timestamp_to_datetime(timestamp):
    if timestamp >=0:
        return datetime.datetime.fromtimestamp(timestamp)
    else: # Workaround for Windows 
        return datetime.datetime(1970,1,1) + datetime.timedelta(seconds=int(timestamp))

def rename_folder(conn, path, args):
    log.info("Renaming folders...")
    paths=[]
    for row in conn.execute('SELECT ZPATIENTID, ZFIRSTNAME, ZLASTNAME, ZGENDER, strftime("%Y-%m-%d",ZDOB), ZDOB, strftime("%Y-%m-%d",\'now\') FROM ZPATIENTINFO'):
        original_path=row[0]
        time1 = timestamp_to_datetime(row[5]+978307200 + 12*60*60)
        #log.info row[5],row[5]+978307200+12*60*60, time1
        human_path=", ".join([row[2],row[1],row[3], "(" + "-".join([str(time1.year),str(time1.month).zfill(2),str(time1.day).zfill(2)]) + ")",row[0]])
        paths.append((original_path,human_path))
    print(paths)
    return paths

def validate_backup_path(path):
    document_root = os.sep.join([path, 'AppDomain-in.zeiss.med.opmicommunicator',
                        'Documents'])
    db_root = os.sep.join([path, 'AppDomain-in.zeiss.med.opmicommunicator',
                        'Documents','DeleteForLater'])
    files = ["ConnectApp.sqlite", 'SingleViewCoreData.sqlite']
    for db_file in files:
        file = os.sep.join([db_root, db_file])
        if os.path.exists(file):
            return [db_root, document_root, db_file]
            
    return []

def rename_files(conn, path, args):
    paths_dictionaries=rename_folder(conn.cursor(), path, args)
    log.info("Renaming files...")
    
    for row in conn.execute('SELECT ZISARCHIVED, ZLASTMODIFIEDDATE, ZRECORDPATH FROM ZVISITRECORDS'):
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
                            log.info("Overwriting %s to %s" % (src, dst))
                            os.remove(dst)
                    else:
                        if args.verbose:
                            log.info("Renaming %s to %s" % (src, dst))
                    os.renames(src, dst)
                else:
                    log.info("Source not found, skip renaming %s to %s" % (src, dst))
                    
        except Exception as ex:
            log.info("Error occured when renaming %s to %s" % (src, dst))
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            log.info(message)

logging.basicConfig(filename=f'{__name__}.log', level=logging.INFO, format = '%(asctime)s\t%(levelname)s\t%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the handler to the root logger
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

main()