
class BaseRenderer(object):
    
    def __init__(self, form):
        self.form = form
        self.output = []
        self.element_count = 0
        
    def startForm(self):
        return ''
    
    def finishForm(self):
        return ''
    
    def startGroup(self):
        return ''
    
    def finishGroup(self):
        return ''
    
    def renderElement(self, element):
        return ''

    def render(self):
        self.output.append(self.startForm())
        for element in self.form.render_els:
            self.element_count += 1
            self.output.append(self.renderElement(element))
        self.output.append(self.finishForm())
        
        return '\n'.join(self.output)
# renderElement
# renderHeader
# renderHidden
# renderHtml


class CssRenderer(BaseRenderer):
    def __init__(self, form):
        BaseRenderer.__init__(self, form)
        
        self.first = True
        self.alt_count = 0
        
        from util import StringIndentHelper
        self.ind = StringIndentHelper()
        self.hidden_fields = StringIndentHelper()
        self.hidden_fields.level = 1
        self.div_open = False
        
    def renderFirstClass(self):
        if self.first == True:
            return ' first'
        return ''
    
    def renderAltClass(self):
        if self.alt_count % 2 == 0:
            return ' even'
        return ' odd'
    
    def startForm(self):
        from webhelpers.html.tags import form
        attr = self.form.get_attrs()
        self.ind.inc(form(self.form.action, **attr))
        return self.ind.get()
    
    def finishForm(self):
        if self.div_open:
            self.ind.dec('</div>')
        from webhelpers.html.tags import end_form
        self.ind.dec(end_form())
        return '%s\n%s' % (self.hidden_fields.get(), self.ind.get() )
    
    def renderElement(self, element):
        try:
            if element.type == 'header':
                return self.renderHeader(element)
            elif element.type == 'static':
                self.alt_count += 1
                return self.renderStatic(element)
            elif element.type == 'hidden':
                return self.renderHidden(element)
            elif element.type == 'suasdfbmit':
                self.alt_count += 1
                return self.renderSubmit(element)
            elif element.type == 'group':
                self.alt_count += 1
                return self.renderGroup(element)
            elif element.type == 'passthru':
                return ''
            else:
                self.alt_count += 1
                return self.renderField(element)
        finally:
            non_first_reset_elements = ('header', 'hidden', 'passthru')
            if element.type not in non_first_reset_elements:
                self.first = False
    
    def renderField(self, element):
        first_class = self.renderFirstClass()
        alt_class = self.renderAltClass()
        self.ind.inc('<div class="row %s%s%s">' % (element.type, first_class, alt_class))
        
        try:
            self.ind(element.label())
            no_label_class = ''
        except AttributeError:
            no_label_class = ' no-label'
    
        self.ind.inc('<div class="field-wrapper%s">' % (no_label_class, ))
        if element.required:
            self.ind('<span class="required-star">*</span>')
        self.ind(element())
        
        # field notes
        if len(element.notes) == 1:
            self.ind('<p class="note">%s</p>' % (element.notes[0], ))
        elif len(element.notes) > 1:
            self.ind.inc('<ul class="notes">')
            for msg in element.notes:
                self.ind('<li>%s</li>' % (msg, ))
            self.ind.dec('</ul>')
            
        # field errors
        if len(element.errors) == 1:
            self.ind('<p class="error">%s</p>' % (element.errors[0], ))
        elif len(element.errors) > 1:
            self.ind.inc('<ul class="errors">')
            for msg in element.errors:
                self.ind('<li>%s</li>' % (msg, ))
            self.ind.dec('</ul>')
        self.ind.dec('</div>')
        self.ind.dec('</div>')
        return self.ind.get()
    
    def renderSubmit(self, element):
        first_class = self.renderFirstClass()
        alt_class = self.renderAltClass()
        self.ind.inc('<div class="row buttons-only%s%s">' % (first_class, alt_class))    
        self.ind(element())
        self.ind.dec('</div>')
        return self.ind.get()
    
    def renderHidden(self, element):
        self.hidden_fields(element())
        return ''
    
    def renderHeader(self, element):
        if self.div_open:
            self.ind.dec('</div>')
        self.div_open = True
        # reset first so that the next element gets the first class
        self.first = True
        # alternate rows should start over after a header is rendered
        self.alt_count = 0
        self.ind('<div id="%s-wrapper">' % element.id)
        self.ind(element())
        # opening div is closed either at next header or at end of form
        return self.ind.get()
    
    def renderGroup(self, element):
        for el in element.elements:
            self.ind(el())
        return self.ind.get()
    
    def renderStatic(self, element):
        self.ind(element())
        return self.ind.get()

    def _indent(self, level):
        return '    '*level