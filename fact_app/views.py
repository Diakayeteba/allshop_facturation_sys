from django.shortcuts import render
from django.views.generic import TemplateView
from .models import  *
from django.views import View
from django.contrib import messages





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
    

    class AddCustomerView(View):
        """ View to add a new customer """
        template_name = 'add_customer.html'
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
                    messages.error(request, 'Sorry our system is detecting the following issues: {e}')

            return render(request, self.template_name,)