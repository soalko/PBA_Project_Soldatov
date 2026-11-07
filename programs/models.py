from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from artists.models import Artist
from venues.models import Venue


class Program(models.Model):
    """Концертная программа: исполнитель выступает на площадке в дату.

    Связи «многие к одному»: у исполнителя и у площадки может быть
    много программ, а программа относится к одному исполнителю и
    одной площадке. Внешние ключи artist_id и venue_id хранятся
    в таблице программ.
    """

    title = models.CharField("Название", max_length=200)
    artist = models.ForeignKey(
        Artist,
        # PROTECT: нельзя удалить исполнителя, у которого есть
        # программы, — иначе пропала бы история концертов.
        on_delete=models.PROTECT,
        # Обратный доступ: artist.programs.all().
        related_name="programs",
        verbose_name="Исполнитель",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="programs",
        verbose_name="Площадка",
    )
    genre = models.CharField("Жанр", max_length=50)
    # DateField хранит дату, а не строку: сравнения дат в запросах
    # (event_date=..., event_date__gt=...) работают корректно.
    event_date = models.DateField("Дата концерта")
    # DecimalField хранит деньги без ошибок округления float.
    base_price = models.DecimalField(
        "Базовая цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    class Meta:
        ordering = ["event_date", "pk"]
        verbose_name = "программа"
        verbose_name_plural = "программы"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(base_price__gte=0),
                name="program_base_price_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.title} ({self.event_date:%d.%m.%Y})"

    def is_upcoming(self):
        """Дата концерта ещё не наступила (правило из ПР3)."""
        return self.event_date > timezone.localdate()
