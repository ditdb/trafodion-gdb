
import os
import sys
import gdb

class PRel(gdb.Command):
    """Parse and print tree struct."""

    def __init__ (self):
        super (PRel, self).__init__ ("PRel", gdb.COMMAND_USER)

    def invoke (self, arg, from_tty):
        self.level = 0
        self.val = gdb.parse_and_eval(arg)
        
        if self.val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        if self.val.type.code == gdb.TYPE_CODE_PTR:
            self.val = self.val.dereference()

        #print(self.val.dynamic_type)
        #print(self.get_text(self.val))
        #print(self.get_oper(self.val))
        #print(self.get_arity(self.val))
        self.display(self.val, self.level)
        self.display_input_vars(self.val, self.level)
        self.display_output_vars(self.val, self.level)
        #print("-{0}".format(current.dynamic_type))

    def get_call_str(self, val, method, param=None):
        call_str = ("(*(" + str(val.dynamic_type) + "*)" + 
               "(" + str(val.address) + "))." + method)
        if param == None:
            call_str = call_str + "()"
        else:
            call_str = call_str + "(" + param + ")"

        return call_str

    def get_call_ptr_str(self, val, method, param=None):
        call_str = ("((" + str(val.dynamic_type) + "*)" + 
               "(" + str(val.address) + "))->" + method)
        if param == None:
            call_str = call_str + "()"
        else:
            call_str = call_str + "(" + param + ")"

        return call_str

    def get_data_str(self, val, data):
        data_str = ("(*(" + str(val.dynamic_type) + "*)" + 
                    "(" + str(val.address) + "))." + data)
        
        return data_str

    def get_data_ptr_str(self, val, data):
        data_str = ("((" + str(val.dynamic_type) + "*)" + 
                    "(" + str(val.address) + "))->" + data)
        
        return data_str
    
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
        
        info = (prefix + '|   ' * level + '|-- ' +
                self.get_text(val) + ": " + str(self.get_oper(val)))
        print(info)
        
        arity = self.get_arity(val)
        iter = 0
        while iter < arity:
            child = self.get_child(val, iter)
            self.display(child, level + 1)
            iter += 1
    
    def get_input_entry_num(self, val):
        entries_call_str = (self.get_data_str(val, 'inputVars_') +
                            '.entries()')
        #print(entries_call_str)
        entries = gdb.parse_and_eval(entries_call_str)

        return entries

    def get_input_entry(self, val, index):
        entry_call_str = (self.get_data_str(val, 'inputVars_') +
                          '[' + str(index) + ']' + '.getItemExpr()')
        entry = gdb.parse_and_eval(entry_call_str)

        return entry.dereference()
    
    def display_input_vars(self, val, level):
        if str(val.dynamic_type) == 'RelRoot':
            entries_num = self.get_input_entry_num(val)
            if entries_num <= 0:
                print('Input: None')
            else:
                iter = 0;
                while iter < entries_num:
                    print('Input ' + str(iter) + ': ')
                    entry = self.get_input_entry(val, iter)
                    self.display(entry, level)
                    iter += 1
        else:
            print('Input: None')

    def get_output_entry_num(self, val):
        entries_call_str = (self.get_data_str(val, 'outputVars_') +
                            '.entries()')
        entries = gdb.parse_and_eval(entries_call_str)

        return entries

    def get_output_entry(self, val, index):
        entry_call_str = (self.get_data_str(val, 'outputVars_') +
                          '[' + str(index) + ']' + '.getItemExpr()')
        entry = gdb.parse_and_eval(entry_call_str)

        return entry.dereference()
    
    def display_output_vars(self, val, level):
        if str(val.dynamic_type) == 'RelRoot':
            entries_num = self.get_output_entry_num(val)
            if entries_num <= 0:
                print('Output: None')
            else:
                iter = 0;
                while iter < entries_num:
                    print('Output ' + str(iter) + ': ')
                    entry = self.get_output_entry(val, iter)
                    self.display(entry, level)
                    iter += 1
        else:
            print('Output: None')
    
PRel()
