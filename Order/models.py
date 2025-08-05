from django.db import models
import uuid
from django.core.validators import MinValueValidator




class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.IntegerField(default=None)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('paid', 'Paid'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('canceled', 'Canceled')),
        default='pending'
    )
    basket_id = models.UUIDField(null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField(blank=True, null=True)
    store_id = models.IntegerField(null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    is_locked = models.BooleanField(default=False)  # Флаг неизменности
    msg_for_couriers = models.TextField(blank=True, null=True)
    msg_for_order = models.TextField(blank=True, null=True)

    cancel_reason = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Order {self.id} for {self.customer} - {self.status}"

    def save(self, *args, **kwargs):
        # Блокируем изменение после установки статуса 'paid' или выше
        if self.status in ['paid', 'shipped', 'delivered', 'canceled'] and not self.is_locked:
            self.is_locked = True
        super().save(*args, **kwargs)



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField(null=False)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена на момент покупки
    name_at_purchase = models.CharField(max_length=255, blank=True, null=True)  # Название на момент покупки
    created_at = models.DateTimeField(auto_now_add=True)  # Фиксация времени добавления
    sku = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('order', 'product_id')

    def __str__(self):
        return f"{self.quantity} x Product {self.product_id} in Order {self.order.id}"

