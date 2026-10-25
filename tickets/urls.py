from django.urls import path

from . import views

app_name = "tickets"

urlpatterns = [
    path("", views.tickets, name="list"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:ticket_id>/", views.ticket_detail, name="detail"),
]
