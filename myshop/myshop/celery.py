import os
from celery import Celery
from django.conf import settings

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

# Создание экземпляра объекта Celery
app = Celery('myshop')

# Загрузка настроек из файла settings.py
app.config_from_object('django.conf:settings')

# Автоматическое обнаружение задач во всех приложениях Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)