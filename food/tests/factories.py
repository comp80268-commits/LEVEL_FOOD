import factory
from decimal import Decimal
from food.models import (
    Category, Product, DeliveryZone, Order, OrderItem,
    Advantage, Certificate,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("slug",)

    name = factory.Sequence(lambda n: f"Категория {n}")
    slug = factory.Sequence(lambda n: f"category-{n}")
    order = 0


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product
        django_get_or_create = ("slug",)

    category = factory.SubFactory(CategoryFactory)
    name = factory.Sequence(lambda n: f"Товар {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = "Описание товара"
    price = Decimal("2000.00")
    is_new = True
    stock_quantity = 10


class DeliveryZoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryZone

    name = factory.Sequence(lambda n: f"Населённый пункт {n}")
    price = Decimal("600.00")


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    name = "Иван Иванов"
    phone = "+79990001122"
    email = "ivan@example.com"
    comment = ""
    delivery_zone = factory.SubFactory(DeliveryZoneFactory)


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price_at_order = Decimal("2000.00")


class AdvantageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Advantage

    title = factory.Sequence(lambda n: f"Преимущество {n}")
    description = "Описание преимущества"
    order = 0


class CertificateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Certificate

    image = factory.django.ImageField(filename="certificate.jpg")
    title = factory.Sequence(lambda n: f"Сертификат {n}")
    order = 0