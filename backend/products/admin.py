from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "quantity", "source", "created_at")
    list_filter = ("source",)
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
