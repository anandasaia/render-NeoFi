"""
URL configuration for notetaking_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from notes.views import register_user
from notes.views import login_user
from notes.views import create_note
from notes.views import get_note, update_note, delete_note
from notes.views import share_note
from notes.views import note_history
from django.urls import path, include, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Note Taking API",
        default_version='v1',
        description=" description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="sai@sai.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup', register_user, name='signup'),
    path('login', login_user, name='login'),
    # Including the 'notes' app's URLs
    path('notes/', include('notes.urls')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc')
]
"""    path('notes/create', create_note, name='create-note'),
    path('notes/<int:id>', get_note, name='get-note'),
    path('notes/<int:id>/update', update_note, name='update-note'),
    path('notes/<int:id>/delete', delete_note, name='delete-note'),
    path('notes/share', share_note, name='share-note'),
    path('notes/version-history/<int:id>', get_note_history, name='note-history'),"""
