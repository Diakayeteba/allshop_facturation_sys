from urllib import request

from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from .models import  *
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin  
from django.db import transaction






# Create your views here.
class HomeView(TemplateView):
    """ Main page view """
    template_name = 'index.html'
    
    Invoice = Invoice.objects.select_related('customer').all()

    context = {
        'invoices': Invoice,    
    }

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
    
    def post(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)    
    

class AddCustomerView(LoginRequiredMixin, View):
        """ View to add a new customer """
        template_name = 'add_customer.html'
        login_url = '/admin/' # Redirige ici si l'utilisateur n'est pas connecté
        def get(self, request, *args, **kwargs):
            # Logic to add a new customer
            return render(request, self.template_name,)
        
        def post(self, request, *args, **kwargs):
            # Logic to handle form submission for adding a new customer
            data= {
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone'),
                'address': request.POST.get('address'),
                'sex': request.POST.get('sex'),
                'age': request.POST.get('age'),
                'city': request.POST.get('city'),
                'zip_code': request.POST.get('zip'),    
                'saved_by': request.user,  # Assuming the user is authenticated
                
            }
            
            try:
                  created= Customer.objects.create(**data)

                  if created:
                    messages.success(request, 'Customer registered successfully!')   

                  else:
                         messages.error(request, 'Sorry,. Please try again the sent data is not valid!')

            except Exception as e:
                    messages.error(request, f"Sorry, our system detected the following issue: {e}")
            return render(request, self.template_name,)
        

class AddInvoiceView(LoginRequiredMixin, View):
            """ View to add a new invoice """
            template_name = 'add_invoice.html'

            Customer = Customer.objects.select_related('saved_by').all()

            context = {
                'customers': Customer,    
            }

            login_url = '/admin/' # Redirige ici si l'utilisateur n'est pas connecté
            def get(self, request, *args, **kwargs):
                # Logic to add a new invoice
                return render(request, self.template_name, self.context)
            
            @transaction.atomic
            def post(self, request, *args, **kwargs):
                # Logic to handle form submission for adding a new invoice
                items = []

                try:

                   customer_id = request.POST.get('customer')
                   invoice_type = request.POST.get('invoice_type')
                    # On récupère le total général (une seule valeur, pas une liste)
                   total_invoice = request.POST.get('total') 
                   comments = request.POST.get('comments')

                    # Listes pour les articles
                   articles_names = request.POST.getlist('article')
                   qties = request.POST.getlist('qty')
                   units = request.POST.getlist('unit')
                   totals_art = request.POST.getlist('total-a')

                    # 1. Création de la Facture
                   invoice = Invoice.objects.create(
                        customer_id=customer_id,
                        saved_by=request.user,
                        total=total_invoice,
                        invoice_type=invoice_type,
                        comments=comments
                    )

                    # 2. Préparation des Articles
                   for index, name in enumerate(articles_names):
                        
                        Article.objects.create(
                            invoice=invoice, # On passe l'objet invoice directement
                            name=name,
                            unit_price=units[index], 
                            quantity=qties[index],
                            total_line=totals_art[index]
                        )
                        # On crée et on sauvegarde chaque article un par un
                        data = Article(
                            invoice=invoice, # On passe l'objet invoice directement
                            name=name,
                            # On utilise 'unit_price' car c'est le nom dans ton modèle Article
                            unit_price=units[index], 
                            # Note: Ton modèle Article n'a pas de champ 'quantity' ou 'total'
                            # Si tu veux les garder, il faudra les ajouter à ton modèle Article
                        )
                        items.append(data)

                    # 3. Enregistrement groupé
                        if items:
                            Article.objects.bulk_create(items)
                            messages.success(request, 'Invoice and articles saved successfully!')
                            return redirect('home') # Toujours rediriger après un succès POST
                        else:
                            messages.error(request, 'Please add at least one article.')

                except Exception as e:
                    # En cas d'erreur, la transaction est annulée automatiquement grâce à atomic
                    messages.error(request, f"Database Error: {e}")
                    
                return render(request, self.template_name, self.context)