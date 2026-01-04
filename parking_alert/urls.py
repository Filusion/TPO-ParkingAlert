"""
URL configuration for parking_alert project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from api.views import Test, Signup, Login, DeleteUser, EditUser, SlovenskaMestaAPI, ParkirnaMestaAPI, SlovenskeUliceAPI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', Test.as_view(), name='test'),
    path('api/signup/', Signup.as_view(), name='signup'),
    path('api/login/', Login.as_view(), name='login'),
    path('api/delete-user/', DeleteUser.as_view(), name='delete-user'),
    path('api/edit-user/', EditUser.as_view(), name='edit-user'),
    path('api/slovenska-mesta/', SlovenskaMestaAPI.as_view(), name='slovenska-mesta'),
    path('api/parkirna-mesta/', ParkirnaMestaAPI.as_view(), name='parkirna-mesta'),
    path('api/slovenske-ulice/', SlovenskeUliceAPI.as_view(), name='slovenske-ulice'),
]
