
class ElementHolder(object):
    """
    A container object that holds instantiated elements in the order they are
    created and is iterable
    """
    
    def __init__(self):
        #: holds the instantiated element objects
        self._elements = []
        
        #: maps a field's name to its position in _elements, for efficient lookups
        self._map = {}
        
    def add(self, element):
        """
        adds an instantiated element object
        """
        
        self._elements.append(element)
        
        pos = len(self._elements) - 1
        
        self._map[element.id] = pos
    
    def __iter__(self): 
        for element in self._elements:
            yield element
    
    def __getattr__(self, name):
        try:
            return self._elements[self._map[name]]
        except KeyError:
            raise AttributeError(name)
    
    def __repr__(self):
        return str([(k, self._elements[i]) for k,i in self._map.items()])

class HtmlAttributeHolder(object):
    def __init__(self, **kwargs):
        #: a dictionary that represents html attributes
        self.attributes = kwargs
        
    def setAttributes(self, **kwargs ):
        self.attributes.update(kwargs)
        
    def setAttribute(self, key, value):
        self.attributes[key] = value
    
    def getAttributes(self):
        return self.attributes
    
    def getAttribute(self, attr):
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
    