from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "main"
urlpatterns = [

    path("", views.login, name="login"),
   
    path("auth/", views.authenticate, name="authenticate"),

    path("administration/", views.administration, name="administration"),
    
    path("dashboard/", views.dashboard, name="dashboard"),

    path("settings/", views.settings, name="settings"),

    path("reports/", views.reports, name="reports"),

    path("transactions/", views.transactions, name="transactions"),

    path("data/", views.data, name="data"),

]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)