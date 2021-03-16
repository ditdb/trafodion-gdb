
import os
import sys
import re
import gdb

class BuildCallStr:
    """ build a string to be used by gdb"""
    def __init__(self, val):
        self.val = val
    
    def get_call_str(self, method, param=None):
        call_str = '(*((' + str(self.val.dynamic_type) + '*)(' + \
            str(self.val.address) + '))).' + method
        
        if param == None:
            call_str = call_str + '()'
        else:
            call_str = call_str + '(' + param + ')'

        return call_str

    def get_call_ptr_str(self, method, param=None):
        call_str = '((' + str(self.val.dynamic_type) + '*)(' + \
            str(self.val.address) + '))->' + method
        
        if param == None:
            call_str = call_str + '()'
        else:
            call_str = call_str + '(' + param + ')'

        return call_str

    def get_data_str(self, data):
        data_str = '(*((' + str(self.val.dynamic_type) + '*)(' + \
            str(self.val.address) + '))).' + data
        
        return data_str

    def get_data_ptr_str(self, data):
        data_str = '((' + str(self.val.dynamic_type) + '*)(' + \
            str(self.val.address) + '))->' + data
        
        return data_str

class PNAString(object):
    """NAString."""
    def __init__(self, val):
        self.val = val

    def to_string(self):
        bcs = BuildCallStr(self.val)
        call_str = bcs.get_call_str('data');
        val_str = gdb.parse_and_eval(call_str)
        return val_str.string()

class PCatalogName(object):
    """CatalogName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_catalogName_ = PNAString(self.val['catalogName_'])

    def to_string(self):
        return self.str_catalogName_.to_string()

class PSchemaName(object):
    """SchemaName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_c = PCatalogName(self.val.cast(gdb.lookup_type('CatalogName')))
        self.str_schemaName_ = PNAString(self.val['schemaName_'])

    def to_string(self):
        return self.str_c.to_string() + \
            '.' + self.str_schemaName_.to_string()

class PQualifiedName(object):
    """QualifiedName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_cs = PSchemaName(self.val.cast(gdb.lookup_type('SchemaName')))
        self.str_objectName_ = PNAString(self.val['objectName_'])

    def to_string(self):
        return self.str_cs.to_string() + \
            '.' + self.str_objectName_.to_string()

class PExtendedQualName(object):
    """ExtendedQualName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_qualName_ = PQualifiedName(self.val['qualName_'])

    def to_string(self):
        return self.str_qualName_.to_string()


class PCorrName(object):
    """CorrName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_qualName_ = PExtendedQualName(self.val['qualName_'])
        self.str_corrName_ = PNAString(self.val['corrName_'])
        self.str_ugivenName_ = PNAString(self.val['ugivenName_'])

    def get_qualName():
        return self.str_qualName_.to_string()
    
    def to_string(self):
        return 'qualName: ' + self.str_qualName_.to_string() + '\n' + \
            'corrName: ' + self.str_corrName_.to_string() + '\n' + \
            'ugivenName: ' + self.str_ugivenName_.to_string()

class PColRefName(object):
    """ColRefName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_corrName_ = PCorrName(self.val['corrName_'])
        self.str_colName_ = PNAString(self.val['colName_'])

    def to_string(self):
        return self.str_corrName_.get_qualName() + '.' + \
            self.str_colName_.to_string()

class PTableRefName(object):
    """TableRefName."""
    def __init__(self, val):
        self.val = val
        if val.type.code == gdb.TYPE_CODE_REF:
            self.val = self.val.referenced_value()
        self.str_tableCorr_ = PCorrName(self.val['tableCorr_'])
        self.str_tableName_ = PNAString(self.val['tableName_'])
        self.str_refName_ = PNAString(self.val['refName_'])

    def to_string(self):
        return self.str_tableCorr_.to_string + '\n' + \
            'tableName: ' + self.str_tableName_.to_string() + '\n' + \
            'refName: ' + self.str_refName_.to_string()
    
def register_lookup(val):
    type_name = str(val.type)
    if type_name == 'NAString' or \
       type_name == 'const NAString' :
        return PNAString(val)
    elif type_name == 'CatalogName' or \
         type_name == 'const CatalogName':
        return PCatalogName(val)
    elif type_name == 'SchemaName' or \
         type_name == 'const SchemaName':
        return PSchemaName(val)
    elif type_name == 'QualifiedName' or \
         type_name == 'const QualifiedName':
        return PQualifiedName(val)
    elif type_name == 'ExtendedQualName' or \
         type_name == 'const ExtendedQualName':
        return PExtendedQualName(val)
    elif type_name == 'CorrName' or \
         type_name == 'const CorrName':
        return PCorrName(val)
    elif type_name == 'ColRefName' or \
         type_name == 'const ColRefName':
        return PColRefName(val)
    elif type_name == 'TableRefName' or \
         type_name == 'const TableRefName':
        return PTableRefName(val)
    return None

#register printers
gdb.pretty_printers.append(register_lookup)
