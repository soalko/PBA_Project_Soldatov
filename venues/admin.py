from django.contrib import admin

from .models import Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "capacity")
    search_fields = ("name", "address")
