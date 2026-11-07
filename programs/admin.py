from django.contrib import admin

from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "venue", "event_date", "base_price")
    list_filter = ("genre", "venue")
    search_fields = ("title",)
