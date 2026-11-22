import pytest
from decimal import Decimal

from food.models import Order
from food.serializers import OrderCreateSerializer
from .factories import ProductFactory, DeliveryZoneFactory

pytestmark = pytest.mark.django_db


def _valid_payload(product, quantity=1, delivery_zone=None):
    return {
        "name": "Иван Иванов",
        "phone": "+79990001122",
        "email": "ivan@example.com",
        "comment": "",
        "delivery_zone": delivery_zone.id if delivery_zone else None,
        "items": [{"product_id": product.id, "quantity": quantity}],
    }


def test_order_create_uses_price_from_database_not_from_client():
    """
    Главный тест безопасности: даже если бы фронт прислал цену,
    сериализатор её не принимает вообще — берёт только product_id.
    Цена всегда из базы.
    """
    product = ProductFactory(price=Decimal("2000.00"), stock_quantity=10)
    serializer = OrderCreateSerializer(data=_valid_payload(product, quantity=2))

    assert serializer.is_valid(), serializer.errors
    order = serializer.save()

    item = order.items.first()
    assert item.price_at_order == Decimal("2000.00")
    assert order.items_total == Decimal("4000.00")


def test_order_create_decreases_stock():
    product = ProductFactory(stock_quantity=10)
    serializer = OrderCreateSerializer(data=_valid_payload(product, quantity=3))

    assert serializer.is_valid(), serializer.errors
    serializer.save()

    product.refresh_from_db()
    assert product.stock_quantity == 7


def test_order_create_fails_when_quantity_exceeds_stock():
    product = ProductFactory(stock_quantity=2)
    serializer = OrderCreateSerializer(data=_valid_payload(product, quantity=5))

    assert serializer.is_valid(), serializer.errors
    with pytest.raises(Exception):
        serializer.save()

    assert Order.objects.count() == 0
    product.refresh_from_db()
    assert product.stock_quantity == 2


def test_order_create_with_empty_items_is_invalid():
    serializer = OrderCreateSerializer(data={
        "name": "Иван Иванов",
        "phone": "+79990001122",
        "items": [],
    })
    assert not serializer.is_valid()
    assert "items" in serializer.errors


def test_order_grand_total_includes_delivery():
    product = ProductFactory(price=Decimal("2000.00"), stock_quantity=10)
    zone = DeliveryZoneFactory(price=Decimal("600.00"))
    serializer = OrderCreateSerializer(
        data=_valid_payload(product, quantity=2, delivery_zone=zone)
    )

    assert serializer.is_valid(), serializer.errors
    order = serializer.save()

    assert order.grand_total == Decimal("4600.00")