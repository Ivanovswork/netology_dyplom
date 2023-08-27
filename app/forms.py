from django import forms


class ContactForm(forms.Form):
    adress = forms.CharField()
    t_number = forms.CharField()


class OrderItemForm(forms.Form):
    product_info = forms.CharField()
    quantity = forms.IntegerField()


class OrderItemUpdateForm(forms.Form):
    orderitem_id = forms.CharField()
    quantity = forms.IntegerField()
