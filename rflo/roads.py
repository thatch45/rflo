'''
The road stack behaviors
'''

import os
from collections import deque

import ioflo.base.deeding
from raet import raeting
from raet.road.stacking import RoadStack
import raet.road.estating


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
        main = self.opts.value.get('raet_main', False)
        mutable = self.opts.value.get('raet_mutable', False)
        always = self.opts.value.get('open_mode', False)
        mutable = mutable or always
        uid = None
        basedirpath = os.path.abspath(os.path.join(self.opts.value['cachedir'], name))
        txMsgs = self.txmsgs.value
        rxMsgs = self.rxmsgs.value
        ha = (self.opts.value['interface'], self.opts.value['port'])
        self.road.value = RoadStack(store=self.store,
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
                                     offset=0.5,
                                     dirpath=basedirpath)


class RaftRx(ioflo.base.deeding.Deed):
    Ioinits = {'road': '.raft.road'}

    def action(self):
        self.road.value.serviceAllRx()
        while self.road.value.txmsgs:
            print(self.road.value.txmsgs.popleft())


class RaftTx(ioflo.base.deeding.Deed):
    Ioinits = {'road': '.raft.road'}

    def action(self):
        self.road.value.serviceAllTx()


class RaftAddRemote(ioflo.base.deeding.Deed):
    Ioinits = {'road': '.raft.road',
               'opts': '.etc.opts'}

    def action(self):
        '''
        '''
        if not self.opts.value.get('remote'):
            return
        self.statck.value.addRemote(
                raet.road.estating.RemoteEstate(
                    self.stack.value,
                    ha=self.opts.value.get('remote')))

        for remote in self.stack.value.nameRemotes:
            self.stack.value.message('foobar', self.stack.value.nameRemotes[remote].uid)
