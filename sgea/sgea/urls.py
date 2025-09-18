"""
URL configuration for sgea project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from login import views
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = 'home'),
    path("usuarios/", views.usuarios, name = 'listagem_usuarios'),
    path("cadastro_eventos/", views.ev, name = 'ev'),
    path("eventos/", views.eventos, name = 'visu_eventos'),
    path("todos_eventos/", views.todos_eventos, name = "even"),
    path("deletar_usuario/<int:pk>/", views.deletar_usuario, name = "deletar_usuario"),
    path("deletar_evento/<int:pk>/", views.deletar_evento, name = "deletar_evento"),
    path("login/", views.loginU, name = "login"),
    path("home_inscricao/", views.home_inscricao, name = "inscricao"),
    path("inscrever/<int:usuario_id>/<int:evento_id>/", views.inscricao_evento, name = "inscricao_evento"),
    path("meus_eventos/<int:usuario_id>/", views.usuario_eventos, name = "meus_eventos"),
]
