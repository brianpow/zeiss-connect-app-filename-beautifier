from distutils.core import setup
import py2exe 

setup(console=['zcafb.py'], options={"py2exe": {"bundle_files": 3, "compressed": True}})