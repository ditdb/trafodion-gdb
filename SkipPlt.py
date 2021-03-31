
import os
import sys
import gdb
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#from StringIO import StringIO

class SkipPlt(gdb.Command):
    """Greet the whole world."""

    def __init__ (self):
        super (SkipPlt, self).__init__ ('Splt', gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        lines=gdb.execute('info break', True, True)
        for l in StringIO(lines).readlines():
            if '@plt' in l:
                bp=l.split()[0]
                gdb.execute('disa {0}'.format(bp))
                print('disabling {0}'.format(bp))

SkipPlt()
