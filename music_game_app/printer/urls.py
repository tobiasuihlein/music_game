from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("pdf", views.display_pdf, name="pdf")
]
