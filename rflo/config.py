'''
Behaviors to generate the config
'''
import ioflo.base.deeding
import yaml
import copy
import io
import socket

DEFAULTS = {
    'interface': '0.0.0.0',
    'port': 7750,
    'cachedir': '/var/cache/rflo'
    }


class RaftConfig(ioflo.base.deeding.Deed):
    '''
    '''
    Ioinits = {'opts': '.etc.opts'}

    def action(self):
        '''
        Read in the config
        '''
        self.opts.value = copy.deepcopy(DEFAULTS)
        path = '/etc/rflo/main'
        try:
            with io.open(path, 'rb') as fp_:
                self.opts.value.update(yaml.safe_load(fp_.read()))
        except (IOError, OSError):
            pass
        if not self.opts.value.get('id'):
            self.opts.value['id'] = socket.getfqdn()
