from django.db import models


class Artist(models.Model):
    """Исполнитель: коллектив или солист.

    Модель заменяет таблицу artists из sql/schema.sql (ПР7).
    Поле id не объявлено: Django создаёт первичный ключ сам
    (тип задан DEFAULT_AUTO_FIELD в settings.py).
    """

    name = models.CharField("Название", max_length=200)
    # blank=True: страна необязательна. Пустое значение хранится
    # как "", а не NULL — так принято для строковых полей Django.
    country = models.CharField("Страна", max_length=100, blank=True)
    genre = models.CharField("Жанр", max_length=50)

    class Meta:
        # Порядок записей по умолчанию для Artist.objects.all().
        ordering = ["name"]
        verbose_name = "исполнитель"
        verbose_name_plural = "исполнители"

    def __str__(self):
        return self.name
