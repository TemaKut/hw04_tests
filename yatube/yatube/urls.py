from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('', include('posts.urls', namespace='posts')),
]
