
class WerkzeugTranslator(object):
    def __init__(self, value):
        self.file_name = value.filename
        self.content_type = value.content_type
        self.content_length = value.content_length