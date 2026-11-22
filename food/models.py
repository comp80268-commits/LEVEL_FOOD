from django.db import models


# ---------------------------------------------------------------------------
# КАТАЛОГ
# ---------------------------------------------------------------------------

class Category(models.Model):
    """Категория товаров: Говядина, Свинина, Курица, Морепродукты."""
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("Слаг (для URL/фильтра)", unique=True)
    order = models.PositiveIntegerField("Порядок отображения", default=0)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Товар каталога."""
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        related_name="products",
        on_delete=models.PROTECT,
    )
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("Слаг", unique=True)
    description = models.TextField("Описание", blank=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    image = models.ImageField("Картинка", upload_to="products/", blank=True, null=True)
    is_new = models.BooleanField("Новинка", default=False)
    stock_quantity = models.PositiveIntegerField("Количество в наличии", default=0)
    related_products = models.ManyToManyField(
        "self",
        verbose_name="Сопутствующие товары",
        blank=True,
        symmetrical=False,
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.price} Р)"

    @property
    def in_stock(self):
        return self.stock_quantity > 0


# ---------------------------------------------------------------------------
# ЗАКАЗЫ И ДОСТАВКА
# ---------------------------------------------------------------------------

class DeliveryZone(models.Model):
    """Населённый пункт доставки с фиксированной ценой."""
    name = models.CharField("Название населённого пункта", max_length=150)
    price = models.DecimalField("Цена доставки", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Зона доставки"
        verbose_name_plural = "Зоны доставки"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — {self.price} Р"


class Order(models.Model):
    """Заявка/заказ клиента."""

    STATUS_NEW = "new"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_DONE = "done"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новая"),
        (STATUS_IN_PROGRESS, "В обработке"),
        (STATUS_DONE, "Выполнена"),
        (STATUS_CANCELED, "Отменена"),
    ]

    name = models.CharField("Имя", max_length=150)
    phone = models.CharField("Телефон", max_length=30)
    email = models.EmailField("Email", blank=True)
    comment = models.TextField("Комментарий", blank=True)
    attachment = models.FileField("Файл", upload_to="order_attachments/", blank=True, null=True)

    delivery_zone = models.ForeignKey(
        DeliveryZone,
        verbose_name="Зона доставки",
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )

    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.pk} от {self.name}"

    @property
    def items_total(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def delivery_price(self):
        return self.delivery_zone.price if self.delivery_zone else 0

    @property
    def grand_total(self):
        return self.items_total + self.delivery_price


class OrderItem(models.Model):
    """Позиция в заказе: товар + количество + цена на момент заказа."""
    order = models.ForeignKey(Order, verbose_name="Заказ", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Товар", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField("Количество", default=1)
    price_at_order = models.DecimalField("Цена на момент заказа", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def line_total(self):
        return self.price_at_order * self.quantity


# ---------------------------------------------------------------------------
# КОНТЕНТ (О компании, преимущества, сертификаты, настройки сайта)
# ---------------------------------------------------------------------------

class Advantage(models.Model):
    """Блок 'Наши преимущества'."""
    title = models.CharField("Заголовок", max_length=150)
    description = models.TextField("Описание")
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Преимущество"
        verbose_name_plural = "Преимущества"
        ordering = ["order"]

    def __str__(self):
        return self.title


class Certificate(models.Model):
    """Картинка сертификата."""
    image = models.ImageField("Картинка", upload_to="certificates/")
    title = models.CharField("Название", max_length=150, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ["order"]

    def __str__(self):
        return self.title or f"Сертификат #{self.pk}"


class SiteSettings(models.Model):
    """Синглтон: один общий набор настроек/текстов сайта."""
    about_intro_text = models.TextField("Текст 'О компании' (вступление)", blank=True)
    about_quality_text = models.TextField("Текст 'Мы работаем на качество'", blank=True)
    about_video = models.FileField("Видео 'О компании'", upload_to="about_videos/", blank=True, null=True)
    master_class_video = models.FileField("Видео мастер-класса", upload_to="about_videos/", blank=True, null=True)
    meat_cuts_scheme = models.ImageField("Схема отрубов", upload_to="scheme/", blank=True, null=True)

    products_intro_text = models.TextField("Текст на странице 'Товары'", blank=True)

    phone_1 = models.CharField("Телефон 1", max_length=30, blank=True)
    phone_2 = models.CharField("Телефон 2", max_length=30, blank=True)
    email = models.EmailField("Email", blank=True)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    work_hours = models.CharField("Рабочее время", max_length=100, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    latitude = models.FloatField("Широта (для карты)", null=True, blank=True)
    longitude = models.FloatField("Долгота (для карты)", null=True, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj