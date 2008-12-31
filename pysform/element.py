from os import path
import cgi
from webhelpers.html import HTML, tags
import formencode
import formencode.validators as fev
from pysform.util import HtmlAttributeHolder, is_empty, multi_pop, NotGiven, \
        tolist, NotGivenIter, is_notgiven, is_iterable, ElementRegistrar, \
        is_given
from pysform.processors import Confirm, Select, MultiValues

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
            kwargs['for'] = self.element.getidattr()
        return HTML.label(self.value, **kwargs)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
    
    def __str__(self):
        if self.value is NotGiven:
            return self.element.id
        return self.value

class ElementBase(HtmlAttributeHolder):
    """
    Base class for form elements.
    """
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, **kwargs):
        HtmlAttributeHolder.__init__(self, **kwargs)

        self._defaultval = NotGiven
        self._displayval = NotGiven
        
        self.id = eid
        self.label = Label(self, label)
        self.form = form
    
        self.defaultval = defaultval
        self.set_attr('id', self.getidattr())

        self._bind_to_form()
    
    def _bind_to_form(self):
        self.form.bind_element(self)
    
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
    def __init__(self, form, eid, label=NotGiven, vtype = NotGiven, defaultval=NotGiven, strip=True, **kwargs):
        # if this field was not submitted, we can substitute
        self.if_missing = kwargs.pop('if_missing', NotGiven)
        # if the field was submitted, but is an empty value
        self.if_empty = kwargs.pop('if_empty', NotGiven)
        # if the field is invalid, return this value
        self.if_invalid = kwargs.pop('if_invalid', NotGiven)
        #: is this field required in order for the form submission to be valid?
        self.required = kwargs.pop('required', False)
        HasValueElement.__init__(self, form, eid, label, defaultval, **kwargs)

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
        self.vtype = vtype
        
    def _get_submittedval(self):
        return self._submittedval
    def _set_submittedval(self, value):
        self._valid = None
        self.errors = []
        self._submittedval = value
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def _get_displayval(self):
        if is_notgiven(self.submittedval):
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
    
    def required_empty_test(self, value):
        return is_empty(value)
    
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
        if is_notgiven(value) and self.if_missing is not NotGiven:
            value = self.if_missing
        
        # handle empty or missing submit value with if_empty
        if is_empty(value) and self.if_empty is not NotGiven:
            value = self.if_empty
        # standardize all empty values as None if if_empty not given
        elif is_empty(value) and not is_notgiven(value):
            value = None  

        # process required
        if self.required and self.required_empty_test(value):
            valid = False
            self.add_error('"%s" is required' % self.label)
        
        # process processors
        for processor, msg in self.processors:
            try:
                processor = MultiValues(processor)
                value = processor.to_python(value, self)
            except formencode.Invalid, e:
                valid = False
                self.add_error((msg or str(e)))
        else:
            # we rely on MultiValues for this, but if no processor,
            # it doesn't get called
            if getattr(self, 'multiple', False) and not is_iterable(value):
                value = tolist(value)

        # If its empty, there is no reason to run the converters.  By default,
        # the validators don't do anything if the value is empty and they WILL
        # try to convert our NotGiven value, which we want to avoid.  Therefore,
        # just skip the conversion.
        if not is_empty(value):
            # process type conversion
            if self.vtype is not NotGiven:
                if self.vtype in ('boolean', 'bool'):
                    tvalidator = formencode.compound.Any(fev.Bool(), fev.StringBoolean())
                elif self.vtype in ('integer', 'int'):
                    tvalidator = fev.Int
                elif self.vtype in ('number', 'num', 'float'):
                    tvalidator = fev.Number
                elif self.vtype in ('str', 'string'):
                    tvalidator = fev.String
                elif self.vtype in ('unicode', 'uni'):
                    tvalidator = fev.UnicodeString
                try:
                    tvalidator = MultiValues(tvalidator, multi_check=False)
                    value = tvalidator.to_python(value, self)
                except formencode.Invalid, e:
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
    def __init__(self, etype, *args, **kwargs):
        FormFieldElementBase.__init__(self, *args, **kwargs)
        # use to override using the id as the default "name" attribute
        self.nameattr = None
        self.set_attr('class_', etype)
        self.etype = etype

    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        if self.displayval and self.displayval is not NotGiven:
            self.set_attr('value', self.displayval)
        self.set_attr('name', self.nameattr or self.id)
        self.set_attrs(**kwargs)
        return HTML.input(type=self.etype, **self.attributes)

class ButtonElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'button', *args, **kwargs)
form_elements['button'] = ButtonElement

class CheckboxElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        checked = kwargs.pop('checked', NotGiven)
        InputElementBase.__init__(self, 'checkbox', *args, **kwargs)
        
        # some sane defaults for a checkbox IMO
        if self.vtype is NotGiven:
            self.vtype = 'bool'
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
    
    def required_empty_test(self, value):
        return not bool(value)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        # have to override InputBase.render or it will put a value attribute
        # for a checkbox
        if self.displayval and self.displayval is not NotGiven:
            self.set_attr('checked', 'checked')
        else:
            try:
                self.del_attr('checked')
            except KeyError:
                pass
        self.set_attr('name', self.nameattr or self.id)
        self.set_attrs(**kwargs)
        return HTML.input(type=self.etype, **self.attributes)
form_elements['checkbox'] = CheckboxElement

class FileElement(InputElementBase):
    def __init__(self, form, eid, label=NotGiven, vtype = NotGiven, defaultval=NotGiven, strip=True, **kwargs):
        InputElementBase.__init__(self, 'file', form, eid, label, vtype, defaultval, strip, **kwargs)
        
        # validation related
        self._allowed_exts = []
        self._allowed_types = []
        self._denied_exts = []
        self._denied_types = []
        self._maxsize = NotGiven
    
    def _bind_to_form(self):
        self.form.bind_element(self, default=False)
        
    def _get_defaultval(self):
        return NotGiven
    def _set_defaultval(self, value):
        if is_given(value):
            raise NotImplementedError('FileElement doesn\'t support default values')
    defaultval = property(_get_defaultval, _set_defaultval)

    def _get_displayval(self):
        return NotGiven
    displayval = property(_get_displayval)
    
    def _get_submittedval(self):
        return self._submittedval
    def _set_submittedval(self, value):
        self._valid = None
        self.errors = []
        self._submittedval = self.form.fu_translator(value)
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def maxsize(self, size):
        "set the maximum allowed file upload size"
        self._maxsize = size
    
    def allow_extension(self, *args):
        "allowed extensions, (with or without dots)"
        self._allowed_exts.extend([('.%s' % a.lstrip('.').lower()) for a in args])
    
    def deny_extension(self, *args):
        "denied extensions, (with or without dots)"
        self._denied_exts.extend([('.%s' % a.lstrip('.').lower()) for a in args])
    
    def allow_type(self, *args):
        "allowed mime type strings"
        self._allowed_types.extend(args)
    
    def deny_type(self, *args):
        "denied mime type strings"
        self._denied_types.extend(args)
    
    def _to_python_processing(self):
         # if the value has already been processed, don't process it again
        if self._valid != None:
            return
        
        valid = True
        value = self.submittedval
        
        # process required
        if self.required and (
            not value.file_name or not value.content_type or
            not value.content_length):
            valid = False
            self.add_error('"%s" is required' % self.label)
        
        if value.file_name is not None:
            _ , ext = path.splitext(value.file_name)
            ext  = ext.lower()
            if self._allowed_exts and ext not in self._allowed_exts:
                valid = False
                self.add_error('extension "%s" not allowed' % ext)
            
            if self._denied_exts and ext in self._denied_exts:
                valid = False
                self.add_error('extension "%s" not permitted' % ext)
        
        if value.content_type is not None:
            if self._allowed_types and value.content_type not in self._allowed_types:
                valid = False
                self.add_error('content type "%s" not allowed' % value.content_type)
            
            if self._denied_types and value.content_type in self._denied_types:
                valid = False
                self.add_error('content type "%s" not permitted' % value.content_type)
        
        if self._maxsize:
            if value.content_length > self._maxsize:
                valid = False
                self.add_error('file too big (%s), max size %s' %
                               (value.content_length, self._maxsize))
                
        self._valid = valid
        if valid:
            self._safeval = self.submittedval
    
    def add_validator(self, *args, **kwargs):
        raise NotImplementedError('FileElement does not support add_validator()')
form_elements['file'] = FileElement

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
        if self.defaultval is NotGiven:
            self.defaultval = 'Reset'
form_elements['reset'] = ResetElement

class SubmitElement(InputElementBase):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'submit', *args, **kwargs)
        if self.defaultval is NotGiven:
            self.defaultval = 'Submit'
            
form_elements['submit'] = SubmitElement

class CancelElement(SubmitElement):
    def __init__(self, *args, **kwargs):
        InputElementBase.__init__(self, 'submit', *args, **kwargs)
        if self.defaultval is NotGiven:
            self.defaultval = 'Cancel'
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

class ConfirmElement(TextElement):
    def __init__(self, *args, **kwargs):
        match = kwargs.pop('match')
        TextElement.__init__(self, *args, **kwargs)
        if isinstance(match, basestring):
            self.mel = self.form.all_els[match]
        else:
            self.mel = match
        # do we need to act like a password element?
        if isinstance(self.mel, PasswordElement):
            # override the type
            self.etype = 'password'
            # class attribute set already, override that too
            self.set_attr('class_', 'password')
                
        self.add_processor(Confirm(self.mel))
        
    def _get_displayval(self):
        if isinstance(self.mel, PasswordElement) and not self.mel.default_ok:
            return None
        return TextElement._get_displayval(self)
    displayval = property(_get_displayval)
form_elements['confirm'] = ConfirmElement

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
        self.etype = 'password'
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
    Class to dynamically create an HTML select.  Includes methods for working
    with the select's options.
    """
    def __init__(self, form, eid, options, label=NotGiven, vtype = NotGiven,
                 defaultval=NotGiven, strip=True, choose='Choose:',
                 auto_validate=True, invalid = [], error_msg = None,
                 required = False, **kwargs):
        self.multiple = bool(kwargs.pop('multiple', False))
        FormFieldElementBase.__init__(self, form, eid, label,
                vtype, defaultval, strip, required=required, **kwargs)

        self.options = options
        self.choose = None
        if choose:
            if isinstance(choose, list):
                self.choose = choose
            else:
                self.choose = [(-2, choose), (-1, '-'*25)]
                if required:
                    invalid = [-2, -1] + tolist(invalid)
               
            self.options = self.choose + options
        
        if auto_validate: 
            if required:
                self.add_processor(Select(self.options, invalid), error_msg)
            else:
                # NotGiven is a valid option as long as a value isn't required
                ok_values = self.options + [(NotGiven, 0)] + [(NotGivenIter, 0)]
                self.add_processor(Select(ok_values, invalid), error_msg)
    
    def _to_python_processing(self):
        """
            if "choose" value was chosen, we need to return an emtpy
            value appropriate to `multi`
        """
        do_processing = bool(self._valid == None)
        FormFieldElementBase._to_python_processing(self)
        if self.choose and do_processing and not is_notgiven(self._safeval):
            value = self._safeval
            # strip out choose values
            if self.multiple:
                value = [v for v in value if unicode(v) not in (u'-1', u'-2')]
            else:
                if unicode(value) in (u'-1', u'-2'):
                    value = None
            
            # re-apply if_empty settings
            if is_empty(value) and self.if_empty is not NotGiven:
                value = self.if_empty
        
            self._safeval = value
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        if self.multiple:
            self.set_attr('multiple', 'multiple')
        self.set_attrs(**kwargs)
        return tags.select(self.id, self.displayval or None, self.options, **self.attributes)
form_elements['select'] = SelectElement

class MultiSelectElement(SelectElement):
    def __init__(self, *args, **kwargs):
        kwargs['multiple'] = True
        SelectElement.__init__(self, *args, **kwargs)
        self.submittedval = NotGivenIter
form_elements['mselect'] = MultiSelectElement

class TextAreaElement(FormFieldElementBase):
    """
    HTML class for a textarea type field
    """
    def __init__(self, *args, **kwargs):
        # set default values
        kwargs['rows'] = kwargs.pop('rows', 7)
        kwargs['cols'] = kwargs.pop('cols', 40)
        FormFieldElementBase.__init__(self, *args, **kwargs)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        self.set_attrs(**kwargs)
        return tags.textarea(self.id, self.displayval or '', **self.attributes)
form_elements['textarea'] = TextAreaElement

class LogicalGroupElement(FormFieldElementBase):
    """
        used to support MultiCheckboxElement and RadioElement
    """
    def __init__(self, is_multiple, *args, **kwargs):
        self.auto_validate = kwargs.pop('auto_validate', True)
        self.error_msg = kwargs.pop('error_msg', None)
        self.invalid = kwargs.pop('invalid', [])
        FormFieldElementBase.__init__(self, *args, **kwargs)
        
        self.multiple = is_multiple
        self.members = {}
        self.to_python_first = True
        self.submittedval = NotGivenIter

    def _bind_to_form(self):
        self.form.bind_element(self, render=False)
        
    def _get_defaultval(self):
        return self._defaultval
    def _set_defaultval(self, value):
        self._displayval = NotGiven
        self._defaultval = value
        
        # if you do this every time, then ElementBase ends up
        # setting this value in it's __init__, but that happens before
        # _submittedval is created in FormFieldElementBase, and we get an error
        if value:
            # call displayval to make sure any _from_python processing gets done
            displayval = FormFieldElementBase._get_displayval(self)
            self._set_members(displayval)
    defaultval = property(_get_defaultval, _set_defaultval)

    def _get_submittedval(self):
        return self._submittedval
    def _set_submittedval(self, value):
        self._valid = None
        self.errors = []
        self._submittedval = value
        
        # use self.value to make sure processing gets done
        if is_given(value) and self.is_valid():
            self._set_members(self.value)
    submittedval = property(_get_submittedval, _set_submittedval)

    def _to_python_processing(self):
        """
            we may need to add a processor, but this can't happen in init
            because we want to allow more members to be added
        """
        if self.to_python_first:
            self.to_python_first = False
            if self.auto_validate:
                options = list(self.members.items())
                if self.required:
                    self.add_processor(Select(options, self.invalid), self.error_msg)
                else:
                    # NotGiven is a valid option as long as a value isn't required
                    self.add_processor(Select(options + [(NotGivenIter, 0)], self.invalid), self.error_msg)
        FormFieldElementBase._to_python_processing(self)
    
    def _set_members(self, values):
        # convert to dict with unicode keys so our comparisons are always
        # the same type
        values = dict([(unicode(v), 1) for v in tolist(values)])

        # based on our values, set our members to chosen or not chosen
        for key, el in self.members.items():
            if values.has_key(unicode(key)):
                el.chosen = True
            else:
                el.chosen = False

    def add_member(self, el):
        if self.members.has_key(el.displayval):
            raise ValueError('a member of this group already exists with value "%s"' % el.displayval)
        self.members[el.displayval] = el

class PassThruElement(HasValueElement):
    """
    This element is a non-rendering element that simply allows you to set
    a value and get that same value as .value.  It is impossible
    for this field to be set by submitted values, so .value is safe as long
    as your original was correct.
    """
    def __init__(self, form, eid, defaultval=NotGiven, label=NotGiven, **kwargs):
        HasValueElement.__init__(self, form, eid, label, defaultval, **kwargs)

    def _bind_to_form(self):
        self.form.bind_element(self, render=False, submit=False)
    
    def _get_submittedval(self):
        raise NotImplementedError('element does not allow submitted values')
    def _set_submittedval(self, value):
        raise NotImplementedError('element does not allow submitted values')
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def _get_value(self):
        return self.defaultval
    value = property(_get_value)
form_elements['passthru'] = PassThruElement

class FixedElement(PassThruElement):
    """
    Like PassThruElement, but renders like a StaticElement
    """
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, **kwargs):
        PassThruElement.__init__(self, form, eid, defaultval, label, **kwargs)

    def _bind_to_form(self):
        self.form.bind_element(self, submit=False)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        self.set_attrs(**kwargs)
        return HTML.tag('div', self.value, **self.attributes)
form_elements['fixed'] = FixedElement

class StaticElement(ElementBase):
    """
    This element renders, but does not take submitted values or return values.
    It is for display/rendering purposes only.
    """
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, *args, **kwargs):
        ElementBase.__init__(self, form, eid, label, defaultval, *args, **kwargs)

    def _bind_to_form(self):
        self.form.bind_element(self, submit=False, retval=False)
    
    def _get_submittedval(self):
        raise NotImplementedError('element does not allow submitted values')
    def _set_submittedval(self, value):
        raise NotImplementedError('element does not allow submitted values')
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def _get_value(self):
        raise NotImplementedError('element does not have a value')
    value = property(_get_value)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
        
    def render(self, **kwargs):
        self.set_attrs(**kwargs)
        return HTML.tag('div', self.displayval or '', **self.attributes)
form_elements['static'] = StaticElement

class GroupElement(StaticElement, ElementRegistrar):
    """
    HTML class for a form element group
    
    Groups can be used both for visual grouping of the elements (e.g. putting
    "Submit" and "Reset" buttons in one row or two text fields for first and
    last name in one row).
    """
    def __init__(self, form, eid, label=NotGiven, **kwargs):
        StaticElement.__init__(self, form, eid, label, NotGiven, **kwargs)
        ElementRegistrar.__init__(self, form, self)

        # duplicate form variables for when the elements "bind" to us
        self.all_els = form.all_els
        self.defaultable_els = form.defaultable_els
        self.submittable_els = form.submittable_els
        self.returning_els = form.returning_els
        self.element_id_formatter = form.element_id_formatter
        self.name = form.name
        
        # but we keep the rendering elements to ourself
        self.render_els = []
form_elements['elgroup'] = GroupElement

class HeaderElement(StaticElement):
    """
    A rendering element used for adding headers to a form
    
    Headers will normally be rendered differently than other static elements,
    hence they have their own class
    """
    def __init__(self, form, eid, defaultval, level='h3', **kwargs):
        StaticElement.__init__(self, form, eid, label=NotGiven, defaultval=defaultval, **kwargs)
        self.level = level
        
    def render(self, **kwargs):
        self.set_attrs(**kwargs)
        return HTML.tag(self.level, self.displayval, **self.attributes)
form_elements['header'] = HeaderElement

class LogicalSupportElement(ElementBase):
    """
        a checkbox for "group" use.  `defaultval` is what goes in the "value"
        attribute.  `chosen` is set by the parent LogicalGroupElement when
        it's submitval is set.
        
        these elements are used to support LogicalGroupElement
    """
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, group=NotGiven, *args, **kwargs):
        ElementBase.__init__(self, form, eid, label, defaultval, *args, **kwargs)
        if isinstance(group, basestring):
            self.lgroup = getattr(form, group, None)
            if not self.lgroup:
                self.lgroup = LogicalGroupElement(self.is_multiple, form, group)
        elif not isinstance(group, LogicalGroupElement):
            raise TypeError('lgroup should be a string or LogicalGroupElement')
        else:
            self.lgroup = group
        self.lgroup.add_member(self)
        self.chosen = False
        self.chosen_attr = 'checked'
    
    def _bind_to_form(self):
        self.form.bind_element(self, submit=False, retval=False)
    
    def _get_submittedval(self):
        raise NotImplementedError('element does not allow submitted values')
    def _set_submittedval(self, value):
        raise NotImplementedError('element does not allow submitted values')
    submittedval = property(_get_submittedval, _set_submittedval)
    
    def _get_value(self):
        raise NotImplementedError('element does not have a value')
    value = property(_get_value)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)
    
    def render(self, **kwargs):
        if self.displayval:
            self.set_attr('value', self.displayval)
        self.set_attr('class_', self.etype)
        if self.chosen:
            self.set_attr(self.chosen_attr, self.chosen_attr)
        else:
            try:
                self.del_attr(self.chosen_attr)
            except KeyError:
                pass
        self.set_attr('name', self.lgroup.id)
        self.set_attrs(**kwargs)
        return HTML.input(type=self.etype, **self.attributes)

class MultiCheckboxElement(LogicalSupportElement):
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, group=NotGiven, checked=False, *args, **kwargs):
        chosen = bool(checked)
        self.is_multiple = True
        LogicalSupportElement.__init__(self, form, eid, label, defaultval, group, *args, **kwargs)
        self.chosen = chosen
        self.chosen_attr = 'checked'
        self.etype = 'checkbox'
form_elements['mcheckbox'] = MultiCheckboxElement

class RadioElement(LogicalSupportElement):
    def __init__(self, form, eid, label=NotGiven, defaultval=NotGiven, group=NotGiven, selected=False, *args, **kwargs):
        chosen = bool(selected)
        self.is_multiple = False
        LogicalSupportElement.__init__(self, form, eid, label, defaultval, group, *args, **kwargs)
        self.chosen = chosen
        self.chosen_attr = 'selected'
        self.etype = 'radio'
form_elements['radio'] = RadioElement



