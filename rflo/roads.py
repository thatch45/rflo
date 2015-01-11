'''
The road stack behaviors
'''
# Import python libs
import os
from collections import deque

# Import raet/ioflo libs
import ioflo.base.deeding
from raet.road.stacking import RoadStack
import raet.road.estating


class RaetRoadStackSetup(ioflo.base.deeding.Deed):
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
                                     auto=True,
                                     dirpath=basedirpath)


class RaetRx(ioflo.base.deeding.Deed):
    '''
    Behavior to recive inbound messages
    '''
    Ioinits = {'road': '.raft.road',
               'rxmsgs': '.raft.rxmsgs'}

    def action(self):
        self.road.value.serviceAllRx()


class RaetTx(ioflo.base.deeding.Deed):
    '''
    Behavior to send outbount messages
    '''
    Ioinits = {'road': '.raft.road'}

    def action(self):
        self.road.value.serviceAllTx()


class RaetAddRemote(ioflo.base.deeding.Deed):
    '''
    Behavior to add the remote specified in the config/cli
    '''
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
    Ioinits = {'road': '.raft.road'}

    def action(self, **kwa):
        '''
        Join with all masters
        '''
        road = self.road.value
        if road and isinstance(road, RoadStack):
            for remote in road.remotes.values():
                road.join(uid=remote.uid, timeout=0.0)


class RaetRoadStackJoined(ioflo.base.deeding.Deed):
    '''
    Updates status with .joined of zeroth remote estate (master)
    FloScript:

    do raet road stack joined
    go next if joined in .raft.status

    '''
    Ioinits = {'inode': '.raft',
               'road': 'road',
               'status': {'ipath': 'status', 'ival': {'joined': False,
                                                      'allowed': False,
                                                      'alived': False,
                                                      'rejected': False,
                                                      'idle': False,}}}

    def action(self, **kwa):
        '''
        Update .status share
        '''
        road = self.road.value
        joined = False
        if road and isinstance(road, RoadStack):
            if road.remotes:
                for remote in road.remotes.values():
                    joined = any([remote.joined for remote in road.remotes.values()])
        self.status.update(joined=joined)


class RaetRoadStackAllower(ioflo.base.deeding.Deed):
    '''
    Initiates allow (CurveCP handshake) transaction with master
    FloScript:

    do raet road stack allower at enter

    '''
    Ioinits = {
            'inode': '.raft',
            'road': 'road'}

    def action(self, **kwa):
        '''
        Receive any udp packets on server socket and put in rxes
        Send any packets in txes
        '''
        road = self.road.value
        if road and isinstance(road, RoadStack):
            road.allow(timeout=0.0)
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
            'stack': 'road',
            'status': {'ipath': 'status', 'ival': {'joined': False,
                                                   'allowed': False,
                                                   'alived': False,
                                                   'rejected': False,
                                                   'idle': False}}}

    def action(self, **kwa):
        '''
        Update .status share
        '''
        road = self.road.value
        allowed = False
        if road and isinstance(road, RoadStack):
            if road.remotes:
                for remote in road.remotes.values():
                    allowed = any([remote.allowed for remote in road.remotes.values()])
        self.status.update(allowed=allowed)


class RaetRoadStackStarted(ioflo.base.deeding.Deed):
    '''
    Send a started ping to all remotes
    '''
    Ioinits = {
            'road': '.raft.road',
            }

    def action(self):
        '''
        Send an initial message on the connection
        '''
        for remote in self.road.value.remotes.values():
            self.road.value.message({'Started': True}, remote.uid)
