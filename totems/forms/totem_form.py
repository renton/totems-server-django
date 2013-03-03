from django import forms

class TotemForm(forms.Form):
    client_device_id = forms.CharField()
    message = forms.TextField()
    
