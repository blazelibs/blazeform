from os import path

renderers = ('default', 'withaction')
rendir = ''

def test_all():
    global rendir
    for rname in renderers:
        rmod = __import__('renderers.%s' % rname, globals(), locals(), ['TestForm'])
        if rendir == '':
            rendir = path.dirname(rmod.__file__)
        tf = rmod.TestForm()
        form_html = tf.render()
        form_html_lines = form_html.strip().splitlines()
        htmlfile = open(path.join(rendir, '%s.html' % rname))
        try:
            file_html_lines = htmlfile.read().strip().splitlines()
        finally:
            htmlfile.close()
        
        try:
            for lnum in range(0, len(form_html_lines)):
                formstr = form_html_lines[lnum]
                filestr = file_html_lines[lnum]
                assert formstr == filestr, 'line %d not equal\n  form: %s\n  file: %s' % (lnum, formstr, filestr)
        except AssertionError:
            # write the form output next to the test file for an easy diff
            formfile = open(path.join(rendir, '%s.form.html' % rname), 'w')
            try:
                formfile.write(form_html)
            finally:
                formfile.close()
            raise
if __name__ == "__main__":
    test_all()