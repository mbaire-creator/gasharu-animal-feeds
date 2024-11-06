"""gasharusmanagementsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from djangogasharustore import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('bloggasharustore'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views  

urlpatterns = [
    path('', views.loginPage, name='login'),  
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('home/', views.homepage, name='homepage'), 
    path('admin/', admin.site.urls), 
    path('gasharustore/',include('gasharusstore.urls')),
]

