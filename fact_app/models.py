from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin



# Create your models here.

class Customer(models.Model):
    SEX_TYPES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )
    name = models.CharField(max_length=255)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    
    address = models.TextField(blank=True, null=True)
    sex = models.CharField(max_length=10, blank=True, null=True, choices=SEX_TYPES)
    age = models.PositiveIntegerField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    saved_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
class Invoice(models.Model):


    INVOI_TYPE = (
        ('R', 'RECU'),
        ('P', 'PROFORMA FACTURE'),
        ('F', 'FACTURE'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT) 

    saved_by = models.ForeignKey('auth.User', on_delete=models.PROTECT)

    invoice_date_time = models.DateTimeField(auto_now_add=True)

    total = models.DecimalField(max_digits=10000, decimal_places=2, default=0.00)

    last_updated_date = models.DateTimeField(null=True, blank=True)

    paid = models.BooleanField(default=False)

    invoice_type = models.CharField(max_length=1, choices=INVOI_TYPE, default='F')
    
    comments = models.TextField(blank=True, null=True, max_length=1000)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        
    def __str__(self):
            return f"{self.customer.name} _{self.invoice_date_time}"
    
    @property
    def get_total(self):
        articles = self.article_set.all()
        total = sum(article.get_total for article in articles)
    

class Article(models.Model):
    """
    Name: Article model definition
    Description: This model represents an article that can be added to an invoice. It includes fields for the article's name, description, price, and timestamps for when it was created and last updated.
    Authors: madoudiakayeteba@gmail.com
      """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']

    def __str__(self):
        return self.name    