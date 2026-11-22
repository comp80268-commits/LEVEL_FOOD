import pytest
from decimal import Decimal

from food.models import Product
from food.filters import ProductFilter
from .factories import CategoryFactory, ProductFactory

pytestmark = pytest.mark.django_db


def test_filter_by_category_slug():
    beef = CategoryFactory(slug="govyadina")
    pork = CategoryFactory(slug="svinina")
    ProductFactory(category=beef, name="Говядина 1")
    ProductFactory(category=pork, name="Свинина 1")

    result = ProductFilter({"category": "govyadina"}, queryset=Product.objects.all()).qs
    assert result.count() == 1
    assert result.first().category.slug == "govyadina"


def test_filter_by_is_new():
    ProductFactory(is_new=True)
    ProductFactory(is_new=False)

    result = ProductFilter({"is_new": "true"}, queryset=Product.objects.all()).qs
    assert result.count() == 1
    assert result.first().is_new is True


def test_filter_by_price_range():
    ProductFactory(price=Decimal("1000.00"))
    ProductFactory(price=Decimal("2500.00"))
    ProductFactory(price=Decimal("5000.00"))

    result = ProductFilter(
        {"min_price": "1500", "max_price": "3000"},
        queryset=Product.objects.all(),
    ).qs
    assert result.count() == 1
    assert result.first().price == Decimal("2500.00")


def test_filter_in_stock():
    ProductFactory(stock_quantity=5)
    ProductFactory(stock_quantity=0)

    result = ProductFilter({"in_stock": "true"}, queryset=Product.objects.all()).qs
    assert result.count() == 1
    assert result.first().stock_quantity == 5