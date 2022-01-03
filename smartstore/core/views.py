import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import CheckoutForm
from .models import Item, RecommendedItem, Order, OrderItem, ShippingAddress, Payment
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

'''
Classe utilizzta per visualizzare tutti gli elementi all' interno del' homepage
'''
class AllItemView(ListView):
    model = Item
    paginate_by = 4
    template_name = 'core/item_page.html'
    queryset = Item.objects.filter(ordinato=False).order_by("-pk")

''' 
Funzione utilizzata per visualizzare e eseguire azioni sulla homepage
'''
def HomeView(request):
    object_list = Item.objects.filter(ordinato=False).order_by("-data")
    if (request.user.is_authenticated):
        recommended_items = RecommendedItem.objects.filter(user=request.user)
        for racc in recommended_items:
            racc.save()
        if recommended_items.exists():
            order_qs = Order.objects.filter(user=request.user, is_ordered=True)
            order_item_qs = OrderItem.objects.filter(user=request.user, is_ordered=True, recommended=False)

            for item in order_item_qs:
                for racc in recommended_items:
                    if (item.product.condizione == 'N'):
                        racc.condizioneN += 1
                    if (item.product.condizione == 'U'):
                        racc.condizioneU += 1
                    racc.num_item += 1
                    racc.sum_prezzo += item.product.prezzo
                    racc.prezzo = racc.sum_prezzo / racc.num_item
                    item.recommended = True
                    item.save()

            for racc in recommended_items:
                print(racc.prezzo)
                print(racc.num_item)
                racc.save()
                print(racc.num_item)

        else:
            recommended_items = RecommendedItem.objects.create(user=request.user)
            order_qs = Order.objects.filter(user=request.user, is_ordered=True)
            order_item_qs = OrderItem.objects.filter(user=request.user, is_ordered=True, recommended=False)

            for item in order_item_qs:
                if (item.product.condizione == 'N'):
                    recommended_items.condizioneN += 1
                if (item.product.condizione == 'U'):
                    racc.condizioneU += 1
                recommended_items.num_item += 1
                recommended_items.sum_prezzo += item.product.prezzo
                recommended_items.prezzo = recommended_items.sum_prezzo / recommended_items.num_item
                item.recommended = True
                item.save()
            recommended_items.save()
            print('Da creare')

    recommendation_list = []
    newconvenient_list = []
    usedconvenient_list = []
    if (request.user.is_authenticated):
        recommended_items = RecommendedItem.objects.filter(user=request.user)
        for it in object_list:
            for recommended in recommended_items:
                if (it.venditore != request.user):
                    if ((it.prezzo >= recommended.prezzo and it.prezzo <= recommended.prezzo + 100) or (
                            it.prezzo <= recommended.prezzo and it.prezzo >= recommended.prezzo - 100)):
                        if ((recommended.condizioneN == recommended.condizioneU) and (
                                recommended.condizioneN >= 2 or recommended.condizioneU >= 2)):
                            if (it not in recommendation_list):
                                recommendation_list.append(it)
                        if ((recommended.condizioneN > recommended.condizioneU) and (
                                recommended.condizioneN >= 2 or recommended.condizioneU >= 2)):
                            if (it.condizione == 'N'):
                                if (it not in recommendation_list):
                                    recommendation_list.append(it)
                        else:
                            if ((recommended.condizioneN < recommended.condizioneU) and (recommended.condizioneN >= 2 or recommended.condizioneU >= 2)):
                                if (it.condizione == 'U'):
                                    if (it not in recommendation_list):
                                        recommendation_list.append(it)

    for it in object_list:
        if (it.prezzo <=300 and it.condizione == 'N'):
            newconvenient_list.append(it)
        if (it.prezzo <=300 and it.condizione == 'U'):
            usedconvenient_list.append(it)

    recommendation_list = sorted(recommendation_list[:4], key=lambda item: (item.prezzo))  # ordino gli item consigliati da quello con prezzo minore
    newconvenient_list = sorted(newconvenient_list[:4], key=lambda item: (item.prezzo))
    usedconvenient_list = sorted(usedconvenient_list[:4], key=lambda item: (item.prezzo))

    context = {
        'object_list': object_list,
        "recommendation_list": recommendation_list,
        "newconvenient_list": newconvenient_list,
        "usedconvenient_list": usedconvenient_list
    }
    print(recommendation_list)
    return render(request, 'core/homepage.html', context)

'''
Visualizza la pagina del profilo utente
@param username : Nome dell' utente
return: la pagina del profilo utente
'''
def UserProfileView(request, username):
    if request.user.username != username:
        return OtherUserProfileView(request, username)
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=False).order_by("-pk")
    paginator = Paginator(user_items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_items": page_obj, "page_obj": page_obj}
    return render(request, 'core/profilo.html', context)


'''
Utilizzata per la creazione e inserimento di un articolo
Estende la view CreateView di Django
'''
class AddItem(CreateView):
    model = Item
    fields = ["nome", "descrizione", "immagine", "prezzo", "categoria", "condizione",
              "luogo", "CAP"]
    template_name = "core/inserisci_articolo.html"

    def form_valid(self, form):
        form.instance.venditore_id = self.request.user.pk
        print(form.instance.nome)
        return super(AddItem, self).form_valid(form)

    def get_success_url(self):
        success_url = reverse_lazy("homepage")
        return success_url

'''
Visualizza la pagina dei dettagli di un articolo
'''
class ItemDetailView(DetailView):
    model = Item
    template_name = "core/item.html"


class UserItemDetailView(DetailView):
    model = Item
    template_name = "core/item.html"

'''
Permette agli utenti di visualizzare il profilo di altri utenti
'''
def OtherUserProfileView(request, username):
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=False).order_by("-pk")
    paginator = Paginator(user_items, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_items": page_obj, "page_obj": page_obj}
    return render(request, 'core/user_profile.html', context)


'''
Classe utilizzata per l' eliminazione di un articolo
'''
class ItemDelete(DeleteView):
    model = Item
    template_name = 'core/item_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)

        if user.id is not item.venditore.id:
            messages.info(request, "Non puoi accedere a questa pagina!")
            return HomeView(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)
        user = get_object_or_404(User, username=item.venditore)
        return reverse_lazy('user_profile', kwargs={'username': user})


'''
Classe utilizzata per modificare i campi di un articolo
'''
class ItemModify(UpdateView):
    model = Item
    fields = ('nome', 'descrizione', 'prezzo', 'categoria', 'condizione', 'luogo', 'CAP')
    template_name = 'core/item_modify.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)

        if user.id is not item.venditore.id:
            messages.info(request, "Non puoi accedere a questa pagina!")
            return HomeView(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        itemid = self.kwargs['pk']
        item = get_object_or_404(Item, id=itemid)
        user = get_object_or_404(User, username=item.venditore)
        return reverse_lazy('user_profile', kwargs={'username': user})


def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(product=item, user=request.user, is_ordered=False)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=item.slug).exists():
            order_item.quantità = 1
            order_item.save()
            messages.info(request, "Hai già aggiunto questo articolo al carrello!")
        else:
            order.items.add(order_item)
            messages.info(request, "L' articolo è stato aggiunto con successo al carrello")
            return redirect('homepage')
    else:
        date_ordered = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=date_ordered)
        order.items.add(order_item)
        messages.info(request, "L' articolo è stato aggiunto con successo al carrello")

    return redirect('homepage')


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(product=item, user=request.user, is_ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "L' articolo è stato rimosso correttamente dal carrello")
            return redirect(reverse_lazy('order_summary'))
        else:
            messages.info(request, "L' articolo non è nel carrello")
            return redirect(reverse_lazy('item_view', kwargs={'slug': slug}))
    else:
        messages.info(request, "Non hai un ordine attivo")
        return redirect(reverse_lazy('item_view', kwargs={'slug': slug}))


'''
Funzione utilizzata per verificare che i campi dei vari form siano non vuoti
'''
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class OrderSummary(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {'object': order}
            return render(self.request, 'core/order/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Il carrello è vuoto")
            return redirect('homepage')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        context = {'form': form}

        shipping_address_qs = ShippingAddress.objects.filter(user=self.request.user, default=True)
        if shipping_address_qs.exists():
            context.update({'default_shipping_address': shipping_address_qs[0]})
        return render(self.request, 'core/order/checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            if form.is_valid():
                form.use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if form.use_default_shipping:
                    print('Uso indirizzo di default')
                    address_qs = ShippingAddress.objects.filter(user=self.request.user, default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order_items = order.items.all()
                        order_items.update(is_ordered=True)
                        order.shipping_address = shipping_address
                        for item in order_items:
                            item.product.ordinato = True
                            item.product.acquirente = order.get_username()
                            item.product.indirizzo = order.get_address()
                            item.product.data = timezone.now()
                            item.product.save()
                            item.save()

                        order.shipping_address = shipping_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()
                    else:
                        messages.info(self.request, "Nessun indirizzo di default")
                        return redirect('checkout')
                else:
                    form.stato = form.cleaned_data.get('stato')
                    form.città = form.cleaned_data.get('città')
                    form.via = form.cleaned_data.get('via')
                    form.cap = form.cleaned_data.get('cap')
                    form.interno = form.cleaned_data.get('interno')
                    form.note = form.cleaned_data.get('note')

                    form.opzioni_pagamento = form.cleaned_data.get('opzioni_pagamento')
                    if is_valid_form([form.stato, form.città, form.via, form.cap]):
                        shipping_address = ShippingAddress(
                            user=self.request.user,
                            stato=form.stato,
                            città=form.città,
                            via=form.via,
                            cap=form.cap,
                            interno=form.interno,
                            note=form.note
                        )
                        shipping_address.save()
                        order_items = order.items.all()
                        order_items.update(is_ordered=True)
                        order.shipping_address = shipping_address
                        for item in order_items:
                            item.product.ordinato = True
                            item.product.acquirente = order.get_username()
                            item.product.data = timezone.now()
                            item.product.indirizzo = order.get_address()
                            item.product.save()
                            item.save()

                        order.shipping_address = shipping_address
                        order.is_ordered = True
                        order.ordered_date = timezone.now()
                        order.save()
                        payment = Payment()
                        payment.user = self.request.user
                        payment.amount = order.get_total()
                        payment.order = order
                        payment.save()

                        form.save_info = form.cleaned_data.get('save_info')
                        if form.save_info:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Compila tutti i campi per continuare")
                        return redirect('checkout')

            messages.info(self.request, "L' ordine è stato ricevuto con successo")
            return redirect('homepage')

            messages.warning(self.request, "Il pagamento non è andato a buon fine")
            return redirect('homepage')
            return render(self.request, 'core/order/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "Non hai nessun ordine in corso")
            return redirect('order_summary')


class AcquistiView(View):
    model = User
    template_name = '/core/acquisti.html'

    def get(self, *args, **kwargs):
        user_id = self.request.user.id
        user = User.objects.get(id=user_id)
        acquisti = Payment.objects.filter(user=user).order_by("-pk")
        paginator = Paginator(acquisti, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'User': user,
            'lista_acquisti': page_obj,
            'page_obj': page_obj
        }
        return render(self.request, 'core/acquisti.html', context)

'''
Utilizzato per visualizzare il riepilogo degli ordini
'''
class OrderDisplay(View):
    model = Order
    template_name = 'core/order/order_display.html'

    def get(self, *argss, **kwargs):
        order_id = self.kwargs['pk']
        order = Order.objects.get(id=order_id, is_ordered=True)
        context = {
            'User': self.request.user,
            'lista_acquisti': order.items.all()
        }
        return render(self.request, 'core/order/order_display.html', context)

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        order_id = self.kwargs["pk"]
        order = get_object_or_404(Order, id=order_id)

        if user.id is not order.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return HomeView(request)

        return super().dispatch(request, *args, **kwargs)

'''
Utilizzato per filtrare gli articoli per categorie
'''
def CategoryFilter(request, cat):
    object_list = Item.objects.filter(categoria=cat, ordinato=False).order_by("-pk")
    paginator = Paginator(object_list, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'object_list': object_list,
        'object_list': page_obj,
        'page_obj': page_obj
    }
    return render(request, 'core/homepageCat.html', context)


'''
Visualizza gli articoli venduti da un utente
'''
def VenditeView(request, username):
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return HomeView(request)
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=True).order_by('-data')
    paginator = Paginator(user_items, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {"user": user, "user_items": page_obj, "page_objj": page_obj}
    return render(request, 'core/vendite_user.html', context)


'''
Barra di ricerca
@param: ritorna la pagina contenente i risultati della ricerca
'''
def cerca(request):
    if "kw" in request.GET:
        querystring = request.GET.get("kw")
        if len(querystring) == 0:
            return redirect("/cerca/")
        items = Item.objects.filter(nome__icontains=querystring, ordinato=False).order_by("-pk")
        users = User.objects.filter(username__icontains=querystring)
        context = {"items": items, "users": users}
        return render(request, 'core/cerca.html', context)
    else:
        return render(request, 'core/cerca.html')


def address_view(request, username):
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return HomeView(request)
    user = get_object_or_404(User, username=username)
    user_address = ShippingAddress.objects.filter(user=user.pk)
    context = {"user": user, "user_address": user_address}
    return render(request, 'accounts/address_page.html', context)


def address_detail(request, pk):
    address = ShippingAddress.objects.get(pk=pk)
    if request.user.id != address.user.id:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return HomeView(request)
    return render(request, 'accounts/address.html', context={"object": address})


'''
Utilizzato per l' eliminazione di un indirizzo
'''
class AddressDelete(DeleteView):
    model = ShippingAddress
    template_name = 'accounts/address_delete.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return HomeView(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


'''
Modifica l' indirizzo e permette di scegliere l' indirizzo di default
'''
class AddressChange(UpdateView):
    model = ShippingAddress
    fields = ('città', 'via', 'stato', 'cap', 'default')
    template_name = 'accounts/address_change.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)

        if user.id is not address.user.id:
            messages.info(request, "Non puoi accedere a questa pagina !")
            return HomeView(request)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        address_id = self.kwargs['pk']
        address = get_object_or_404(ShippingAddress, id=address_id)
        user = get_object_or_404(User, username=address.user)
        return reverse_lazy('address_page', kwargs={"username": user})


class PrezzoCrescente(ListView):
    model = Item
    paginate_by = 4
    template_name = "core/item_page.html"
    queryset = Item.objects.filter(ordinato=False).order_by("prezzo")


class PrezzoDecrescente(ListView):
    model = Item
    paginate_by = 4
    template_name = "core/item_page.html"
    queryset = Item.objects.filter(ordinato=False).order_by("-prezzo")


class CondizioneUsata(ListView):
    model = Item
    paginate_by = 4
    template_name = "core/item_page.html"
    queryset = Item.objects.filter(condizione='U', ordinato=False).order_by("-pk")


class CondizioneNuova(ListView):
    model = Item
    paginate_by = 4
    template_name = "core/item_page.html"
    queryset = Item.objects.filter(condizione='N', ordinato=False).order_by("-pk")


def grafico_vendite(request, username):
    now = datetime.datetime.now()
    start_date = int(now.strftime("%m"))
    print(start_date)
    if request.user.username != username:
        messages.info(request, "Non puoi accedere a questa pagina !")
        return HomeView(request)
    user = get_object_or_404(User, username=username)
    user_items = Item.objects.filter(venditore=user.pk, ordinato=True, data__month=start_date)
    items = {}
    for x in items:
        items[x] = 0
    for x in user_items:
        items[int(x.data.strftime("%d"))] = 0
    for x in user_items:
        if (x.data):
            items[int(x.data.strftime("%d"))] += 1

    list = [(k, v) for k, v in items.items()]
    print(list)

    context = {'items': list, }
    return render(request, 'core/grafico_vendite.html', context)
