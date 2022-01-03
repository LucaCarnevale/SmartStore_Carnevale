from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
from .forms import FormRegistrazione

'''
Test per il login di un utente
Prima viene testato con credenziali errate, poi con credenziali corrette
'''
class LoginTest(TestCase):

    def setUp(self):
        self.test_user = User.objects.create_user(username='test', password='gamberetto', email='test@test.com')

    def test_login(self):
        wrong_credential = {'username': 'ciao', 'password': 'ciao'}
        true_credential = {'username': 'test', 'password': 'gamberetto'}
        t_cred = self.client.login(**true_credential)
        w_cred = self.client.login(**wrong_credential)

        self.assertTrue(t_cred)
        self.assertFalse(w_cred)
