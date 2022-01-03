from django.contrib import admin
from .models import Item, OrderItem, Order, ShippingAddress, Payment, RecommendedItem
# Register your models here.

class ItemModelAdmin(admin.ModelAdmin):
    model = Item
    list_display = ["nome", "prezzo", "categoria", "condizione", "luogo", "CAP", "venditore", "data"]
    search_fields = ["nome", "categoria", "luogo", "CAP", "venditore", "data"]
    list_filter = ["categoria", "luogo", "venditore", "data"]

admin.site.register(Item, ItemModelAdmin)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(ShippingAddress)
admin.site.register(Payment)
admin.site.register(RecommendedItem)