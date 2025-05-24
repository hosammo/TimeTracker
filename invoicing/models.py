from django.db import models
from core.models import Client

class Invoice(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    def __str__(self):
        return f"Invoice {self.id} for {self.client.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.TextField()
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    rate = models.DecimalField(max_digits=8, decimal_places=2)

    @property
    def amount(self):
        return self.hours * self.rate