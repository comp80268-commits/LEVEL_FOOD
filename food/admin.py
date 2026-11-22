from django.contrib import admin
from .models import (
    Category, Product, DeliveryZone, Order, OrderItem,
    Advantage, Certificate, SiteSettings,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock_quantity", "is_new", "created_at"]
    list_filter = ["category", "is_new"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ["related_products"]


@admin.register(DeliveryZone)
class DeliveryZoneAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]
    search_fields = ["name"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["price_at_order"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "phone", "status", "delivery_zone", "created_at"]
    list_filter = ["status", "delivery_zone"]
    search_fields = ["name", "phone", "email"]
    inlines = [OrderItemInline]
    readonly_fields = ["created_at"]


@admin.register(Advantage)
class AdvantageAdmin(admin.ModelAdmin):
    list_display = ["title", "order"]
    ordering = ["order"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["title", "order"]
    ordering = ["order"]


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Синглтон — запрещаем создавать вторую запись и удалять единственную."""

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False