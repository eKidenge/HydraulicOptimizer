from django import forms

class OptimizationForm(forms.Form):
    inp_file = forms.FileField(label='Upload EPANET INP File')
