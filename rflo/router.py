'''
The core message routing
'''
# Import python libs
import collections

# Import raet/ioflo libs
import ioflo.base.deeding


class RaftRouter(ioflo.base.deeding.Deed):
    Ioinits = {
            'opts': '.etc.opts',
            'txmsgs': '.raft.txmsgs',
            'rxmsgs': '.raft.rxmsgs',
            'work': {
                'ipath': '.raft.work',
                'ival': collections.defaultdict(collections.deque)},
            }

    def action(self):
        '''
        Route messages
        '''
        # Just make sure it works for now
        while self.rxmsgs.value:
            msg, sender = self.rxmsgs.value.popleft()
            if 'share' in msg:
                self.work.value[msg['share']].append((msg, sender))


class RaftWorkClean(ioflo.base.deeding.Deed):
    '''
    Clean up the work queue of any invalid options, this is to prevent any
    unhanddled data from piling up in memory. This empties the work dict
    '''
    Ioinits = {'work', '.raft.work'}

    def action(self):
        '''
        Clear the work of rubbish
        '''
        self.work.value = collections.defaultdict(collections.deque)
