from webhelpers.html import literal

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

class NotGivenIterBase(NotGivenBase):
    def __str__(self):
        return '[]'
    
    def __unicode__(self):
        return u'[]'
    
    def __nonzero__(self):
        return False
    
    def __ne__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return False
        return True
    
    def __eq__(self, other):
        if other == [] or isinstance(other, NotGivenBase):
            return True
        return False
    
    # we also want to emulate an empty list
    def __iter__(self):
        return self
    
    def next(self):
        raise StopIteration
    
    def __len__(self):
        return 0
NotGivenIter = NotGivenIterBase()

def tolist(x, default=[]):
    if x is None:
        return default
    if not isinstance(x, (list, tuple)):
        return [x]
    else:
        return x
    
def is_iterable(possible_iterable):
    if isinstance(possible_iterable, basestring):
        return False
    try:
        iter(possible_iterable)
        return True
    except TypeError:
        return False

def is_notgiven(object):
    return isinstance(object, NotGivenBase)
    
class ElementRegistrar(object):
        
    def __getattr__(self, name):
        """
            we want to enable add_* methods on the object
            that correspond to elements we have available
        """
        if name.startswith('add_'):
            type = name.replace('add_', '')
            func = self.add_element
        elif self.all_els.has_key(name):
            return self.all_els[name]
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
        
        def wrapper(eid, *args, **kwargs):
            return func(type, eid, *args, **kwargs)
        return wrapper
    
    def add_element(self, type, eid, *args, **kwargs):
        if self.all_els.has_key(eid):
            raise ValueError('element id "%s" already used' % eid)
        return self._create_element(type, eid, *args, **kwargs)
    
    def _create_element(self, type, eid, *args, **kwargs):
        try:
            eclass = self._registered_types[type]
        except KeyError:
            raise ValueError('"%s" is not a registered element type' % type)
        
        return eclass(self, eid, *args, **kwargs)
