from django.test import TestCase
from django.contrib.auth.models import User

# Create your tests here.
from .models import Item, ShippingAddress


class CoreCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', email='test@test.com', password='gamberetto')
        self.credential = {'username': 'test', 'password': 'gamberetto'}
        self.item = Item.objects.create(nome="Item Test",
                                        prezzo="30",
                                        categoria="A",
                                        descrizione="Descrizione Item Test",
                                        immagine="n",
                                        condizione='N',
                                        venditore=self.user)

        self.address = ShippingAddress.objects.create(user=self.user,
                                                      città="Del Sole",
                                                      stato="O",
                                                      cap="45667",
                                                      via="n",
                                                      interno="3",
                                                      note="ciao")
        self.user2 = User.objects.create_user(username='test2', email='test2@test.com', password='gamberetto')
        self.credential2 = {'username': 'test2', 'password': 'gamberetto'}

    def test_item_create(self):
        '''
        Verifico che nell' inserimento di un articolo i campi obbligatori siano rispettati
        '''
        self.client.login(**self.credential)
        response = self.client.post('/inserisci_articolo/', {})
        self.assertFormError(response, 'form', 'nome', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'prezzo', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'categoria', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'descrizione', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'immagine', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'condizione', 'Questo campo è obbligatorio.')

        self.assertTemplateUsed(response, 'core/inserisci_articolo.html')
        self.assertEqual(response.status_code, 200)  # verifica per capire se il template utilizzato è quello corretto

        response = self.client.post('/inserisci_articolo/',
                                    {'nome': 'Computer Asus', 'prezzo': '1250', 'categoria': 'I',
                                     'descrizione': 'funzionante',
                                     'immagine': 's',
                                     'condizione': 'U'})
        self.assertTemplateUsed(response, 'core/inserisci_articolo.html')
        self.assertEqual(response.status_code, 200)

    '''
    Test per verificare che l' eliminazione di un articolo vada a buon fine
    '''
    def test_item_delete(self):
        # con utente autenticato
        self.client.login(**self.credential)
        response = self.client.get('/item/' + str(self.item.id) + '/delete/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/item/' + str(self.item.id) + '/delete/', {})
        self.assertRedirects(response, '/user/' + self.user.username + '/')
        self.client.logout()

        # con utente autenticato ma non creatore
        self.client.login(**self.credential2)
        response = self.client.get('/item/' + str(self.item.id) + '/delete/')
        self.assertTemplateNotUsed(response, 'core/item_delete.html')


    '''
    Test per verificare se all' inserimento di un articolo, un utente non loggato
    viene reindirizzato prima nella schermata di login.
    '''
    def test_login_required(self):
        response = self.client.get('/inserisci_articolo/')
        self.assertRedirects(response, '/accounts/login/?next=/inserisci_articolo/')
        # 302 --> FOUND: pagina esiste ma non puoi entrarci
        self.assertEqual(response.status_code, 302)

    '''
    Test della visualizzazione del profilo di un utente autenticato
    e per la visualizzazione del profilo di altri utenti.
    '''
    def test_userProfileView(self):
        # con utente autenticato
        # su il tuo profilo
        self.client.login(**self.credential)
        response = self.client.get('/user/' + self.user.username + '/')
        self.assertTemplateUsed(response, 'core/profilo.html')
        self.assertTrue(response.status_code, 200)

        # sul profilo degli altri
        response = self.client.get('/otheruser/' + self.user2.username + '/')
        self.assertTemplateNotUsed(response, 'core/profilo.html')
        self.assertTemplateUsed(response, 'core/user_profile.html')

        # con utente non autenticato
        self.client.logout()
        response = self.client.get('/otheruser/' + self.user.username + '/')
        self.assertTemplateUsed(response, 'core/user_profile.html')
        self.assertTrue(response.status_code, 200)

    '''
    Test per il cambio dell' indirizzo di un utente 
    '''
    def test_address_change(self):
        # con utente autenticato
        self.client.login(**self.credential)
        response = self.client.get('/user/address/' + str(self.address.id) + '/modify/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/user/address/' + str(self.address.id) + '/modify/', {})
        self.assertFormError(response, 'form', 'città', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'via', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'stato', 'Questo campo è obbligatorio.')
        self.assertFormError(response, 'form', 'cap', 'Questo campo è obbligatorio.')
        response = self.client.post('/user/address/' + str(self.address.id) + '/modify/',
                                    {'città': 'chieti', 'via': 'strada', 'stato': 'it', 'cap': '85710'})
        self.assertRedirects(response, '/user/' + self.user.username + '/address_page/')
        self.client.logout()

        # con utente  autenticato ma non creatore
        self.client.login(**self.credential2)
        response = self.client.get('/user/address/' + str(self.address.id) + '/modify/')
        self.assertTemplateUsed(response, 'core/homepage.html')
        self.assertTemplateNotUsed(response, 'accounts/address_change.html')


    ''' 
    Test per l' eliminazione di un indirizzo dell' utente
    '''
    def test_address_delete(self):
        # con utente autenticato
        self.client.login(**self.credential)
        response = self.client.get('/user/address/' + str(self.address.id) + '/delete/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/user/address/' + str(self.address.id) + '/delete/', {})
        self.assertRedirects(response, '/user/' + self.user.username + '/address_page/')
        self.client.logout()

        # con utente autenticato ma non creatore
        self.client.login(**self.credential2)
        response = self.client.get('/user/address/' + str(self.address.id) + '/delete/')
        self.assertTemplateNotUsed(response, 'accounts/address_delete.html')
