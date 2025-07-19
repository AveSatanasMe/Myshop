from decimal import Decimal
from django.conf import settings
from shop.models import Product
from coupons.models import Coupon  # Добавляем импорт модели Coupon


class Cart(object):
    def __init__(self, request):
        """
        Инициализация корзины с учетом купонов
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Сохраняем пустую корзину в сессии
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # Сохраняем ID примененного купона из сессии
        self.coupon_id = self.session.get('coupon_id')

    def add(self, product, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный"
        self.session.modified = True

    def remove(self, product):
        """
        Удаление товара из корзины
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет общей стоимости товаров в корзине
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Очистка корзины и удаление купона
        """
        del self.session[settings.CART_SESSION_ID]
        # Удаляем купон из сессии при очистке корзины
        if 'coupon_id' in self.session:
            del self.session['coupon_id']
        self.session.modified = True

    # Новые методы для работы с купонами

    @property
    def coupon(self):
        """
        Возвращает объект купона, если он активен и применен
        """
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        """
        Рассчитывает сумму скидки по купону
        """
        if self.coupon:
            # Скидка рассчитывается как процент от общей суммы
            return (self.coupon.discount / Decimal('100')) * self.get_total_price()
        return Decimal('0')

    def get_total_price_after_discount(self):
        """
        Возвращает итоговую сумму после применения скидки
        """
        return self.get_total_price() - self.get_discount()