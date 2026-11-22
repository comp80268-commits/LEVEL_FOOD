import pytest
from decimal import Decimal

from .factories import (
    CategoryFactory, ProductFactory, DeliveryZoneFactory,
    OrderFactory, OrderItemFactory,
)

pytestmark = pytest.mark.django_db


def test_category_str():
    category = CategoryFactory(name="Говядина")
    assert str(category) == "Говядина"


def test_product_in_stock_true():
    product = ProductFactory(stock_quantity=5)
    assert product.in_stock is True


def test_product_in_stock_false():
    product = ProductFactory(stock_quantity=0)
    assert product.in_stock is False


def test_order_item_line_total():
    item = OrderItemFactory(quantity=3, price_at_order=Decimal("2000.00"))
    assert item.line_total == Decimal("6000.00")


def test_order_items_total_sums_all_items():
    order = OrderFactory()
    OrderItemFactory(order=order, quantity=2, price_at_order=Decimal("2000.00"))
    OrderItemFactory(order=order, quantity=1, price_at_order=Decimal("1500.00"))
    assert order.items_total == Decimal("5500.00")


def test_order_delivery_price_from_zone():
    zone = DeliveryZoneFactory(price=Decimal("600.00"))
    order = OrderFactory(delivery_zone=zone)
    assert order.delivery_price == Decimal("600.00")


def test_order_delivery_price_zero_without_zone():
    order = OrderFactory(delivery_zone=None)
    assert order.delivery_price == 0


def test_order_grand_total_is_items_plus_delivery():
    zone = DeliveryZoneFactory(price=Decimal("400.00"))
    order = OrderFactory(delivery_zone=zone)
    OrderItemFactory(order=order, quantity=2, price_at_order=Decimal("2000.00"))
    assert order.grand_total == Decimal("4400.00")