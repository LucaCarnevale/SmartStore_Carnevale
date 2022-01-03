from django import forms

PAYMENT_CHOICES = (
    ('C', 'Pagamento alla consegna'),
)

'''
Form utilizzato per il checkout nel quale vengono inserite
tutte le informazioni relative al pagamento e all' indirizzo di spedizione.
'''
class CheckoutForm(forms.Form):
    stato = forms.CharField(required=False)
    città = forms.CharField(required=False)
    via = forms.CharField(required=False)
    cap = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Codice postale'}))
    interno = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': ' Numero appartamento '}))
    note = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': ' ulteriori precisazioni '}))
    save_info = forms.BooleanField(required=False)  # set default shipping
    use_default_shipping = forms.BooleanField(required=False)
    opzioni_pagamento = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)  # ne possiamo selezionare solo uno alla volta
