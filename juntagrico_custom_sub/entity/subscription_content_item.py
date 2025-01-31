from django.db import models
from juntagrico_custom_sub.entity.subscription_content import SubscriptionContent
from juntagrico_custom_sub.entity.product import Product

class SubscriptionContentItem(models.Model):
    subscription_content = models.ForeignKey(SubscriptionContent,on_delete=models.CASCADE,related_name="products")
    product = models.ForeignKey(Product,on_delete=models.PROTECT)
    amount = models.IntegerField()
    @property
    def display_amount(self):
        return self.amount * self.product.display_units
    @property
    def amount_base_units(self):
        return self.amount * self.product.units
    class Meta:
        unique_together = (("subscription_content", "product"),)