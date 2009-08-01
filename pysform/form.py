import formencode
from pysform.element import form_elements, CancelElement, CheckboxElement, \
        MultiSelectElement, LogicalGroupElement
from pysform.util import HtmlAttributeHolder, NotGiven, ElementRegistrar
from pysform.file_upload_translators import WerkzeugTranslator
from pysform.processors import Wrapper
from pysform.exceptions import ElementInvalid, ProgrammingError

class FormBase(HtmlAttributeHolder, ElementRegistrar):
    """
    Base class for forms.
    """
    
    def __init__(self, name, static=False, **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)
        ElementRegistrar.__init__(self, self, self)
        
        self._name = name       
        # include a hidden field so we can check if this form was submitted
        self._form_ident_field = '%s-submit-flag' % name
        # registered element types
        self._registered_types = {}
        # our renderer
        self._renderer = None
        # this string is used to generate the HTML id attribute for each
        # rendering element
        self._element_id_formatter = '%(form_name)s-%(element_id)s'
        # our validators
        self._validators = []
        # file upload translator
        self._fu_translator = WerkzeugTranslator
        # form errors
        self._errors = []
        # exception handlers
        self._exception_handlers = []
        # is the form static?
        self._static = static
        
        # element holders
        self._all_els = {}
        self._defaultable_els = {}
        self._render_els = []
        self._submittable_els = {}
        self._returning_els = []
        
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

    def render(self, **kwargs):
        return self._renderer(self).render(**kwargs)

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
        self._errors.append(msg)
    
    def is_cancel(self):
        if not self.is_submitted():
            return False
        
        # look for any CancelElement that has a non-false submit value
        # which means that was the button clicked
        for element in self._submittable_els.values():
            if isinstance(element, CancelElement):
                if element.is_submitted():
                    return True
        return False
    
    def add_validator(self, validator, msg = None):
        """
            form level validators are only validators, no manipulation of
            values can take place.  The validator should be a formencode
            validator or a callable.  If a callable, the callable should take
            one argument, the form object.  It should raise a ValueInvalid
            exception if applicable.
            
            def validator(form):
                if form.myfield.is_valid():
                    if form.myfield.value != 'foo':
                        raise ValueInvalid('My Field: must have "foo" as value')
        """
        if not formencode.is_validator(validator):
            if callable(validator):
                validator = Wrapper(to_python=validator)
            else:
                raise TypeError('validator must be a Formencode validator or a callable')
        self._validators.append((validator, msg))

    def is_valid(self):
        if not self.is_submitted():
            return False
        valid = True
        
        # element validation
        for element in self._submittable_els.values():
            if not element.is_valid():
                valid = False
        
        # whole form validation
        for validator, msg in self._validators:
            try:
                value = validator.to_python(self)
            except formencode.Invalid, e:
                valid = False
                msg = (msg or str(e))
                if msg:
                    self.add_error(msg)
            except ElementInvalid, e:
                # since we are getting an ElementInvalid exception, that means
                # our validator needed the value of an element to complete
                # validation, but that element is invalid.  In that case,
                # our form will already be invalid, but we don't want to issue
                # an error
                valid = False

        return valid
    
    def set_submitted(self, values):
        """ values should be dict like """
        
        # if the form is static, it shoudl not get submitted values
        if self._static:
            raise ProgrammingError('static forms should not get submitted values')
        
        self._errors = []
        
        # ident field first since we need to know that to now if we need to
        # apply the submitted values
        identel = getattr(self, self._form_ident_field)
        ident_key = identel.nameattr or identel.id
        if values.has_key(ident_key):
            identel.submittedval = values[ident_key]
        
        if self._is_submitted():
            for el in self._submittable_els.values():
                key = el.nameattr or el.id
                if values.has_key(key):
                    el.submittedval = values[key]
                elif isinstance(el, (CheckboxElement, MultiSelectElement, LogicalGroupElement)):
                        el.submittedval = None                    
                
    def set_defaults(self, values):
        for key, el in self._defaultable_els.items():
            if values.has_key(key):
                el.defaultval = values[key]
    
    def get_values(self):
        "return a dictionary of element values"
        retval = {}
        for element in self._returning_els:
            try:
                key = element.nameattr or element.id
            except AttributeError:
                key = element.id
            retval[key] = element.value
        return retval
    values = property(get_values)
    
    def add_handler(self, exception_txt, error_msg, exc_type=None):
        self._exception_handlers.append((exception_txt, error_msg, exc_type))

    def handle_exception(self, exc):
        # try element handlers first
        for el in self._submittable_els.values():
            if el.handle_exception(exc):
                return True
        # try our own handlers
        for looking_for, error_msg, exc_type in self._exception_handlers:
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
    def __init__(self, name, static=False, **kwargs):        
        # make the form's name the id
        if not kwargs.has_key('id'):
            kwargs['id'] = name
            
        FormBase.__init__(self, name, static, **kwargs)
        
        # import here or we get circular import problems
        from pysform.render import get_renderer
        self._renderer = get_renderer

        
        
        
