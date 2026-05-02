from django.db import models
from django.contrib.auth.models import User



# =========================
# CUSTOMER
# =========================
class Customer(models.Model):
    SEX_TYPES = (
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    sex = models.CharField(max_length=10, choices=SEX_TYPES, blank=True, null=True)
    AGE_CHOICES = (
    ('0-18', '0-18'),
    ('18-30', '18-30'),
    ('30+', '30+'),
)

    age = models.CharField(max_length=10, choices=AGE_CHOICES, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    saved_by = models.ForeignKey(User, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# =========================
# INVOICE
# =========================
class Invoice(models.Model):

    INVOICE_TYPE = (
        ('R', 'RECIEPT'),
        ('P', 'PROFORMA INVOICE'),
        ('I', 'INVOICE'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    saved_by = models.ForeignKey(User, on_delete=models.PROTECT)

    invoice_date_time = models.DateTimeField(auto_now_add=True)

    # ✔️ corrigé (valeur réaliste)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    last_updated_date = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)

    invoice_type = models.CharField(max_length=1, choices=INVOICE_TYPE, default='I')

    comments = models.TextField(blank=True, null=True, max_length=1000)

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    def __str__(self):
        return f"{self.customer.name} - {self.invoice_date_time}"

    @property
    def get_total(self):
        """
        Calcule le total de la facture
        """
        return sum(article.price for article in self.articles.all())


# =========================
# ARTICLE
# =========================
class Article(models.Model):

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="articles"
    )

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