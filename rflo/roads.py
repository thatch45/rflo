'''
The road stack behaviors
'''

import os
from collections import deque

import ioflo.base.deeding.Deed
from raet import raeting
from raet.road.stacking import RoadStack
import raet.keeping

class RaftRoadStackSetup(ioflo.base.deeding.Deed):
    '''
    Init the main road stack to use
    '''
    Ioinits = {
            'inode': 'raft.',
            'road': 'road',
            'txmsgs': {'ipath': 'txmsgs',
                       'ival': deque()},
            'rxmsgs': {'ipath': 'rxmsgs',
                       'ival': deque()},
            'opts': '.etc.opts',
            }

    def postinitio(self):
        '''
        Assign default stack values
        '''
        RoadStack.Bk = raeting.bodyKinds.msgpack
        RoadStack.JoinentTimeout = 0.0

    def action(self):
        '''
        Setup the roadstack, only cal this once with an enter
        '''
        kind = self.opts.value.get('kind', 'raft')
        role = self.opts.value['id']
        name = '{0}_{1}'.format(role, kind)
        main = self.opts.value.get('raet_main', self.local.data.main)
        mutable = self.opts.value.get('raet_mutable', self.local.data.mutable)
        always = self.opts.value.get('open_mode', False)
        mutable = mutable or always
        uid = None
        basedirpath = os.path.abspath(os.path.join(self.opts.value['cachedir'], 'raet'))
        txMsgs = self.txmsgs.value
        rxMsgs = self.rxmsgs.value
        keep = raet.keeping.Keep(basedirpath)
        ha = (self.opts.value['interface'], self.opts.value['port'])
        self.road.value = RoadStack(store=self.store,
                                     keep=keep,
                                     name=name,
                                     uid=uid,
                                     ha=ha,
                                     role=role,
                                     main=main,
                                     kind=kind,
                                     mutable=mutable,
                                     txMsgs=txMsgs,
                                     rxMsgs=rxMsgs,
                                     period=3.0,
                                     offset=0.5)


class RaftRx(ioflo.base.deeding.Deed):
    Ioinits = {'road': '.raft.road'}

    def action(self):
        self.road.value.serviceAllRx()


class RaftTx(ioflo.base.deeding.Deed):
    Ioinit = {'road': '.raft.road'}

    def action(self):
        self.road.value.serviceAllTx()
