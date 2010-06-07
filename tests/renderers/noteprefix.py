import datetime
from pysform import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'noteprefixform')
        el = self.elements.add_header('header', 'Header')
        el = self.elements.add_text('text', 'Text', required=True)
        el.add_note('hi there!')
        el = self.elements.add_text('text2', 'Text', settings={'note_prefix':''})
        el.add_note('hi there!')
        
submitted_vals = {
    'noteprefixform-submit-flag' : 'submit'
}

render_opts = {
    'note_prefix' : 'np - ',
    'error_prefix' : 'ep - ',
}