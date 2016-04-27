from django import forms


class TestSuiteDetailForm(forms.Form):
    result_overview_from = forms.DateField(
        label=u'Dato fra:',
        input_formats=['%d-%m-%Y'],
        required=False
    )
    result_overview_to = forms.DateField(
        label=u'Dato til:',
        input_formats=['%d-%m-%Y'],
        required=False
    )
    executed_tests_from = forms.DateField(
        label=u'Dato fra:',
        input_formats=['%d-%m-%Y'],
        required=False
    )
    executed_tests_to = forms.DateField(
        label=u'Dato til:',
        input_formats=['%d-%m-%Y'],
        required=False
    )

    def __init__(self, qdict, *args, **kwargs):
        super(TestSuiteDetailForm, self).__init__(qdict, *args, **kwargs)
        extra_classes = {
            'result_overview_from': 'datepicker',
            'result_overview_to': 'datepicker',
            'executed_tests_from': 'datepicker',
            'executed_tests_to': 'datepicker'
        }

        # Add classnames to all fields
        for fname, f in self.fields.iteritems():
            f.widget.attrs['class'] = " ".join([
                x for x in (
                    f.widget.attrs.get('class'),
                    extra_classes.get(fname)
                ) if x
            ])
            f.widget.attrs['data-provide'] = "datepicker"
