"""Main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_swagger.views import get_swagger_view
from crm.views import AgentViewSet,CustomerViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'agents', AgentViewSet)

schema_view = get_swagger_view(title='API Docs')
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^',include('crm.urls')),
    url(r'^docs/', schema_view),

]
urlpatterns += router.urls


# if the DEBUG is on in settings, then append the urlpatterns as below
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
