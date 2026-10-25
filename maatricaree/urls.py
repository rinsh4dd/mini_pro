from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from maatricaree import settings
from myapp import views as myapp_views

urlpatterns = [
    path('', myapp_views.home, name='root_home'),
    path('login/', myapp_views.logins, name='root_login'),
    path('admin/', admin.site.urls),
    path('myapp/', include('myapp.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
