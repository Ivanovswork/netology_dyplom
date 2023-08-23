from django import forms


class ContactForm(forms.Form):
    adress = forms.CharField()
    t_number = forms.CharField()
