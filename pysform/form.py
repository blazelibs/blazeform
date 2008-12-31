import formencode
from pysform.element import form_elements, CancelElement, CheckboxElement, \
        MultiSelectElement, LogicalGroupElement
from pysform.util import HtmlAttributeHolder, NotGiven, ElementRegistrar
from pysform.file_upload_translators import WerkzeugTranslator
from pysform.processors import Wrapper

class FormBase(HtmlAttributeHolder, ElementRegistrar):
    """
    Base class for forms.
    """
    
    def __init__(self, name, action='', **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)
        ElementRegistrar.__init__(self, self, self)
        
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
        # our validators
        self.validators = []
        # file upload translator
        self.fu_translator = WerkzeugTranslator
        # form errors
        self.errors = []
        # exception handlers
        self.exception_handlers = []
        
        # element holders
        self.all_els = {}
        self.defaultable_els = {}
        self.render_els = []
        self.submittable_els = {}
        self.returning_els = []
        
        # init actions
        self.register_elements(form_elements)
        self.add_hidden(self._form_ident_field, value='submitted')
    
    def register_elements(self, dic):
        for type, eclass in dic.items():
            self.register_element_type(type, eclass)
            
    def register_element_type(self, type, eclass):
        if self._registered_types.has_key(type):
            raise ValueError('type "%s" is already registered' % type)
        self._registered_types[type] = eclass

    def render(self):
        return self.renderer(self).render()

    def is_submitted(self):
        """ In a normal workflow, is_submitted will only be called once and is
        therefore a good method to override if something needs to happen
        after __init__ but before anything else.  However, we also need to
        to use is_submitted internally, but would prefer to make it a little
        more user friendly.  Therefore, we do this and use _is_submitted
        internally.
        """
        return self._is_submitted()
    
    def _is_submitted(self):
        if getattr(self, self._form_ident_field).is_submitted():
            return True
        return False
    
    def add_error(self, msg):
        self.errors.append(msg)
    
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
    
    def add_validator(self, validator, msg = None):
        """
            form level validators are only validators, no manipulation of
            values can take place.  The validator should be a formencode
            validator or a callable.  If a callable, the callable should take
            one argument, the form object.  It should raise an exception
            to indicate in invalid condition.
            
            def validator(form):
                if form.myfield.is_valid():
                    if form.myfield.value != 'foo':
                        raise ValueError('My Field: must have "foo" as value')
        """
        if not formencode.is_validator(validator):
            if callable(validator):
                validator = Wrapper(to_python=validator)
            else:
                raise TypeError('validator must be a Formencode validator or a callable')
        self.validators.append((validator, msg))

    def is_valid(self):
        if not self.is_submitted():
            return False
        valid = True
        
        # element validation
        for element in self.submittable_els.values():
            if not element.is_valid():
                valid = False
        
        # whole form validation
        for validator, msg in self.validators:
            try:
                value = validator.to_python(self)
            except formencode.Invalid, e:
                valid = False
                msg = (msg or str(e))
                if msg:
                    self.add_error(msg)

        return valid
    
    def set_submitted(self, values):
        """ values should be dict like """
        self.errors = []
        
        for key, el in self.submittable_els.items():
            if values.has_key(key):
                el.submittedval = values[key]
        
        # this second loop is to make sure we clear checkboxes,
        # LogicalGroupElements, and multi-selects if the form is submitted,
        # they have a default value, but the field wasn't submitted.
        #
        # It can't be done above because _is_submitted() can't be trusted until
        # we are certain all submitted values have been processed.
        if self._is_submitted():
            for key, el in self.submittable_els.items():
                if not values.has_key(key):
                    if isinstance(el, (CheckboxElement, MultiSelectElement, LogicalGroupElement)):
                        el.submittedval = None
                
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
    
    def add_handler(self, exception_txt, error_msg, exc_type=None):
        self.exception_handlers.append((exception_txt, error_msg, exc_type))

    def handle_exception(self, exc):
        # try element handlers first
        for el in self.submittable_els.values():
            if el.handle_exception(exc):
                return True
        # try our own handlers
        for looking_for, error_msg, exc_type in self.exception_handlers:
            if looking_for in str(exc) and (exc_type is None or isinstance(exc, exc_type)):
                self._valid = False
                self.add_error(error_msg)
                return True
        # if we get here, the exception wasn't handled, just return False
        return False

class Form(FormBase):
    """
    Main form class using default HTML renderer and Werkzeug file upload
    translator
    """
    def __init__(self, name, **kwargs):        
        # make the form's name the id
        if not kwargs.has_key('id'):
            kwargs['id'] = name
            
        FormBase.__init__(self, name, **kwargs)
        
        # import here or we get circular import problems
        from pysform.render import get_renderer
        self.renderer = get_renderer

        
        
        
