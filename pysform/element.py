from os import path
import cgi
from webhelpers.html import HTML
import formencode
import formencode.validators as fev
from pysform.util import HtmlAttributeHolder, is_empty, multi_pop, NotGiven

form_elements = {}

class ElementInvalid(Exception):
    pass

class Label(object):
    """
    A class which represents the label associated with an element
    """
    def __init__(self, element, value):
        """
        @param element: the parent element of this label
        @type element: instantiated object that inherits pyHtmlQuickForm.element.ElementBase
        """
        
        if isinstance(element, ElementBase):
            #: the parent element this label is attached to
            self.element = element
        else:
            raise TypeError('Label expects pyHtmlQuickForm.element.ElementBase' )
        
        #: the value of the label
        self.value = value
    
    def render(self, **kwargs):
        if isinstance(self.element, FormFieldElementBase):
            kwargs['for'] = self.element.getId()
        return HTML.label(self.value, **kwargs)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
    
    def __str__(self):
        return self.value

class ElementBase(HtmlAttributeHolder):
    """
    Base class for form elements.
    """
    def __init__(self, type, form, eid, label=NotGiven, defaultval=NotGiven, **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)

        self._defaultval = NotGiven
        self._displayval = NotGiven
        
        self.id = eid
        self.label = Label(self, label)
        self.type = type
        self.form = form
    
        self.defaultval = defaultval
        self.set_attr('id', self.getidattr())
        self.set_attr('class_', self.type)

        self._bind_to_form()
    
    def _bind_to_form(self):
        f = self.form
        f.all_els[self.id] = self
        f.defaultable_els[self.id] = self
        f.render_els.append(self)
        f.submittable_els[self.id] = self
        f.returning_els.append(self)
    
    def _get_defaultval(self):
        return self._defaultval
    def _set_defaultval(self, value):
        self._displayval = NotGiven
        self._defaultval = value
    defaultval = property(_get_defaultval, _set_defaultval)
    
    def _get_displayval(self):
        if self._displayval is NotGiven:
            self._from_python_processing()
        return self._displayval
    displayval = property(_get_displayval)

    def _from_python_processing(self):
        self._displayval = self._defaultval
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
    
    def getidattr(self):
        return self.form.element_id_formatter % {'form_name':self.form.name, 'element_id':self.id}

class HasValueElement(ElementBase):
    def __init__(self, *args, **kwargs):
        ElementBase.__init__(self, *args, **kwargs)
        
        self.render_group = None
        
    def _get_value(self):
        raise NotImplimentedError('this method needs to be overriden')
    value = property(_get_value)

class FormFieldElementBase(HasValueElement):
    """
    Base class for form elements that represent form fields (input, select, etc.)
    as opposed to Elements that are only for display (i.e. static, headers).
    """
    def __init__(self, etype, form, eid, label=NotGiven, vtype = NotGiven, defaultval=NotGiven, strip=True, **kwargs):
        # if this field was not submitted, we can substitute
        self.if_missing = kwargs.pop('if_missing', NotGiven)
        # if the field was submitted, but is an empty value
        self.if_empty = kwargs.pop('if_empty', NotGiven)
        # if the field is invalid, return this value
        self.if_invalid = kwargs.pop('if_invalid', NotGiven)
        #: is this field required in order for the form submission to be valid?
        self.required = kwargs.pop('required', False)
        HasValueElement.__init__(self, etype, form, eid, label, defaultval, **kwargs)

        self._submittedval = NotGiven
        self._safeval = NotGiven
        #: a list of error messages for this field (C{str})
        self.errors = []
        #: a list of user messages for this field (C{str})
        self.notes = []
        #: validators/converters
        self.processors = []
        #: whether or not this field is valid, None means the field has not been processed yet
        self._valid = None
        #: allows a form/element to "expect" an exception and handle gracefully
        self.exception_handlers = []
        #: strip string submitted values?
        self.strip = strip
        
        # types
        vtypes = ('boolean', 'bool', 'int', 'integer', 'number', 'num',
                        'str', 'string', 'unicode', 'uni', 'float')
        if vtype is not NotGiven:
            try:
                vtype = vtype.lower()
                if vtype not in vtypes:
                    raise ValueError('invalid vtype "%s"' % vtype)
            except AttributeError, e:
                raise TypeError('vtype should have been a string, got %s instead' % type(vtype))
        self._vtype = vtype
        
    
    def _get_submittedval(self):
        return self._submittedval
    def _set_submittedval(self, value):
        self._valid = None
        self.errors = []
        self._submittedval = value
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def _get_displayval(self):
        if self.submittedval is NotGiven:
            return HasValueElement._get_displayval(self)
        return self.submittedval
    displayval = property(_get_displayval)

    def _get_value(self):
        self._to_python_processing()
        if self._valid != True:
            raise ElementInvalid('element value is not valid')
        return self._safeval
    value = property(_get_value)

    def _from_python_processing(self):
        # process processors
        value = self.defaultval
        
        # If its empty, there is no reason to run the converters.  By default,
        # the validators don't do anything if the value is empty and they WILL
        # try to convert our NotGiven value, which we want to avoid.  Therefore,
        # just skip the conversion.
        if not is_empty(value):
            for processor, msg in self.processors:
                value = processor.from_python(value)
        self._displayval = value
    
    def _to_python_processing(self):
        """
        filters, validates, and converts the submitted value based on
        element settings and processors
        """

        # if the value has already been processed, don't process it again
        if self._valid != None:
            return
        
        valid = True
        value = self.submittedval
        
        # strip if necessary
        if self.strip and isinstance(value, basestring):
            value = value.strip()
        
        # if nothing was submitted, but we have an if_missing, substitute
        if value is NotGiven and self.if_missing is not NotGiven:
            value = self.if_missing
        
        # handle empty or missing submit value with if_empty
        if is_empty(value) and self.if_empty is not NotGiven:
            value = self.if_empty
        # standardize all empty values as None if if_empty not given
        elif is_empty(value) and value is not NotGiven:
            value = None  

        # process required
        if self.required and is_empty(value):
            valid = False
            self.add_error('"%s" is required' % self.label)
        
        # process processors
        for validator, msg in self.processors:
            try:
                value = validator.to_python(value)
            except formencode.Invalid, e:
                valid = False
                self.add_error((msg or str(e)))
            
        # If its empty, there is no reason to run the converters.  By default,
        # the validators don't do anything if the value is empty and they WILL
        # try to convert our NotGiven value, which we want to avoid.  Therefore,
        # just skip the conversion.
        if not is_empty(value):
            # process type conversion
            if self._vtype is not NotGiven:
                if self._vtype in ('boolean', 'bool'):
                    tvalidator = formencode.compound.Any(fev.Bool(), fev.StringBoolean())
                elif self._vtype in ('integer', 'int'):
                    tvalidator = fev.Int
                elif self._vtype in ('number', 'num', 'float'):
                    tvalidator = fev.Number
                elif self._vtype in ('str', 'string'):
                    tvalidator = fev.String
                elif self._vtype in ('unicode', 'uni'):
                    tvalidator = fev.UnicodeString
                try:
                    value = tvalidator.to_python(value)
                except (formencode.Invalid, ValueError), e:
                    valid = False
                    self.add_error(str(e))

        # save
        if valid:
            self._safeval = value
            self._valid = True
        else:
            # is if_invalid if applicable
            if self.if_invalid is not NotGiven:
                # we might want to clear error messages too, but the extra
                # detail probably won't hurt (for now)
                self._safeval = self.if_invalid
                self._valid = True
            else:
                self._valid = False
    
    def is_submitted(self):
        return self.submittedval is not NotGiven
    
    def is_valid(self):
        self._to_python_processing()
        return self._valid
    
    def add_error(self, error):
        self.errors.append(error)
    
    def add_note(self, note, escape = True):
        if escape:
            note = cgi.escape(note)
        self.notes.append(note)
    
    def add_processor(self, processor, msg = None):
        if not formencode.is_validator(processor):
            if callable(processor):
                processor = formencode.validators.Wrapper(to_python=processor)
            else:
                raise TypeError('processor must be a Formencode validator or a callable')
        self.processors.append((processor, msg))
        
    def add_handler(self, exception_txt, error_msg, exc_type=None):
        self.exception_handlers.append((exception_txt, error_msg, exc_type))

    def handle_exception(self, exc):
        for looking_for, error_msg, exc_type in self.exception_handlers:
            if looking_for in str(exc) and (exc_type is None or isinstance(exc, exc_type)):
                self._valid = False
                self.add_error(error_msg)
                return True
        return False

class InputElementBase(FormFieldElementBase):
    """
    Base class for input form elements.
    
    Since <input> elements have very similar HTML representations, they have
    this common base class. You don't need to instantiate it directly,
    use one of the child classes.
    """
    def __init__(self, *args, **kwargs):
        FormFieldElementBase.__init__(self, *args, **kwargs)
        # use to override using the id as the default "name" attribute
        self.nameattr = None
    
    def render(self, **kwargs):
        if self.displayval and self.displayval is not NotGiven:
            self.set_attr('value', self.displayval)
        self.set_attr('name', self.nameattr or self.id)
        self.set_attrs(**kwargs)
        return HTML.input(type=self.type, **self.attributes)

class ButtonElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'button', *args, **kwargs)
form_elements['button'] = ButtonElement

class CheckboxElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        checked = kwargs.pop('checked', NotGiven)
        InputElementBase.__init__(self, 'checkbox', *args, **kwargs)
        
        # some sane defaults for a checkbox IMO
        if self._vtype is NotGiven:
            self._vtype = 'bool'
        if self.if_empty is NotGiven:
            self.if_empty = False
        if self.defaultval is NotGiven:
            self.defaultval = bool(checked)

    def _get_submittedval(self):
        return self._submittedval
    def _set_submittedval(self, value):
        self._valid = None
        self.errors = []
        self._submittedval = bool(value)
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def render(self, **kwargs):
        # have to override InputBase.render or it will put a value attribute
        # for a checkbox
        if self.displayval and self.displayval is not NotGiven:
            self.set_attr('checked', 'checked')
        self.set_attr('name', self.nameattr or self.id)
        self.set_attrs(**kwargs)
        return HTML.input(type=self.type, **self.attributes)
form_elements['checkbox'] = CheckboxElement

class HiddenElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'hidden', *args, **kwargs)
form_elements['hidden'] = HiddenElement

class ImageElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'image', *args, **kwargs)
form_elements['image'] = ImageElement

class ResetElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'reset', *args, **kwargs)
form_elements['reset'] = ResetElement

class SubmitElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'submit', *args, **kwargs)
form_elements['submit'] = SubmitElement

class CancelElement(SubmitElement):
    pass
form_elements['cancel'] = CancelElement

class TextElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        maxlength = kwargs.pop('maxlength', None)
        InputElementBase.__init__(self, 'text', *args, **kwargs)
        
        self.set_length(maxlength)
            
    def set_length(self, len):
        # if size is none, set it to None and return
        if len == None:
            return
        
        # make sure the size is an integer
        if type(1) != type(len):
            raise TypeError('maxlength should have been int but was %s' % type(size))
        
        self.set_attr('maxlength', len)
        
        # set a maxlength validator on this
        self.add_processor(fev.MaxLength(len))
form_elements['text'] = TextElement

class DateElement(TextElement):
    def __init__(self, *args, **kwargs):
        vargs = multi_pop(kwargs, 'accept_day', 'month_style', 'datetime_module')
        TextElement.__init__(self, *args, **kwargs)
        self.add_processor(fev.DateConverter(**vargs))
form_elements['date'] = DateElement

class EmailElement(TextElement):
    def __init__(self, *args, **kwargs):
        vargs = multi_pop(kwargs, 'resolve_domain')
        TextElement.__init__(self, *args, **kwargs)
        self.add_processor(fev.Email(**vargs))
form_elements['email'] = EmailElement

class PasswordElement(TextElement):
    """
    techincally, password is on the same level as text as both are types
    of input elements, but I want to inherit the text maxlength validator
    """
    def __init__(self, *args, **kwargs):
        self.default_ok = kwargs.pop('default_ok', False)
        TextElement.__init__(self, *args, **kwargs)
        # override the type
        self.type = 'password'
        # class attribute set already, override that too
        self.set_attr('class_', 'password')
        
    def _get_displayval(self):
        if self.default_ok:
            return TextElement._get_displayval(self)
        return None
    displayval = property(_get_displayval)
form_elements['password'] = PasswordElement

class TimeElement(TextElement):
    def __init__(self, *args, **kwargs):
        vargs = multi_pop(kwargs, 'use_ampm', 'prefer_ampm', 'use_seconds',
                          'use_datetime', 'datetime_module')
        TextElement.__init__(self, *args, **kwargs)
        self.add_processor(fev.TimeConverter(**vargs))
form_elements['time'] = TimeElement

class URLElement(TextElement):
    def __init__(self, *args, **kwargs):
        vargs = multi_pop(kwargs, 'check_exists', 'add_http', 'require_tld')
        TextElement.__init__(self, *args, **kwargs)
        self.add_processor(fev.URL(**vargs))
form_elements['url'] = URLElement

class SelectElement(FormFieldElementBase):
    """
    Class to dynamically create an HTML SELECT.  Includes methods for working
    with the select's OPTIONS.
    """
    def __init__(self, form, eid, options, displayName=None, choose='Choose:', auto_validate=True, invalid_msg='Please select a valid option', required = False, **kwargs):
        FormFieldElementBase.__init__(self, form, eid, displayName, required=required, **kwargs)
        self.setType('select')
        self.options_orig = options
        self.options = options
        self.choose = None
        if choose:
            if isinstance(choose, list):
                self.choose = choose
            else:
                self.choose = [(-2, choose), (-1, '-'*25)]
               
            self.options = self.choose + options
        
        if auto_validate:
            if required:
                self.addValidator(Select(self.options_orig), invalid_msg)
            else:
                self.addValidator(Select(self.options), invalid_msg)
    
    def getSubmitValue(self):
        """
            if choose was true but required false, strip out the values
            that came from the choose and return None instead
        """
        value = self.submittedValue
        if self.choose:
            choose = [unicode(d[0]) for d in self.choose]
            if not self.required:
                if value in choose:
                    return None
        return value
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import select
        return select(self.name, self.currentValue(), self.options, **self.attributes)

class TextAreaElement(FormFieldElementBase):
    """
    HTML class for a textarea type field
    """
    def __init__(self, form, eid, displayName=None, rows = 7, cols=40, **kwargs):
        FormFieldElementBase.__init__(self, form, eid, displayName, rows=rows, cols=cols, **kwargs)
        self.setType('textarea')
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import textarea
        return textarea(self.name, self.currentValue(), **self.attributes)

class FileElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'file', *args, **kwargs)
        self.content_type = None
        self.file_name = None
        self._allowed_exts = []
        self._allowed_types = []
        self._denied_exts = []
        self._denied_types = []
        self._maxsize = None
        
    def maxsize(self, size):
        self._maxsize = size
    
    def allow_extension(self, *args):
        "allowed extensions"
        self._allowed_exts.extend([('.%s' % a.lstrip('.').lower()) for a in args])
    
    def deny_extension(self, *args):
        "denied extensions, without dots"
        self._denied_exts.extend(args)
    
    def allow_type(self, *args):
        self._allowed_types.extend(args)
    
    def deny_type(self, *args):
        self._denied_types.extend(args)
        
    def setDefaultValue(self, value):
        # file element does not have default values
        pass

    def getDefaultValue(self, value):
        # file element does not have default values
        pass
    
    def setSubmitValue(self, value):
        raise NotImplementedError('FileElement does not impliment setSubmitValue()')
        
    def getSubmitValue(self):
        raise NotImplementedError('FileElement does not impliment getSubmitValue()')
    
    def currentValue(self):
        raise NotImplementedError('FileElement does not impliment currentValue()')
    
    def getValue(self):
        if self.file_name and self.content_type:
            return True
        return False
    
    def _processValue(self):
        valid = True
        
        # process required
        if self.required and (not self.file_name or not self.content_type):
            valid = False
            self.addError('"%s" is required' % self.getDisplayName())
        
        if self.file_name is not None:
            _ , ext = path.splitext(self.file_name)
            ext  = ext.lower()
            if self._allowed_exts and ext not in self._allowed_exts:
                valid = False
                self.addError('extension "%s" not allowed, must be one of: %s' % (ext, ', '.join(self._allowed_exts)))
            
            if self._denied_exts and ext in self._denied_exts:
                valid = False
                self.addError('extension "%s" not permitted' % ext)
        
        if self.content_type is not None:
            if self._allowed_types and self.content_type not in self._allowed_types:
                valid = False
                self.addError('content type "%s" not allowed, must be one of: %s' % (self.content_type, ', '.join(self._allowed_types)))
            
            if self._denied_types and self.content_type in self._denied_types:
                valid = False
                self.addError('content type "%s" not permitted' % self.content_type)
        
        if self._maxsize:
            if self.content_length > self._maxsize:
                valid = False
                self.addError('file too big, max size %d' % self._maxsize)
                
        self._valid = valid
    
    def addValidator(self, *args, **kwargs):
        raise NotImplementedError('FileElement does not support addValidator()')

class StaticValueElement(InputElementBase):
    def __init__(self, form, eid, displayName=None, length=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('static-value')

    def render(self, **kwargs):
        self._renderPrep(kwargs)
        return self.currentValue()

class StaticElement(ElementBase):
    """
    class for static HTML fields in the form.
    
    A static element is an element that cannot have a submit value and thus
    cannot change due to user input. Such elements are usually used to improve
    form presentation.
    """
    def __init__(self, form, eid, displayName, **kwargs):
        # initialize the base element
        LabelElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('static')
    
    def setSubmitValue(self, value):
        """
        DOES NOTHING: a static element silently ignores a call to setSubmitValue()
        """
        pass
        
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        return self.getDefaultValue()
        #from webhelpers.html import HTML
        #attr = self.getAttributes()
        #return HTML.div(self.getDefaultValue(), **attr)
    
    def isValid(self):
        """
        just returns true since static elements are not validated
        """
        return True

class PassThruElement(FormFieldElementBase):
    """
    allows us to pass a non-rendered value through the form without the user
    being able to touch it
    """
    def __init__(self, form, eid, value=None, displayName=None, **kwargs):
        FormFieldElementBase.__init__(self, form, eid, displayName, value=value, hasLabel=False, **kwargs)
        self.setType('passthru')
        self.render = False
        self.pt_value = value

    def setSubmitValue(self, value):
        pass
    
    def render(self, **kwargs):
        return ''
    
    def isValid(self):
        """
        just returns true since static elements are not validated
        """
        return True
    
    def getValue(self):
        return self.pt_value

class GroupElement(StaticElement):
    """
    HTML class for a form element group
    
    Groups can be used both for visual grouping of the elements (e.g. putting "Submit" and "Reset" buttons on one line), grouping of the elements with the same name (e.g. groups of checkboxes and radio buttons) and logical grouping of the elements (e.g. group for person's name consisting of two text fields for first and last name).
    """
    def __init__(self, form, eid, displayName=None, **kwargs):
        StaticElement.__init__(self, form, eid, displayName, **kwargs)
        self.setType('group')
        self.elements = ElementHolder()
    
    def addElement(self, type, eid, *args, **kwargs):
        element = self.form.createElement(type, eid, *args, **kwargs)
        self.elements.add(element)
        return element

    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html import HTML
        attr = self.getAttributes()
        return HTML.div(self.getDefaultValue(), **attr)


class HeaderElement(StaticElement):
    """
    A pseudo-element used for adding headers to a form
    
    Headers will normally be rendered differently than other static elements,
    hence they have their own class
    """
    def __init__(self, form, eid, value=None, element='h3', **kwargs):
        # initialize the base element
        StaticElement.__init__(self, form, eid, None, value=value, **kwargs)
        self.setType('header')
        self.element_type = element
        
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html import HTML
        attr = self.getAttributes()
        return HTML.tag(self.element_type, self.getDefaultValue(), **attr)

