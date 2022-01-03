from autoslug import AutoSlugField
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

CATEGORIA = (
    ('A', 'Abbigliamento e Scarpe'),
    ('B', 'Accessori'),
    ('C', 'Casalinghi'),
    ('L', 'Console e Videogiochi'),
    ('E', 'Elettronica'),
    ('F', 'Ferramenta'),
    ('D', 'Fiori e Piante'),
    ('G', 'Giocattoli'),
    ('H', 'Hobbistica'),
    ('I', 'Informatica'),
    ('N', 'Libri e Cultura'),
    ('M', 'Sport'),
)

CONDIZIONE = (
    ('N', 'Nuovo'),
    ('U', 'Usato'),
    ('R', 'Rotto'),
    ('A', 'Altro - Pezzi di ricambio')
)


class Item(models.Model):
    nome = models.CharField(max_length=100)
    descrizione = models.TextField(max_length=1000)
    immagine = models.ImageField()
    prezzo = models.FloatField(validators=[MinValueValidator(0.0)])
    categoria = models.CharField(choices=CATEGORIA, max_length=20)
    slug = AutoSlugField(populate_from='nome', unique=True)  # chiave primaria
    condizione = models.CharField(choices=CONDIZIONE, max_length=2)
    luogo = models.CharField(max_length=30)
    CAP = models.CharField(max_length=5)
    venditore = models.ForeignKey(User, on_delete=models.CASCADE, related_name="item")
    data = models.DateTimeField(auto_now_add=True)  # Data in cui vine effettuato l' ordine
    ordinato = models.BooleanField(default=False)  # Indica se l' ooggetto è stato acquistato o meno
    acquirente = models.CharField(null=True, max_length=50, blank=True)  # Indica il nome dell' acquirente
    indirizzo = models.CharField(null=True, max_length=100, blank=True)  # Indica l' indirizzo di spedizione

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("item_view", kwargs={"slug": self.slug})

    def visualizza_articolo(self):
        return reverse("user_item_view", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_from_cart', kwargs={'slug': self.slug})


class OrderItem(models.Model):
    product = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    is_ordered = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(default=1)
    ordered_date = models.DateTimeField(default=timezone.now)
    recommended = models.BooleanField(default=False)

    def __str__(self):
        return self.product.nome

    def get_total_quantity(self):
        return self.product.quantità

    def get_tot_price(self):
        return self.product.prezzo * self.quantity

    def get_final_price(self):
        return self.get_tot_price()

    class Meta:
        verbose_name_plural = 'Order Items'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    ordered_date = models.DateTimeField()
    shipping_address = models.ForeignKey('ShippingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def __str__(self):
        return self.user.username

    def get_username(self):
        return self.user.username

    def get_address(self):
        return self.shipping_address.città + " " + self.shipping_address.via


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stato = models.CharField(max_length=30)
    città = models.CharField(max_length=30)
    cap = models.CharField(max_length=5)
    via = models.CharField(max_length=50)
    interno = models.CharField(max_length=30, blank=True)
    note = models.TextField(blank=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class RecommendedItem(models.Model):
    num_item = models.PositiveIntegerField(default=0)
    condizioneN = models.PositiveIntegerField(default=0)
    condizioneU = models.PositiveIntegerField(default=0)
    condizioneO = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prezzo = models.FloatField(validators=[MinValueValidator(0.0)], default=0)
    sum_prezzo = models.FloatField(default=0)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Recommended Item'
