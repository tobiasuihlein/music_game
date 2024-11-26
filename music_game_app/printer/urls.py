from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("pdf", views.display_pdf, name="pdf")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
