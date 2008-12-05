class HtmlAttributeHolder(object):
    def __init__(self, **kwargs):
        #: a dictionary that represents html attributes
        self.attributes = kwargs
        
    def set_attrs(self, **kwargs ):
        self.attributes.update(kwargs)
        
    def set_attr(self, key, value):
        self.attributes[key] = value
        
    def del_attr(self, key):
        del self.attributes[key]
    
    def get_attrs(self):
        return self.attributes
    
    def get_attr(self, attr):
        return self.attributes[attr]
    
class StringIndentHelper(object):

    def __init__(self):
        self.output = []
        self.level = 0
        self.indent_with = '    '
    
    def dec(self, value):
        self.level -= 1
        return self.render(value)
            
    def inc(self, value):
        self.render(value)
        self.level += 1
    
    def __call__(self, value, **kwargs):
        self.render(value)
    
    def render(self, value, **kwargs):
        self.output.append('%s%s' % (self.indent(**kwargs), value) )
    
    def indent(self, level = None):
        if level == None:
            return self.indent_with * self.level
        else:
            return self.indent_with * self.level
    
    def get(self):
        retval = '\n'.join(self.output)
        self.output = []
        return retval

def is_empty(value):
    if not value and value is not 0 and value is not False:
        return True
    return False

def multi_pop(d, *args):
    retval = {}
    for key in args:
        if d.has_key(key):
            retval[key] = d.pop(key)
    return retval

class NotGivenBase(object):
    """ an empty sentinel object """
    
    def __str__(self):
        return 'None'
    
    def __unicode__(self):
        return u'None'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other is None or isinstance(other, NotGivenBase):
            return True
        return False
    
NotGiven = NotGivenBase()