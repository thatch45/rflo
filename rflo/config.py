'''
Behaviors to generate the config
'''
# Import ioflo
import ioflo.base.deeding

# Import python libs
import copy
import io
import socket
import argparse

# Import third party libs
import yaml

DEFAULTS = {
    'interface': '0.0.0.0',
    'port': 7750,
    'cachedir': '/var/cache/rflo'
    }


class RaftCli(ioflo.base.deeding.Deed):
    '''
    Parse the command line
    '''
    Ioinits = {'cli': '.etc.cli'}

    def action(self):
        '''
        Parse the cli
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument(
                '-p',
                dest='port',
                default='7750',
                type=int,
                )
        parser.add_argument(
                '-i',
                dest='id',
                default=None)
        args = parser.parse_args()
        self.cli.value = args.__dict__

class RaftConfig(ioflo.base.deeding.Deed):
    '''
    Read in the config file
    '''
    Ioinits = {'opts': '.etc.opts',
               'cli': '.etc.cli'}

    def action(self):
        '''
        Read in the config
        '''
        self.opts.value = copy.deepcopy(DEFAULTS)
        self.opts.value.update(self.cli.value)
        path = '/etc/rflo/main'
        try:
            with io.open(path, 'rb') as fp_:
                self.opts.value.update(yaml.safe_load(fp_.read()))
        except (IOError, OSError):
            pass
        if not self.opts.value.get('id'):
            self.opts.value['id'] = socket.getfqdn()
