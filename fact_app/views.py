from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from .models import Customer, Invoice, Article
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin  
from django.db import transaction
from .utils import pagination, get_invoice
import pdfkit
from django.template.loader import get_template
import datetime
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth. mixins import LoginRequiredMixin
from .decorators import *
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import user_passes_test

# Create your views here.

class HomeView(LoginRequiredSuperuserMixin, TemplateView):
    """ Vue de la page principale (Liste des factures + Actions CRUD) """
    template_name = 'index.html'

    def get_queryset(self):
        """ Récupère toutes les factures avec les données clients liées """
        return Invoice.objects.select_related('customer').all().order_by('-invoice_date_time')

    def get(self, request, *args, **kwargs):
        # Utilisation de la fonction utilitaire de pagination
        items = pagination(request, self.get_queryset())
        context = {
            'invoices': items,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # --- LOGIQUE DE MODIFICATION DU STATUT DE PAIEMENT ---
        if request.POST.get('id_modified'):
            paid_status = request.POST.get('modified')
            invoice_id = request.POST.get('id_modified')
            try:
                obj = Invoice.objects.get(id=invoice_id)
                obj.paid = (paid_status == 'True') 
                obj.save()
                messages.success(request, _('Change made successfully!'))
            except Exception as e:
                messages.error(request, f"Error: {e}")

        # --- LOGIQUE DE SUPPRESSION ---
        if request.POST.get('id_supprimer'):
            invoice_id = request.POST.get('id_supprimer')
            try:
                obj = Invoice.objects.get(pk=invoice_id)
                obj.delete()
                messages.success(request, _('The invoice was deleted successfully!'))
            except Exception as e:
                messages.error(request, f"Error: {e}")

        # Re-calcul de la pagination après action POST pour l'affichage
        items = pagination(request, self.get_queryset())
        context = {'invoices': items}
        return render(request, self.template_name, context)    
    

class AddCustomerView(LoginRequiredSuperuserMixin, View):
    """ Vue pour ajouter un nouveau client """
    template_name = 'add_customer.html'
    login_url = '/admin/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):
        data = {
            'name': request.POST.get('name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'address': request.POST.get('address'),
            'sex': request.POST.get('sex'),
            'age': request.POST.get('age'),
            'city': request.POST.get('city'),
            'zip_code': request.POST.get('zip'),    
            'saved_by': request.user,
        }
        
        try:
            Customer.objects.create(**data)
            messages.success(request, _('Customer registered successfully!'))
            return redirect('home')
        except Exception as e:
            messages.error(request, f"System error: {e}")
        return render(request, self.template_name)


class AddInvoiceView(LoginRequiredSuperuserMixin, View):
    """ Vue pour créer une facture et ses articles associés """
    template_name = 'add_invoice.html'
    login_url = '/admin/'

    def get(self, request, *args, **kwargs):
        customers = Customer.objects.all()
        return render(request, self.template_name, {'customers': customers})
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            customer_id = request.POST.get('customer')
            invoice_type = request.POST.get('invoice_type')
            total_invoice = request.POST.get('total') 
            comments = request.POST.get('comments')

            # Listes envoyées par le formulaire dynamique (plusieurs articles)
            articles_names = request.POST.getlist('article')
            qties = request.POST.getlist('qty')
            units = request.POST.getlist('unit')
            totals_art = request.POST.getlist('total-a')

            # 1. Création de la Facture parente
            invoice = Invoice.objects.create(
                customer_id=customer_id,
                saved_by=request.user,
                total=total_invoice,
                invoice_type=invoice_type,
                comments=comments
            )

            # 2. Création des Articles liés
            if articles_names:
                for index, name in enumerate(articles_names):
                    # --- CONVERSION CRUCIALE ICI ---
                    # On transforme le texte en nombres pour permettre le calcul
                    unit_p = float(units[index]) if units[index] else 0.0
                    qty = int(qties[index]) if qties[index] else 0
                    t_line = float(totals_art[index]) if totals_art[index] else 0.0
                    Article.objects.create(
                        invoice=invoice,
                        name=name,
                        unit_price=unit_p, 
                        quantity=qty,
                        total_line=totals_art[index]
                    )
                messages.success(request, _('Invoice and articles saved successfully!'))
                return redirect('home')
            else:
                messages.error(request, _('Please add at least one article.'))

        except Exception as e:
            messages.error(request, f"Database Error: {e}")
            
        customers = Customer.objects.all()
        return render(request, self.template_name, {'customers': customers})
    

class InvoiceDetailView(LoginRequiredSuperuserMixin, View):
    """ This views helps to visualize the invoice """
    template_name = 'invoice.html'

    def get(self, request, *args, **kwargs):
        
        pk=kwargs.get('pk')

        context = get_invoice(pk)
        
        return render(request, self.template_name, context)
    
@user_passes_test(lambda u: u.is_superuser)
def getinvoice_pdf(request, *args, **kwargs):
    """ Generate pdf file from html file """
    pk = kwargs.get('pk')

# 1. Récupérer les données (utilise ta fonction corrigée avec 'articles')
    context = get_invoice(pk)

    context['date'] = datetime.date.today()

    # getting html file
    # 2. Charger le template HTML dédié au PDF
    template = get_template('invoice-pdf.html')

    # rendering the html file with context variables

    html = template.render(context)

    # 3. CONFIGURATION WINDOWS (Le point crucial)
    # On définit le chemin exact vers l'exécutable wkhtmltopdf
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

    # options for pdf generation
    options = {
        'page-size': 'letter',
        'encoding': "UTF-8",
        'margin-top': '10mm',
        'margin-bottom': '10mm',
        'margin-left': '10mm',
        'margin-right': '10mm',
        'no-outline': None, # Optionnelle : aide parfois à la stabilité
    }


    # generating pdf from html
    pdf = pdfkit.from_string(html, False, options=options , configuration=config)

    # sending the generated pdf to client
    response = HttpResponse(pdf, content_type='application/pdf')

    response['Content-Disposition'] = f'attachment; filename="invoice_{pk}.pdf"'

    return response