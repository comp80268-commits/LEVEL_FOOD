import pytest
from rest_framework.test import APIClient

from .factories import CategoryFactory, ProductFactory, DeliveryZoneFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category(db):
    return CategoryFactory(name="Говядина", slug="govyadina")


@pytest.fixture
def product(db, category):
    return ProductFactory(category=category, name="Мраморная говядина 1 кг", price="2000.00", stock_quantity=5)


@pytest.fixture
def delivery_zone(db):
    return DeliveryZoneFactory(name="посёлок Леневка", price="400.00")