import os

ROOT_DIR = os.path.dirname( os.path.abspath( __file__ ) )
print( ROOT_DIR )
DATABASE_DIR = ROOT_DIR
DATABASE = ROOT_DIR + "/invest.db"
ICON_DIR = ROOT_DIR + "/images/"