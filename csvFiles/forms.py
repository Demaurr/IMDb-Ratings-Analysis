# myapp/forms.py
from django import forms

class FileUploadForm(forms.Form):
    csv_file = forms.FileField()
