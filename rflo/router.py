'''
The core message routing
'''

import ioflo.base.deeding


class RaftRouter(ioflo.base.deeding.Deed):
    Ioinits = {
            'opts': '.etc.opts',
            'txmsgs': '.raft.txmsgs',
            'rxmsgs': '.raft.rxmsgs',
            }

    def action(self):
        '''
        Route messages
        '''
        # Just make sure it works for now
        while self.rxmsgs.value:
            print(self.rxmsgs.value.popleft())
