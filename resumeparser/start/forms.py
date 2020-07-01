from django import forms


class UploadFileForm(forms.Form):
    file = forms.FileField(label='',widget=forms.FileInput(attrs={'style' : 'display:none;','value':'choosefile','placeholder':'choosefile'}))