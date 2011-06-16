import urllib2
import subprocess
import os, sys

from configobj import ConfigObj
from validate import Validator

class Config(object):
    configSpec = os.path.join(os.getenv('TEMP'),'configspec.spec')
    
    def __init__(self, filename):
        self.filename = filename
        self.config = None
        self.username = ""
        self.password = ""
        self.hash = ""
        self.appdata = ""
        
    def writeSpec(self):
        with open(self.configSpec, 'w') as specfile:
            specfile.write('[General]\n')
            specfile.write('username = string(min=3, default="User")\n')
            specfile.write('password = string(min=3, default="Pass")\n')
            specfile.write('hashcache = string(min=3, default="None")\n')
            specfile.write('appdata = string(min=3, default="None")\n')

    def read(self):
        self.config = ConfigObj(self.filename, configspec=self.configSpec)
        validator = Validator()
        self.config.validate(validator, copy=True)

        self.readData()

        if not os.path.exists(self.filename):
            self.writeData()

    def readData(self):
        self.username = self.config['General']['username']
        self.password = self.config['General']['password'] 
        self.hash = self.config['General']['hashcache']
        self.appdata = self.config['General']['appdata']
        
        if self.appdata == "None":
            self.appdata = None
        
    def writeData(self):
        self.config['General']['username'] = self.username
        self.config['General']['password'] = self.password
        self.config['General']['hashcache'] = self.hash
        self.config['General']['appdata'] = self.appdata
        
        self.config.write()

class LoginError(Exception): pass
class BadLogin(LoginError): pass

def getSessionID(user, pass_, conf):
    loginurl = "https://login.minecraft.net/?&user={0}&password={1}&version=9999"
    data = urllib2.urlopen(loginurl.format(user, pass_))
    retn = data.read().strip("\r\n")
    
    if ":" in retn:
        parts = retn.split(":")
        gamever = parts[0]
        downloadticket = parts[1]
        username = parts[2]
        session = parts[3]
        conf.hash = session
        conf.writeData()
        return True
        
    return False
        
def launchMC(user=None, session=None, appdata=None):
    if appdata:
        appdata = os.path.abspath(appdata)
        os.putenv("APPDATA", appdata)
    else:
        appdata = os.getenv("APPDATA")
        
    line = r'java -cp "{0}\.minecraft\bin\*" ' + \
        r'-Djava.library.path="{0}\.minecraft\bin\natives" ' + \
        r'net.minecraft.client.Minecraft'
     
    line = line.format(appdata)
    
    if user and session:
        line += ' "{0}" "{1}"'.format(user, session)

    mc = subprocess.Popen(line)
    mc.wait()
    
    if mc.returncode:
        print "oops! please make sure {0} contains the binaries required!".format(appdata)
    
if __name__ == "__main__":
    config = Config("config.ini")
    config.writeSpec()
    config.read()

    print "attempting to log in..."
    
    try:
        if not getSessionID(config.username, config.password, config):
            print "bad login, or failed login too many times."
            sys.exit(1)

    except urllib2.URLError, e:
        print "login site not available, using old hash: {0}".format(e)
        
    print "launching... ({0})".format(config.hash)

    if config.appdata and not os.path.exists(config.appdata):
        os.mkdir(config.appdata)

    launchMC(config.username, config.hash, config.appdata)
        