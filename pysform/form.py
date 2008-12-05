from pysform.element import form_elements, FormFieldElementBase, \
    FileElement, CancelElement
from pysform.util import HtmlAttributeHolder, NotGiven

class FormBase(HtmlAttributeHolder):
    """
    Base class for forms.
    """
    
    def __init__(self, name, action='', **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)
        
        self.name = name       
        # include a hidden field so we can check if this form was submitted
        self._form_ident_field = '%s-submit-flag' % name
        # registered element types
        self._registered_types = {}
        # our renderer
        self.renderer = None
        # this string is used to generate the HTML id attribute for each
        # rendering element
        self.element_id_formatter = '%(form_name)s-%(element_id)s'
        # the form's action attribute
        self.action = action
        # our validators and converters
        self.processors = []
        
        # element holders
        self.all_els = {}
        self.defaultable_els = {}
        self.render_els = []
        self.submittable_els = {}
        self.returning_els = []
        
        # init actions
        self.register_elements(form_elements)
        self.add_element('hidden', self._form_ident_field, value='submitted')
    
    def __getattr__(self, name):
        """
            we want to enable add_* methods on the form object
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
    
    def register_elements(self, dic):
        for type, eclass in dic.items():
            self.register_element_type(type, eclass)
            
    def register_element_type(self, type, eclass):
        if self._registered_types.has_key(type):
            raise ValueError('type "%s" is already registered' % type)
        self._registered_types[type] = eclass
    
    def add_element(self, type, eid, *args, **kwargs):
        if self.all_els.has_key(eid):
            raise ValueError('element id "%s" already used' % eid)
        if type == 'file':
            self.set_attr('enctype', 'multipart/form-data')
        return self._create_element(type, eid, *args, **kwargs)
    
    def _create_element(self, type, eid, *args, **kwargs):
        try:
            eclass = self._registered_types[type]
        except KeyError:
            raise ValueError('"%s" is not a registered element type' % type)
        
        return eclass(self, eid, *args, **kwargs)

    def render(self):
        return self.renderer(self).render()

    def is_submitted(self):
        return self._is_submitted()
    
    def _is_submitted(self):
        if getattr(self, self._form_ident_field).is_submitted():
            return True
        return False
    
    def is_cancel(self):
        if not self.is_submitted():
            return False
        
        # look for any CancelElement that has a non-false submit value
        # which means that was the button clicked
        for element in self.submittable_els.values():
            if isinstance(element, CancelElement):
                if element.is_submitted():
                    return True
        return False
    
    def add_validator(self, validator):
        self.validators.append(validator)
    
    def is_valid(self):
        if not self.is_submitted():
            return False
        valid = True
        
        # element validation
        for element in self.elements:
            if not element.isValid():
                valid = False
        
        # whole form validation
        values = self.get_values()
        for validator in self.validators:
            result = validator(values)
            if isinstance(result, dict) and len(result) > 0:
                for elname in result:
                    self.elements.__getattr__(elname).addError(result[elname])
                valid = False
        
        return valid
    
    def set_submitted(self, values):
        """ values should be dict or Werkzeug MultiDict"""
        for key, el in self.submittable_els.items():
            if values.has_key(key):
                el.submittedval = values[key]
        
        # this second loop is to make sure we clear checkboxes,
        # LogicalGroupElements, and multi-selects if the form is submitted,
        # they have a default value, but the field wasn't submitted
        if self._is_submitted():
            for key, el in self.submittable_els.items():
                if values.has_key(key) == False:
                    if el.type == 'checkbox':
                        element.submittedval = False
    
    def set_files(self, files):
        for name, obj in files.items():
            try:
                fname = obj.filename
                ftype = obj.content_type
                fsize = obj.content_length
            except AttributeError:
                try:
                    fname = obj['filename']
                    ftype = obj['content_type']
                    fsize = obj['content_length']
                except KeyError:
                    raise TypeError('`files` parameter was given an unrecognized object.  Expecting "filename", "content_type", and "content_length" as either attributes or keys.')
            element = getattr(self.elements, name, None)
            if isinstance(element, FileElement):
                element.file_name = fname
                element.content_type = ftype
                element.content_length = fsize
                
    def set_defaults(self, values):
        for key, el in self.defaultable_els.items():
            if values.has_key(key):
                el.defaultval = values[key]
    
    def get_values(self):
        "return a dictionary of element values"
        retval = {}
        for element in self.returning_els:
            retval[element.id] = element.value
        return retval
    values = property(get_values)
    
    def handle_exception(self, exc):
        exc_text = str(exc)
        found = False
        for element in self.elements:
            if element.handle_exception(exc_text):
                found = True
        return found

class Form(FormBase):
    """
    Main form class using default HTML renderer
    """
    def __init__(self, name, **kwargs):        
        # make the form's name the id
        if not kwargs.has_key('id'):
            kwargs['id'] = name
            
        FormBase.__init__(self, name, **kwargs)
        
        from render import CssRenderer
        self.renderer = CssRenderer

        
        
        
