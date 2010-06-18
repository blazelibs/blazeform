import datetime
from pysform import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'testform')

        el = self.add_button('button', 'Button', defaultval='PushMe')
        el = self.add_checkbox('checkbox', 'Checkbox')
        el = self.add_file('file', 'File')
        el = self.add_hidden('hidden', defaultval='my hidden val')
        el = self.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.add_reset('reset')
        el = self.add_submit('submit')
        el = self.add_cancel('cancel')
        el = self.add_text('text', 'Text')
        # a little out of order
        el = self.add_password('password', 'Password')
        el = self.add_confirm('confirm', 'Confirm Password', match='password')
        el = self.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        emel = self.add_email('email', 'Email')
        el = self.add_time('time', 'Time')
        el = self.add_url('url', 'URL')
        options = [('1', 'one'), ('2','two')]
        el = self.add_select('select', options, 'Select')
        el = self.add_mselect('mselect', options, 'Multi Select')
        el = self.add_textarea('textarea', 'Text Area')
        el = self.add_passthru('passthru', 123)
        el = self.add_fixed('fixed', 'Fixed', 'fixed val')
        el = self.add_static('static', 'Static', 'static val')
        el = self.add_header('header', 'header')
        
        # test element group with class attribute
        sg = self.add_elgroup('group')
        sg.add_text('ingroup1', 'ingroup1')
        sg.add_text('ingroup2', 'ingroup2')
        
        self.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.add_radio('r2', 'r2', defaultval='car', group='rgroup')
        
        self.add_radio('animal_dog', 'dog', defaultval='dog', group='animalgroup', label_after=True)
        self.add_radio('animal_cat', 'cat', defaultval='cat', group='animalgroup', label_after=True)
