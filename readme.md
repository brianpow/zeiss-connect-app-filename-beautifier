# Zeiss Connect App Filename Beautifier

## Background

I experience some difficulties with Zeiss Connect App to archive pictures and videos via SMB. It always gives timeout error for big files. It also does not export file timestamp and patient information so it is extremely difficult to locate the files needed. I prefer to have patient name as folder name and filename in taken date. This script will do it for you. It also supports reverting back to original meaningless filenames.

## Requirement

* Python 2.7 or above
* Tested on Windows, but should work in OSX
* Backup via iTunes with NO password
* My another script - iTunes Backup Filename Unobfuscater

## Usage

### Under Windows

To rename 
```
python ibfu.py "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
python zcafb.py "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
*Please replace XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX with the real folder name found on your computer

*Please add '-a "C:\ARCHIVE"' after zcafb.py if your also want to beautify the filenames in archive (optional)

To undo
```
python zcafb.py -u "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
python ibfu.py -u "%USERPROFILE%\AppData\Roaming\Apple Computer\MobileSync\Backup\XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

For additional features, see help
```
python zcafb.py -h
``` 

## Limitation

- New Connect App will encrypt the SQLite DB and is not currently supported. Unless the key can be found

## Licence
AGPL v3.0