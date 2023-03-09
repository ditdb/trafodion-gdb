import os
import sys
import re
import gdb

class Pmemo(gdb.Command):
    """Parse and print tree struct."""
    def __init__ (self):
        super (Pmemo, self).__init__ ('Pmemo', gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        gdb.execute('frame function PexprOptimize', False, True)
        self.val = gdb.parse_and_eval('eng.m_pmemo->DbgStr()')
        gdb.execute('frame level 0', False, True)
        
        restr = str(self.val['_M_dataplus']['_M_p'])
        restr = re.sub('0x.* L"', '', restr)
        restr = re.sub(r'\\"', '', restr)
        restr = re.sub(r'(.*)"$', '\g<1>', restr)
        restr = re.sub('", . . <repeats ([0-9]*) times>, "', extendSpace, restr)
        restr = re.sub(r'\\n', '\n', restr)
        print(restr)

Pmemo()
