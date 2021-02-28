
import os
import sys
import gdb
import base64

class PValueIdSet(gdb.Command):
    """Parse and print ValueIdList."""

    def __init__ (self):
        super (PValueIdSet, self).__init__ ('Pvis', gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        self.level = 0
        self.val = gdb.parse_and_eval(arg)
        
        if self.val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        elif self.val.type.code == gdb.TYPE_CODE_PTR:
            self.val = self.val.dereference()
        elif self.val.type.code == TYPE_CODE_STRUCT:
            pass
        else:
            print('Unknown Type')
            return
        
        self.display_entries(self.val, self.level)
        
    def get_call_str(self, val, method, param=None):
        if val.address != None:
            call_str = '(*((' + str(val.dynamic_type) + '*)(' + \
                str(val.address) + '))).' + method
        else:
            call_str = '(*((ItemExpr *)(' + str(val) + '))).' + method
        
        if param == None:
            call_str = call_str + '()'
        else:
            call_str = call_str + '(' + param + ')'

        return call_str

    def get_data_str(self, val):
        if val.address != None:
            data_str = '(*((' + str(val.dynamic_type) + '*)(' + \
                str(val.address) + ')))'
        else:
            data_str = '(*((ItemExpr *)(' + str(val) + ')))'
        
        return data_str

    def get_entries_num(self, val):
        entries_call_str = self.get_data_str(val) + '.entries_'
        entries = gdb.parse_and_eval(entries_call_str)
        
        return entries
    
    def display_entries(self, val, level):
        entries = self.get_entries_num(val)
        if entries > 0:
            mallocIter = '(ValueId *)calloc(4, 1)'
            iterPtr = gdb.parse_and_eval(mallocIter)
            iter = 0;
            while iter < entries:
                gdb.parse_and_eval(self.get_call_str(self.val, \
                    'next', '*(ValueId*)(' + str(iterPtr) + ')'))
                
                itemPtr = gdb.parse_and_eval('((ValueId*)(' +
                    str(iterPtr) + '))->getItemExpr()')
                print('Entries:' + str(iter) + ':')
                self.display(itemPtr, level)

                gdb.parse_and_eval(self.get_call_str(self.val, \
                    'advance', '*(ValueId*)(' + str(iterPtr) + ')'))
                iter += 1
            
            freeIter = '(void)free((ValueId *)' + str(iterPtr) + ')'
            gdb.parse_and_eval(freeIter)
        else:
            print('Entries: None')
    
    def get_text(self, val):
        str_call_str = (self.get_call_str(val, 'getText') + '.data()')
        val_str = gdb.parse_and_eval(str_call_str)

        return val_str.string()

    def get_oper(self, val):
        oper_call_str = self.get_call_str(val, 'getOperatorType')

        oper = gdb.parse_and_eval(oper_call_str)

        return oper

    def get_arity(self, val):
        arity_call_str = self.get_call_str(val, 'getArity')
        arity = gdb.parse_and_eval(arity_call_str)

        return arity

    def get_child(self, val, index):
        child_call_str = self.get_call_str(val, 'getChild', str(index))
        child = gdb.parse_and_eval(child_call_str)

        return child.dereference()
    
    def display(self, val, level):
        prefix = ''
        if level == 0:
            prefix = '.\n'
        
        info = prefix + '|   ' * level + '|-- ' + \
            self.get_text(val) + ": " + str(self.get_oper(val))
        print(info)
        
        arity = self.get_arity(val)
        iter = 0
        while iter < arity:
            child = self.get_child(val, iter)
            self.display(child, level + 1)
            iter += 1
    
PValueIdSet()
