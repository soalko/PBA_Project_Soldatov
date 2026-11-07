from django.core.validators import MinValueValidator
from django.db import models

from programs.models import Program


class Ticket(models.Model):
    """Билет на концертную программу (таблица tickets из ПР7).

    Отменённый билет не удаляется, а получает статус «cancelled»:
    так сохраняется история продаж.
    """

    class Status(models.TextChoices):
        # Значение в базе и подпись для людей.
        SOLD = "sold", "продан"
        CANCELLED = "cancelled", "отменён"

    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="tickets",
        verbose_name="Программа",
    )
    seat = models.CharField("Место", max_length=10)
    category = models.CharField("Категория", max_length=50, blank=True)
    price = models.DecimalField(
        "Цена",
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        "Статус",
        max_length=10,
        choices=Status.choices,
        default=Status.SOLD,
    )

    class Meta:
        ordering = ["pk"]
        verbose_name = "билет"
        verbose_name_plural = "билеты"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="ticket_price_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["sold", "cancelled"]),
                name="ticket_status_valid",
            ),
            # Одно место на программу нельзя продать дважды.
            # Отменённые билеты в проверке не участвуют (condition),
            # поэтому место после отмены можно продать снова.
            models.UniqueConstraint(
                fields=["program", "seat"],
                condition=models.Q(status="sold"),
                name="unique_sold_seat_per_program",
            ),
        ]

    def __str__(self):
        return f"Билет №{self.pk}: {self.program.title}, место {self.seat}"

    def is_active(self):
        """Билет действует, пока его не отменили (правило из ПР3)."""
        return self.status == self.Status.SOLD

    def cancel(self):
        """Отменить билет и сохранить только изменённое поле."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])
