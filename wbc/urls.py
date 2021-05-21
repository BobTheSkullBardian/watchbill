"""wbc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.conf import settings
# from django.conf.urls.static import static
from django.urls import path
from sailors.views import process
from events.views import (
    CalendarView,
    QuickView,
    # index,
    login_user,
    logout_user,
)


urlpatterns = [
    # path('', view=index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('upload/', process, name='process'),
    path('', view=QuickView.as_view(), name='quickview'),
    path('calendar/', view=CalendarView.as_view(), name='calendar'),
    path('quickview/', view=QuickView.as_view(), name='quickview'),
] # + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
