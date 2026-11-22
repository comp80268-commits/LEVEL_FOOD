import pytest
from decimal import Decimal
from django.urls import reverse

from .factories import (
    CategoryFactory, ProductFactory, DeliveryZoneFactory,
    AdvantageFactory, CertificateFactory,
)

pytestmark = pytest.mark.django_db


def test_category_list(api_client, category):
    url = reverse("category-list")
    response = api_client.get(url)
    assert response.status_code == 200
    assert any(c["slug"] == category.slug for c in response.data["results"] if "results" in response.data) \
        or any(c["slug"] == category.slug for c in response.data)


def test_product_list(api_client, product):
    url = reverse("product-list")
    response = api_client.get(url)
    assert response.status_code == 200


def test_product_list_filtered_by_category(api_client):
    beef = CategoryFactory(slug="govyadina")
    pork = CategoryFactory(slug="svinina")
    ProductFactory(category=beef)
    ProductFactory(category=pork)

    url = reverse("product-list")
    response = api_client.get(url, {"category": "govyadina"})
    assert response.status_code == 200
    data = response.data["results"] if "results" in response.data else response.data
    assert len(data) == 1


def test_product_detail(api_client, product):
    url = reverse("product-detail", args=[product.id])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data["name"] == product.name
    assert "category" in response.data


def test_delivery_zone_list(api_client, delivery_zone):
    url = reverse("delivery-zone-list")
    response = api_client.get(url)
    assert response.status_code == 200


def test_order_create_success(api_client, product, delivery_zone):
    url = reverse("order-list")
    payload = {
        "name": "Иван Иванов",
        "phone": "+79990001122",
        "email": "ivan@example.com",
        "comment": "Комментарий",
        "delivery_zone": delivery_zone.id,
        "items": [{"product_id": product.id, "quantity": 2}],
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 201

    product.refresh_from_db()
    delivery_zone.refresh_from_db()
    expected_total = product.price * 2 + delivery_zone.price
    assert Decimal(str(response.data["grand_total"])) == expected_total


def test_order_create_fails_without_items(api_client):
    url = reverse("order-list")
    payload = {"name": "Иван Иванов", "phone": "+79990001122", "items": []}
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400


def test_order_create_fails_when_stock_insufficient(api_client, product):
    url = reverse("order-list")
    payload = {
        "name": "Иван Иванов",
        "phone": "+79990001122",
        "items": [{"product_id": product.id, "quantity": product.stock_quantity + 100}],
    }
    response = api_client.post(url, payload, format="json")
    assert response.status_code == 400


def test_advantage_list(api_client):
    AdvantageFactory()
    url = reverse("advantage-list")
    response = api_client.get(url)
    assert response.status_code == 200


def test_certificate_list(api_client):
    CertificateFactory()
    url = reverse("certificate-list")
    response = api_client.get(url)
    assert response.status_code == 200


def test_site_settings_retrieve(api_client):
    url = reverse("site-settings")
    response = api_client.get(url)
    assert response.status_code == 200