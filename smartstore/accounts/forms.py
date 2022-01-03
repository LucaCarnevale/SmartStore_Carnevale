from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

"""
Classe utilizzata per la registrazione di un utente.
Essa estende il form predefinito di Django, associando 
un indirizzo email all' account.
"""


class FormRegistrazione(UserCreationForm):
    email = forms.CharField(max_length=100, required=True, widget=forms.EmailInput())
    """
    Classe contenente i campi che il guest deve compilare per potersi registrare.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
