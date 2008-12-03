from os import path
from util import HtmlAttributeHolder, ElementHolder
import formencode
import formencode.validators as fevalidators
from validators import Select

class Label(object):
    """
    A class which represents the label associated with an element
    """
    def __init__(self, element):
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
        self.value = None
    
    def setValue(self, value):
        """
        @param value: the value the label should display
        @type value: C{str}
        """
        self.value = value
    
    def getValue(self):
        return self.value
    
    def render(self, **kwargs):
        from webhelpers.html import HTML
        kwargs['for'] = self.element.getId()
        return HTML.label(self.value, **kwargs)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)

class ElementBase(HtmlAttributeHolder):
    """
    Base class for form elements.
    """
    def __init__(self, form, eid, displayName, value=None, name=None, **kwargs):
        """
        @param form: the parent form of this element
        @type form: instantiated pyHtmlQuickForm.form
        @param eid: the id of this element.  It will be used to create the
            html "id" attribute.
        @type eid: C{str}
        @param name: the name of this element.  It corresponds to the html "name"
            attribute.
        @type name: C{str}
        @param displayName: the display name of this element (used in labels and
            error messages)
        @type displayName: C{str}
        @param attrs: HTML attributes for this element
        @type attrs: dictionary
        """
        HtmlAttributeHolder.__init__(self, **kwargs)
        
        #: unique id for this element
        self.id = eid
        #: the parent form of this element
        self.form = form
        #: the name of this element
        self._name = name
        #: the display name of this element (used for labels and error messages)
        self.displayName = displayName
        #: the element type, corresponds to the name of a registered type (C{str})
        self._type = None
        #: the default value that is set programmatically
        self.defaultValue = None
                
        # set the default value
        self.setDefaultValue(value)

    def getType(self):
        """
        returns the element's type, which corresponds to the name of a
        registered element (C{str})
        """
        return self._type
    
    def setType(self, type):
        """
        @param type: the element's type, which corresponds to the name of a
        registered type
        @type type: C{str}
        """
        self._type = type
        
    def setDefaultValue(self, value):
        """
        @param value: the value the form field should start with, usually from
            a database or programmatically set
        @type value: any Python type, will be converted to a C{str}
        """
        self.defaultValue = value
        
    def getDefaultValue(self):
        return self.defaultValue
    
    def _renderPrep(self, attrs):
        self.setAttribute('id', self.getId())
        self.setAttribute('class', self.getType())
        self.setAttributes(**attrs)
    
    def __call__(self, **kwargs):
        return self.render(**kwargs)

    def getDisplayName(self):
        if not self.displayName:
            return self.name
        return self.displayName
    
    def getId(self):
        return self.form.element_id_formatter % {'form_name':self.form.name, 'element_id':self.id}
    
    def _get_name(self):
        return self._name or self.id
    
    name = property(_get_name)
    
    def handle_exception(self, e):
        """ can be overridden to help with handling expected exceptions """
        return False

class LabelElementBase(ElementBase):
    """
    Abstract base class for elements that have a label.  Instantiates a label object,
    assigns that object to an instance variable and provides methods for working
    with the label.
    """
    def __init__(self, form, eid, displayName, hasLabel = True, **kwargs):
        ElementBase.__init__(self, form, eid, displayName, **kwargs)
        
        #: an instantiated pyhtmlquickform.element.ElementLabel object
        if hasLabel:
            self.label = Label(self)
    
    def setLabel(self, value):
        """
        @param value: the value to set the label's display text to
        @type value: C{str}
        """
        try:
            self.label.setValue(value)
        except AttributeError:
            pass

class FormFieldElementBase(LabelElementBase):
    """
    Base class for form elements that represent form fields (input, select, etc.)
    as opposed to Elements that are only for display (i.e. static, headers).
    """
    def __init__(self, form, eid, displayName, required = False, **kwargs):

        # initialize the base element
        LabelElementBase.__init__(self, form, eid, displayName, **kwargs)

        #: the raw value that is set from a form submission C{str}
        self.submittedValue = None
        #: the value after it has passed through all filters and rules and been converted to a Python type
        self.processedValue = None
        #: a list of error messages for this field (C{str})
        self.errors = []
        #: a list of user messages for this field (C{str})
        self.notes = []
        #: pre-validation conversion
        self.filters = []
        #: a list of validators for this field
        self.validators = []
        #: a list of converters for this field
        self.converters = []
        #: is this field required in order for the form submission to be valid?
        self.required = required
        #: whether or not this field is valid, None means the field has not been processed yet
        self.valid = None
        #: allows a form/element to "expect" an exception and handle gracefully
        self.exception_handlers = []
        
        # set the default value of the label
        self.setLabel(self.displayName)
    
    def setSubmitValue(self, value):
        """
        @param value: the value from a POST or GET form submission.  This value
            should be considered UNSAFE until it passes through all the elements
            filters, rules, and is converted to a Python type.
        @type value: any Python type, will be converted to a C{str}
        """
        # we want to process the value again since it might have been changed
        self.valid = None
        
        self.submittedValue = value
        
    def getSubmitValue(self):
        return self.submittedValue

    def currentValue(self, submittedValue=None):
        """
        returns the current value of this element.  Looks for a submitted value
        first and if not found then looks for a default value
        """
        #if submittedValue != None:
        #    self.setSubmittedValue(submittedValue)
        
        if self.submittedValue != None:
            return self.submittedValue
        else:
            return self.defaultValue

    def getValue(self):
        """
        returns a "safe" value after the submitted value has been 
        processed through all filters, rules, and conversions succesfully
        """
        self._processValue()
        return self.processedValue

    def isValid(self):
        """
            tests whether the submitted value is valid
        """
        self._processValue()
        return self.valid
    
    def _processValue(self):
        """
        filters, validates, and converts the submitted value
        """
        valid = True
        
        # if the value has already been processed, don't process it again
        if self.valid != None:
            return
        
        value = self.getSubmitValue()

        # process filters
        for vfilter in self.filters:
            if isinstance(value, list):
                value = map(vfilter, value)
            else:
                value = vfilter(value)
        
        # process required
        if self.required and (value == '' or value == None):
            valid = False
            self.addError('"%s" is required' % self.getDisplayName())
        
        # process validators
        for validator, msg in self.validators:
            try:
                try:
                    value = validator.to_python(value)
                except AttributeError, e:
                    value = validator(value)
            except (formencode.Invalid, ValueError), e:
                valid = False
                self.addError((msg or e))
        # convert
        
        # save
        if valid:
            self.processedValue = value
            self.valid = True
        else:
            self.valid = False
    
    def addError(self, error):
        self.errors.append(error)
    
    def addNote(self, note, escapeHtml = True):
        if escapeHtml:
            from cgi import escape
            note = escape(note)
        self.notes.append(note)
    
    def addValidator(self, validator, msg = None):
        self.validators.append((validator, msg))
    
    def add_filter(self, filter):
        self.filters.append(filter)
    
    def onexc(self, looking_for, error_msg):
        self.exception_handlers.append((looking_for, error_msg))

    def handle_exception(self, exception_text):
        for looking_for, error_msg in self.exception_handlers:
            if looking_for in exception_text:
                self.valid = False
                self.addError(error_msg)
                return True
        return False

class InputElementBase(FormFieldElementBase):
    """
    Base class for input form elements.
    
    Since <input> elements have very similar HTML representations, they have this common base class. You don't need to instantiate it directly, use one of the child classes.
    """        
    pass
        

class TextElement(InputElementBase):
    def __init__(self, form, eid, displayName=None, length=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('text')
        
        #: the number of characters allowed in the field
        self.length = None
        
        self.setLength(length)
        
    def setLength(self, size):
        """
        @param size: the number of characters allowed in the field
        @type size: C{int}
        """
        
        # if size is none, set it to None and return
        if size == None:
            self.length = None
            return
        
        # make sure the size is an integer
        if type(1) == type(size):
            self.length = size
        else:
            raise TypeError('Length should have been int but was %s' % type(size))
    
    def _renderPrep(self, attrs):
        # do any render prep in ancestor classes
        super(TextElement, self)._renderPrep(attrs)
        
        self.setAttribute('maxlength', self.length)
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import text
        return text(self.name, self.currentValue(), **self.attributes)

class DateTimeElement(TextElement):
    def __init__(self, form, eid, displayName=None, **kwargs):
        TextElement.__init__(self, form, eid, displayName, **kwargs)
        
        self.addValidator(fevalidators.DateConverter())

class PasswordElement(TextElement):
    def __init__(self, form, eid, displayName=None, length=None, **kwargs):
        TextElement.__init__(self, form, eid, displayName, **kwargs)
        self.setType('password')

    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import password
        return password(self.name, u'', **self.attributes)

class CheckboxElement(InputElementBase):
    def __init__(self, form, eid, displayName=None, checked=False, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('checkbox')
        
        if checked != False:
            self.setDefaultValue(1)
    
    def getValue(self):
        value = InputElementBase.getValue(self)
        if value:
            return True
        return False
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import checkbox
        #print str(self.getDefaultValue()) + ' ' + str(self.getSubmitValue()) + ' ' + str(self.currentValue())
        if self.currentValue() == None or self.currentValue() == False or self.currentValue() == '':
            checked = False
        else:
            checked = True
        return checkbox(self.name, checked=checked, **self.attributes)

class SubmitElement(InputElementBase):
    def __init__(self, form, eid, value=None, displayName=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, value=value, hasLabel=False, **kwargs)
        self.setType('submit')
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import submit
        return submit(self.name, self.currentValue(), **self.attributes)

class CancelElement(SubmitElement):
    pass

class HiddenElement(InputElementBase):
    def __init__(self, form, eid, value=None, displayName=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, value=value, hasLabel=False, **kwargs)
        self.setType('hidden')
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import hidden
        return hidden(self.name, self.currentValue(), **self.attributes)

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
    def __init__(self, form, eid, displayName=None, maxsize=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('file')
        self.content_type = None
        self.file_name = None
        self._allowed_exts = []
        self._allowed_types = []
        self._denied_exts = []
        self._denied_types = []
        self._maxsize = maxsize
        
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
                
        self.valid = valid
    
    def addValidator(self, *args, **kwargs):
        raise NotImplementedError('FileElement does not support addValidator()')
    
    def render(self, **kwargs):
        self._renderPrep(kwargs)
        from webhelpers.html.tags import file
        return file(self.name, '', **self.attributes)

class StaticValueElement(InputElementBase):
    def __init__(self, form, eid, displayName=None, length=None, **kwargs):
        InputElementBase.__init__(self, form, eid, displayName, **kwargs)
        self.setType('static-value')

    def render(self, **kwargs):
        self._renderPrep(kwargs)
        return self.currentValue()

class StaticElement(LabelElementBase):
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

#: elements that correspond to HTML form elements
form_elements = {
    'text': TextElement,
    'submit': SubmitElement,
    'hidden': HiddenElement,
    'checkbox': CheckboxElement,
    'textarea': TextAreaElement,
    'select': SelectElement,
    'password': PasswordElement,
    'datetime': DateTimeElement,
    'file': FileElement,
    'cancel': CancelElement,
    'static-value': StaticValueElement,
    'passthru' : PassThruElement
}

#: elements that correspond to non-form HTML elements
html_elements = {
    'static': StaticElement,
    'header': HeaderElement,
    'group': GroupElement
}

#: all elements
all_elements = {}
all_elements.update(html_elements)
all_elements.update(form_elements)

