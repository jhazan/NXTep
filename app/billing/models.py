from django.db import models
from django.utils import timezone
from clients.models import Client, ServiceAgreement
from monitoring.models import Device


class Quote(models.Model):
    """Model representing a quote for services."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    client = models.ForeignKey(Client, related_name='quotes', on_delete=models.CASCADE)
    quote_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expiration_date = models.DateField()
    
    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Notes and terms
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    
    def __str__(self):
        return f"Quote #{self.quote_number} for {self.client.name}"
    
    def save(self, *args, **kwargs):
        # Calculate tax and total
        self.tax_amount = round(self.subtotal * (self.tax_percent / 100), 2)
        self.total = self.subtotal + self.tax_amount
        
        # Generate quote number if not provided
        if not self.quote_number:
            prefix = "Q"
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last_quote = Quote.objects.filter(
                quote_number__startswith=f"{prefix}{year}{month}"
            ).order_by('quote_number').last()
            
            if last_quote:
                # Extract the sequential number from the last quote and increment
                last_number = int(last_quote.quote_number[7:])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.quote_number = f"{prefix}{year}{month}{new_number:04d}"
            
        super().save(*args, **kwargs)


class QuoteItem(models.Model):
    """Model representing a line item in a quote."""
    quote = models.ForeignKey(Quote, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.description} - {self.quote.quote_number}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update quote totals
        self.quote.subtotal = sum(item.total_price for item in self.quote.items.all())
        self.quote.save()


class Invoice(models.Model):
    """Model representing an invoice to a client."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('canceled', 'Canceled'),
    ]
    
    client = models.ForeignKey(Client, related_name='invoices', on_delete=models.CASCADE)
    service_agreement = models.ForeignKey(ServiceAgreement, related_name='invoices', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Recurring
    is_recurring = models.BooleanField(default=False)
    billing_period_start = models.DateField(null=True, blank=True)
    billing_period_end = models.DateField(null=True, blank=True)
    
    # Payment
    stripe_invoice_id = models.CharField(max_length=100, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    
    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Notes
    notes = models.TextField(blank=True)
    payment_terms = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-issue_date']
        
    def __str__(self):
        return f"Invoice #{self.invoice_number} for {self.client.name}"
    
    def save(self, *args, **kwargs):
        # Calculate tax and total
        self.tax_amount = round(self.subtotal * (self.tax_percent / 100), 2)
        self.total = self.subtotal + self.tax_amount
        
        if self.status != 'paid':
            self.balance_due = self.total
        
        # Generate invoice number if not provided
        if not self.invoice_number:
            prefix = "INV"
            year = timezone.now().strftime('%Y')
            month = timezone.now().strftime('%m')
            last_invoice = Invoice.objects.filter(
                invoice_number__startswith=f"{prefix}{year}{month}"
            ).order_by('invoice_number').last()
            
            if last_invoice:
                # Extract the sequential number from the last invoice and increment
                last_number = int(last_invoice.invoice_number[9:])
                new_number = last_number + 1
            else:
                new_number = 1
                
            self.invoice_number = f"{prefix}{year}{month}{new_number:04d}"
            
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """Model representing a line item in an invoice."""
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # For device-based billing
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        # Calculate total price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice totals
        self.invoice.subtotal = sum(item.total_price for item in self.invoice.items.all())
        self.invoice.save()


class Payment(models.Model):
    """Model representing a payment for an invoice."""
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('ach', 'ACH Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]
    
    invoice = models.ForeignKey(Invoice, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Stripe payment details
    stripe_payment_id = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Payment of ${self.amount} for {self.invoice.invoice_number}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Update invoice balance due and status
        invoice = self.invoice
        total_payments = sum(payment.amount for payment in invoice.payments.all())
        invoice.balance_due = invoice.total - total_payments
        
        if invoice.balance_due <= 0:
            invoice.status = 'paid'
        elif invoice.status == 'paid':
            invoice.status = 'sent'
            
        invoice.save()
