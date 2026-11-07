from django.core.validators import MinValueValidator
from django.db import models


class Venue(models.Model):
    """Концертная площадка (таблица venues из ПР7)."""

    name = models.CharField("Название", max_length=200)
    address = models.CharField("Адрес", max_length=300, blank=True)
    # PositiveIntegerField не пропускает отрицательные числа,
    # валидатор и ограничение ниже запрещают ещё и ноль.
    capacity = models.PositiveIntegerField(
        "Вместимость",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "площадка"
        verbose_name_plural = "площадки"
        constraints = [
            # Аналог CHECK (capacity > 0) из sql/schema.sql:
            # проверку выполняет сама база данных.
            models.CheckConstraint(
                condition=models.Q(capacity__gt=0),
                name="venue_capacity_positive",
            ),
        ]

    def __str__(self):
        return self.name

    def is_suitable_for(self, people_count):
        """Вмещает ли площадка указанное число зрителей."""
        return self.capacity >= people_count

    def is_free_on(self, day):
        """Свободна ли площадка в дату: нет ни одной программы.

        self.programs — обратная связь, её имя задано параметром
        related_name="programs" в модели Program.
        """
        return not self.programs.filter(event_date=day).exists()
