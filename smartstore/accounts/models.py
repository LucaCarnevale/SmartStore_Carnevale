from django.contrib.auth.models import User
from django.db import models
from core.models import Item
import json
import string

"""
Modello utilizzato per registrare i dati dell' utente nel sito.
"""


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    item = models.ManyToManyField(Item)

    def __str__(self):
        return self.user.username