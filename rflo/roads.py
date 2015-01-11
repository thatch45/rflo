'''
The road stack behaviors
'''

import os
from collections import deque

import ioflo.base.deeding
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
        RoadStack.JoinentTimeout = 0.0

    def action(self):
        '''
        Setup the roadstack, only cal this once with an enter
        '''
        kind = 1
        role = self.opts.value['id']
        name = '{0}_{1}'.format(role, kind)
        main = self.opts.value.get('raet_main', True)
        mutable = self.opts.value.get('raet_mutable', True)
        always = self.opts.value.get('open_mode', True)
        mutable = mutable or always
        uid = None
        basedirpath = os.path.abspath(os.path.join(self.opts.value['cachedir'], name))
        txMsgs = self.txmsgs.value
        rxMsgs = self.rxmsgs.value
        ha = (self.opts.value['interface'], self.opts.value['port'])
        #keep = raet.road.keeping.RoadKeep(basedirpath=basedirpath)
        self.road.value = RoadStack(store=self.store,
                                     name=name,
                                     uid=uid,
                                     ha=ha,
                                     role=role,
                                     main=main,
                                     kind=kind,
                                     #keep=keep,
                                     mutable=mutable,
                                     txMsgs=txMsgs,
                                     rxMsgs=rxMsgs,
                                     period=3.0,
                                     offset=0.5,
                                     auto=True,
                                     dirpath=basedirpath)


class RaftRx(ioflo.base.deeding.Deed):
    Ioinits = {'road': '.raft.road',
               'rxmsgs': '.raft.rxmsgs'}

    def action(self):
        self.road.value.serviceAllRx()
        while self.rxmsgs.value:
            print(self.rxmsgs.value.popleft())


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
        remote = self.opts.value['remote']
        comps = remote.split(':')
        ha = (comps[0], int(comps[1]))
        remote = raet.road.estating.RemoteEstate(self.road.value, fuid=0, sid=0, ha=ha)
        self.road.value.addRemote(remote)


class RaetRoadStackJoiner(ioflo.base.deeding.Deed):
    '''
    Initiates join transaction with master
    FloScript:

    do raet road stack joiner at enter
    '''
    Ioinits = {'stack': '.raft.road',
               'opts': '.etc.opts'}

    def action(self, **kwa):
        '''
        Join with all masters
        '''
        stack = self.stack.value
        if stack and isinstance(stack, RoadStack):
            for remote in stack.remotes.values():
                stack.join(uid=remote.uid, timeout=0.0)


class RaetRoadStackJoined(ioflo.base.deeding.Deed):
    '''
    Updates status with .joined of zeroth remote estate (master)
    FloScript:

    do raet road stack joined
    go next if joined in .raft.status

    '''
    Ioinits = {'inode': '.raft',
               'stack': 'road',
               'status': {'ipath': 'status', 'ival': {'joined': False,
                                                      'allowed': False,
                                                      'alived': False,
                                                      'rejected': False,
                                                      'idle': False,}}}

    def action(self, **kwa):
        '''
        Update .status share
        '''
        stack = self.stack.value
        joined = False
        if stack and isinstance(stack, RoadStack):
            if stack.remotes:
                for remote in stack.remotes.values():
                    joined = any([remote.joined for remote in stack.remotes.values()])
                    print(joined)
        self.status.update(joined=joined)


class RaetRoadStackAllower(ioflo.base.deeding.Deed):
    '''
    Initiates allow (CurveCP handshake) transaction with master
    FloScript:

    do raet road stack allower at enter

    '''
    Ioinits = {
            'inode': '.raft',
            'stack': 'stack'}

    def action(self, **kwa):
        '''
        Receive any udp packets on server socket and put in rxes
        Send any packets in txes
        '''
        stack = self.stack.value
        if stack and isinstance(stack, RoadStack):
            stack.allow(timeout=0.0)
        return None


class RaetRoadStackAllowed(ioflo.base.deeding.Deed):
    '''
    Updates status with .allowed of zeroth remote estate (master)
    FloScript:

    do raet road stack allowed
    go next if allowed in .raft.status

    '''
    Ioinits = {
            'inode': '.raft',
            'stack': 'stack',
            'status': {'ipath': 'status', 'ival': {'joined': False,
                                                   'allowed': False,
                                                   'alived': False,
                                                   'rejected': False,
                                                   'idle': False}}}

    def action(self, **kwa):
        '''
        Update .status share
        '''
        stack = self.stack.value
        allowed = False
        if stack and isinstance(stack, RoadStack):
            if stack.remotes:
                for remote in stack.remotes.values():
                    allowed = any([remote.allowed for remote in stack.remotes.values()])
        self.status.update(allowed=allowed)
