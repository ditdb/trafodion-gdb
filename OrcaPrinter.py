import os
import sys
import re
import gdb

def extendSpace(match):
    return ' ' * int(match.group(1))

class Porca(gdb.Command):
    """Parse and print tree struct."""
    def __init__ (self):
        super (Porca, self).__init__ ('Porca', gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        val = gdb.parse_and_eval(arg)
        if val.address == None or str(val.address) == '0x0':
            print('The pointer is NULL')
            return
        
        call_str = str(arg) + '->DbgStr()'
        self.val = gdb.parse_and_eval(call_str)
        restr = str(self.val['_M_dataplus']['_M_p'])
        restr = re.sub('0x.* L"', '', restr)
        restr = re.sub(r'\\"', '', restr)
        restr = re.sub(r'(.*)"$', '\g<1>', restr)
        restr = re.sub('", . . <repeats ([0-9]*) times>, "', extendSpace, restr)
        restr = re.sub(r'\\n', '\n', restr)
        print(restr)

Porca()
