from pysform.form import Form

# fix the bug in the formencode MaxLength validator
from formencode.validators import MaxLength
MaxLength._messages['__buggy_toolong'] = MaxLength._messages['tooLong']
MaxLength._messages['tooLong'] = 'Enter a value not greater than %(maxLength)i characters long'

#all_by_module = {
#    'pysform.forms':       ['Form'],
#    'pysform.elements':    ['ButtonElement', 'CheckboxElement', 'FileElement',
#            'HiddenElement', 'ImageElement', 'SubmitElement', 'ResetElement',
#            'CancelElement', 'TextElement', 'ConfirmElement', 'DateElement', 
#            'DateTimeElement', 'EmailElement', 'PasswordElement', 'TimeElement',
#            'URLElement', 'SelectElement', 'TextAreaElement', 'PassThru', 
#            'StaticElement', 'RenderGroupElement', 'HeaderElement',
#            'RadioElement', 'CheckboxGroupElement'
#    ]
#        
#}