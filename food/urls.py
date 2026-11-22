from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, ProductViewSet, DeliveryZoneViewSet, OrderViewSet,
    AdvantageViewSet, CertificateViewSet, SiteSettingsView,
)

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("products", ProductViewSet, basename="product")
router.register("delivery-zones", DeliveryZoneViewSet, basename="delivery-zone")
router.register("orders", OrderViewSet, basename="order")
router.register("advantages", AdvantageViewSet, basename="advantage")
router.register("certificates", CertificateViewSet, basename="certificate")

urlpatterns = [
    # Синглтон site-settings не через роутер — см. комментарий в views.py
    path("site-settings/", SiteSettingsView.as_view(), name="site-settings"),
    path("", include(router.urls)),
]