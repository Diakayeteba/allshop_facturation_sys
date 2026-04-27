from django.shortcuts import render
from django.views.generic import TemplateView
from .models import  *
from django.views import View

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
    