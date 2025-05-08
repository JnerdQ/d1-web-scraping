from django.db import models

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre")
    price = models.FloatField(verbose_name="Precio")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de imagen")
    category = models.CharField(max_length=100, blank=True, verbose_name="Categoría")
    description = models.TextField(blank=True, verbose_name="Descripción")
    quantity = models.CharField(max_length=50, blank=True, verbose_name="Cantidad")
    source = models.CharField(max_length=50, default="D1", verbose_name="Fuente")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - ${self.price}"
