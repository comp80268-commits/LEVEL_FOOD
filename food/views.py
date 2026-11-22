from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import (
    Category, Product, DeliveryZone, Order,
    Advantage, Certificate, SiteSettings,
)
from .filters import ProductFilter
from .serializers import (
    CategorySerializer, ProductShortSerializer, ProductDetailSerializer,
    DeliveryZoneSerializer, OrderCreateSerializer,
    AdvantageSerializer, CertificateSerializer, SiteSettingsSerializer,
)


# ---------------------------------------------------------------------------
# КАТАЛОГ
# ---------------------------------------------------------------------------

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Роутер сам создаёт:
      GET /api/categories/        -> list
      GET /api/categories/<id>/   -> retrieve
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/products/        -> список (с фильтрами)
    GET /api/products/<id>/   -> карточка 'Подробнее'

    Фильтры: ?category=govyadina&is_new=true&min_price=1000&max_price=3000
    """
    queryset = Product.objects.select_related("category").prefetch_related("related_products").all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProductDetailSerializer
        return ProductShortSerializer


# ---------------------------------------------------------------------------
# ЗАКАЗЫ И ДОСТАВКА
# ---------------------------------------------------------------------------

class DeliveryZoneViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/delivery-zones/"""
    queryset = DeliveryZone.objects.all()
    serializer_class = DeliveryZoneSerializer


class OrderViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    Только создание заказа: POST /api/orders/
    (list/retrieve/update/delete намеренно не подключены — заказ создаётся
    один раз при оформлении корзины и больше через этот эндпоинт не трогается).
    """
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    # Это открытый публичный API без логина — сессии не нужны,
    # а именно сессионная аутентификация включает проверку CSRF на POST.
    authentication_classes = []
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save()


# ---------------------------------------------------------------------------
# КОНТЕНТ
# ---------------------------------------------------------------------------

class AdvantageViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/advantages/"""
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/certificates/"""
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class SiteSettingsView(RetrieveAPIView):

    serializer_class = SiteSettingsSerializer

    def get_object(self):
        return SiteSettings.load()