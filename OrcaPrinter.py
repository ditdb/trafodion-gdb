import os
import sys
import re
import gdb

class Porca(gdb.Command):
    """Parse and print tree struct."""
    def __init__ (self):
        super (Porca, self).__init__ ('Porca', gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        call_str = str(arg) + '->DbgStr()'
        self.val = gdb.parse_and_eval(call_str)
        restr = str(self.val['_M_dataplus']['_M_p'])
        restr = re.sub('0x.*L', '', restr)
        restr = re.sub(r'\\"', '', restr)
        restr = re.sub(r'\\n', '\n', restr)
        print(restr)

Porca()
