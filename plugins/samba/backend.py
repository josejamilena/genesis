import os
import shutil

from genesis.api import *
from genesis.com import *
from genesis.utils import *


class SambaConfig(Plugin):
    implements(IConfigurable)
    name = 'Samba'
    id = 'samba'
    iconfont = 'gen-upload-2'
    shares = {}
    general = {}
    users = {}

    general_defaults = {
        'server string': '',
        'workgroup': 'WORKGROUP',
        'interfaces': ''
    }

    defaults = {
        'browseable': 'yes',
        'valid users': '',
        'path': '',
        'read only': 'yes',
        'guest ok': 'yes',
        'only guest': 'no'
    }

    editable = {
        'Account Flags': '-c',
        'User SID': '-U',
        'Primary Group SID': '-G',
        'Full Name': '-f',
        'Home Directory': '-h',
        'HomeDir Drive': '-D',
        'Logon Script': '-S',
        'Profile Path': '-p',
        'Kickoff time': '-K'
    }

    fields = []

    def __init__(self):
        self.cfg_file = self.app.get_config(self).cfg_file
        if not os.path.exists(self.cfg_file):
            shutil.copyfile('/etc/samba/smb.conf.default', self.cfg_file)

    def list_files(self):
        return [self.cfg_file]

    def load(self):
        self.shares = {}

        if os.path.exists(self.cfg_file):
            fn = self.cfg_file
        else:
            fn = self.cfg_file + '.default'
        ss = ConfManager.get().load('samba', fn).split('\n')
        cs = ''
        for s in ss:
            s = s.strip()
            try:
                if s[0] != '#' and s[0] != ';':
                    if s[0] == '[':
                        cs = s[1:-1]
                        if cs == 'homes' or cs == 'printers':
                            continue
                        else:
                            self.shares[cs] = self.new_share() if cs != 'global' else self.general_defaults.copy()
                    else:
                        s = s.split('=')
                        self.shares[cs][s[0].strip()] = s[1].strip()
            except:
                pass

        self.general = self.shares['global']
        self.shares.pop('global')

        self.users = {}
        ss = [s.split(',')[0].split(':')[0] for s in shell('pdbedit -L').split('\n')]
        for s in ss:
            if s != '':
                x = shell('pdbedit -L -v -u ' + s).split('\n')
                self.users[s] = {}
                self.fields = []
                for l in x:
                    try:
                        self.users[s][l.split(':')[0]] = l.split(':')[1].strip()
                        self.fields.append(l.split(':')[0])
                    except:
                        pass


    def save(self):
        print self.shares
        ss = ''
        ss += '[global]\n'
        for k in self.general:
            if not k in self.general_defaults or \
                self.general[k] != self.general_defaults[k]:
                ss += '\t%s = %s\n' % (k,self.general[k])
        for s in self.shares:
            ss += '\n[%s]\n' % s
            for k in self.shares[s]:
                #if not k in self.defaults or self.shares[s][k] != self.defaults[k]:
                ss += '\t%s = %s\n' % (k,self.shares[s][k])
        ConfManager.get().save('samba', self.cfg_file, ss)
        ConfManager.get().commit('samba')

    def modify_user(self, u, p, v):
        shell('pdbedit -r -u %s %s "%s"' % (u,self.editable[p],v))

    def del_user(self, u):
        shell('pdbedit -x -u ' + u)

    def add_user(self, u, p):
        shell_stdin('smbpasswd -as %s' % u, p+'\n'+p+'\n')

    def get_shares(self):
        return self.shares.keys()

    def new_share(self):
        return self.defaults.copy()

    def set_param(self, share, param, value):
        if share == 'general':
            self.general[param] = value
        else:
            self.shares[share][param] = value

    def set_param_from_vars(self, share, param, vars):
        if share == 'general':
            value = vars.getvalue(param, self.general_defaults[param])
        else:
            value = vars.getvalue(param, self.defaults[param])
        self.set_param(share, param, value)

    def set_param_from_vars_yn(self, share, param, vars):
        if share == 'general':
            value = 'yes' if vars.getvalue(param, self.general_defaults[param]) == '1' else 'no'
        else:
            value = 'yes' if vars.getvalue(param, self.defaults[param]) == '1' else 'no'
        self.set_param(share, param, value)


class GeneralConfig(ModuleConfig):
    target=SambaConfig
    platform = ['debian', 'centos', 'arch', 'arkos', 'gentoo', 'mandriva']
    
    labels = {
        'cfg_file': 'Configuration file'
    }
    
    cfg_file = '/etc/samba/smb.conf'
   
   
class BSDConfig(GeneralConfig):
    implements((IModuleConfig, -100))
    platform = ['freebsd']
    
    cfg_file = '/usr/local/etc/samba/smb.conf'

