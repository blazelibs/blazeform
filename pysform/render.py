
from pysform.form import FormBase
from pysform.util import StringIndentHelper, NotGiven, HtmlAttributeHolder
from pysform import element
from webhelpers.html import tags, HTML
from webhelpers.html.builder import make_tag

class FormRenderer(object):
    def __init__(self, element):
        self.element = element
        self.output = StringIndentHelper()
        self.header_section_open = False
        self.settings = {}

    def begin(self):
        attr = self.element.get_attrs()
        action = attr.pop('action', '')
        self.output.inc(tags.form(action, **attr))
    
    def render(self, **kwargs):
        self.settings.update(kwargs)
        self.begin()
        on_first = True
        on_alt = False
        for child in self.rendering_els():
            if isinstance(child, element.HeaderElement):
                if self.header_section_open:
                    self.output.dec('</div>')
                on_first = True
                hstr = '<div id="%s-section" class="header-section">' % child.getidattr()
                self.output.inc(hstr)
                self.header_section_open = True
            rcls = get_renderer(child)
            r = rcls(child, self.output, on_first, on_alt, 'row', self.settings)
            r.render()
            if r.uses_alt:
                on_alt = not on_alt
            if r.uses_first:
                on_first = False
        self.end()
        return self.output.get()
    
    def rendering_els(self):
        for el in self.element._render_els:
            yield el
    
    def end(self):
        if self.header_section_open:
            self.output.dec('</div>')
        self.output.dec('</form>')

class StaticFormRenderer(FormRenderer):
    no_render = (
        element.ButtonElement,
        element.FileElement,
        element.HiddenElement,
        element.ImageElement,
        element.ResetElement,
        element.SubmitElement,
        element.CancelElement,
        element.PasswordElement,
        element.ConfirmElement
    )
    def begin(self):
        attrs = HtmlAttributeHolder(**self.element.attributes)
        attrs.add_attr('class', 'static-form')
        for attr in ('enctype', 'method', 'action'):
            try:
                attrs.del_attr(attr)
            except KeyError:
                pass
        self.output.inc(HTML.div(None, _closed=False, **attrs.attributes))
    
    def rendering_els(self):
        for el in self.element._render_els:
            if not isinstance(el, self.no_render):
                yield el
            
    def end(self):
        if self.header_section_open:
            self.output.dec('</div>')
        self.output.dec('</div>')
        
class Renderer(object):
    def __init__(self, element, output, is_first, is_alt, wrap_type, settings):
        self.element = element
        self.output = output
        self.wrap_type = wrap_type
        self.uses_alt = False
        self.uses_first = False
        self.is_first = is_first
        self.is_alt = is_alt
        self.settings = settings
            
    def first_class(self):
        if self.is_first:
            return ' first'
        return ''
    
    def alt_class(self):
        if self.is_alt:
            return ' even'
        return ' odd'
    
    def begin(self):
        pass
    def render(self):
        self.begin()
        self.output(self.element.render())
        self.end()
    def end(self):
        pass

class HeaderRenderer(Renderer):
    def render(self):
        self.begin()
        if self.element.defaultval is not NotGiven:
            self.output(self.element.render())
        self.end()

class FieldRenderer(Renderer):
    def __init__(self, element, output, is_first, is_alt, wrap_type, settings):
        Renderer.__init__(self, element, output, is_first, is_alt, wrap_type, settings)
        self.uses_first = True
        self.uses_alt = True
    def begin(self):
        self.begin_row()
        self.label()
        self.field_wrapper()
        self.required()
    def begin_row(self):
        self.output.inc('<div id="%s-%s" class="%s%s%s">' %
                (self.element.getidattr(), self.wrap_type, self.wrap_type,
                 self.alt_class(), self.first_class())
            )
    def label(self):
        if self.element.label.value:
            self.element.label.value += ':'
            self.output(self.element.label())
            self.no_label_class = ''
        else:
           self.no_label_class = ' no-label'
    def field_wrapper(self):
        self.output.inc('<div id="%s-fw" class="field-wrapper%s">' %
                            (self.element.getidattr(), self.no_label_class))
    def required(self):
        if self.element.required and not self.element.form._static:
            self.output('<span class="required-star">*</span>')
    def notes(self):
        if len(self.element.notes) == 1:
            self.output('<p class="note">%s%s</p>' % (
                self.settings.get('note_prefix', ''),
                self.element.notes[0]
            ))
        elif len(self.element.notes) > 1:
            self.output.inc('<ul class="notes">')
            for msg in self.element.notes:
                self.output('<li>%s%s</li>' % (
                    self.settings.get('note_prefix', ''),
                    msg
                ))
            self.output.dec('</ul>')
    def errors(self):
        if len(self.element.errors) == 1:
            self.output('<p class="error">%s%s</p>' % (
                self.settings.get('error_prefix', ''),
                self.element.errors[0]
            ))
        elif len(self.element.errors) > 1:
            self.output.inc('<ul class="errors">')
            for msg in self.element.errors:
                self.output('<li>%s%s</li>' % (
                    self.settings.get('error_prefix', ''),
                    msg
                ))
            self.output.dec('</ul>')
    def end(self):
        self.notes()
        self.errors()
        # close field wrapper
        self.output.dec('</div>')
        # close row
        self.output.dec('</div>')
        
        
class InputRenderer(FieldRenderer):
    def begin_row(self):
        self.output.inc('<div id="%s-%s" class="%s %s%s%s">' %
                (self.element.getidattr(), self.wrap_type, self.element.etype,
                 self.wrap_type, self.alt_class(), self.first_class())
            )

class StaticRenderer(FieldRenderer):
    def required(self):
        pass
    def errors(self):
        pass
    
class GroupRenderer(StaticRenderer):
    
    def begin_row(self):
        self.element.set_attr('id', '%s-%s' % (self.element.getidattr(), self.wrap_type))
        class_str = '%s%s%s' % (self.wrap_type, self.alt_class(), self.first_class())
        self.element.add_attr('class', class_str)
        # make_tag should not close the div
        attrs = self.element.get_attrs()
        attrs['_closed'] = False
        self.output.inc(make_tag('div', **attrs))
    def field_wrapper(self):
        self.output.inc('<div id="%s-fw" class="group-wrapper%s">' %
                            (self.element.getidattr(), self.no_label_class))
    def render(self):
        self.begin()
        self.render_children()
        #self.output.dec('</div>')
        self.end()
    
    def render_children(self):
        on_first = True
        on_alt = False
        for child in self.element._render_els:
            r = get_renderer(child)
            rcls = get_renderer(child)
            r = rcls(child, self.output, on_first, on_alt, 'grpel', self.settings)
            r.render()
            if r.uses_alt:
                on_alt = not on_alt
            if r.uses_first:
                on_first = False

def get_renderer(el):
    plain = (
        element.HiddenElement,
    )
    field = (
        element.SelectElement,
        element.TextAreaElement,
    )
    static = (
        element.FixedElement,
        element.StaticElement,
        element.RadioElement,
        element.MultiCheckboxElement,
    )
    if isinstance(el, FormBase):
        if el._static:
            return StaticFormRenderer(el)
        return FormRenderer(el)
    elif isinstance(el, element.GroupElement):
        return GroupRenderer
    elif isinstance(el, element.HeaderElement):
        return HeaderRenderer
    elif isinstance(el, plain):
        return Renderer
    elif isinstance(el, element.InputElementBase):
        return InputRenderer
    elif isinstance(el, field):
        return FieldRenderer
    elif isinstance(el, static):
        return StaticRenderer