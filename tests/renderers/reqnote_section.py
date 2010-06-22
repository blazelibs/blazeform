import datetime
from blazeform.form import Form

class TestForm(Form):
    """ required note at form-top position, but header not in first position """
    def __init__(self):
        Form.__init__(self, 'reqnoteform')
        el = self.add_header('header', 'Header')
        el = self.add_text('text', 'Text')
        el = self.add_text('text3', 'Text3')
        el = self.add_header('header2', 'Header2')
        el = self.add_text('text2', 'Text2')
        el = self.add_text('text4', 'Text4')
        
render_opts = {
    'req_note_level' : 'section'
}