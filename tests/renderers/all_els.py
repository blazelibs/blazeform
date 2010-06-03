import datetime
from pysform import Form

class TestForm(Form):
    def __init__(self):
        Form.__init__(self, 'testform')

        blah = self._name
        
        el = self.fields.add_button('button', 'Button', defaultval='PushMe')
        el = self.fields.add_checkbox('checkbox', 'Checkbox')
        el = self.fields.add_file('file', 'File')
        el = self.fields.add_hidden('hidden', defaultval='my hidden val')
        el = self.fields.add_image('image', 'Image', defaultval='my image val', src='images/icons/b_edit.png')
        el = self.fields.add_reset('reset')
        el = self.fields.add_submit('submit')
        el = self.fields.add_cancel('cancel')
        el = self.fields.add_text('text', 'Text')
        # a little out of order
        el = self.fields.add_password('password', 'Password')
        el = self.fields.add_confirm('confirm', 'Confirm Password', match='password')
        el = self.fields.add_date('date', 'Date', defaultval=datetime.date(2009, 12, 3))
        emel = self.fields.add_email('email', 'Email')
        el = self.fields.add_time('time', 'Time')
        el = self.fields.add_url('url', 'URL')
        options = [('1', 'one'), ('2','two')]
        el = self.fields.add_select('select', options, 'Select')
        el = self.fields.add_mselect('mselect', options, 'Multi Select')
        el = self.fields.add_textarea('textarea', 'Text Area')
        el = self.fields.add_passthru('passthru', 123)
        el = self.fields.add_fixed('fixed', 'Fixed', 'fixed val')
        el = self.fields.add_static('static', 'Static', 'static val')
        el = self.fields.add_header('header', 'header')
        
        # test element group with class attribute
        sg = self.fields.add_elgroup('group')
        sg.add_text('ingroup1', 'ingroup1')
        sg.add_text('ingroup2', 'ingroup2')
        
        self.fields.add_mcheckbox('mcb1', 'mcb1', defaultval='red', group='mcbgroup')
        self.fields.add_mcheckbox('mcb2', 'mcb2', defaultval='green', group='mcbgroup')

        self.fields.add_radio('r1', 'r1', defaultval='truck', group='rgroup')
        self.fields.add_radio('r2', 'r2', defaultval='car', group='rgroup')
        
        self.fields.add_radio('animal_dog', 'dog', defaultval='dog', group='animalgroup', label_after=True)
        self.fields.add_radio('animal_cat', 'cat', defaultval='cat', group='animalgroup', label_after=True)
