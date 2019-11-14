from libs import *

_scriptdir = ''
_user = ''
_mywidgetspath = ''
_mywidgets_imagepath = ''
_wv_imagepath = ''
_anlagenvpath = ''

def _providePathsAndUser():
    global _scriptdir
    global _user
    global _mywidgets_imagepath
    global _wv_imagepath
    global _mywidgetspath
    global _anlagenvpath

    scriptpath = os.path.realpath(__file__)
    _scriptdir = scriptpath.replace('/utils.py', '')
    _wv_imagepath = _scriptdir + '/images'
    _mywidgetspath = _scriptdir.replace('Wohnungsverwaltung', '/mywidgets')
    _mywidgets_imagepath = _mywidgetspath + '/images'
    _anlagenvpath = scriptpath + '/anlagen'

    # check if a configuration file exists. If so, connect remote, else local.
    configfile = _scriptdir + '/connect_remote'
    _user = 'd02bacec' if os.path.isfile(configfile) else 'test'

_providePathsAndUser()
sys.path.append(_mywidgetspath)

def getUser():
    global _user
    return _user

def getScriptPath():
    global _scriptdir
    return _scriptdir

def getWvImagePath():
    global _wv_imagepath
    return _wv_imagepath

def getMyWidgetsImagePath():
    global _imagepath
    return _imagepath

def getMyWidgetsPath():
    global _mywidgetspath
    return _mywidgetspath

def getAnlagenVPath():
    global _anlagenvpath
    return _anlagenvpath

def test():
    user = getUser()
    print(user)
    user = getUser()
    print(user)

if __name__ == '__main__':
    test()