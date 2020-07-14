from __future__ import absolute_import
from blazeform.form import Form


class TestForm(Form):
    """ required note at form-top position, but header not in first position """
    def __init__(self):
        Form.__init__(self, 'reqnoteform')
        self.add_header('header', 'Header')
        self.add_text('text', 'Text')
        self.add_header('header2', 'Header2')
        self.add_text('text2', 'Text2')


render_opts = {
    'req_note': '<div>required field</div>',
    'req_note_level': 'form'
}
