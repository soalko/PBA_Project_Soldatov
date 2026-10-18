from django.urls import path

from . import views

app_name = "programs"

urlpatterns = [
    path("", views.programs, name="list"),
    path("<int:program_id>/", views.program_detail, name="detail"),
]
