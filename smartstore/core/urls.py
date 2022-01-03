from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [

    # url delle schermate generali
    path('item_page/', views.AllItemView.as_view(), name='item_page'),
    path('', views.HomeView, name='homepage'),
    path('categorie/<str:cat>', views.CategoryFilter, name='categorie'),
    path('cerca/', views.cerca, name='cerca'),
    path('crescente_prezzo/', views.PrezzoCrescente.as_view(), name='prezzo_crescente'),
    path('decrescente_prezzo/', views.PrezzoDecrescente.as_view(), name='prezzo_decrescente'),
    path('articoli_nuovi/', views.CondizioneNuova.as_view(), name='articoli_nuovi'),
    path('articoli_usati/', views.CondizioneUsata.as_view(), name='articoli_usati'),

    # url riguardanti un utente
    path('user_item_page/<slug>', views.UserItemDetailView.as_view(), name='user_item_view'),
    path('user/<username>/', views.UserProfileView, name='user_profile'),
    path('otheruser/<username>/', views.OtherUserProfileView, name='otheruser_profile'),
    path('user/acquisti', login_required(views.AcquistiView.as_view()), name='acquisti'),
    path('inserisci_articolo/', login_required(views.AddItem.as_view()), name='inserisci_articolo'),
    path('user/<username>/vendite/', login_required(views.VenditeView), name='vendite_user'),
    path('user/<username>/address_page/', login_required(views.address_view), name='address_page'),
    path('user/address/<int:pk>/', login_required(views.address_detail), name='address'),
    path('user/address/<int:pk>/delete/', login_required(views.AddressDelete.as_view()), name='address_delete'),
    path('user/address/<int:pk>/modify/', login_required(views.AddressChange.as_view()), name='address_modifica'),
    path('user/<username>/grafico_vendite/', login_required(views.grafico_vendite), name='grafico_vendite_user'),

    # url riguardanti gli articoli
    path('product/<slug>', views.ItemDetailView.as_view(), name='item_view'),
    path('item/<int:pk>/delete/', login_required(views.ItemDelete.as_view()), name='item_delete'),
    path('item/<int:pk>/modify/', login_required(views.ItemModify.as_view()), name='item_modify'),

    # url riguardanti gli ordini
    path('add_to_cart/<slug>', login_required(views.add_to_cart), name='add_to_cart'),
    path('remove_from_cart/<slug>', login_required(views.remove_from_cart), name='remove_from_cart'),
    path('order_summary/', login_required(views.OrderSummary.as_view()), name='order_summary'),
    path('checkout/', login_required(views.CheckoutView.as_view()), name='checkout'),
    path('order_display/<pk>', login_required(views.OrderDisplay.as_view()), name='order_display'),

]