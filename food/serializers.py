from rest_framework import serializers
from .models import (
    Category, Product, DeliveryZone, Order, OrderItem,
    Advantage, Certificate, SiteSettings,
)


# ---------------------------------------------------------------------------
# КАТАЛОГ
# ---------------------------------------------------------------------------

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "order"]


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "price",
            "image", "is_new", "stock_quantity", "in_stock",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    related_products = ProductShortSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "name", "slug", "description", "price",
            "image", "is_new", "stock_quantity", "in_stock",
            "related_products", "created_at",
        ]


# ---------------------------------------------------------------------------
# ЗАКАЗЫ И ДОСТАВКА
# ---------------------------------------------------------------------------

class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = ["id", "name", "price"]


class OrderItemInputSerializer(serializers.Serializer):
    """То, что реально присылает фронт для одной позиции корзины."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemOutputSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "product_name", "quantity", "price_at_order", "line_total"]


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    POST /api/orders/
    Принимает корзину целиком и считает цены/итог сам, с фронта цифрам не доверяет.
    """
    items = OrderItemInputSerializer(many=True, write_only=True)
    items_result = OrderItemOutputSerializer(source="items", many=True, read_only=True)
    items_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    delivery_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "name", "phone", "email", "comment", "attachment",
            "delivery_zone", "items", "items_result",
            "items_total", "delivery_price", "grand_total",
            "status", "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Корзина пуста.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        for item in items_data:
            product = Product.objects.select_for_update().get(pk=item["product_id"])
            quantity = item["quantity"]

            if quantity > product.stock_quantity:
                order.delete()
                raise serializers.ValidationError(
                    f"Недостаточно товара '{product.name}' в наличии "
                    f"(запрошено {quantity}, в наличии {product.stock_quantity})."
                )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price_at_order=product.price,
            )
            product.stock_quantity -= quantity
            product.save(update_fields=["stock_quantity"])

        return order


# ---------------------------------------------------------------------------
# КОНТЕНТ
# ---------------------------------------------------------------------------

class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = ["id", "title", "description", "order"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "image", "title", "order"]


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "about_intro_text", "about_quality_text", "about_video",
            "master_class_video", "meat_cuts_scheme", "products_intro_text",
            "phone_1", "phone_2", "email", "telegram", "work_hours",
            "address", "latitude", "longitude",
        ]