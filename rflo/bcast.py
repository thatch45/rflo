'''
Simple broadcast consensus
'''
# Message comes in with a share of write
# Form the bcast data struct
# Message is queued for consensus algo
# 1. Send write broadcast to all nodes (including local system queue)
# 2. Receiving systems ack broadcast via a broadcast
# 3. All systems count the acks
# 4. When quorum is reached, make the write
# 5. At quorum respond to original requester

# Import python libs
import os
import collections

# Import raet/ioflo libs
import ioflo.base.deeding

W_KEYS = ('owner', 'seq', 'data', 'key')


class WriteRequest(ioflo.base.deeding.Deed):
    '''
    Send a write request to all nodes
    '''
    Ioinits = {'bcast': '.raft.bcast',
               'work': '.raft.work',
               'tracks': '.raft.var.tracks'}

    def postioinit(self):
        self.bcast.value = collections.deque()
        self.tracks.value = {}

    def action(self):
        if 'write' in self.work.value:
            while self.work.value['write']:
                msg, sender = self.work.value['write'].popleft()
                if any(key not in msg for key in W_KEYS):
                    continue
                msg['ctag'] = os.urandom(8)
                msg['share'] = 'write_veri'
                self.bcast.value.append(msg)
                self.tracks.value[msg['ctag']] = {
                        'owner': msg['owner'],
                        'seq': msg['seq'],
                        'key': msg['key'],
                        'sender': sender}


class WriteVeri(ioflo.base.deeding.Deed):
    '''
    Process an initial write request by broadcasting that the request is received
    '''
    Ioinits = {'bcast': '.raft.bcast',
               'work': '.raft.work',
               'votes': {
                   'ipath': '.raft.votes',
                   'ival': collections.defaultdict({})},
              }
    
    def action(self):
        '''
        broadcast out the vote and set up the local vote tracking data
        '''
        if 'write_veri' in self.work.value:
            while self.work.value['write_veri']:
                msg, sender = self.work.value['write_veri'].popleft()
                bmsg = {'share': 'write_vote', 'ctag': msg['ctag']}
                self.bcast.value.append(bmsg)
                self.votes.value[msg['ctag']]['msg'] = msg
                if 'votes' in self.votes.value[msg['ctag']]:
                    self.votes.value[msg['ctag']]['votes'].append('self')
                else:
                    self.votes.value[msg['ctag']]['votes'] = ['self']


class WriteVote(ioflo.base.deeding.Deed):
    '''
    Tally the remote votes for a write
    '''
    Ioinits = {'bcast': '.raft.bcast',
               'work': '.raft.work',
               'votes': {
                   'ipath': '.raft.votes',
                   'ival': collections.defaultdict({})},
              }

    def action(self):
        '''
        Tally the votes and set a write flag if the data is ready to be
        written
        '''
        if 'write_vote' in self.work.value:
            while self.work.value['write_vote']:
                msg, sender = self.work.value['write_vote'].popleft()
                if 'votes' in self.votes.value[msg['ctag']]:
                    self.votes.value[msg['ctag']]['votes'].append(sender)
                else:
                    self.votes.value[msg['ctag']]['votes'] = [sender]


class Bcast(ioflo.base.deeding.Deed):
    '''
    Broadcast the messages on the bcast queue
    '''
    Ioinits = {'bcast': '.raft.bcast',
               'road': '.raft.road'}

    def action(self):
        '''
        '''
        while self.bcast.value:
            for remote in self.road.value.remotes():
                msg = self.bcast.value.popleft()
                self.road.value.message(msg)
