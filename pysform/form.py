
from element import all_elements, FormFieldElementBase, \
    FileElement, CancelElement
from util import HtmlAttributeHolder, ElementHolder

class FormBase(HtmlAttributeHolder):
    """
    Base class for forms.
    """
    
    def __init__(self, name, action='', **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)
        
        self.name = name
        self.elements = ElementHolder()
        self._registered_types = {}
        self.register_elements(all_elements)
        self.renderer = None
        self.action = action
        self.validators = []
        
        # this string is used to generate the HTML id attribute for each
        # element
        self.element_id_formatter = '%(form_name)s-%(element_id)s'
        
        # include a hidden field so we can check if this form was submitted
        self._form_ident_field = '%s-submit-flag' % name
        self.add_element('hidden', self._form_ident_field, value='submitted')
    
    def __getattr__(self, name):
        """
            we want to enable add_*, create_* methods on the form object
            that correspond to elements we have available
        """
        if name.startswith('add_'):
            type = name.replace('add_', '')
            func = self.add_element
        elif name.startswith('create_'):
            type = name.replace('create_', '')
            func = self.create_element
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
        if type == 'file':
            self.setAttribute('enctype', 'multipart/form-data')
        element = self.createElement(type, eid, *args, **kwargs)
        self.elements.add(element)
        return element
    
    def create_element(self, type, eid, *args, **kwargs):
        try:
            eclass = self._registered_types[type]
        except KeyError:
            raise ValueError('"%s" is not a registered element type' % type)
        
        return eclass(self, eid, *args, **kwargs)

    def render(self):
        return self.renderer(self).render()

    def is_submitted(self, submitValues=None):
        if submitValues != None:
            self.setSubmitValues(submitValues)
        
        return self._is_submitted()
    
    def _is_submitted(self):
        flag_value = getattr(self.elements, self._form_ident_field).getSubmitValue()

        if flag_value:
            return True
        return False
    
    def is_cancel(self):
        if not self.is_submitted():
            return False
        
        # look for any CancelElement that has a non-false submit value
        # which means that was the button clicked
        for element in self.elements:
            if isinstance(element, CancelElement):
                if element.getSubmitValue():
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
        for element in self.elements:
            if isinstance(element, FormFieldElementBase) and values.has_key(element.name):
                try:
                    value = values.getlist(element.name)
                    if len(value) == 0:
                        value = None
                    elif len(value) == 1:
                        value = value[0]
                        
                    element.setSubmitValue(value)
                except AttributeError:
                    element.setSubmitValue(values.get(element.name))
        
        # this second loop is to make sure we set checkboxes and radio
        # boxes to False if the form was submitted but the
        # element wasn't passed in the POST
        if self._is_submitted():
            for element in self.elements:
                if element.getType() == 'checkbox' and values.has_key(element.name) == False:
                    element.setSubmitValue(False)
    
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
        for element in self.elements:
            try:
                element.setDefaultValue(values[element.name])
            except(KeyError):
                pass
    
    def get_values(self):
        "return a dictionary of element values"
        retval = {}
        for element in self.elements:
            if isinstance(element, FormFieldElementBase):
                retval[element.name] = element.getValue()
        return retval

    def handle_exception(self, exc):
        exc_text = str(exc)
        found = False
        for element in self.elements:
            if element.handle_exception(exc_text):
                found = True
        return found
    
    # The functions below are for backwards compatibility
        
    def createElement(self, type, eid, *args, **kwargs):
        return self.create_element(type, eid, *args, **kwargs)
    
    def addElement(self, type, eid, *args, **kwargs):
        return self.add_element(type, eid, *args, **kwargs)
    
    def isSubmitted(self, submitValues=None):
        return self.is_submitted(submitValues)
    
    def isCancel(self):
        return self.is_cancel()
    
    def isValid(self):
        return self.is_valid()
    
    def iscancel(self):
        return self.is_cancel()
    
    def isvalid(self):
        return self.is_valid()
    
    #*  HTML_QuickForm
    #* accept
    #* addFormRule
    #* addGroup
    #* addGroupRule
    #* addRule
    #* apiVersion
    #* applyFilter
    #* arrayMerge
    #* createElement
    #* defaultRenderer
    #* elementExists
    #* errorMessage
    #* exportValue
    #* exportValues
    #* freeze
    #* getElement
    #* getElementError
    #* getElementType
    #* getElementValue
    #* getMaxFileSize
    #* getRegisteredRules
    #* getRegisteredTypes
    #* getRequiredNote
    #* getSubmitValue
    #* getSubmitValues
    #* getValidationScript
    #* insertElementBefore
    #* isElementFrozen
    #* isElementRequired
    #* isError
    #* isFrozen
    #* isRuleRegistered
    #* isSubmitted
    #* isTypeRegistered
    #* process
    #* registerElementType
    #* registerRule
    #* removeElement
    #* setConstants
    #* setDatasource
    #* setDefaults
    #* setElementError
    #* setJsWarnings
    #* setMaxFileSize
    #* setRequiredNote
    #* toArray
    #* toHtml
    #* updateElementAttr
    #* validate


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

        
        
        
