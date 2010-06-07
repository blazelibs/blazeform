import datetime
from pysform import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'testform')

        el = self.elements.add_button('button', 'Button', defaultval='PushMe')
        el = self.elements.add_checkbox('checkbox', 'Checkbox')
        el = self.elements.add_file('file', 'File')
        el = self.elements.add_hidden('hidden', defaultval='my hidden val')
        el = self.elements.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.elements.add_reset('reset')
        el = self.elements.add_submit('submit')
        el = self.elements.add_cancel('cancel')
        el = self.elements.add_text('text', 'Text')
        # a little out of order
        el = self.elements.add_password('password', 'Password')
        el = self.elements.add_confirm('confirm', 'Confirm Password', match='password')
        el = self.elements.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        emel = self.elements.add_email('email', 'Email')
        el = self.elements.add_time('time', 'Time')
        el = self.elements.add_url('url', 'URL')
        options = [('1', 'one'), ('2','two')]
        el = self.elements.add_select('select', options, 'Select')
        el = self.elements.add_mselect('mselect', options, 'Multi Select')
        el = self.elements.add_textarea('textarea', 'Text Area')
        el = self.elements.add_passthru('passthru', 123)
        el = self.elements.add_fixed('fixed', 'Fixed', 'fixed val')
        el = self.elements.add_static('static', 'Static', 'static val')
        el = self.elements.add_header('header', 'header')
        
        # test element group with class attribute
        sg = self.elements.add_elgroup('group')
        sg.elements.add_text('ingroup1', 'ingroup1')
        sg.elements.add_text('ingroup2', 'ingroup2')
        
        self.elements.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.elements.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.elements.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.elements.add_radio('r2', 'r2', defaultval='car', group='rgroup')
        
        self.elements.add_radio('animal_dog', 'dog', defaultval='dog', group='animalgroup', label_after=True)
        self.elements.add_radio('animal_cat', 'cat', defaultval='cat', group='animalgroup', label_after=True)
