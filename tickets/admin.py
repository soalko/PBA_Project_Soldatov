from django.contrib import admin

from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "program", "seat", "category", "price", "status")
    list_filter = ("status",)
