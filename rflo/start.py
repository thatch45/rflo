import ioflo.app.run
import os


class Manager(object):
    '''
    Manage the main ioflo process
    '''
    def __init__(self):
        self.behaviors = ['rflo.config', 'rflo.roads', 'rflo.router']
        self.floscript = os.path.join(os.path.dirname(__file__), 'raft.flo')

    def start(self):
        ioflo.app.run.start(
                name='rflo',
                period=0.01,
                stamp=0.0,
                filepath=self.floscript,
                behaviors=self.behaviors,
                verbose=2,
                )
